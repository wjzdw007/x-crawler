#!/usr/bin/env python3
"""Regression tests: mock summaries must not look like success."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from summarizer import (  # noqa: E402
    DAILY_SUMMARY_LANGUAGE_CONSTRAINT,
    DEFAULT_LLM_BASE_URL,
    DEFAULT_LLM_MODEL,
    LLMUnavailableError,
    TENCENT_DEEPSEEK_FALLBACK_MODELS,
    TwitterSummarizer,
    apply_daily_summary_language_constraint,
    data_day_yyyymmdd,
    format_data_date_label,
    is_mock_summary,
    normalize_api_key,
    resolve_llm_api_key,
)


LLM_ENV_KEYS = (
    "TENCENT_DEEPSEEK_API_KEY",
    "LKEAP_API_KEY",
    "OPENAI_API_KEY",
    "LLM_API_KEY",
    "OPENROUTER_API_KEY",
    "OPENAI_MODEL",
    "OPENAI_BASE_URL",
    "LKEAP_BASE_URL",
    "ALLOW_MOCK_SUMMARY",
    "DATA_DIR",
)


SAMPLE_TWEETS = [
    {
        "id": "1",
        "text": "hello world",
        "user": {"screen_name": "dotey"},
        "created_at": "Wed Oct 21 12:00:00 +0000 2026",
    }
]


class FailClosedTests(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self._tmpdir = tempfile.mkdtemp()
        self._saved_env = {k: os.environ.get(k) for k in LLM_ENV_KEYS}
        for key in LLM_ENV_KEYS:
            os.environ.pop(key, None)
        os.chdir(self._tmpdir)

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self._tmpdir, ignore_errors=True)
        for key, value in self._saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_is_mock_summary_detects_placeholder_markers(self):
        mock = TwitterSummarizer(allow_mock=True).generate_mock_summary()
        self.assertTrue(is_mock_summary(mock))
        self.assertTrue(is_mock_summary("由于API配置限制，当前显示模拟内容"))
        self.assertTrue(is_mock_summary("配置LLM API密钥后将显示详细智能分析结果"))
        self.assertFalse(is_mock_summary("## 核心动态\n- Grok 发布"))
        self.assertFalse(is_mock_summary(""))

    def test_normalize_api_key_rejects_placeholders(self):
        self.assertIsNone(normalize_api_key(""))
        self.assertIsNone(normalize_api_key("  "))
        self.assertIsNone(normalize_api_key("your_openrouter_api_key_here"))
        self.assertIsNone(normalize_api_key("your_tencent_deepseek_api_key_here"))
        self.assertEqual(normalize_api_key(" sk-real "), "sk-real")

    def test_missing_key_raises_instead_of_mock(self):
        summarizer = TwitterSummarizer(allow_mock=False)
        self.assertIsNone(summarizer.api_key)
        with self.assertRaises(LLMUnavailableError) as ctx:
            summarizer.call_llm_api("summarize these tweets")
        self.assertIn("TENCENT_DEEPSEEK_API_KEY", str(ctx.exception))

    def test_openrouter_key_is_ignored(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-should-be-ignored"
        self.assertIsNone(resolve_llm_api_key())
        summarizer = TwitterSummarizer(allow_mock=False)
        self.assertIsNone(summarizer.api_key)
        with self.assertRaises(LLMUnavailableError):
            summarizer.call_llm_api("hi")

    def test_tencent_key_is_preferred(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-ignored"
        os.environ["TENCENT_DEEPSEEK_API_KEY"] = "sk-tencent-real"
        self.assertEqual(resolve_llm_api_key(), "sk-tencent-real")
        summarizer = TwitterSummarizer()
        self.assertEqual(summarizer.api_key, "sk-tencent-real")

    def test_default_provider_is_tencent_deepseek_not_openrouter(self):
        summarizer = TwitterSummarizer(allow_mock=True)
        self.assertEqual(summarizer.base_url, DEFAULT_LLM_BASE_URL)
        self.assertIn("lkeap.cloud.tencent.com", summarizer.base_url)
        self.assertNotIn("openrouter", summarizer.base_url)
        self.assertEqual(summarizer.llm_config["default_model"], DEFAULT_LLM_MODEL)
        self.assertEqual(DEFAULT_LLM_MODEL, "deepseek-v3.2")
        self.assertTrue(all("deepseek" in m for m in summarizer.llm_config["fallback_models"]))
        self.assertNotIn("anthropic/claude-3-haiku", summarizer.llm_config["fallback_models"])
        self.assertNotIn("openai/gpt-4o", summarizer.llm_config["fallback_models"])
        self.assertEqual(tuple(summarizer.llm_config["fallback_models"]), TENCENT_DEEPSEEK_FALLBACK_MODELS)

    def test_allow_mock_opt_in_still_tagged(self):
        summarizer = TwitterSummarizer(allow_mock=True)
        text = summarizer.call_llm_api("anything")
        self.assertTrue(is_mock_summary(text))

    def test_mock_title_uses_data_day_not_run_day(self):
        summarizer = TwitterSummarizer(allow_mock=True)
        summarizer._summary_date = "20261021"
        text = summarizer.generate_mock_summary()
        self.assertIn("2026年10月21日", text)
        self.assertNotIn("2026年10月22日", text)

    def test_data_day_follows_beijing_yesterday(self):
        from zoneinfo import ZoneInfo

        utc = ZoneInfo("UTC")
        # Workflow cron 01:00 UTC = 09:00 Beijing on Oct 22 → data day Oct 21
        self.assertEqual(
            data_day_yyyymmdd(datetime(2026, 10, 22, 1, 0, tzinfo=utc)),
            "20261021",
        )
        # 15:59 UTC Oct 21 = 23:59 Beijing Oct 21 → yesterday Oct 20
        self.assertEqual(
            data_day_yyyymmdd(datetime(2026, 10, 21, 15, 59, tzinfo=utc)),
            "20261020",
        )
        self.assertEqual(format_data_date_label("20261021"), "2026年10月21日")

    def test_generate_summary_without_key_does_not_save_summary(self):
        summarizer = TwitterSummarizer(allow_mock=False)
        with self.assertRaises(LLMUnavailableError):
            summarizer.generate_summary(SAMPLE_TWEETS, "user_daily", {"screen_name": "dotey"},
                                       summary_date="20261021")
        summaries = Path("crawler_data/user_summaries")
        if summaries.exists():
            self.assertEqual(list(summaries.glob("*summary*.md")), [])
            self.assertEqual(list(summaries.glob("*summary*.json")), [])

    def test_empty_tweets_returns_error_without_mock(self):
        summarizer = TwitterSummarizer(allow_mock=False)
        result = summarizer.generate_summary([], "user_daily", {"screen_name": "dotey"})
        self.assertEqual(result["error"], "没有推文数据可供总结")
        self.assertFalse(is_mock_summary(result.get("summary")))

    def test_prompt_includes_data_date(self):
        summarizer = TwitterSummarizer(allow_mock=True)
        summarizer._summary_date = "20261021"
        prompt = summarizer.generate_simple_prompt(SAMPLE_TWEETS, {"screen_name": "dotey"})
        self.assertIn("20261021", prompt)
        self.assertIn("2026年10月21日", prompt)
        self.assertTrue(prompt.startswith(DAILY_SUMMARY_LANGUAGE_CONSTRAINT))

    def _write_repo_templates(self):
        src = REPO_ROOT / "user_prompt_templates.json"
        dest = Path("user_prompt_templates.json")
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        return json.loads(src.read_text(encoding="utf-8"))

    def test_built_prompt_forces_simplified_chinese_for_default_and_user_templates(self):
        templates = self._write_repo_templates()
        self.assertIn("default", templates)
        self.assertIn("dotey", templates)

        summarizer = TwitterSummarizer(allow_mock=True)
        summarizer._summary_date = "20261021"

        default_prompt = summarizer.generate_simple_prompt(
            SAMPLE_TWEETS, {"screen_name": "unknown_user_without_template"}
        )
        user_prompt = summarizer.generate_simple_prompt(
            SAMPLE_TWEETS, {"screen_name": "dotey"}
        )

        for prompt in (default_prompt, user_prompt):
            self.assertTrue(prompt.startswith(DAILY_SUMMARY_LANGUAGE_CONSTRAINT))
            self.assertIn("简体中文", prompt)
            self.assertIn("标题与正文均为中文", prompt)
            self.assertIn("@账号可保留原文", prompt)

        self.assertIn("分析用户今天的推文", default_prompt)
        self.assertIn("dotey是AI技术专家", user_prompt)
        self.assertNotEqual(default_prompt, user_prompt)

    def test_fallback_template_prompt_also_includes_chinese_constraint(self):
        summarizer = TwitterSummarizer(allow_mock=True)
        self.assertEqual(summarizer.user_prompt_templates, {})
        prompt = summarizer.generate_simple_prompt(
            SAMPLE_TWEETS, {"screen_name": "nobody"}
        )
        self.assertTrue(prompt.startswith(DAILY_SUMMARY_LANGUAGE_CONSTRAINT))
        self.assertIn("简体中文", prompt)

    def test_language_constraint_helper_is_idempotent(self):
        once = apply_daily_summary_language_constraint("hello")
        twice = apply_daily_summary_language_constraint(once)
        self.assertEqual(once, twice)
        self.assertEqual(
            DAILY_SUMMARY_LANGUAGE_CONSTRAINT,
            "输出必须使用简体中文。标题与正文均为中文；专有名词、品牌名、@账号可保留原文。",
        )

    def test_llm_call_sends_chinese_system_constraint(self):
        summarizer = TwitterSummarizer(api_key="sk-test-tencent", allow_mock=False)
        captured = {}

        class FakeCompletions:
            def create(self, **kwargs):
                captured["messages"] = kwargs["messages"]
                msg = type("M", (), {"content": "## 核心动态\n- 测试"})()
                choice = type("C", (), {"message": msg})()
                return type("R", (), {"choices": [choice]})()

        class FakeChat:
            def __init__(self):
                self.completions = FakeCompletions()

        class FakeClient:
            def __init__(self, *args, **kwargs):
                self.chat = FakeChat()

        fake_openai = type(sys)("openai")
        fake_openai.OpenAI = FakeClient
        with patch.dict(sys.modules, {"openai": fake_openai}):
            result = summarizer.call_llm_api("hello")
        self.assertEqual(captured["messages"][0]["role"], "system")
        self.assertEqual(captured["messages"][0]["content"], DAILY_SUMMARY_LANGUAGE_CONSTRAINT)
        self.assertEqual(captured["messages"][1]["role"], "user")
        self.assertIn("核心动态", result)

    def test_api_error_does_not_return_mock(self):
        summarizer = TwitterSummarizer(api_key="sk-test-tencent", allow_mock=False)
        fake_openai = type(sys)("openai")

        class Boom:
            def __init__(self, *args, **kwargs):
                pass

            @property
            def chat(self):
                raise RuntimeError("403 quota exceeded")

        fake_openai.OpenAI = Boom
        with patch.dict(sys.modules, {"openai": fake_openai}):
            with self.assertRaises(LLMUnavailableError) as ctx:
                summarizer.call_llm_api("hello")
        self.assertIn("失败", str(ctx.exception))


class CrawlerFailClosedTests(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self._tmpdir = tempfile.mkdtemp()
        self._saved_env = {k: os.environ.get(k) for k in LLM_ENV_KEYS}
        for key in LLM_ENV_KEYS:
            os.environ.pop(key, None)
        os.chdir(self._tmpdir)
        from crawler import UserSummaryError, XCrawler
        self.UserSummaryError = UserSummaryError
        self.XCrawler = XCrawler

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self._tmpdir, ignore_errors=True)
        for key, value in self._saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def _write_user_day(self, username: str, date_str: str):
        users_dir = Path("crawler_data/users_daily")
        users_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "user": {"screen_name": username},
            "date": date_str,
            "tweets": SAMPLE_TWEETS,
        }
        path = users_dir / f"{username}_{date_str}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_missing_key_fails_and_does_not_write_md(self):
        self._write_user_day("dotey", "20261021")
        crawler = self.XCrawler(data_dir="crawler_data")
        with self.assertRaises(self.UserSummaryError) as ctx:
            crawler.generate_user_summaries_for_date("20261021")
        self.assertIn("TENCENT_DEEPSEEK_API_KEY", str(ctx.exception))
        md = Path("crawler_data/user_summaries/dotey_20261021_summary.md")
        self.assertFalse(md.exists())

    def test_missing_data_files_fail_loudly(self):
        crawler = self.XCrawler(data_dir="crawler_data")
        with self.assertRaises(self.UserSummaryError) as ctx:
            crawler.generate_user_summaries_for_date("20261021")
        self.assertIn("未找到日期", str(ctx.exception))

    def test_existing_real_summary_is_skipped(self):
        self._write_user_day("dotey", "20261021")
        summaries = Path("crawler_data/user_summaries")
        summaries.mkdir(parents=True, exist_ok=True)
        md = summaries / "dotey_20261021_summary.md"
        md.write_text("## 核心动态\n- 真实总结", encoding="utf-8")
        crawler = self.XCrawler(data_dir="crawler_data")
        result = crawler.generate_user_summaries_for_date("20261021")
        self.assertEqual(result["skipped"], ["dotey"])
        self.assertEqual(md.read_text(encoding="utf-8"), "## 核心动态\n- 真实总结")

    def test_existing_mock_is_not_treated_as_success(self):
        self._write_user_day("dotey", "20261021")
        summaries = Path("crawler_data/user_summaries")
        summaries.mkdir(parents=True, exist_ok=True)
        md = summaries / "dotey_20261021_summary.md"
        mock = TwitterSummarizer(allow_mock=True).generate_mock_summary()
        md.write_text(mock, encoding="utf-8")
        crawler = self.XCrawler(data_dir="crawler_data")
        with self.assertRaises(self.UserSummaryError):
            crawler.generate_user_summaries_for_date("20261021")
        self.assertTrue(is_mock_summary(md.read_text(encoding="utf-8")))

    def test_cli_exits_nonzero_without_key(self):
        import subprocess

        os.environ["DATA_DIR"] = str(Path(self._tmpdir) / "empty_data")
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "run_crawler.py"), "--user-summaries"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            env={**os.environ, "DATA_DIR": str(Path(self._tmpdir) / "empty_data")},
        )
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


class CheckScriptTests(unittest.TestCase):
    def test_check_script_rejects_mock_file(self):
        import subprocess

        with tempfile.TemporaryDirectory() as tmp:
            mock_path = Path(tmp) / "dotey_20261021_summary.md"
            mock_path.write_text(
                TwitterSummarizer(allow_mock=True).generate_mock_summary(),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts/check_summaries_not_mock.py"), str(mock_path)],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

            real_path = Path(tmp) / "dotey_real.md"
            real_path.write_text("## 核心动态\n- Grok 发布", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts/check_summaries_not_mock.py"), str(real_path)],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
