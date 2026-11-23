"""Rules of the pr-review poster: bodies, vote, reconciliation and both host adapters, run against fakes."""
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / 'claude/plugins/pr-review/skills/pr-review/scripts'
SPEC = importlib.util.spec_from_file_location('post_review', SCRIPTS / 'post_review.py')
post_review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(post_review)

ACTIVE, BOT, HUMAN = post_review.ACTIVE, post_review.BOT_RESOLVED, post_review.HUMAN_RESOLVED


class FakeHost:
    """A host adapter that records what the core asks of it."""

    def __init__(self, anchorable=True):
        self.calls = []
        self.anchorable = anchorable

    def create_thread(self, content, path=None, line=None, status='active'):
        self.calls.append(('create', content.split('\n', 1)[0], path, line))
        if not self.anchorable:
            return None
        return {'id': 99, 'status': ACTIVE, 'comments': [content], 'url': 'https://host/t/99'}

    def reply(self, thread, content):
        self.calls.append(('reply', thread['id'], content.split(' at ')[0].split('. ')[0]))

    def set_status(self, thread, status):
        self.calls.append(('status', thread['id'], status))

    def kinds(self):
        return [c[0] + (':' + c[2] if c[0] == 'status' else '') for c in self.calls]


def finding(fid, severity, status='open', **extra):
    return {'id': fid, 'severity': severity, 'status': status, 'title': fid, 'pr_comment': 'x',
            'file': 'a.kt', 'line': 3, **extra}


def thread(tid, status, comments=()):
    return {'id': tid, 'status': status, 'comments': list(comments), 'url': f'https://host/t/{tid}'}


def doc(*findings, verdict='request_changes', **scope):
    return {'schema': 'pr-review/v1', 'mode': 'feature', 'verdict': verdict, 'findings': list(findings),
            'scope': {'source_head': 'abc123def4567', 'merge_base': '0123456789ab', 'target': 'develop', **scope}}


class BodyTest(unittest.TestCase):
    def test_finding_body_explains_itself(self):
        body = post_review.finding_body(finding('M1', 'major', root_cause='the seam is missing',
                                                symptom_sites=['b.kt:9'], verify_fixed_when='a test fails'))
        self.assertIn('**Major** (please ticket, does not block the merge) · **M1**', body)
        self.assertIn('**Why:** the seam is missing', body)
        self.assertIn('**Also at:** `b.kt:9`', body)
        self.assertIn('**Verified fixed when:** a test fails', body)
        self.assertNotIn('[pr-review:', body)
        self.assertEqual('M1', post_review.marker_of(body))

    def test_markers_new_and_legacy(self):
        self.assertEqual('M1', post_review.marker_of('_pr-review M1 · see the review summary_'))
        self.assertEqual('summary', post_review.marker_of('_pr-review summary_'))
        self.assertEqual('B2', post_review.marker_of('old text [pr-review:B2]'))
        self.assertIsNone(post_review.marker_of('mentions M1 but no marker'))
        by = post_review.index_threads([thread(1, ACTIVE, ['[pr-review:M1]']), thread(2, ACTIVE, ['_pr-review N1_'])])
        self.assertEqual({'M1', 'N1'}, set(by))

    def test_summary_carries_scope_legend_index_nits_and_credit(self):
        d = doc(finding('M1', 'major'), finding('N1', 'nit'), verdict='approve_with_comments', commits=1, files=28)
        d['genuinely_good'] = ['clean seams']
        body = post_review.summary_body(d, {'M1': thread(7, ACTIVE)})
        self.assertIn('**Verdict: Approve with comments.**', body)
        self.assertIn('`0123456789ab..abc123def456` against `develop` (1 commit, 28 files)', body)
        self.assertIn('**Major** please ticket, does not block the merge', body)
        self.assertIn('| [M1](https://host/t/7) | Major |', body)
        self.assertIn('- **N1** N1, `a.kt:3`. x', body)
        self.assertIn('- clean seams', body)
        self.assertEqual('summary', post_review.marker_of(body))

    def test_summary_promotion_scope_and_plurals(self):
        d = doc(finding('B1', 'blocker'), commits=3, files=1, source='sit')
        d['mode'] = 'promotion'
        body = post_review.summary_body(d)
        self.assertIn('cover only the sit to develop delta', body)
        self.assertIn('(3 commits, 1 file)', body)
        self.assertIn('not technical sign-off', body)

    def test_summary_lists_unanchored_findings(self):
        f = finding('M1', 'major')
        body = post_review.summary_body(doc(f), {}, [f])
        self.assertIn('(outside the diff, see below)', body)
        self.assertIn('**Outside the diff.**', body)


