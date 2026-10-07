"""Source anchor parsing, extraction, verification and lint, tested against a fake opener. No network."""
import importlib.util
import json
import tempfile
import unittest
import urllib.error
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('source_anchors', REPO / 'tools/source_anchors.py')
anchors = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(anchors)

CONFIG = {'retries': 2, 'browser_hosts': ['m3.material.io'], 'max_quote_chars': 300,
          'max_quote_sentences': 2, 'hosts': {'developer.apple.com': {'apple_json': True}}}
FILLER = ' Filler text so the page is long enough to count as read.' * 5

ANCHORS = """---
verified: 2026-10-01
sources: inline
---

# Source anchors

### HIG-LAYOUT
- URL: https://developer.apple.com/design/human-interface-guidelines/layout
- Quote: "Respecting the safe area is essential to make sure system UI doesn’t obstruct content."
- Confirmed: not yet

### AND-A11Y
- URL: https://developer.android.com/guide/topics/ui/accessibility/apps
- Quote: "Each interactive UI element has a touch target of at least 48dp."
- Confirmed: 2026-09-29 (html)

### M3-MOTION
- URL: https://m3.material.io/styles/motion/overview/how-it-works
- Quote: "The physics system has two preset motion schemes"

### House
- URL: https://github.com/Mark-Hine/ai-toolkit
- Quote: none (house)
"""

APPLE_JSON = json.dumps({'primaryContentSections': [{'content': [{'type': 'paragraph', 'inlineContent': [
    {'type': 'text', 'text': 'Respecting the safe area is essential to make sure system UI '},
    {'type': 'emphasis', 'inlineContent': [{'type': 'text', 'text': "doesn't"}]},
    {'type': 'text', 'text': ' obstruct content.' + FILLER}]}]}]}).encode()
ANDROID_HTML = (b'<html><head><script>var x = "Each interactive";</script></head><body><p>Each interactive UI '
                b'element has a touch target of <b>at least 48dp</b>.</p><p>' + FILLER.encode() + b'</p></body></html>')


def opener_for(routes):
    def opener(url, method, headers, timeout):
        assert 'Mozilla' in headers['User-Agent'], 'pages are read with a browser user agent'
        status, body = routes.get(url, (404, b''))
        if status >= 400:
            raise urllib.error.HTTPError(url, status, 'x', {}, None)
        return status, url, body
    return opener


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'source-anchors.md'
        self.path.write_text(ANCHORS, encoding='utf-8')
        self.items, self.problems = anchors.parse(self.path)
        self.by_key = {a.key: a for a in self.items}

    def tearDown(self):
        self.tmp.cleanup()

    def reader(self, routes, chrome=None, dom=None):
        r = anchors.Reader(CONFIG, opener=opener_for(routes), chrome=chrome, sleep=lambda s: None)
        if dom:
            r.dom = dom
        return r


class ParseAndMatchTest(Fixture):
    def test_parse(self):
        self.assertEqual([], self.problems)
        self.assertEqual(['HIG-LAYOUT', 'AND-A11Y', 'M3-MOTION', 'House'], [a.key for a in self.items])
        self.assertEqual('not yet', self.by_key['HIG-LAYOUT'].confirmed)
        self.assertTrue(self.by_key['House'].no_quote)
        self.assertIsNone(self.by_key['M3-MOTION'].confirmed)

    def test_matching_ignores_whitespace_markup_and_curly_quotes(self):
        page = anchors.normalise('Respecting the safe\n area is essential to make sure system UI doesn\'t  obstruct content.')
        self.assertIn(anchors.normalise('Respecting the safe area is essential to make sure system UI doesn’t obstruct content.'), page)

    def test_soft_hyphens_are_ignored(self):
        self.assertIn(anchors.normalise('Aim for an average line length'), anchors.normalise('Aim for an av\u00aderage line length'))

    def test_extractors(self):
        self.assertIn("doesn't", anchors.apple_text(APPLE_JSON))
        text = anchors.html_text(ANDROID_HTML.decode())
        self.assertNotIn('var x', text)
        self.assertIn('touch target of at least 48dp', text)


