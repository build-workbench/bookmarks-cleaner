# 文档信息架构规范化（2026-03-13）

## 变更背景

- 继续推进仓库群 GitHub Pages 与文档入口标准化。
- 此前 `README.md`、`README.zh-CN.md` 与 `docs/index.md` 都同时承担“仓库入口 + 文档入口”职责，内容重复较多。
- 本次调整目标是把 README 收敛为仓库入口，把文档首页收敛为文档入口，并统一导航命名。

## 导航与目录调整

- `docs/.vitepress/config.mts` 一级导航统一为：`概览`、`快速开始`、`使用指南`、`架构设计`、`开发指南`、`参考`、`归档`。
- 侧边栏按相同信息架构重组，避免原先 `入门 / 设计 / 进阶` 与顶部导航语义不一致。
- 保留原有文档文件路径，不做大规模迁移，仅通过导航重新组织入口顺序。

## 首页调整

- `README.md` / `README.zh-CN.md` 收敛为仓库入口，只保留项目定位、最小运行方式和文档入口链接。
- `docs/index.md` 改为文档首页，新增项目定位、适合谁、从哪里开始、推荐阅读路径、核心文档表。
- 文档首页不再重复大段流水线和技术栈细节，把深度内容下沉到已有页面。

## Pages / Workflow 调整

- 本次未修改 `pages.yml` 的构建逻辑；现有 `master, main` 触发与 `docs/package-lock.json` 缓存路径保持可用。
- 保持 VitePress 构建目录仍为 `docs/.vitepress/dist`，避免引入额外部署风险。

## 验证结果

- 人工检查 `README` 与 `docs/index.md` 职责已分离：仓库入口与文档入口不再重复堆叠。
- 人工检查导航命名已统一，首页两次点击内可到达快速上手、架构设计和开发指南。
- 已在 `docs/` 目录执行 `npm run docs:build`，VitePress 构建成功，产物输出到 `docs/.vitepress/dist/`。
- 已检查构建产物中的 HTML 页面：`bookmarks-cleaner` 输出 10 个 HTML 页面，首页与核心文档页均已生成。

## 后续待办

- 继续清理 `docs/guides/development_guide.md` 中历史结构描述，减少与当前代码树不一致的内容。
- 评估是否为 `changelog/` 增加索引页，方便仓库内长期查阅文档治理记录。