class VoteTest(unittest.TestCase):
    def test_open_blocker_gates(self):
        self.assertEqual('waiting_for_author', post_review.compute_vote(doc(finding('B1', 'blocker')), {}, False))

    def test_regressed_and_partial_blockers_gate(self):
        for status in ('regressed', 'partial'):
            self.assertEqual('waiting_for_author',
                             post_review.compute_vote(doc(finding('B1', 'blocker', status)), {}, False), status)

    def test_human_resolution_does_not_lift_a_blocker(self):
        self.assertEqual('waiting_for_author',
                         post_review.compute_vote(doc(finding('B1', 'blocker')), {'B1': thread(1, HUMAN)}, False))

    def test_fixed_blocker_with_open_nit_is_suggestions(self):
        d = doc(finding('B1', 'blocker', 'fixed'), finding('N1', 'nit'), verdict='approve_with_comments')
        self.assertEqual('approve_with_suggestions', post_review.compute_vote(d, {}, False))

    def test_all_fixed_is_approve(self):
        d = doc(finding('B1', 'blocker', 'fixed'), finding('M1', 'major', 'retracted'), verdict='approve')
        self.assertEqual('approve', post_review.compute_vote(d, {}, False))

    def test_question_gates_until_its_thread_is_resolved(self):
        d = doc(finding('Q1', 'question'))
        self.assertEqual('waiting_for_author', post_review.compute_vote(d, {}, False))
        self.assertEqual('approve', post_review.compute_vote(d, {'Q1': thread(1, HUMAN)}, False))

    def test_reject_flag(self):
        self.assertEqual('reject', post_review.compute_vote(doc(finding('B1', 'blocker')), {}, True))


class ValidateTest(unittest.TestCase):
    def test_unknown_severity_and_status(self):
        problems = post_review.validate(doc(finding('X1', 'minor'), finding('X2', 'nit', 'untouched')))
        self.assertEqual(2, len(problems))

    def test_gating_blocker_needs_request_changes(self):
        self.assertTrue(post_review.validate(doc(finding('B1', 'blocker', 'regressed'), verdict='approve')))
        self.assertEqual([], post_review.validate(doc(finding('B1', 'blocker', 'regressed'))))


class ReconcileTest(unittest.TestCase):
    def run_case(self, f, t, host=None):
        host = host or FakeHost()
        post_review.reconcile(host, doc(f), {} if t is None else {f['id']: t})
        return host.kinds()

    def test_missing_thread(self):
        for status in ('open', 'regressed', 'partial'):
            self.assertEqual(['create'], self.run_case(finding('B1', 'blocker', status), None), status)
        for status in ('fixed', 'retracted'):
            self.assertEqual([], self.run_case(finding('B1', 'blocker', status), None), status)

    def test_nits_get_no_new_thread(self):
        self.assertEqual([], self.run_case(finding('N1', 'nit'), None))

    def test_existing_nit_thread_still_reconciles(self):
        self.assertEqual(['reply', 'status:resolved'], self.run_case(finding('N1', 'nit', 'fixed'), thread(1, ACTIVE)))

    def test_active_thread(self):
        self.assertEqual([], self.run_case(finding('B1', 'blocker', 'open'), thread(1, ACTIVE)))
        self.assertEqual([], self.run_case(finding('B1', 'blocker', 'regressed'), thread(1, ACTIVE)))
        self.assertEqual(['reply', 'status:resolved'], self.run_case(finding('B1', 'blocker', 'fixed'), thread(1, ACTIVE)))
        self.assertEqual(['reply', 'status:closed'], self.run_case(finding('B1', 'blocker', 'retracted'), thread(1, ACTIVE)))

    def test_bot_resolved_thread(self):
        self.assertEqual(['reply', 'status:active'], self.run_case(finding('M1', 'major', 'open'), thread(1, BOT)))
        self.assertEqual([], self.run_case(finding('Q1', 'question', 'open'), thread(1, BOT)))
        self.assertEqual(['reply', 'status:active'], self.run_case(finding('B1', 'blocker', 'regressed'), thread(1, BOT)))
        self.assertEqual(['reply', 'status:active'], self.run_case(finding('B1', 'blocker', 'partial'), thread(1, BOT)))
        self.assertEqual([], self.run_case(finding('B1', 'blocker', 'fixed'), thread(1, BOT)))

    def test_person_resolved_open_nit_is_left_alone(self):
        self.assertEqual([], self.run_case(finding('N4', 'nit', 'open'), thread(1, HUMAN)))

    def test_human_resolution_is_never_reopened(self):
        self.assertEqual([], self.run_case(finding('M1', 'major', 'open'), thread(1, HUMAN)))
        self.assertEqual(['reply'], self.run_case(finding('M1', 'major', 'regressed'), thread(1, HUMAN)))
        already = thread(1, HUMAN, comments=['Marked regressed at `abc` _pr-review M1_'])
        self.assertEqual([], self.run_case(finding('M1', 'major', 'regressed'), already))
        self.assertEqual([], self.run_case(finding('M1', 'major', 'fixed'), thread(1, HUMAN)))

    def test_unanchorable_finding_moves_to_summary(self):
        f = finding('M1', 'major')
        threads, outside = post_review.reconcile(FakeHost(anchorable=False), doc(f), {})
        self.assertEqual({}, threads)
        self.assertEqual(['M1'], [o['id'] for o in outside])


