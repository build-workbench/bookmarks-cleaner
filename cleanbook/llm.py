"""LLM 分类器（可选）- OpenAI 兼容接口"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests

from cleanbook.config import load_json_config, resolve_config_path
from cleanbook.text_utils import normalize_category_string, strip_category_prefix

_CHINESE_REGEX = re.compile(r"[\u4e00-\u9fff]")
_ENGLISH_REGEX = re.compile(r"[a-zA-Z]")
_KEYWORD_REGEX = re.compile(r"[a-zA-Z\u4e00-\u9fff]{2,}")

logger = logging.getLogger(__name__)


class LLMPromptBuilder:
    """构建 LLM 分类提示词"""

    DEFAULT_STEPS = [
        "解析书签的标题、URL、域名、上下文，识别主题与意图。",
        "将识别出的意图映射到提供的类别库，必要时推测最匹配的主/子分类。",
        "校验置信度范围 [0,1]，并用 JSON 输出最终结果。",
    ]

    DEFAULT_EXPECTED_KEYS = {
        "category": "最终的主分类或主/子分类字符串（必须来自提供的类别列表）",
        "confidence": "0~1 的浮点数，代表置信度；若不确定应降低分值。",
        "reasons": ["1~3 条简短中文理由，解释分类依据。"],
        "subcategory": "可选，若主分类下还可细分则给出。",
        "facets": {"resource_type_hint": "可选，指出内容形态，如教程、文档、视频。"},
        "priority_tags": ["可选，推荐使用的重点标签，如 '需要跟进'。"],
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        llm_conf = config.get("llm") or {}
        prompt_conf = llm_conf.get("prompt") or {}
        self._steps: List[str] = prompt_conf.get("steps") or self.DEFAULT_STEPS
        self._task_description: str = prompt_conf.get("task_description", "请以智能代理的方式，完成浏览器书签的精准分类。")
        self._scoring_notes: str = prompt_conf.get("scoring_notes", "当置信度不足或类别不在列表中时，请返回 '未分类'，同时给出最主要的疑惑点。")
        self._force_json: bool = prompt_conf.get("force_json", True)
        self._few_shots: List[Dict[str, Any]] = prompt_conf.get("few_shots") or []
        self._expected_schema: Dict[str, Any] = prompt_conf.get("expected_schema", self.DEFAULT_EXPECTED_KEYS)

    def build_messages(self, *, bookmark: Dict[str, Any], hints: Dict[str, Any], category_library: List[Dict[str, Any]]) -> Tuple[List[Dict[str, str]], Optional[Dict[str, str]]]:
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": self._build_system_prompt(category_library)}
        ]
        for shot in self._few_shots:
            user_payload = {"demo": True, "bookmark": shot.get("bookmark", {}), "hints": shot.get("hints", {})}
            assistant_payload = shot.get("expected", {})
            if not assistant_payload:
                continue
            messages.append({"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)})
            messages.append({"role": "assistant", "content": json.dumps(assistant_payload, ensure_ascii=False)})
        request_payload = {
            "task": self._task_description, "bookmark": bookmark, "hints": hints,
            "category_library": category_library, "workflow": self._steps,
            "expected_output_keys": self._expected_schema, "notes": self._scoring_notes,
        }
        messages.append({"role": "user", "content": json.dumps(request_payload, ensure_ascii=False)})
        response_format = {"type": "json_object"} if self._force_json else None
        return messages, response_format

    def _build_system_prompt(self, category_library: List[Dict[str, Any]]) -> str:
        primary_categories = [e["name"] for e in category_library if "/" not in e["name"]]
        primary_hint = ", ".join(primary_categories[:12])
        steps_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(self._steps))
        schema_preview = json.dumps(self._expected_schema, ensure_ascii=False, indent=2)
        return (
            "你是 CleanBook-Agent，一名资深浏览器书签信息架构师。\n"
            "目标：在保持原始信息完整的前提下，为书签匹配最合适的分类，并输出结构化结果。\n"
            f"主分类参考（部分）：{primary_hint}\n"
            "请务必遵循以下工作流：\n"
            f"{steps_text}\n\n"
            "输出要求：\n"
            "- 严格使用 JSON，不添加额外文本。\n"
            "- 仅使用提供的类别，允许返回 '未分类'。\n"
            "- 置信度需与理由一致，避免夸大。\n\n"
            f"JSON 字段说明示例：\n{schema_preview}\n"
        )


class LLMClassifier:
    """LLM 分类器，通过 OpenAI 兼容接口进行分类推断"""

    def __init__(self, config_path: str | None = None):
        resolved_path, _ = resolve_config_path(config_path)
        self.config_path = str(resolved_path)
        self.config = self._load_config()
        self.llm_conf = self.config.get("llm", {}) or {}
        self.prompt_builder = LLMPromptBuilder(self.config)
        self._cache: Dict[str, Dict] = {}
        self._stats = {
            "enabled": bool(self.llm_conf.get("enable", False)),
            "calls": 0, "cache_hits": 0, "failures": 0,
        }

    def enabled(self) -> bool:
        return bool(self.llm_conf.get("enable", False))

    def classify(self, url: str, title: str, context: Optional[Dict] = None) -> Optional[Dict]:
        if not self.enabled():
            return None
        api_key_env = self.llm_conf.get("api_key_env", "OPENAI_API_KEY")
        api_key = os.getenv(api_key_env, "")
        if not api_key:
            return None

        h = hashlib.md5(f"{url}::{title}".encode()).hexdigest()
        if h in self._cache:
            self._stats["cache_hits"] += 1
            return self._cache[h]

        base_url = (self.llm_conf.get("base_url") or "https://api.openai.com").rstrip("/")
        model = self.llm_conf.get("model", "gpt-4o-mini")
        temperature = float(self.llm_conf.get("temperature", 0.0))
        top_p = float(self.llm_conf.get("top_p", 1.0))
        timeout = int(self.llm_conf.get("timeout_seconds", 25))
        max_retries = int(self.llm_conf.get("max_retries", 1))

        categories = self._collect_valid_categories(self.config)
        category_library = self._build_category_library(categories)
        bookmark_payload = self._build_bookmark_payload(url, title, context or {})
        hints = self._build_hint_profile(url, title, bookmark_payload)
        messages, response_format = self.prompt_builder.build_messages(
            bookmark=bookmark_payload, hints=hints, category_library=category_library,
        )

        payload = {"model": model, "temperature": temperature, "top_p": top_p, "messages": messages}
        if response_format:
            payload["response_format"] = response_format
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        url_chat = f"{base_url}/v1/chat/completions"

        data = None
        last_err = None
        for _ in range(max_retries + 1):
            try:
                self._stats["calls"] += 1
                resp = requests.post(url_chat, headers=headers, json=payload, timeout=timeout)
                if resp.status_code >= 400:
                    last_err = f"HTTP {resp.status_code}: {resp.text[:200]}"
                    continue
                j = resp.json()
                content = j.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                data = self._safe_parse_json(content)
                if data:
                    break
                last_err = f"invalid JSON: {content[:200]}"
            except Exception as e:
                last_err = str(e)

        if not data:
            self._stats["failures"] += 1
            return None

        category = self._map_to_known_category(data.get("category", "未分类"), categories)
        confidence = float(data.get("confidence", 0.0))
        reasons = data.get("reasons") or data.get("reason") or []
        if isinstance(reasons, str):
            reasons = [reasons]

        result = {
            "category": category,
            "confidence": max(0.0, min(1.0, confidence)),
            "reasoning": [f"LLM: {r}" for r in reasons],
            "method": "llm",
            "facets": data.get("facets") or {},
            "subcategory": data.get("subcategory"),
            "priority_tags": data.get("priority_tags", []),
        }
        self._cache[h] = result
        return result

    def get_stats(self) -> Dict:
        return dict(self._stats)

    def _load_config(self) -> Dict:
        data, _, _ = load_json_config(self.config_path)
        return data

    def _collect_valid_categories(self, config: Dict) -> List[str]:
        cats: List[str] = []
        if isinstance(config.get("category_order"), list):
            for x in config["category_order"]:
                nx = normalize_category_string(str(x))
                if nx and nx not in cats:
                    cats.append(nx)
        rules = config.get("category_rules", {}) or {}
        for k in rules.keys():
            nk = normalize_category_string(k)
            if nk and nk not in cats:
                cats.append(nk)
        if "未分类" not in cats:
            cats.append("未分类")
        return cats

    def _map_to_known_category(self, cat: str, valid: List[str]) -> str:
        cat_n = normalize_category_string(cat)
        if not cat_n:
            return "未分类"
        if cat_n in valid:
            return cat_n
        low = cat_n.strip().lower()
        for v in valid:
            if v.strip().lower() == low:
                return v
        if "/" in cat_n:
            main = cat_n.split("/", 1)[0].strip()
            for v in valid:
                if v.strip().lower() == main.lower():
                    return v
        return "未分类"

    def _safe_parse_json(self, text: str) -> Optional[Dict]:
        text = text.strip()
        if not text:
            return None
        if text.startswith("```"):
            text = text.strip("`").replace("json\n", "", 1)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            try:
                start = text.find("{")
                end = text.rfind("}")
                if start >= 0 and end > start:
                    return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                logger.debug(f"JSON解析失败: {text[:100]}")
                return None
        return None

    def _build_category_library(self, categories: List[str]) -> List[Dict[str, str]]:
        library = []
        for name in categories:
            entry = {"name": name, "description": ""}
            if "/" in name:
                main, sub = name.split("/", 1)
                entry["parent"] = main
                entry["description"] = f"{main} 下的 {sub}"
            else:
                entry["parent"] = None
                entry["description"] = f"主分类 {name}"
            library.append(entry)
        return library

    def _build_bookmark_payload(self, url: str, title: str, context: Dict[str, Any]) -> Dict[str, Any]:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path_segments = [seg for seg in parsed.path.split("/") if seg]
        query_params = parse_qs(parsed.query)
        keywords = self._extract_keywords(title)
        return {
            "url": url, "title": title, "domain": domain,
            "path_segments": path_segments[:8],
            "query_params": {k: v[:5] for k, v in query_params.items()},
            "keywords": keywords[:12], "context": context,
        }

    def _build_hint_profile(self, url: str, title: str, bookmark_payload: Dict[str, Any]) -> Dict[str, Any]:
        title_lower = title.lower()
        hints: Dict[str, Any] = {
            "contains_code": any(t in title_lower for t in ["github", "repo", "代码", "编程"]),
            "contains_doc": any(t in title_lower for t in ["doc", "文档", "documentation"]),
            "likely_video": self._is_video_url(url),
            "likely_news": any(t in title_lower for t in ["news", "资讯", "快讯"]),
            "likely_forum": any(t in bookmark_payload["domain"] for t in ["forum", "bbs", "community"]),
        }
        hints["language"] = self._detect_language(title)
        hints["secure_scheme"] = url.lower().startswith("https://")
        return hints

    def _extract_keywords(self, text: str) -> List[str]:
        tokens = _KEYWORD_REGEX.findall(text.lower())
        seen = set()
        keywords = []
        for token in tokens:
            if token not in seen:
                seen.add(token)
                keywords.append(token)
        return keywords

    def _detect_language(self, text: str) -> str:
        if _CHINESE_REGEX.search(text):
            return "zh"
        if _ENGLISH_REGEX.search(text):
            return "en"
        return "unknown"

    def _is_video_url(self, url: str) -> bool:
        lower = url.lower()
        return any(host in lower for host in ["youtube.com", "bilibili.com", "vimeo.com"])
