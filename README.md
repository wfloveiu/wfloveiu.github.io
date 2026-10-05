# 吴方的博客：日常写作入口

网站：[wfloveiu.github.io](https://wfloveiu.github.io/)。你平时只需要编辑 Markdown 文章和图片，不需要修改网页模板。

## 只关注这三个目录

| 目录 | 用途 |
| --- | --- |
| `_posts/` | 技术文章，显示在 Tech Blog |
| `_personal_posts/` | 生活随笔，显示在 Personal Blog |
| `assets/images/posts/` | 文章图片，建议每篇一个子文件夹 |

旧的 19 篇文章是从 Hexo 发布页面迁移的 HTML，保留了代码缩进、图片和旧网址。新文章全部使用 `.md` 即可；原有 `.html` 不必照着写。

## 1. 新建文章

在仓库目录运行下面一种命令，英文短名用于文件名，中文标题用于网页展示：

```sh
./blog new tech deepseek-v4-1 "DeepSeek V4.1 阅读笔记"
./blog new personal weekend "周末随记"
```

第一种生成 `_posts/当天日期-deepseek-v4-1.md`，第二种生成 `_personal_posts/weekend.md`。命令会打印完整路径，也会准备对应的图片文件夹。相同文件已存在时会退出，不会覆盖。

生成的文件开头包含文章信息：

```yaml
---
layout: post
title: "DeepSeek V4.1 阅读笔记"
date: 2026-10-05 12:00:00 +0800
description: "整理 CED、CSA2 与 SWA Bounded Replay。"
published: false
categories: [模型架构]
tags: [DeepSeek, Attention]
---
```

标题、摘要和正文按需填写。日期由命令自动生成，示例日期无需照抄。分类和标签可自行增加，也可以保留 `[]`；列表和链接会自动生成，不必再建对应 HTML 页面。

在第二个 `---` 下面写 Markdown，正文标题从 `##` 开始。页面会自动展示文章标题。

## 2. 添加图片

把图片放到 `assets/images/posts/deepseek-v4-1/`，在正文引用：

```markdown
![架构示意图](/assets/images/posts/deepseek-v4-1/architecture.png)
```

文章内使用网站根路径 `/assets/...`，不要引用电脑上的 `/Users/...` 或 Typora 临时路径。

## 3. 本地预览

```sh
./blog preview
```

打开 <http://127.0.0.1:4000/>，保存文章后 Jekyll 会自动重新生成页面，刷新浏览器即可。停止预览按 `Ctrl+C`。端口被占用时可运行 `./blog preview --port 4001`。

预览包含 `published: false` 的草稿；正式构建只展示已发布文章。草稿标记控制网页展示，公开 GitHub 仓库中的源码仍然可见。

本机已经配置 Ruby 路径，保存在不会提交的 `.bundle/ruby-bin`。换电脑时安装 Ruby 3.3+，运行 `bundle install` 和 `python3 -m pip install -r requirements-migration.txt` 即可；如使用非默认 Ruby，可把其 bin 目录写入 `.bundle/ruby-bin`。

## 4. 发布

写完后把该文章的 `published: false` 改成 `published: true`，然后运行：

```sh
./blog check
```

检查通过后提交文章和它的图片。下面的路径请替换成命令实际生成的文件路径：

```sh
git add _posts/2026-10-05-deepseek-v4-1.md assets/images/posts/deepseek-v4-1/
git diff --cached --stat
git commit -m "Add DeepSeek V4.1 notes"
git push origin HEAD:main
```

个人文章则提交对应的 `_personal_posts/文章短名.md`。没有图片时不必提交图片目录。当前在 `codex/jekyll-rebuild` 开发分支，推送到 `main` 才会触发正式发布。若推送提示远端有新提交，先同步合并，不要强制推送。

在 [GitHub Actions](https://github.com/wfloveiu/wfloveiu.github.io/actions) 查看构建和部署；成功后刷新公网网页。

## 其他目录为什么存在

| 文件或目录 | 用途；日常写作一般不用动 |
| --- | --- |
| `index.html` | 首页介绍、教育与工作经历 |
| `_data/publications.yml` | 论文信息 |
| `_layouts/`、`_includes/`、`assets/css/`、`assets/js/` | 布局、样式与交互 |
| `archives/`、`categories/`、`tags/`、`page/` | 旧网址兼容页面 |
| `img/`、`photos/` | 旧站图片，保留旧引用 |
| `migration/`、`scripts/migrate.py` | 迁移记录与导入工具 |
| `_site/`、`preview/`、`vendor/`、`.jekyll-cache/` | 自动生成的页面、预览、依赖与缓存，已忽略提交 |
| `.github/`、`Gemfile`、`_config.yml` | 自动部署、依赖与站点设置 |

迁移核对结果见 [migration/REPORT.md](migration/REPORT.md)，标识来源见 [migration/LOGO-SOURCES.md](migration/LOGO-SOURCES.md)。旧站提交 `edfa44337cfd6565ced41a142bce6c46e387e1c5` 保留在 Git 历史中。网站布局参考 [Jinyan Su 的主页](https://jinyansu1.github.io/)，由本项目重新实现。

文章规范参考 [Jekyll Posts](https://jekyllrb.com/docs/posts/) 与 [Front Matter](https://jekyllrb.com/docs/front-matter/)。
