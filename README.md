# NEC 新能源开发者社区 · 文档站

[![在线文档](https://img.shields.io/badge/docs-docs.newenergycoder.club-blue)](https://docs.newenergycoder.club/)
[![Docs Check](https://github.com/necc-hub/docs/actions/workflows/docs-check.yml/badge.svg)](https://github.com/necc-hub/docs/actions/workflows/docs-check.yml)
[![官网](https://img.shields.io/badge/官网-newenergycoder.club-green)](https://www.newenergycoder.club/)
[![主代码仓](https://img.shields.io/badge/GitHub-new__energy__coder__club-black)](https://github.com/necc-hub/new_energy_coder_club)
[![License](https://img.shields.io/badge/license-Mulan%20PSL%20v2-orange)](./LICENSE)

> 面向机器人竞赛与真实工程项目的开源工程社区文档站：沉淀 ROBOCON、RoboMaster、智能汽车、节能减排等赛事的机械设计、嵌入式开发、机器视觉、运动控制与运营经验，并提供 150+ AI Coding Skills 的索引与详情。

**在线访问：https://docs.newenergycoder.club/**

推送代码到本仓库 `main` 分支后，[Mintlify](https://mintlify.com) 会自动构建并部署。

## 站点内容

站点共 7 个顶部 Tab、319 个 MDX 页面，页面按「学习路径由浅入深」组织：

| Tab | 内容 |
| --- | --- |
| **首页** | 站点入口与板块导览 |
| **文档** | 快速开始、新手上路、10 日集训、工种培训手册、机构 SIG（底盘 / 全向轮 / 麦克纳姆轮 / 设备与加工手册 / LumenPnP 贴片机）、视觉与嵌入式、AI 工具、模板与规范、解决方案 |
| **竞赛** | 竞赛概览（ROBOCON / 节能减排 / 智能汽车）、CURC 2026、CURC 2027 |
| **社区** | 关于我们、社区与活动、治理与安全、财务公开、核心团队、贡献指南 |
| **Wiki** | 飞书 Wiki 导出快照：新人入门、社区协作、培训资源、规范与安全 |
| **关于** | 路线图、AI 搜索与 GEO 权威问答、资源汇总 |
| **技能库** | 151 个 AI Coding Skills 详情页（6 大平台收录，12 个分类 + NEC 精选 7 个） |

## 技术栈

- [Mintlify](https://mintlify.com) — 文档站点框架（`mint` 4.2，版本由 `package-lock.json` 固定）
- MDX — 页面内容与可复用 React 片段（`snippets/`）
- PostCSS — 自定义主题 `style.css` 的解析与校验
- Python 3 — 文档健康检查、PageInsights 与 LLM 索引生成
- GitHub Actions — `docs-check.yml` 持续集成

## 本地开发

### 环境要求

- Node.js 20.17+（`<25`）
- Python 3.10+
- Git

### 安装与预览

```bash
npm ci
npm run dev
```

本地服务器默认在 http://localhost:3000 启动，保存文件后自动热更新。无需全局安装 Mintlify CLI。

## 提交前检查

```bash
npm ci
npm run check
```

`npm run check` 依次执行：

1. `npm test` — 回归测试（Node + Python unittest）
2. `insights:generate` / `insights:sync` — 重新生成 PageInsights 并同步到页面挂载
3. `llms:generate` — 由 `docs.json` 与 frontmatter 重新生成 `llms-full.txt`
4. `check:css` — 用 PostCSS 解析 `style.css`
5. `mint validate` — 校验 Mintlify 配置与页面
6. `check:docs` — 文档健康检查（导航页面存在性、frontmatter、内部链接、canonical、robots 等）

Python 脚本统一通过 `tools/ci/run_python.mjs` 调用：macOS/Linux 使用 `python3`，Windows 使用 `py -3`，无需系统提供 `python` 命令。

单独运行：

```bash
npm run llms:generate   # 只更新 llms-full.txt
npm run llms:check      # 只检查 llms-full.txt 是否同步
npm run check:generated # CI 用：确认已提交的生成物与当前规则一致
```

修改导航或页面 frontmatter 后，请重新生成并一并提交 PageInsights、`llms-full.txt` 及自动挂载变更。

## 项目结构

```
.
├── index.mdx                # 站点首页
├── docs.json                # Mintlify 站点配置、导航与 SEO
├── style.css                # 自定义主题样式
├── geo.mdx                  # AI 搜索权威事实与问答页（/geo）
├── robots.txt               # 搜索引擎与 AI 爬虫指引
├── llms.txt                 # 精选 LLM 抓取指引（手工维护）
├── llms-full.txt            # 全站页面索引（脚本生成，勿手改）
├── AGENTS.md                # 给 AI Agent 的项目说明
├── SKILL-INTERFACE.md       # 内置维护 Skill 的接口说明
├── start-here/              # 快速开始与新手上路
├── training/                # 10 日集训（day01–day05）
├── handbook/                # 工种培训手册（机械/电控/硬件/视觉/运营…）
├── mechanical/              # 机械设计专题（含 lumenpnp/ 贴片机文档）
├── vision/                  # 机器视觉专题
├── embedded-software/       # 嵌入式软件专题
├── ai-tools/                # AI 工具指南（IDE / MCP / 可行性研究）
├── competition/             # 竞赛概览
├── curc26/                  # CURC 2026 赛季文档
├── curc27/                  # CURC 2027 赛季文档
├── skills/                  # 151 个 AI Coding Skills 详情页
├── community/               # 社区介绍、治理与财务公开
├── contributing/            # 贡献指南
├── solutions/               # 外部解决方案（飞书、LiblibAI 等）
├── wiki/                    # 飞书 Wiki 导出快照
├── templates/               # 竞赛 / 项目 / 周报文档模板
├── snippets/                # MDX 可复用片段（含 PageInsights 组件）
├── generated/               # PageInsights 生成数据与报告
├── images/ · logo/ · public/ # 图片、Logo 与静态附件
├── tests/                   # 回归测试
├── tools/ci/                # CI 与健康检查脚本
└── .github/workflows/       # docs-check.yml
```

> 说明：Wiki 中的技术教程已按主题迁移到对应 SIG / 工具目录（如机械设计、嵌入式软件、AI 工具），`wiki/` 主要保留新人入口、社区协作、培训资源与安全规范等飞书原始沉淀。

## 内容来源与导入

- `wiki/` 与部分专题文档（如 `mechanical/lumenpnp/`）来自飞书 Wiki，可通过仓库内的 `.kimi/skills/feishu-to-nec-mdx/` Skill 从飞书增量导入并自动转换为带 frontmatter 的 MDX。
- 单篇飞书文档需要**在飞书内部克隆备份**（不动 MDX）时，用 `.kimi/skills/feishu-doc-clone/`：正文逐块搬运，图片下载后传 Cloudflare R2 再改写成 CDN 链接，断点续跑。
- 大文件（PDF、压缩包、视频等）托管于 Cloudflare R2 CDN（`https://cdn.newenergycoder.club`），页面只引用 CDN 链接，不入 Git 仓库。
- 旧 Wiki URL 已通过 `docs.json` 的 `redirects` 自动跳转。
- 仓库内置 `nec-docs-maintainer` Skill 封装日常维护流程，见 [SKILL-INTERFACE.md](./SKILL-INTERFACE.md)。

## 仓库分工

本仓只负责**发布态文档站**；原始资料与项目代码在主代码仓，两者互不合并、互不镜像。

| | 文档仓（本仓） | 主代码仓 |
| --- | --- | --- |
| 地址 | [necc-hub/docs](https://github.com/necc-hub/docs) → https://docs.newenergycoder.club | [necc-hub/new_energy_coder_club](https://github.com/necc-hub/new_energy_coder_club) |
| 内容 | `.mdx` 页面 + frontmatter + `docs.json` 导航 | 历年赛事档案、项目代码与模型、共享素材 |
| 大二进制 | 不入 git，统一走 R2 CDN | 直接入库 |

内容流向是单向提炼：主代码仓沉淀原始材料 → 本仓整理为带导航的发布页。

## AI 搜索与 GEO

- `llms.txt`：手工维护的精选抓取指引（站点定位、关键词、权威入口）
- `llms-full.txt`：由导航与 frontmatter 自动生成的全站索引，**不要手工编辑**
- `geo.mdx`（`/geo`）：面向生成式搜索的权威事实与常见问题
- `robots.txt`：显式允许主流 AI 爬虫，并声明 sitemap 与上述入口

修改导航或页面 frontmatter 后运行 `npm run llms:generate`；CI 通过 `npm run llms:check` 与 `check_docs.py` 防止索引漂移。

## 贡献指南

1. 阅读 [贡献规范](/contributing/guidelines.mdx)、[工作流程](/contributing/workflow.mdx) 与 [代码风格](/contributing/code-style.mdx)。
2. 创建或修改 `.mdx` 页面，确保包含非空 `title` 与 `description` 的 YAML frontmatter。
3. 在 `docs.json` 的 `navigation` 中注册新页面。
4. 运行 `npm run check` 确认无错误，并提交生成物变更。
5. 从最新 `main` 创建功能分支，提交 PR 并等待 Review。

不要引入 Sphinx / Read the Docs 配置，不要创建仅含 toctree 的 `.rst` 索引文件，空菜单不要上线。

## 社区

- 官网：https://www.newenergycoder.club/
- GitHub 主代码仓：https://github.com/necc-hub/new_energy_coder_club
- GitHub 文档仓库：https://github.com/necc-hub/docs
- ROBOCON 官网：https://www.cnrobocon.net/

## 许可证

本项目采用 [木兰宽松许可证第 2 版（Mulan PSL v2）](./LICENSE)。