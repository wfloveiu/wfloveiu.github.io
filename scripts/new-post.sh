#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export TZ=Asia/Shanghai
python3 - "$@" <<'PY'
import json
import re
import sys
from datetime import datetime
from pathlib import Path

args = sys.argv[1:]
if len(args) == 1:
    args = ['tech', args[0]]  # Preserve the original one-slug command.
if len(args) not in (2, 3) or args[0] not in ('tech', 'personal'):
    sys.exit('用法：./blog new <tech|personal> <英文短名> ["文章标题"]')
kind, slug = args[:2]
if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
    sys.exit('英文短名只能包含小写字母、数字和连字符，例如 deepseek-v4-1。')
title = args[2] if len(args) == 3 else slug
now = datetime.now().astimezone()
folder = Path('_posts' if kind == 'tech' else '_personal_posts')
folder.mkdir(exist_ok=True)
post = folder / (f'{now:%Y-%m-%d}-{slug}.md' if kind == 'tech' else f'{slug}.md')
content = f'''---
layout: post
title: {json.dumps(title, ensure_ascii=False)}
date: {now:%Y-%m-%d %H:%M:%S %z}
description: "在这里填写一句话摘要。"
published: false
categories: []
tags: []
---

## 开始

在这里开始写作。

<!-- 图片放在 assets/images/posts/{slug}/，正文引用示例：
![图片说明](/assets/images/posts/{slug}/diagram.png)
-->
'''
try:
    with post.open('x', encoding='utf-8') as file:
        file.write(content)
except FileExistsError:
    sys.exit(f'文件已存在，未覆盖：{post}')
(Path('assets/images/posts') / slug).mkdir(exist_ok=True)
print(f'已创建：{post.resolve()}')
print('本地预览：./blog preview')
print('准备上线时，将 published: false 改为 true，然后提交并推送。')
PY
