#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 1 ]; then
  echo 'Usage: bash scripts/new-post.sh my-post-slug'
  exit 1
fi
if [[ ! "$1" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo 'Use a lowercase slug with letters, numbers and hyphens.'
  exit 1
fi
cd "$(dirname "$0")/.."
post_file="_posts/$(TZ=Asia/Shanghai date +%F)-$1.md"
if [ -e "$post_file" ]; then echo "Already exists: $post_file"; exit 1; fi
cat > "$post_file" <<EOF
---
layout: post
title: "$1"
date: $(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S %z')
categories: []
tags: []
description: ""
---

在这里开始写作。
EOF
echo "$post_file"
