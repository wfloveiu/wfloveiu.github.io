# FangWu 的博客

网站：[fangwu0314.github.io](https://fangwu0314.github.io/) · [部署状态](https://github.com/FangWu0314/FangWu0314.github.io/actions)

## 日常只需要这三个目录

| 目录 | 用途 |
| --- | --- |
| `site/_posts/` | 技术文章，显示在 Tech Blog |
| `site/_personal_posts/` | 生活随笔，显示在 Personal Blog |
| `site/assets/images/posts/` | 文章配图，每篇新文章一个子文件夹 |

本机项目位置：`~/codes/FangWu0314.github.io`。进入此目录后使用下面的命令。

## 写一篇文章

```sh
./blog new tech deepseek-v4-1 "DeepSeek V4.1 阅读笔记"
./blog new personal weekend "周末随记"
```

任选一种。脚本会生成 Markdown 草稿和对应图片目录，并打印文章路径。文件存在时不会覆盖。

- 技术文章文件名：`site/_posts/日期-英文短名.md`。
- 个人文章文件名：`site/_personal_posts/英文短名.md`。
- 旧的 19 篇 `.html` 文章保留原始内容；新文章使用 `.md` 即可。

文件开头是文章信息，例如：

```yaml
---
layout: post
title: "DeepSeek V4.1 阅读笔记"
date: 2026-10-06 12:00:00 +0800
description: "整理 CED、CSA2 与 SWA 重放。"
published: false
math: true
categories: [模型架构]
tags: [DeepSeek, Attention]
---

## 开始

正文写在这里。
```

日期由脚本自动生成。分类、标签可以自由填写或设为 `[]`，页面会自动更新。需要公式时添加 `math: true`；行内使用 `$N$`，独立公式用单独成行的 `$$` 包围，公式块前后各空一行。公式脚本与字体随网站发布。

将图片放到 `site/assets/images/posts/文章短名/`，正文使用网站路径：

```markdown
![架构示意图](/assets/images/posts/deepseek-v4-1/architecture.png)
```

网址中不包含 `site/`，不要引用电脑上的 `/Users/...` 或 Typora 临时文件。

## 预览与发布

```sh
./blog preview
```

打开 [本地预览](http://127.0.0.1:4000/)，保存文章后刷新即可。预览包含草稿；端口占用时使用 `./blog preview --port 4001`，停止按 `Ctrl+C`。修改 `_config.yml` 后需要重新启动预览。

写完将文章的 `published: false` 改成 `published: true`，然后：

```sh
./blog check
# 以下路径换成实际文章和图片目录；没有图片时省略图片目录。
git add site/_posts/2026-10-06-deepseek-v4-1.md site/assets/images/posts/deepseek-v4-1/
git diff --cached --stat
git commit -m "Add DeepSeek V4.1 notes"
git push origin HEAD:main
```

个人文章提交 `site/_personal_posts/` 中的对应文件。推送到 `main` 会自动部署；在 [GitHub Actions](https://github.com/FangWu0314/FangWu0314.github.io/actions) 查看结果。远端有新提交时先同步，不要强制推送。草稿标记仅控制网站展示，公开仓库中的草稿源码仍可见。

## 目录结构

```text
FangWu0314.github.io/
├── site/                  网站源码，只有这里的内容参与发布
│   ├── _posts/            技术文章
│   ├── _personal_posts/   个人文章
│   ├── assets/            图片、样式、脚本、公式库
│   ├── pages/             博客列表、论文、分类、RSS 等页面
│   │   └── legacy/        旧网址兼容页面，日常不用修改
│   ├── _data/             论文数据
│   ├── _layouts/          页面布局
│   ├── _includes/         共用组件
│   └── index.html         首页资料
├── scripts/               新建文章与构建检查工具
├── docs/                  图片来源、历史迁移核对记录
├── _config.yml            网站配置与构建目录
├── blog                   常用命令入口
├── Gemfile / Gemfile.lock Ruby 依赖与版本锁定
├── requirements.txt       检查工具的 Python 依赖
├── .github/               GitHub Pages 自动部署
├── .bundle/               本机运行环境和依赖，不提交
└── .build/                构建和预览产物，不提交
```

首页在 `site/index.html` 修改，论文在 `site/_data/publications.yml` 修改。旧归档、分类和标签网址仍可访问。文章图片均有引用；`site/assets/lib/katex/` 是公式渲染库和字体，保留其许可证。

已删除不再引用的旧主题图片、重复头像及一次性导入脚本。需要追溯旧文件时可使用 Git 历史；正文校验记录保存在 [docs/migration](docs/migration/)，标识来源见 [docs/LOGO-SOURCES.md](docs/LOGO-SOURCES.md)。

## 换电脑运行

安装 Ruby 3.3+ 和 Python 3，进入项目根目录运行：

```sh
bundle config set --local path .bundle/gems
bundle install
python3 -m pip install -r requirements.txt
./blog preview
```

当前电脑的 Ruby 路径记录在 `.bundle/ruby-bin`，相对路径以项目根目录为基准；项目移动后仍可使用。`.bundle/` 中的本机运行环境不上传 GitHub，GitHub Actions 使用自己的 Ruby 和 Python。

技术参考：[Jekyll 文章规范](https://jekyllrb.com/docs/posts/) · [Front Matter](https://jekyllrb.com/docs/front-matter/) · [KaTeX 公式渲染](https://katex.org/docs/autorender)。网站布局参考 [Jinyan Su 的主页](https://jinyansu1.github.io/)。
