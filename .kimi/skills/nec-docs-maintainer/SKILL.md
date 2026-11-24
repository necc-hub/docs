---
name: nec-docs-maintainer
description: 维护 NEC 新能源开发者社区 Mintlify 文档站点。用于新增页面、修复死链、重构导航、运行 CI 健康检查并推送到 main 分支自动部署。触发词：维护 NEC 文档、修复文档死链、重构导航、新增 NEC 页面、部署文档站、运行 docs-check。
---

# NEC 文档站点维护

## 项目概览

- **仓库**: `https://github.com/necc-hub/docs.git`
- **站点**: `https://docs.newenergycoder.club/`
- **框架**: Mintlify v3，配置在 `docs.json`
- **入口**: `index.mdx`
- **自动部署**: 推送到 `main` 分支后 Mintlify 自动部署
- **本地预览**：`npm ci && npm run dev`（默认 `localhost:3000`），无需全局安装 CLI

## 核心规范

### 文件规范

- 页面使用 `.mdx`（推荐）或 `.md`
- 每个 `.mdx` 必须包含非空 YAML frontmatter：
  ```yaml
  ---
  title: "页面标题"
  description: "页面描述"
  ---
  ```
- 图片统一放入 `images/` 目录，引用路径以 `/images/` 开头
- 禁止重新引入归档目录：`legacy/`、`api-reference/`、`essentials/`
- 允许不注册导航的孤儿文件：`AGENTS.md`、`snippets/snippet-intro.mdx`、`wiki/README.md`

### 导航规则

- 所有新页面必须在 `docs.json` 的 `navigation.tabs[].groups[].pages` 中注册
- 当前 7 个顶部 Tab：首页、文档、竞赛、社区、Wiki、关于、技能库
- 各 Tab 的分组与学习路径顺序以 `AGENTS.md` 的「导航结构」和 `docs.json` 为准
- 修改导航结构后同步更新 `AGENTS.md` 的「导航结构」说明

## 标准工作流

1. **编辑内容**：新增/修改 `.mdx`、图片、`docs.json`
2. **本地检查**：运行 `npm run check`
3. **修复问题**：死链、未注册页面、frontmatter 缺失、localhost 链接等
4. **提交变更**：将正文、导航与 PageInsights 生成物一起提交，使用 Conventional Commits
5. **提交 PR**：从最新 `main` 创建功能分支，经审查合并后由 Mintlify 自动部署

## 常见任务

### 新增页面

1. 在合适目录创建 `.mdx`，写好 frontmatter
2. 如需图片，放入 `images/<topic>/` 并以 `/images/<topic>/file.png` 引用
3. 在 `docs.json` 对应分组注册页面路径（省略 `.mdx` 扩展名）
4. 运行 `npm run check` 并修复报错
5. 提交正文、导航和生成物

### 修复死链

1. 运行 `npm run check:docs`，或运行完整 `npm run check`
2. 内部死链：修正路径或删除链接
3. 外部死链：确认是否真实失效，可加入 `EXTERNAL_LINK_ALLOWLIST` 中登录墙/证书异常的域名
4. 重新运行检查；外链警告仍需人工查看，不要仅凭退出码判断全部健康

### 重构导航

1. 修改 `docs.json` 的 `navigation` 字段
2. 确保所有注册页面存在且非空
3. 更新 `AGENTS.md` 中的导航结构描述
4. 运行 `npm run check` 检查未注册页面
5. 提交变更

## CI 检查项

脚本：`tools/ci/check_docs.py`

- `docs.json` JSON 合法性与推荐字段（`metadata`、`search`、`seo`、`styles`）
- 导航页面文件存在性
- `.mdx` 文件包含非空 `title` 与 `description`
- 内部 Markdown / MDX / HTML 链接可解析
- 无 `localhost` 链接、无非 ASCII 内部路径
- 外部链接抽样检查（HEAD/GET）
- 未引入禁止目录

## 参考文件

- [项目结构与关键文件](references/project-structure.md)
- [CI 脚本说明](references/ci-checks.md)