class FakeHttp:
    """Stands in for post_review.Http: records calls and replays scripted responses or errors."""

    def __init__(self, responses=()):
        self.calls = []
        self.responses = list(responses)
        self.dry_run = False

    def call(self, method, url, body=None, content_type='application/json', read_only=False):
        self.calls.append((method, url, body))
        response = self.responses.pop(0) if self.responses else {}
        if isinstance(response, Exception):
            raise response
        return response

    def upload(self, url, data, content_type='application/octet-stream'):
        return self.call('UPLOAD', url, len(data), content_type)


class AzureAdapterTest(unittest.TestCase):
    def make(self, responses=(), token='pat'):
        ado = post_review.AzureDevOps('https://dev.azure.com/org', 'Proj', 'repo', 5, token, False)
        auth = ado.http.auth_header
        ado.http = FakeHttp(responses)
        return ado, auth

    def test_auth_header_per_token_kind(self):
        self.assertTrue(self.make(token='plainpat')[1].startswith('Basic '))
        self.assertEqual('Bearer eyJa.b.c', self.make(token='eyJa.b.c')[1])

    def test_status_mapping_and_thread_url(self):
        def raw_thread(i, status, *replies):
            bodies = [f'_pr-review M{i}_', *replies]
            return {'id': i, 'status': status, 'comments': [{'content': c} for c in bodies]}
        raw = {'value': [
            raw_thread(1, 'active'),
            raw_thread(2, 'fixed', 'Verified fixed at `abc` (criterion met). _pr-review M2_'),
            raw_thread(3, 'closed', 'Retracted. This finding was wrong. _pr-review M3_'),
            raw_thread(4, 'wontFix'),
            raw_thread(5, 'byDesign'),
            raw_thread(6, 'fixed'),  # a person clicked Resolve, which also sets `fixed`
            raw_thread(7, 'fixed', 'Verified fixed at `a`. _pr-review M7_', 'Still open at `b`. _pr-review M7_'),
        ]}
        ado, _ = self.make([raw])
        threads = ado.threads()
        self.assertEqual([ACTIVE, BOT, BOT, HUMAN, HUMAN, HUMAN, HUMAN], [t['status'] for t in threads])
        self.assertTrue(threads[2]['url'].endswith('/Proj/_git/repo/pullrequest/5?discussionId=3'))

    def test_set_status_and_summary_edit(self):
        ado, _ = self.make()
        ado.set_status({'id': 4}, 'resolved')
        ado.upsert_summary('body', {'id': 8})
        self.assertEqual({'status': 'fixed'}, ado.http.calls[0][2])
        self.assertEqual(('PATCH', {'content': 'body'}), (ado.http.calls[1][0], ado.http.calls[1][2]))
        self.assertIn('/threads/8/comments/1', ado.http.calls[1][1])

    def test_vote_values(self):
        ado, _ = self.make([{'authenticatedUser': {'id': 'me'}}, {}])
        ado.vote('waiting_for_author')
        self.assertEqual({'vote': -5, 'id': 'me'}, ado.http.calls[1][2])


