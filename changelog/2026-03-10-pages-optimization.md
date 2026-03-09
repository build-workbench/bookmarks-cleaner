# GitHub Pages 优化 (2026-03-10)

## 工作流修复与优化

- **pages.yml** — 修复路径触发引用错误（`deploy-docs.yml` → `pages.yml`，原文件名不匹配导致工作流自身变更不触发重建）
- **pages.yml** — 扩展路径触发范围（新增 `README.md`、`README.zh-CN.md`）
- **pages.yml** — 添加 sparse-checkout 仅拉取 `docs/` 目录，加速 CI 构建
- **pages.yml** — `cancel-in-progress` 改为 `true`，避免文档部署排队堆积
- **pages.yml** — 移除不必要的 `fetch-depth: 0` 和 `configure-pages` 步骤

## 文档站首页重写

- **docs/index.md** — 增强 Hero 区：tagline 补充 Python 版本信息，action 按钮新增"系统架构"入口
- **docs/index.md** — Feature 卡片从 4 个扩展到 6 个：新增"统一 Emoji 清理"和"去重 · 健康巡检"
- **docs/index.md** — 新增处理流水线 ASCII 架构图（BookmarkProcessor → AIClassifier → Standardizer → Exporter）
- **docs/index.md** — 新增最小示例代码块和技术栈表格

## README 徽章

- **README.md / README.zh-CN.md** — 统一添加 CI、License、Python 徽章；Docs 徽章改为工作流状态徽章
