#!/usr/bin/env python3
"""Import the published Hexo snapshot without rewriting article prose or code.

python3 scripts/migrate.py ../tmp/wfloveiu-legacy ../tmp/blogImage-main
Dependencies are only needed for migration/verification, not for Jekyll.
"""
import argparse
import copy
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlparse

import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def frontmatter(data, body=''):
    return '---\n' + yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000) + '---\n' + body


def normalized(article):
    node = copy.deepcopy(article)
    for gutter in node.select('.gutter, .headerlink'):
        gutter.decompose()
    return re.sub(r'\s+', '', node.get_text())


def code_text(figure):
    return '\n'.join(line.get_text() for line in figure.select('td.code .line'))


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def migrate(source, image_repo):
    posts, assets, warnings = [], {}, []
    for folder in ['img', 'photos']:
        if (source / folder).exists():
            shutil.copytree(source / folder, ROOT / folder, dirs_exist_ok=True)
    for name in ['avatar.jpg', 'favicon.png']:
        shutil.copy2(source / 'img' / name, ROOT / 'assets/images' / name)

    for file in sorted(source.glob('20*/*/*/*/index.html')):
        soup = BeautifulSoup(file.read_text(), 'html.parser')
        article = soup.select_one('#article-container')
        original_text = normalized(article)
        original_codes = [code_text(fig) for fig in article.select('figure.highlight')]
        title = soup.select_one('h1.post-title').get_text()
        url = '/' + str(file.parent.relative_to(source)) + '/'
        created = soup.select_one('time.post-meta-date-created')['datetime']
        updated = soup.select_one('time.post-meta-date-updated')['datetime']
        categories = [x.get_text() for x in soup.select('a.post-meta-categories')]
        tags = [x.get_text() for x in soup.select('a.post-meta__tags')]
        toc = [{'text': x.get_text(), 'id': x['id'], 'level': int(x.name[1])} for x in article.select('h1[id], h2[id], h3[id]')]
        paragraphs = [x.get_text(' ', strip=True) for x in article.find_all('p', recursive=False) if x.get_text(strip=True)]
        description = next((x for x in paragraphs if not x.startswith(('http', '参考链接')) and len(x) > 15), title)
        description = description[:130] + ('…' if len(description) > 130 else '')
        for a in article.select('.headerlink'):
            a.decompose()
        for figure in article.select('figure.highlight'):
            language = next((c for c in figure.get('class', []) if c != 'highlight'), 'plaintext')
            pre = soup.new_tag('pre', attrs={'class': 'highlight'})
            code = soup.new_tag('code', attrs={'class': 'language-' + language})
            lines = figure.select('td.code .line')
            for i, line in enumerate(lines):
                for child in list(line.contents):
                    code.append(copy.copy(child))
                if i < len(lines) - 1:
                    code.append('\n')
            pre.append(code)
            figure.replace_with(pre)

        image_count = len(article.select('img'))
        for img in list(article.select('img')):
            old = img.get('data-lazy-src') or img.get('src', '')
            if old in assets:
                resolved = assets[old]
            else:
                parsed = urlparse(old)
                resolved = None
                if parsed.netloc == 'raw.githubusercontent.com' and parsed.path.startswith('/wfloveiu/blogImage/main/'):
                    relative = unquote(parsed.path.split('/main/', 1)[1])
                    local = image_repo / relative
                    if local.is_file():
                        name = Path(relative).name
                        if not Path(name).suffix:
                            # This legacy PNG was stored without a file extension.
                            name += '.png'
                        target = ROOT / 'assets/images/posts' / name
                        shutil.copy2(local, target)
                        resolved = '/' + str(target.relative_to(ROOT))
                elif parsed.netloc == 'pic3.zhimg.com':
                    target = ROOT / 'assets/images/posts/transformer-architecture.webp'
                    if target.is_file() and target.stat().st_size > 100:
                        resolved = '/' + str(target.relative_to(ROOT))
                    else:
                        # Preserve external reference if the publisher denies downloads.
                        resolved = old
                        warnings.append({'post': url, 'source': old, 'reason': 'External image host denies download; original reference retained.'})
                elif old.startswith('/') and (source / unquote(old.lstrip('/'))).is_file():
                    resolved = old
                assets[old] = resolved
            if resolved:
                img['src'] = resolved
                img['loading'] = 'lazy'
                img['decoding'] = 'async'
                img.attrs.pop('data-lazy-src', None)
            else:
                warnings.append({'post': url, 'source': old, 'reason': 'Image absent from the published site and public image repository.'})
                placeholder = soup.new_tag('span', attrs={'class': 'missing-image', 'role': 'img', 'aria-label': '原文缺失图片：' + img.get('alt', '')})
                # Empty visible text keeps article prose exactly unchanged; CSS supplies notice.
                placeholder['data-label'] = '原文图片未上传 · ' + img.get('alt', '图片')
                img.replace_with(placeholder)

        for a in article.select('a[href]'):
            parsed = urlparse(a['href'])
            if parsed.netloc in ['wfloveiu.github.io', 'example.com'] and parsed.path.startswith(('/2023/', '/2024/', '/categories/', '/tags/', '/archives/')):
                a['href'] = unquote(parsed.path) + (('#' + parsed.fragment) if parsed.fragment else '')
            if a.get('target') == '_blank':
                a['rel'] = 'noopener noreferrer'

        assert normalized(article) == original_text, f'Prose changed: {title}'
        assert [pre.code.get_text() for pre in article.select('pre.highlight')] == original_codes, f'Code changed: {title}'
        body = article.decode_contents()
        assert '{% endraw %}' not in body, 'An embedded Liquid endraw requires escaping.'
        date = '-'.join(file.relative_to(source).parts[:3])
        filename = date + '-' + file.parent.name + '.html'
        metadata = dict(layout='post', title=title, date=created, last_modified_at=updated, permalink=url,
                        categories=categories, tags=tags, description=description,
                        reading_time=max(1, round(len(original_text) / 650)), toc=toc,
                        search_text=article.get_text(' ', strip=True), migrated_from='Hexo')
        (ROOT / '_posts' / filename).write_text(frontmatter(metadata, '{% raw %}\n' + body + '\n{% endraw %}\n'))
        posts.append(dict(title=title, url=url, file='_posts/' + filename, date=created, updated=updated,
                          categories=categories, tags=tags, image_count=image_count, code_blocks=len(original_codes),
                          source_text_sha256=sha(original_text), source_code_sha256=[sha(x) for x in original_codes]))

    # Re-create all legacy archive, category and tag URLs as actual Jekyll pages.
    for file in source.rglob('index.html'):
        path = str(file.relative_to(source))
        parts = Path(path).parts
        if parts[0] not in ['archives', 'categories', 'tags', 'page'] or len(parts) < 3:
            continue
        url = '/' + str(Path(path).parent) + '/'
        data = dict(layout='listing', title='Archives', nav='archives', permalink=url)
        if parts[0] == 'categories': data.update(title=parts[1], category=parts[1], nav='blog')
        elif parts[0] == 'tags': data.update(title=parts[1], tag=parts[1], nav='blog')
        elif parts[0] == 'archives' and parts[1].isdigit():
            prefix = '/' + '/'.join(parts[1:-1]) + '/'
            data.update(title='Archive · ' + ' / '.join(parts[1:-1]), archive_prefix=prefix)
        elif parts[0] == 'page': data.update(title='Tech Blog', nav='blog')
        output = ROOT / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(frontmatter(data))

    # Keep the old friend-link page's contents, where present.
    file = source / 'link/index.html'
    if file.exists():
        soup = BeautifulSoup(file.read_text(), 'html.parser')
        content = soup.select_one('#article-container')
        links = []
        for a in (content.select('a[href]') if content else []):
            text = a.get_text(' ', strip=True)
            if text: links.append((a['href'], text))
        from html import escape
        body = '<section class="page-container"><h1>友情链接</h1><ul>' + ''.join('<li><a href="' + escape(href) + '">' + escape(text) + '</a></li>' for href, text in links) + '</ul></section>'
        (ROOT / 'links.html').write_text(frontmatter(dict(layout='default', title='友情链接', permalink='/link/'), body))

    commit = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    manifest = dict(source='https://github.com/wfloveiu/wfloveiu.github.io', source_commit=commit,
                    posts=posts, assets=assets, warnings=warnings)
    (ROOT / 'migration/manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'posts': len(posts), 'code_blocks': sum(p['code_blocks'] for p in posts), 'image_references': sum(p['image_count'] for p in posts), 'warnings': warnings}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('legacy', type=Path)
    parser.add_argument('images', type=Path)
    args = parser.parse_args()
    migrate(args.legacy.resolve(), args.images.resolve())
