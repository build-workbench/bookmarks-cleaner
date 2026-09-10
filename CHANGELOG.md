# 更新日志

CleanBookmarks（包名 `cleanbookmarks`）是一个本地运行的书签整理命令行工具：一条命令完成去重、自动分类与整理导出，产出可导回浏览器的 HTML 以及 JSON、Markdown 报告。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

> 本仓库暂无 git tag，以下为项目自初始提交以来的全部变更，统一归入 Unreleased。

## [Unreleased]

### 新增

- 规则 + LLM 两级级联分类：规则、域名与关键词先行，未命中的再交给 LLM。
- LLM 深度参与三阶段增强：语料分析、配置优化与结果审核。
- LLM 组织器、提示模板与导出工具，支持分面提示（faceted prompt）。
- `--eval` 评估子命令，配套真实 demo 数据与人工标注数据集。
- 置信度阈值与「未分类」兜底；规则引擎支持扩展字段。
- 书签标题规范化、分类顺序配置，并去除分类名中的 emoji/图标前缀。
- 多语言检测与可配置的 emoji 置信度指示。
- 从浏览器导出的书签 HTML 到分类后可再导入的 HTML/JSON/Markdown 的端到端流程。
- 智能去重合并、书签统计与未分类日志；支持多文件/glob 与多 worker 并发。
- 现代 CLI（交互菜单、实时进度、`-i/-o/-c/--limit/--workers`），支持 `pipx install cleanbookmarks`。
- 中英文双语 README 与最佳实践文档；CI 覆盖 Python 3.10/3.11/3.12。

### 变更

- 由单文件脚本（`clean&tidy.py`）演进为结构化 `src/` 包，再收敛为精简的扁平包。
- 包结构从 `src/` 演进为扁平 `cleanbookmarks` 包（入口 `cleanbookmarks.cli:main`），完成更名与发布前清理。
- 默认配置去个人化，改为通用分类体系；分类名去除图标前缀并重命名部分分类。
- 分类架构由 ML / 融合引擎收敛为「规则 + LLM 级联」；`BookmarkProcessor` 由上帝类重构为门面模式。
- 多轮架构优化：模块重组与接口抽取、命名常量替换魔法数字、black 格式化、导入健壮性。
- 依赖与打包规范化：`pyproject` 声明版本下限并与 `requirements` 对齐，新增 `requirements-dev` 与 CI 工作流。
- 仓库持续轻量化（中文化文档、精简 AI 治理/specs 与工具链），并由 AICL-Lab 迁移至 vibe-knight。

### 修复

- 修复报告统计为 0、Emoji 置信度累加、未分类、Windows 读取输出 HTML 匹配与类型转换缺陷。
- 加固处理流程与特征相似检索；提升去重性能与服务层健壮性。
- 修复模块导入、运行时路径稳定性与 `urllib3` 兼容性；统一 `__version__`、修复 `bs4` 防御性导入与裸 `except`。
- 修复 ML 模型加载/训练的告警噪音与 langdetect 兼容性问题。
- 对齐依赖版本并稳定 embedding 相关 hypothesis 截止时间抖动；修复测试标题长度断言等兼容问题。
- 修复 GitHub Pages 文档站的语言重定向、locale 路由与部署工作流问题。

### 移除

- 移除 ML 分类器、融合引擎、插件式分类器与主动学习 / embedding 服务，收敛为规则 + LLM 级联。
- 移除 VitePress 文档站及其工具链与流程文件，测试仅保留 pytest。
- 移除不再维护的 Pages / release / dependabot 工作流与历史规格文档。
- 移除纳入版本控制的运行时数据（训练模型、日志、输出目录）并补充忽略规则。
- 删除文档站重构遗留页面、示例脚本与临时文件。
