## 1. 代码架构清洗

- [ ] 1.1 删除重复源文件 `src/data_exporter.py`
- [ ] 1.2 删除重复源文件 `src/cli_interface.py`
- [ ] 1.3 删除重复源文件 `src/emoji_cleaner.py`
- [ ] 1.4 删除重复目录 `config/taxonomy/`
- [ ] 1.5 运行 `pytest -q tests/test_runtime_paths.py` 验证基础功能
- [ ] 1.6 运行 `pytest -q` 验证完整测试套件

## 2. 文件系统清理

- [ ] 2.1 删除 `.omc/` 目录（Opencode 配置）
- [ ] 2.2 删除 `tests/output-round-1/` 目录
- [ ] 2.3 删除 `tests/output-round-2/` 目录
- [ ] 2.4 更新 `.gitignore` 添加运行时产物规则
- [ ] 2.5 删除所有 `bmad-*` skills（保留 `opsx-*`）

## 3. Git 分支清理

- [ ] 3.1 删除远程分支 `dependabot/github_actions/actions/setup-python-6`
- [ ] 3.2 删除远程分支 `dependabot/npm_and_yarn/docs/vitepress-1.6.4`
- [ ] 3.3 删除远程分支 `dependabot/pip/beautifulsoup4-gte-4.12.3-and-lt-4.15.0`
- [ ] 3.4 删除远程分支 `dependabot/pip/mypy-gte-1.10-and-lt-1.21`
- [ ] 3.5 验证本地仓库状态 `git branch -a`

## 4. 文档与 AI 指令优化

- [ ] 4.1 精简 `AGENTS.md` 内容，消除与 `CLAUDE.md` 重复
- [ ] 4.2 验证 `copilot-instructions.md` 已在 `.gitignore` 中
- [ ] 4.3 验证 GitHub Pages 文档构建正常

## 5. 最终验证

- [ ] 5.1 运行完整测试套件 `pytest -q`
- [ ] 5.2 运行代码质量检查 `black --check src/ main.py tests/`
- [ ] 5.3 运行类型检查 `mypy src/`
- [ ] 5.4 验证包构建 `python -m build`
- [ ] 5.5 验证 CLI 入口 `cleanbook --version`
- [ ] 5.6 提交变更并推送到 master
