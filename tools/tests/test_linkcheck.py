"""Link checker policies, tested against a fake opener. No network."""
import importlib.util
import unittest
import urllib.error
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('linkcheck', REPO / 'tools/linkcheck.py')
linkcheck = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(linkcheck)

CONFIG = {'timeout': 5, 'retries': 3, 'hosts': {
    'developer.apple.com': {'apple_json': True},
    'm3.material.io': {'sitemap': 'https://m3.material.io/sitemap.xml'},
    'medium.com': {'blocked_status': [403]},
}}


def make_opener(routes):
    calls = []

    def opener(url, method, headers, timeout):
        calls.append((method, url))
        outcome = routes.get(url)
        if callable(outcome):
            outcome = outcome()
        if isinstance(outcome, Exception):
            raise outcome
        status, final, body = outcome
        if status >= 400:
            raise urllib.error.HTTPError(url, status, 'x', {}, None)
        return status, final, body
    return opener, calls


class LinkcheckTest(unittest.TestCase):
    def check(self, routes, url):
        opener, calls = make_opener(routes)
        checker = linkcheck.Checker(CONFIG, opener=opener, sleep=lambda s: None)
        return checker.check(url), calls

    def test_ok_and_broken(self):
        r, _ = self.check({'https://a.org/x': (200, 'https://a.org/x', b'')}, 'https://a.org/x')
        self.assertEqual('OK', r['class'])
        r, _ = self.check({'https://a.org/gone': (404, 'https://a.org/gone', b'')}, 'https://a.org/gone')
        self.assertEqual('BROKEN', r['class'])

    def test_apple_json_404_is_broken_even_when_shell_is_200(self):
        page = 'https://developer.apple.com/documentation/swiftui/nothing'
        routes = {page: (200, page, b''), 'https://developer.apple.com/tutorials/data/documentation/swiftui/nothing.json': (404, '', b'')}
        r, _ = self.check(routes, page)
        self.assertEqual('BROKEN', r['class'])
        routes['https://developer.apple.com/tutorials/data/documentation/swiftui/nothing.json'] = (200, '', b'{"a": 1}')
        r, _ = self.check(routes, page)
        self.assertEqual('OK', r['class'])

    def test_m3_page_missing_from_sitemap_warns(self):
        page = 'https://m3.material.io/styles/color/roles'
        routes = {page: (200, page, b''), 'https://m3.material.io/sitemap.xml': (200, '', b'<url><loc>https://m3.material.io/styles/color/overview</loc></url>')}
        r, _ = self.check(routes, page)
        self.assertEqual('REDIRECT', r['class'])
        routes['https://m3.material.io/sitemap.xml'] = (200, '', b'<loc>https://m3.material.io/styles/color/roles</loc>')
        checker = linkcheck.Checker(CONFIG, opener=make_opener(routes)[0], sleep=lambda s: None)
        self.assertEqual('OK', checker.check(page)['class'])

    def test_429_then_200_and_medium_403_is_blocked(self):
        attempts = {'n': 0}

        def flaky():
            attempts['n'] += 1
            return (429, '', b'') if attempts['n'] == 1 else (200, 'https://b.org/y', b'')
        r, calls = self.check({'https://b.org/y': flaky}, 'https://b.org/y')
        self.assertEqual('OK', r['class'])
        self.assertEqual(2, attempts['n'])
        r, _ = self.check({'https://medium.com/p': (403, '', b'')}, 'https://medium.com/p')
        self.assertEqual('BLOCKED', r['class'])

    def test_permanent_redirect_and_transport_error(self):
        r, _ = self.check({'https://c.org/old': (200, 'https://c.org/new', b'')}, 'https://c.org/old')
        self.assertEqual('REDIRECT', r['class'])
        r, _ = self.check({'https://d.org/x': urllib.error.URLError('dns')}, 'https://d.org/x')
        self.assertEqual('ERROR', r['class'])

    def test_url_harvest_strips_punctuation_and_fragments(self):
        self.assertEqual(['https://a.org/x'], linkcheck.body_urls('see https://a.org/x. and https://a.org/x,'))
        apple = 'https://developer.apple.com/documentation/swiftui/view/alert(_:ispresented:presenting:actions:message:)'
        self.assertEqual([apple], linkcheck.body_urls(f'see [alert]({apple}) and {apple}.'))
        self.assertEqual([], linkcheck.body_urls('pattern https://developer.apple.com/tutorials/data/documentation/<path>.json here'))
        found = linkcheck.urls_in_scope({'include': ['tools/tests/test_linkcheck.py'], 'skip_url_substrings': ['<']})
        self.assertTrue(all('#' not in u for u in found))


if __name__ == '__main__':
    unittest.main()
