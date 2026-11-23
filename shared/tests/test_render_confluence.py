"""Evidence images in the pr-review Confluence renderer: the storage markup and the attachment upload."""
import argparse
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / 'claude/plugins/pr-review/skills/pr-review/scripts'
SPEC = importlib.util.spec_from_file_location('render_confluence', SCRIPTS / 'render_confluence.py')
render_confluence = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render_confluence)

FINDING = """### <a id="m1"></a>M1: Lookup address passes as manual

**Evidence.** `AddressInfoViewModel.kt:120` clears the lookup ID on any edit.

![Continue enabled for a lookup address](pr-review-evidence/7-m1-lookup.png)

*Continue enabled for a lookup address. Method: real screen on an emulator, at `abc123def456`.*

[Recording of the journey](pr-review-evidence/7-m1-journey.mp4)
"""


class RenderTest(unittest.TestCase):
    def test_relative_image_becomes_a_page_attachment_outside_the_expand(self):
        out = render_confluence.render(FINDING)
        img = ('<ac:image ac:alt="Continue enabled for a lookup address" ac:title="Continue enabled for a '
               'lookup address"><ri:attachment ri:filename="7-m1-lookup.png" /></ac:image>')
        self.assertIn(img, out)
        self.assertLess(out.index('</ac:structured-macro>', out.index('ac:name="expand"')), out.index(img))
        self.assertIn('<em>Continue enabled for a lookup address. Method: real screen on an emulator, at '
                      '<code>abc123def456</code>.</em>', out)

    def test_evidence_link_becomes_an_attachment_link(self):
        out = render_confluence.render(FINDING)
        self.assertIn('<ac:link><ri:attachment ri:filename="7-m1-journey.mp4" /><ac:link-body>Recording of the '
                      'journey</ac:link-body></ac:link>', out)

    def test_external_image_uses_its_url(self):
        out = render_confluence.render('![Shot](https://example.test/a.png)\n')
        self.assertIn('<ri:url ri:value="https://example.test/a.png" />', out)
        self.assertNotIn('<a href', out)

    def test_plain_links_are_unchanged(self):
        out = render_confluence.render('[B1](#b1) and [docs](https://example.test/d)\n')
        self.assertIn('<ac:link ac:anchor="b1">', out)
        self.assertIn('<a href="https://example.test/d">docs</a>', out)


class AttachmentTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        (self.dir / 'pr-review-evidence').mkdir()
        (self.dir / 'pr-review-evidence/7-m1-lookup.png').write_bytes(b'\x89PNG')
        (self.dir / 'pr-review-evidence/7-m1-journey.mp4').write_bytes(b'mp4')

    def tearDown(self):
        self.tmp.cleanup()

    def test_referenced_attachments_resolve_or_exit(self):
        storage = render_confluence.render(FINDING)
        files = render_confluence.referenced_attachments(storage, str(self.dir / 'pr-review-evidence'))
        self.assertEqual(['7-m1-journey.mp4', '7-m1-lookup.png'], sorted(files))
        (self.dir / 'pr-review-evidence/7-m1-lookup.png').unlink()
        with self.assertRaises(SystemExit) as raised:
            render_confluence.referenced_attachments(storage, str(self.dir / 'pr-review-evidence'))
        self.assertIn('7-m1-lookup.png', str(raised.exception))

    def test_multipart_carries_the_file_and_minor_edit(self):
        body, ctype = render_confluence.multipart(str(self.dir / 'pr-review-evidence/7-m1-lookup.png'))
        boundary = ctype.split('boundary=')[1]
        self.assertTrue(ctype.startswith('multipart/form-data; boundary='))
        self.assertIn(b'name="minorEdit"\r\n\r\ntrue', body)
        self.assertIn(b'filename="7-m1-lookup.png"\r\nContent-Type: image/png\r\n\r\n\x89PNG', body)
        self.assertTrue(body.endswith(f'--{boundary}--\r\n'.encode()))

    def test_publish_uploads_after_the_page_and_refuses_a_missing_file_first(self):
        xhtml = self.dir / 'review.xhtml'
        xhtml.write_text(render_confluence.render(FINDING))
        calls = []

        class Fake:
            def __init__(self, base, email, token):
                pass

            def call(self, method, path, body=None):
                calls.append((method, path))
                return {'id': '42', 'version': {'number': 1}, '_links': {'webui': '/p/42'}}

            def set_full_width(self, page_id):
                calls.append(('width', page_id))

            def attach(self, page_id, path):
                calls.append(('attach', Path(path).name))

        args = argparse.Namespace(base_url='https://site.test/wiki', email='e', token_file=None, xhtml=str(xhtml),
                                  page_id=None, expect_version=None, title='T', space_id='1', parent_id=None,
                                  message=None, evidence_dir=None)
        real, saved = render_confluence.Confluence, render_confluence.os.environ.get('CONFLUENCE_TOKEN')
        render_confluence.Confluence = Fake
        try:
            render_confluence.os.environ['CONFLUENCE_TOKEN'] = 't'
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                render_confluence.publish(args)
            self.assertEqual([('POST', '/pages'), ('width', '42'), ('attach', '7-m1-journey.mp4'),
                              ('attach', '7-m1-lookup.png')], calls)
            self.assertEqual(['7-m1-journey.mp4', '7-m1-lookup.png'], json.loads(out.getvalue())['attachments'])
            calls.clear()
            (self.dir / 'pr-review-evidence/7-m1-lookup.png').unlink()
            with self.assertRaises(SystemExit):
                render_confluence.publish(args)
            self.assertEqual([], calls)
        finally:
            render_confluence.Confluence = real
            render_confluence.os.environ.pop('CONFLUENCE_TOKEN', None)
            if saved is not None:
                render_confluence.os.environ['CONFLUENCE_TOKEN'] = saved


if __name__ == '__main__':
    unittest.main()
