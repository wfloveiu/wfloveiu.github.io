# 酷狗 · Jekyll 个人主页

由 `wfloveiu.github.io` 的 Hexo 静态站迁移，使用 Jekyll 4.4。页面布局参考 [Jinyan Su 的主页](https://jinyansu1.github.io/)：白底、细边框顶部导航、窄版文章、个人资料侧栏。样式和模板为本项目重新编写。

首页已填写提供的研究兴趣、两个邮箱、教育背景与三段经历，校徽和公司 Logo 保存在本地，经历按最近在前排序；显示名和头像沿用旧站，可在 `_config.yml`、`assets/images/avatar.jpg` 中修改。学历没有补写未经提供的时间。

## 本地运行

需要 Ruby 3.3 或更新版本。macOS 系统自带的 Ruby 2.6 不适用于本项目。

```sh
bundle install
bundle exec jekyll serve --host 127.0.0.1
```

打开 <http://127.0.0.1:4000/>。博客位于 `/technical-blog/`。

```sh
JEKYLL_ENV=production bundle exec jekyll build --strict_front_matter
python3 -m pip install -r requirements-migration.txt
python3 scripts/verify.py
```

Python 依赖仅用于内容迁移及完整性检查，网站运行只需要 Jekyll。代码样式、搜索、导航没有运行时 CDN 依赖。

## 编辑与写作

- 首页：`index.html`。
- 论文页：`publications.html`；论文信息：`_data/publications.yml`。导航中的 Archives 已替换为 Publications，`/archives/` 自动跳转到 `/publications/`。
- 网站名、作者、网址：`_config.yml`。
- 样式：`assets/css/style.css`。
- 布局：`_layouts/`；文章列表：`_includes/post-list.html`。
- 文章：`_posts/`，图片：`assets/images/posts/`。
- 博客支持全文搜索、分类筛选；关闭 JavaScript 仍可浏览全部文章与分类页。

创建一篇新的 Markdown 文章：

```sh
bash scripts/new-post.sh my-new-post
```

在生成文件的 front matter 中填入标题、摘要、分类和标签，正文按 Markdown 撰写。时间默认使用上海时区。

## 迁移记录

来源仓库只包含生成后的 HTML，没有原始 Markdown。为保留代码缩进、内嵌 HTML、标题锚点和表格，旧文章使用带 YAML front matter 的 `.html` 格式放入 `_posts/`；Jekyll 原生支持该格式。正文由 Liquid `raw` 包裹，避免代码片段被当成模板语法执行。未来新文章可直接用 Markdown。

19 篇文章的标题、发布日期、更新日期、原有分类和标签已保留。每篇使用明确的 `permalink`，保留旧站 `/年/月/日/原始标题/` 地址，包含中文、空格及括号。旧分类、标签、年月归档和分页地址也有对应页面。原文章许可为 CC BY-NC-SA 4.0，继续保留。

`migration/manifest.json` 记录来源提交、每篇正文和代码的 SHA-256、原始图片引用及迁移结果。`scripts/verify.py` 会检查 19 篇旧文的内容一致性、代码块、图片引用数、站内链接、目录锚点、canonical、RSS 和 sitemap。若主动修改旧文正文或代码，应同时审核并更新对应迁移基线，避免把有意修改当成迁移丢失。

可重新执行导入（会覆盖已迁移文章，先提交自己的编辑）：

```sh
python3 scripts/migrate.py /path/to/legacy-site /path/to/blog-image-repository
```

已知源站问题：`服务器删除驱动、安装nvidia驱动、CUDA Tookit` 中有一张图仅引用 Windows 本地 Typora 路径，公开站点和图床均无该文件。迁移保留了缺图提示和原始引用记录；补齐源图后可替换对应占位。没有生成或猜测缺失图片。

## 发布到原 GitHub Pages 地址

站点地址：<https://wfloveiu.github.io/>。开发分支：`codex/jekyll-rebuild`；正式发布分支：`main`。

1. 检查本地预览与迁移记录，提交本地修改并将分支推送到 `wfloveiu/wfloveiu.github.io`。
2. 在 GitHub 建立 PR；PR 的 Actions 会构建及检查，不会发布。
3. 在仓库 **Settings → Pages → Build and deployment** 中将 Source 设为 **GitHub Actions**。
4. 合并到 `main` 后，`.github/workflows/pages.yml` 会构建并发布 `_site` 到原地址。

旧静态站保留在 Git 历史中（迁移前提交 `edfa44337cfd6565ced41a142bce6c46e387e1c5`）。此流程采用 [Jekyll 官方的 GitHub Actions 部署方式](https://jekyllrb.com/docs/continuous-integration/github-actions/)，不能继续使用旧的 Hexo 构建流程。
