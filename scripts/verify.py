#!/usr/bin/env python3
"""Check migrated content, legacy URLs, and the actual Jekyll output."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def verify(site):
    manifest = json.loads((ROOT / 'migration/manifest.json').read_text())
    errors = []
    posts = manifest['posts']
    assert len(posts) == 19, 'Expected the 19 published legacy posts.'
    assert len({p['url'] for p in posts}) == 19, 'Duplicate permalink.'
    for post in posts:
        output = site / post['url'].lstrip('/') / 'index.html'
        if not output.is_file():
            errors.append('Missing original URL: ' + post['url'])
            continue
        soup = BeautifulSoup(output.read_text(), 'html.parser')
        body = soup.select_one('#article-container')
        text = re.sub(r'\s+', '', body.get_text())
        if sha(text) != post['source_text_sha256']:
            errors.append('Prose mismatch: ' + post['title'])
        code_hashes = [sha(pre.code.get_text()) for pre in body.select('pre.highlight')]
        if code_hashes != post['source_code_sha256']:
            errors.append('Code mismatch: ' + post['title'])
        if len(body.select('img, .missing-image')) != post['image_count']:
            errors.append('Image count mismatch: ' + post['title'])
        if unquote(soup.select_one('link[rel="canonical"]')['href']) != 'https://wfloveiu.github.io' + post['url']:
            errors.append('Canonical mismatch: ' + post['title'])

    parsed = {}
    for file in site.rglob('*.html'):
        soup = BeautifulSoup(file.read_text(), 'html.parser')
        parsed[file] = soup
        for node in soup.select('[src], a[href], link[href]'):
            raw = node.get('src') or node.get('href')
            url = urlparse(raw)
            if url.scheme or url.netloc or not url.path.startswith('/'):
                continue
            target = site / unquote(url.path.lstrip('/'))
            if target.is_dir(): target /= 'index.html'
            if not target.is_file(): errors.append(f'Broken internal link in {file.relative_to(site)}: {raw}')
        for link in soup.select('.toc a[href]'):
            fragment = unquote(link['href'].lstrip('#'))
            if soup.find(id=fragment) is None:
                errors.append(f'Broken table of contents in {file}: {fragment}')

    for xml in ['feed.xml', 'sitemap.xml']:
        ElementTree.parse(site / xml)
    homepage = BeautifulSoup((site / 'index.html').read_text(), 'html.parser')
    for heading in ['Research Interests', '📫 Contact', 'Education', 'Experience']:
        assert heading in homepage.get_text(), f'Missing homepage section: {heading}'
    for email in ['fangwu0314@163.com', 'wfiu666666@gmail.com']:
        assert homepage.find('a', href='mailto:' + email), f'Missing contact: {email}'
    blog = BeautifulSoup((site / 'technical-blog/index.html').read_text(), 'html.parser')
    assert len(blog.select('[data-post]')) >= 19
    assert 'example.com' not in (site / 'index.html').read_text()
    if errors: raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(posts)} posts; {sum(p["code_blocks"] for p in posts)} exact code blocks; {sum(p["image_count"] for p in posts)} image references; all internal links and article headings; feed/sitemap XML; homepage sections.')
    print('Source exceptions: ' + str(len(manifest['warnings'])) + ' (see migration/manifest.json).')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, default=ROOT / '_site')
    args = parser.parse_args()
    verify(args.site.resolve())
