"""Rules of the pr-review poster: bodies, vote, reconciliation and both host adapters, run against fakes."""
import importlib.util
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
        raw = {'value': [{'id': i, 'status': s, 'comments': [{'content': f'_pr-review M{i}_'}]}
                         for i, s in enumerate(['active', 'fixed', 'closed', 'wontFix', 'byDesign'], 1)]}
        ado, _ = self.make([raw])
        threads = ado.threads()
        self.assertEqual([ACTIVE, BOT, BOT, HUMAN, HUMAN], [t['status'] for t in threads])
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
