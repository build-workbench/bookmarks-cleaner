"""CLI 入口测试"""

import os
import subprocess
import sys

from cleanbookmarks import __version__

# 仓库根目录（main.py 所在处），保证子进程能 import 到包
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run_cli(*args, cwd=None):
    """在子进程中运行 CLI（python main.py），返回 (returncode, stdout, stderr)"""
    proc = subprocess.run(
        [sys.executable, os.path.join(REPO_ROOT, "main.py"), *args],
        capture_output=True, text=True, cwd=cwd or REPO_ROOT,
        timeout=60,
    )
    return proc.returncode, proc.stdout, proc.stderr


class TestCliHelp:
    def test_version(self):
        code, out, _ = _run_cli("--version")
        assert code == 0
        assert __version__ in out

    def test_help(self):
        code, out, _ = _run_cli("--help")
        assert code == 0
        assert "-i" in out
        assert "--health-check" in out


class TestCliInput:
    def test_no_input_shows_help(self):
        """无输入且无 --health-check 时应打印帮助（退出 0）"""
        code, out, _ = _run_cli()
        assert code == 0
        assert "usage" in out.lower()

    def test_nonexistent_file_exits_1(self, tmp_path):
        code, _, err = _run_cli("-i", str(tmp_path / "missing.html"))
        assert code == 1
        assert "没有找到有效的输入文件" in err

    def test_glob_expansion(self, tmp_path):
        (tmp_path / "a.html").write_text("<a href='https://a.com' add_date='1'>A</a>", encoding="utf-8")
        (tmp_path / "b.html").write_text("<a href='https://b.com' add_date='1'>B</a>", encoding="utf-8")
        out_dir = tmp_path / "out"
        code, _, _ = _run_cli("-i", str(tmp_path / "*.html"), "-o", str(out_dir))
        assert code == 0
        files = list(out_dir.iterdir())
        assert any(f.suffix == ".html" for f in files)
        assert any(f.suffix == ".json" for f in files)

    def test_health_check(self):
        code, out, _ = _run_cli("--health-check")
        assert code == 0
        assert "健康检查" in out

    def test_eval_on_labeled_data(self):
        """--eval 用标注数据评估，应输出准确率统计"""
        labeled = os.path.join(REPO_ROOT, "examples", "labeled_bookmarks.json")
        code, out, _ = _run_cli("--eval", labeled)
        assert code == 0
        assert "评估结果" in out
        assert "各分类准确率" in out

    def test_eval_missing_file_exits_1(self, tmp_path):
        code, _, err = _run_cli("--eval", str(tmp_path / "missing.json"))
        assert code == 1
        assert "标注文件不存在" in err

    def test_eval_invalid_json_exits_1(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("not json", encoding="utf-8")
        code, _, err = _run_cli("--eval", str(bad))
        assert code == 1
        assert "不是合法 JSON" in err

    def test_eval_non_list_json_exits_1(self, tmp_path):
        obj = tmp_path / "obj.json"
        obj.write_text('{"a": 1}', encoding="utf-8")
        code, _, err = _run_cli("--eval", str(obj))
        assert code == 1
        assert "顶层必须是 JSON 数组" in err

    def test_eval_junk_entries_skipped(self, tmp_path):
        """列表中混入非 dict 条目应跳过而非崩溃"""
        junk = tmp_path / "junk.json"
        junk.write_text(
            '[{"url": "https://example.com", "title": "T", "expected": "编程"}, "garbage", 42]',
            encoding="utf-8",
        )
        code, out, _ = _run_cli("--eval", str(junk))
        assert code == 0
        assert "评估结果" in out