class GitHubAdapterTest(unittest.TestCase):
    def make(self, responses=()):
        gh = post_review.GitHub('o', 'r', 3, 'tok', 'abc123', False)
        gh.http = FakeHttp(responses)
        return gh

    def graph(self, nodes):
        return {'data': {'repository': {'pullRequest': {'reviewThreads': {
            'pageInfo': {'hasNextPage': False}, 'nodes': nodes}}}}}

    def node(self, tid, resolved, bodies):
        return {'id': tid, 'isResolved': resolved,
                'comments': {'nodes': [{'databaseId': 10, 'body': b, 'url': f'https://gh/{tid}'} for b in bodies]}}

    def test_resolution_owner_is_read_from_the_posters_own_replies(self):
        gh = self.make([self.graph([
            self.node('T1', False, ['_pr-review M1 · s_']),
            self.node('T2', True, ['_pr-review M2 · s_', 'Verified fixed at `abc` (criterion met). _pr-review M2_']),
            self.node('T3', True, ['_pr-review M3 · s_']),
            self.node('T4', True, ['_pr-review M4 · s_', 'Verified fixed at `a`. _pr-review M4_',
                                   'Still open at `b`, re-verified. _pr-review M4_']),
        ])])
        self.assertEqual([ACTIVE, BOT, HUMAN, HUMAN], [t['status'] for t in gh.threads()])

    def test_create_anchors_at_head_and_falls_back_on_422(self):
        gh = self.make([{'id': 55, 'html_url': 'https://gh/pull/3#discussion_r55'}])
        t = gh.create_thread('body', '/a.kt', 9)
        self.assertEqual({'body': 'body', 'commit_id': 'abc123', 'path': 'a.kt', 'line': 9, 'side': 'RIGHT'},
                         gh.http.calls[0][2])
        self.assertEqual((55, 'https://gh/pull/3#discussion_r55'), (t['first_comment'], t['url']))
        gh = self.make([post_review.HostError(422, 'line must be part of the diff')])
        self.assertIsNone(gh.create_thread('body', 'a.kt', 900))

    def test_resolve_and_reopen_use_graphql(self):
        gh = self.make()
        gh.set_status({'id': 'T1'}, 'resolved')
        gh.set_status({'id': 'T1'}, 'active')
        self.assertIn('resolveReviewThread', gh.http.calls[0][2]['query'])
        self.assertIn('unresolveReviewThread', gh.http.calls[1][2]['query'])

    def test_summary_is_edited_in_place(self):
        gh = self.make([[{'id': 1, 'body': 'hello'}, {'id': 2, 'body': 'old\n_pr-review summary_'}], {}])
        gh.upsert_summary('new', None)
        self.assertEqual(('PATCH', {'body': 'new'}), (gh.http.calls[1][0], gh.http.calls[1][2]))
        self.assertTrue(gh.http.calls[1][1].endswith('/issues/comments/2'))
        gh = self.make([[], {}])
        gh.upsert_summary('new', None)
        self.assertEqual('POST', gh.http.calls[1][0])

    def test_refused_approval_falls_back_to_comment(self):
        gh = self.make([post_review.HostError(422, 'Can not approve your own pull request'), {}])
        gh.vote('approve_with_suggestions')
        self.assertEqual(['APPROVE', 'COMMENT'], [c[2]['event'] for c in gh.http.calls])


class HostDetectionTest(unittest.TestCase):
    def test_order(self):
        detect = post_review.detect_host
        self.assertEqual('github', detect('github', {}, {}, ''))
        self.assertEqual('azure', detect('auto', {'scope': {'host': 'azure'}}, {'GITHUB_ACTIONS': 'true'}, ''))
        self.assertEqual('azure', detect('auto', {}, {'TF_BUILD': 'True'}, 'https://github.com/a/b'))
        self.assertEqual('github', detect('auto', {}, {'GITHUB_ACTIONS': 'true'}, ''))
        self.assertEqual('azure', detect('auto', {}, {}, 'org@vs-ssh.visualstudio.com:v3/org/p/r'))
        self.assertEqual('github', detect('auto', {}, {}, 'git@github.com:a/b.git'))
        with self.assertRaises(SystemExit):
            detect('auto', {}, {}, 'https://gitlab.com/a/b')


PNG = b'\x89PNG\r\n\x1a\n' + b'0' * 32


def shot(**extra):
    return {'kind': 'device_harness', 'path': 'pr-review-evidence/7-m1-lookup.png',
            'caption': 'Continue enabled for a lookup address.', 'method': 'Real screen on an emulator, repository mocked',
            'sha': 'abc123def4567890', 'device': 'API 36 emulator', **extra}


class EvidenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = self.tmp.name
        (Path(self.base) / 'pr-review-evidence').mkdir()
        (Path(self.base) / 'pr-review-evidence/7-m1-lookup.png').write_bytes(PNG)

    def tearDown(self):
        self.tmp.cleanup()

    def test_body_embeds_an_uploaded_image_under_its_caption_and_method(self):
        body = post_review.finding_body(finding('M1', 'major', evidence=[shot()]),
                                        {'pr-review-evidence/7-m1-lookup.png': 'https://host/a/7-m1-lookup.png'})
        self.assertIn('**Evidence:** Continue enabled for a lookup address. Method: Real screen on an emulator, '
                      'repository mocked, at `abc123def456` on API 36 emulator.', body)
        self.assertIn('![Continue enabled for a lookup address](https://host/a/7-m1-lookup.png)', body)
        self.assertEqual('M1', post_review.marker_of(body))
        self.assertLess(body.index('![Continue'), body.index('_pr-review M1'))

    def test_body_falls_back_to_the_document_or_the_items_url(self):
        self.assertIn('Image `7-m1-lookup.png` is in the review document.',
                      post_review.finding_body(finding('M1', 'major', evidence=[shot()])))
        hosted = post_review.finding_body(finding('M1', 'major', evidence=[shot(url='https://wiki/x.png')]))
        self.assertIn('![Continue enabled for a lookup address](https://wiki/x.png)', hosted)

    def test_excerpt_renders_as_a_text_fence(self):
        item = {'kind': 'unit_test', 'caption': 'Fails', 'method': 'JVM unit test', 'excerpt': 'expected false\n'}
        self.assertIn('```text\nexpected false\n```', post_review.finding_body(finding('M1', 'major', evidence=[item])))

    def test_a_finding_without_evidence_keeps_its_body(self):
        f = finding('M1', 'major', verify_fixed_when='a test fails')
        self.assertEqual(post_review.finding_body(f), post_review.finding_body(dict(f, evidence=[])))
        self.assertNotIn('Evidence', post_review.finding_body(f))

    def test_validation(self):
        def problems(*items, severity='major'):
            return post_review.validate(doc(finding('M1', severity, evidence=list(items))), self.base)
        self.assertEqual([], problems(shot()))
        self.assertEqual([], problems({'kind': 'transcript', 'caption': 'c', 'method': 'm', 'excerpt': 'HTTP/1.1 500'}))
        self.assertIn('unknown kind', problems(shot(kind='photo'))[0])
        self.assertIn('method is required', problems(shot(method=''))[0])
        self.assertIn('must be relative', problems(shot(path='/Users/me/x.png'))[0])
        self.assertIn('must be relative', problems(shot(path='pr-review-evidence/../../x.png'))[0])
        self.assertIn('not an image', problems(shot(path='pr-review-evidence/x.exe'))[0])
        self.assertIn('not found', problems(shot(path='pr-review-evidence/missing.png'))[0])
        self.assertIn('path is required', problems({'kind': 'render', 'caption': 'c', 'method': 'm'})[0])
        self.assertIn('blockers, questions and majors', problems(shot(), severity='nit')[0])
        big = Path(self.base) / 'pr-review-evidence/big.png'
        big.write_bytes(b'0' * (post_review.MAX_EVIDENCE_BYTES + 1))
        self.assertIn('larger than 5 MB', problems(shot(path='pr-review-evidence/big.png'))[0])

    def test_reconcile_uploads_only_for_a_new_thread(self):
        class Attaching(FakeHost):
            def attach(self, base_dir, path):
                self.calls.append(('attach', path))
                return 'https://host/a/' + path.rsplit('/', 1)[-1]
        host = Attaching()
        post_review.reconcile(host, doc(finding('M1', 'major', evidence=[shot()])), {}, self.base)
        self.assertEqual(['attach', 'create'], [c[0] for c in host.calls])
        host = Attaching()
        existing = {'M1': thread(4, ACTIVE, ['_pr-review M1 · x_'])}
        post_review.reconcile(host, doc(finding('M1', 'major', evidence=[shot()])), existing, self.base)
        self.assertEqual([], host.calls)

    def test_azure_uploads_the_file_and_reuses_a_matching_name(self):
        ado = post_review.AzureDevOps('https://dev.azure.com/org', 'Proj', 'repo', 5, 'pat', False)
        ado.http = FakeHttp([{'value': [{'displayName': 'old.png', 'url': 'https://ado/old'}]},
                             {'url': 'https://ado/new'}])
        self.assertEqual('https://ado/new', ado.attach(self.base, 'pr-review-evidence/7-m1-lookup.png'))
        self.assertEqual('https://ado/old', ado.attach(self.base, 'pr-review-evidence/old.png'))
        method, url, size = ado.http.calls[1]
        self.assertEqual('UPLOAD', method)
        self.assertTrue(url.endswith('/pullRequests/5/attachments/7-m1-lookup.png?api-version=7.1'))
        self.assertEqual(len(PNG), size)
        self.assertEqual(2, len(ado.http.calls))

    def test_azure_dry_run_prints_the_upload_and_a_placeholder(self):
        ado = post_review.AzureDevOps('https://dev.azure.com/org', 'Proj', 'repo', 5, '', True)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            url = ado.attach(self.base, 'pr-review-evidence/7-m1-lookup.png')
        self.assertEqual('DRY-RUN-ATTACHMENT/7-m1-lookup.png', url)
        self.assertIn(f'<{len(PNG)} bytes, application/octet-stream>', out.getvalue())

    def test_github_and_emit_mode_name_the_file(self):
        gh = post_review.GitHub('o', 'r', 1, '', 'abc', True)
        self.assertIsNone(gh.attach(self.base, 'pr-review-evidence/7-m1-lookup.png'))
        findings = Path(self.base) / 'f.json'
        findings.write_text(json.dumps(doc(finding('M1', 'major', evidence=[shot()]), verdict='approve_with_comments')))
        out = Path(self.base) / 'threads.json'
        self.assertEqual(0, post_review.main([str(findings), '--host', 'azure', '--emit-threads', str(out)]))
        actions = json.loads(out.read_text())['actions']
        self.assertEqual({'action': 'attach', 'path': 'pr-review-evidence/7-m1-lookup.png'}, actions[0])
        self.assertIn('Image `7-m1-lookup.png` is in the review document.', actions[1]['body'])

    def test_entry_point_rejects_a_missing_file(self):
        findings = Path(self.base) / 'f.json'
        findings.write_text(json.dumps(doc(finding('M1', 'major', evidence=[shot(path='pr-review-evidence/no.png')]))))
        with self.assertRaises(SystemExit) as raised:
            post_review.main([str(findings), '--host', 'azure', '--dry-run'])
        self.assertIn('not found beside findings.json', str(raised.exception))


class EntryPointTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.findings = Path(self.tmp.name) / 'f.json'
        d = doc(finding('M1', 'major'), finding('N1', 'nit'), verdict='approve_with_comments', commits=1, files=2)
        self.findings.write_text(json.dumps(d))

    def tearDown(self):
        self.tmp.cleanup()

    def test_emit_threads_matches_the_live_bodies(self):
        out = Path(self.tmp.name) / 'threads.json'
        self.assertEqual(0, post_review.main([str(self.findings), '--host', 'github', '--emit-threads', str(out)]))
        actions = json.loads(out.read_text())['actions']
        self.assertEqual(['create_thread', 'summary', 'vote'], [a['action'] for a in actions])
        d = json.loads(self.findings.read_text())
        self.assertEqual(post_review.finding_body(d['findings'][0]), actions[0]['body'])

    def test_token_file_is_read_and_stripped(self):
        token = Path(self.tmp.name) / 'pat'
        token.write_text('secret\n')
        self.assertEqual('secret', post_review.read_token_file(str(token)))

    def test_azdo_shim_forwards_to_azure(self):
        env = {k: v for k, v in os.environ.items()
               if k not in ('SYSTEM_ACCESSTOKEN', 'AZURE_DEVOPS_EXT_PAT', 'AZURE_DEVOPS_TOKEN_FILE')}
        result = subprocess.run([sys.executable, str(SCRIPTS / 'post_azdo.py'), str(self.findings), '--dry-run',
                                 '--no-vote', '--org-url', 'https://dev.azure.com/org', '--project', 'P',
                                 '--repo', 'r', '--pr', '1'], capture_output=True, text=True, env=env)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('dev.azure.com/org/P/_apis/git/repositories/r/pullRequests/1/threads', result.stdout)
        self.assertIn('host=azure', result.stdout)


if __name__ == '__main__':
    unittest.main()
