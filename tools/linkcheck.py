#!/usr/bin/env python3
"""Check that every URL cited by the canonical standards files still resolves. Standard library only.

Result classes: OK, REDIRECT (permanent redirect, warn with the new URL), BLOCKED (a host that turns
bots away), ERROR (timeout or transport failure after retries, warn), BROKEN (404, 410, DNS failure,
or a failed Apple JSON check). Exit 1 only on BROKEN. Apple's HTML shell returns 200 for any path, so
documentation and HIG pages are also fetched through the JSON endpoint. Material 3 pages are checked
against the site map because the page body is client-rendered.
"""
import argparse
import fnmatch
import json
import os
import sys
import threading
import time
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stamps import body_urls, stamp  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'tools/linkcheck.toml'
USER_AGENT = 'ai-toolkit-linkcheck (+https://github.com/Mark-Hine/ai-toolkit)'


def urls_in_scope(config):
    files = set()
    for pattern in config['include']:
        files.update(p for p in ROOT.glob(pattern) if p.is_file())
    found = {}
    for path in sorted(files):
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(errors='replace')
        _, sources = stamp(path)
        candidates = list(sources) if isinstance(sources, list) else []
        candidates += body_urls(text)
        for url in candidates:
            if any(s in url for s in config.get('skip_url_substrings', [])):
                continue
            url = url.split('#', 1)[0]
            found.setdefault(url, set()).add(rel)
    return found