class VerifyTest(Fixture):
    ROUTES = {
        'https://developer.apple.com/tutorials/data/design/human-interface-guidelines/layout.json': (200, APPLE_JSON),
        'https://developer.android.com/guide/topics/ui/accessibility/apps': (200, ANDROID_HTML),
    }

    def test_confirmed_through_apple_json_and_html(self):
        reader = self.reader(self.ROUTES)
        apple = anchors.verify(self.by_key['HIG-LAYOUT'], reader)
        self.assertEqual(('CONFIRMED', 'apple-json'), (apple['status'], apple['method']))
        android = anchors.verify(self.by_key['AND-A11Y'], reader)
        self.assertEqual(('CONFIRMED', 'html'), (android['status'], android['method']))

    def test_drifted_when_the_quote_is_gone(self):
        routes = dict(self.ROUTES)
        routes['https://developer.android.com/guide/topics/ui/accessibility/apps'] = (200, ANDROID_HTML.replace(b'48dp', b'44dp'))
        result = anchors.verify(self.by_key['AND-A11Y'], self.reader(routes))
        self.assertEqual('DRIFTED', result['status'])

    def test_unreachable_page_and_missing_chrome(self):
        result = anchors.verify(self.by_key['AND-A11Y'], self.reader({}))
        self.assertEqual('UNREACHABLE', result['status'])
        result = anchors.verify(self.by_key['M3-MOTION'], self.reader({}, chrome=None))
        self.assertEqual(('UNREACHABLE', 'browser'), (result['status'], result['method']))

    def test_a_bot_block_page_is_unreachable_not_drifted(self):
        block = b'<title>Attention Required! | Cloudflare</title><p>Sorry, you have been blocked.' + FILLER.encode() + b'</p>'
        routes = {'https://developer.android.com/guide/topics/ui/accessibility/apps': (200, block)}
        result = anchors.verify(self.by_key['AND-A11Y'], self.reader(routes))
        self.assertEqual('UNREACHABLE', result['status'])

    def test_browser_host_reads_the_rendered_dom(self):
        dom = lambda url, chrome, timeout: '<main>The physics system has two preset motion schemes: expressive and standard.' + FILLER + '</main>'
        result = anchors.verify(self.by_key['M3-MOTION'], self.reader({}, chrome='/bin/chrome', dom=dom))
        self.assertEqual(('CONFIRMED', 'browser'), (result['status'], result['method']))

    def test_a_page_is_read_once_for_many_anchors(self):
        calls = []
        base = opener_for(self.ROUTES)

        def counting(url, method, headers, timeout):
            calls.append(url)
            return base(url, method, headers, timeout)
        reader = anchors.Reader(CONFIG, opener=counting, sleep=lambda s: None)
        twin = anchors.Anchor('AND-A11Y-2', self.path, 99)
        twin.url = 'https://developer.android.com/guide/topics/ui/accessibility/apps#labels'
        twin.quotes = ['at least 48dp']
        self.assertEqual('CONFIRMED', anchors.verify(self.by_key['AND-A11Y'], reader)['status'])
        self.assertEqual('CONFIRMED', anchors.verify(twin, reader)['status'])
        self.assertEqual(1, len(calls))

    def test_gzipped_body_is_decompressed(self):
        import gzip
        routes = {'https://developer.android.com/guide/topics/ui/accessibility/apps': (200, gzip.compress(ANDROID_HTML))}
        self.assertEqual('CONFIRMED', anchors.verify(self.by_key['AND-A11Y'], self.reader(routes))['status'])

    def test_house_anchor_is_skipped(self):
        self.assertEqual('SKIPPED', anchors.verify(self.by_key['House'], self.reader({}))['status'])

    def test_write_records_the_date_and_stamp(self):
        reader = self.reader(self.ROUTES)
        results = [anchors.verify(a, reader) for a in self.items[:2]]
        anchors.write_confirmed(results, date(2026, 10, 7))
        text = self.path.read_text(encoding='utf-8')
        self.assertIn('verified: 2026-10-07', text)
        self.assertIn('- Confirmed: 2026-10-07 (apple-json)', text)
        self.assertIn('- Confirmed: 2026-10-07 (html)', text)
        self.assertEqual(4, len(anchors.parse(self.path)[0]))


class LintTest(unittest.TestCase):
    def lint(self, text, enforce=False, registries=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'refs').mkdir()
            (root / 'refs/source-anchors.md').write_text(text, encoding='utf-8')
            (root / 'refs/registry.md').write_text('[MASVS]: https://mas.owasp.org/MASVS/\n[OSV]: https://osv.dev\n', encoding='utf-8')
            config = dict(CONFIG, anchors=['refs/source-anchors.md'], enforce=enforce, registries=registries or [])
            original_root = anchors.ROOT
            try:
                anchors.ROOT = root
                return anchors.lint(config, date(2026, 10, 7))
            finally:
                anchors.ROOT = original_root

    def test_clean_file(self):
        errors, warnings = self.lint(ANCHORS)
        self.assertEqual([], errors)
        self.assertTrue(any('HIG-LAYOUT is not confirmed yet' in w for w in warnings))

    def test_format_errors(self):
        bad = ('### A\n- URL: http://a.org\n- Quote: "' + 'x' * 301 + '"\n- Confirmed: soon\n'
               '### B\n- URL: https://b.org\n- Quote: to fetch\n- Confirmed: 2027-01-01 (html)\n'
               '### C\n- URL: https://c.org\n- Quote: "One. Two. Three."\n- Source: x\n')
        errors, _ = self.lint(bad)
        joined = '\n'.join(errors)
        for fragment in ('A needs an https URL', 'A quote is 301 characters', 'A Confirmed must read',
                         'B still says "to fetch"', 'B is confirmed on a future date',
                         'C quote has more than 2 sentences', 'unknown anchor field'):
            self.assertIn(fragment, joined)

    def test_a_quote_that_mentions_fetching_is_fine(self):
        errors, _ = self.lint('### R\n- URL: https://react.dev/x\n- Quote: "Writing fetch calls is a popular way to fetch data."\n')
        self.assertEqual([], errors)

    def test_coverage_is_a_warning_until_enforced(self):
        registry = [{'files': ['refs/registry.md'], 'pattern': r'^\[([A-Z0-9-]+)\]: https://', 'mode': 'key'}]
        text = '### MASVS\n- URL: https://mas.owasp.org/MASVS/\n- Quote: "The standard."\n'
        errors, warnings = self.lint(text, registries=registry)
        self.assertFalse(any('OSV' in e for e in errors))
        self.assertTrue(any('OSV has no source anchor' in w for w in warnings))
        errors, _ = self.lint(text, enforce=True, registries=registry)
        self.assertTrue(any('OSV has no source anchor' in e for e in errors))

    def test_url_mode_matches_without_fragment(self):
        registry = [{'files': ['refs/registry.md'], 'pattern': r'(https://osv\.dev)', 'mode': 'url'}]
        text = '### OSV\n- URL: https://osv.dev/#top\n- Quote: "A database."\n'
        errors, _ = self.lint(text, enforce=True, registries=registry)
        self.assertEqual([], errors)


if __name__ == '__main__':
    unittest.main()