class Checker:
    def __init__(self, config, opener=None, sleep=time.sleep):
        self.config = config
        self.opener = opener or self.default_opener
        self.sleep = sleep
        self.locks = {}
        self.sitemaps = {}

    @staticmethod
    def default_opener(url, method, headers, timeout):
        req = urllib.request.Request(url, method=method, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.geturl(), resp.read() if method == 'GET' else b''

    def host_policy(self, url):
        host = urllib.parse.urlparse(url).netloc
        return host, self.config.get('hosts', {}).get(host, {})

    def lock_for(self, host, policy):
        if host not in self.locks:
            self.locks[host] = threading.BoundedSemaphore(int(policy.get('concurrency', 4)))
        return self.locks[host]

    def request(self, url, policy, method):
        headers = {'User-Agent': USER_AGENT, 'Accept': '*/*'}
        token = os.environ.get(policy.get('token_env', ''), '') if policy.get('token_env') else ''
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return self.opener(url, method, headers, self.config.get('timeout', 20))

    def fetch(self, url, policy):
        """(status, final_url, body) with retries, HEAD first then GET on 403, 405, 501."""
        last = None
        for attempt in range(self.config.get('retries', 3)):
            try:
                status, final, body = self.request(url, policy, 'HEAD')
                if status in (403, 405, 501):
                    status, final, body = self.request(url, policy, 'GET')
                return status, final, body
            except urllib.error.HTTPError as exc:
                if exc.code in (403, 405, 501) and attempt == 0:
                    try:
                        return self.request(url, policy, 'GET')
                    except urllib.error.HTTPError as inner:
                        exc = inner
                    except Exception as inner:  # noqa: BLE001
                        last = inner
                        continue
                if exc.code == 429 or exc.code >= 500:
                    retry = exc.headers.get('Retry-After') if exc.headers else None
                    self.sleep(float(retry) if retry and retry.isdigit() else 2 ** attempt)
                    last = exc
                    continue
                return exc.code, url, b''
            except Exception as exc:  # noqa: BLE001 - transport errors are reported, not raised
                last = exc
                self.sleep(2 ** attempt)
        raise last

    def sitemap_has(self, sitemap_url, url, policy):
        if sitemap_url not in self.sitemaps:
            try:
                _, _, body = self.request(sitemap_url, policy, 'GET')
                self.sitemaps[sitemap_url] = body.decode(errors='replace')
            except Exception:  # noqa: BLE001
                self.sitemaps[sitemap_url] = None
        text = self.sitemaps[sitemap_url]
        return None if text is None else (url.rstrip('/') in text)

    def apple_json_url(self, url):
        path = urllib.parse.urlparse(url).path.rstrip('/')
        if path.startswith('/documentation/') or path.startswith('/design/human-interface-guidelines'):
            return f'https://developer.apple.com/tutorials/data{path}.json'
        return None

    def check(self, url):
        host, policy = self.host_policy(url)
        with self.lock_for(host, policy):
            if policy.get('delay'):
                self.sleep(float(policy['delay']))
            try:
                status, final, _ = self.fetch(url, policy)
            except Exception as exc:  # noqa: BLE001
                return {'url': url, 'class': 'ERROR', 'detail': type(exc).__name__}
            if status in policy.get('blocked_status', []):
                return {'url': url, 'class': 'BLOCKED', 'detail': f'HTTP {status}'}
            if status in (404, 410):
                return {'url': url, 'class': 'BROKEN', 'detail': f'HTTP {status}'}
            if status >= 400:
                return {'url': url, 'class': 'ERROR', 'detail': f'HTTP {status}'}
            if policy.get('apple_json'):
                json_url = self.apple_json_url(url)
                if json_url:
                    try:
                        jstatus, _, body = self.fetch(json_url, policy)
                        json.loads(body or b'{}')
                        if jstatus in (404, 410):
                            return {'url': url, 'class': 'BROKEN', 'detail': 'Apple JSON endpoint returns 404, the page does not exist'}
                    except ValueError:
                        return {'url': url, 'class': 'ERROR', 'detail': 'Apple JSON endpoint returned non-JSON'}
                    except Exception as exc:  # noqa: BLE001
                        return {'url': url, 'class': 'ERROR', 'detail': f'Apple JSON check failed: {type(exc).__name__}'}
            if policy.get('sitemap'):
                present = self.sitemap_has(policy['sitemap'], url, policy)
                if present is False:
                    return {'url': url, 'class': 'REDIRECT', 'detail': 'not in the site map, confirm the page still exists'}
            if final and final.rstrip('/') != url.rstrip('/'):
                return {'url': url, 'class': 'REDIRECT', 'detail': f'now {final}'}
            return {'url': url, 'class': 'OK', 'detail': f'HTTP {status}'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, help='write a markdown report here')
    parser.add_argument('--config', type=Path, default=CONFIG)
    parser.add_argument('--only', help='check only URLs containing this substring')
    args = parser.parse_args()
    config = tomllib.loads(args.config.read_text())
    found = urls_in_scope(config)
    urls = sorted(u for u in found if not args.only or args.only in u)
    checker = Checker(config)
    with ThreadPoolExecutor(max_workers=config.get('workers', 8)) as pool:
        results = list(pool.map(checker.check, urls))
    for r in results:
        r['files'] = sorted(found[r['url']])
    counts = {}
    for r in results:
        counts[r['class']] = counts.get(r['class'], 0) + 1
    lines = [f'# Link check, {len(results)} URLs', '', '| Class | Count |', '|---|---|'] + [f'| {k} | {v} |' for k, v in sorted(counts.items())] + ['']
    for cls in ('BROKEN', 'REDIRECT', 'BLOCKED', 'ERROR'):
        rows = [r for r in results if r['class'] == cls]
        if rows:
            lines += [f'## {cls}', '', '| URL | Detail | Cited in |', '|---|---|---|']
            lines += [f'| {r["url"]} | {r["detail"]} | {", ".join(r["files"])} |' for r in rows]
            lines.append('')
    report = '\n'.join(lines)
    print(report)
    if args.report:
        args.report.write_text(report)
    for r in results:
        if r['class'] == 'BROKEN':
            print(f'::error::{r["url"]}: {r["detail"]} (cited in {", ".join(r["files"])})')
        elif r['class'] in ('REDIRECT', 'ERROR'):
            print(f'::warning::{r["url"]}: {r["detail"]}')
    return 1 if counts.get('BROKEN') else 0


if __name__ == '__main__':
    sys.exit(main())
