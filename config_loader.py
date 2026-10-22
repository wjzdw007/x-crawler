#!/usr/bin/env python3
"""
配置加载器 - 支持从.env文件和config.json加载配置
优先级: .env > config.json > 默认值
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class ConfigLoader:
    """统一的配置管理器"""

    def __init__(self, config_file="config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()

    def _load_config(self):
        """加载配置，优先级: .env > config.json > 默认值"""
        # 默认配置
        config = {
            "authentication": {
                "cookies": {},
                "headers": {}
            },
            "settings": {
                "requests_per_hour": 400,
                "retry_attempts": 3,
                "retry_delay": 5,
                "timeout": 30
            },
            "targets": {
                "daily_tweet_count": 100,
                "timeline_types": ["recommended"]
            },
            "llm": {
                "api_key": None,
                "model": "deepseek-v3.2",
                "base_url": "https://api.lkeap.cloud.tencent.com/v1"
            },
            "proxy": {
                "http": None,
                "https": None
            }
        }

        # 从config.json加载（如果存在）
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                json_config = json.load(f)
                self._deep_update(config, json_config)

        # 从环境变量覆盖
        # X平台认证
        if os.getenv('X_AUTH_TOKEN'):
            config['authentication']['cookies']['auth_token'] = os.getenv('X_AUTH_TOKEN')
        if os.getenv('X_CT0_TOKEN'):
            config['authentication']['cookies']['ct0'] = os.getenv('X_CT0_TOKEN')
        if os.getenv('X_BEARER_TOKEN'):
            config['authentication']['headers']['Authorization'] = os.getenv('X_BEARER_TOKEN')
        if os.getenv('X_CSRF_TOKEN'):
            config['authentication']['headers']['X-Csrf-Token'] = os.getenv('X_CSRF_TOKEN')

        # LLM配置 — 腾讯云 DeepSeek；不读取 OPENROUTER_API_KEY
        for env_name in ("TENCENT_DEEPSEEK_API_KEY", "LKEAP_API_KEY", "OPENAI_API_KEY", "LLM_API_KEY"):
            value = os.getenv(env_name)
            if value and value.strip():
                config['llm']['api_key'] = value.strip()
                break
        if os.getenv('OPENAI_MODEL', '').strip():
            config['llm']['model'] = os.getenv('OPENAI_MODEL').strip()
        if os.getenv('OPENAI_BASE_URL', '').strip():
            config['llm']['base_url'] = os.getenv('OPENAI_BASE_URL').strip().rstrip('/')
        elif os.getenv('LKEAP_BASE_URL', '').strip():
            config['llm']['base_url'] = os.getenv('LKEAP_BASE_URL').strip().rstrip('/')

        # 代理配置
        if os.getenv('HTTP_PROXY'):
            config['proxy']['http'] = os.getenv('HTTP_PROXY')
        if os.getenv('HTTPS_PROXY'):
            config['proxy']['https'] = os.getenv('HTTPS_PROXY')

        # 爬虫设置
        if os.getenv('REQUESTS_PER_HOUR'):
            config['settings']['requests_per_hour'] = int(os.getenv('REQUESTS_PER_HOUR'))
        if os.getenv('RETRY_ATTEMPTS'):
            config['settings']['retry_attempts'] = int(os.getenv('RETRY_ATTEMPTS'))
        if os.getenv('RETRY_DELAY'):
            config['settings']['retry_delay'] = int(os.getenv('RETRY_DELAY'))
        if os.getenv('TIMEOUT'):
            config['settings']['timeout'] = int(os.getenv('TIMEOUT'))
        if os.getenv('DAILY_TWEET_COUNT'):
            config['targets']['daily_tweet_count'] = int(os.getenv('DAILY_TWEET_COUNT'))

        return config

    def _deep_update(self, base, update):
        """深度更新字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def get(self, key_path, default=None):
        """通过点分路径获取配置值
        例如: get('authentication.cookies.auth_token')
        """
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def save_to_json(self, output_file=None):
        """保存当前配置到JSON文件"""
        output_file = output_file or self.config_file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        print(f"✅ 配置已保存到: {output_file}")

    def validate(self):
        """验证必要的配置是否存在"""
        errors = []

        # 检查X平台认证
        if not self.get('authentication.cookies.auth_token'):
            errors.append("缺少 auth_token (X_AUTH_TOKEN)")
        if not self.get('authentication.cookies.ct0'):
            errors.append("缺少 ct0 (X_CT0_TOKEN)")

        if errors:
            print("⚠️ 配置验证失败:")
            for error in errors:
                print(f"  ❌ {error}")
            return False

        print("✅ 配置验证通过")
        return True

    def get_proxy_settings(self):
        """获取代理设置"""
        proxy = self.config.get('proxy', {})
        if proxy.get('http') or proxy.get('https'):
            return {
                'http': proxy.get('http'),
                'https': proxy.get('https')
            }
        return None


def main():
    """测试配置加载"""
    print("🔧 配置加载器测试")

    loader = ConfigLoader()

    print("\n📋 当前配置:")
    print(f"  Auth Token: {loader.get('authentication.cookies.auth_token', '未设置')[:20]}...")
    print(f"  CT0 Token: {loader.get('authentication.cookies.ct0', '未设置')[:20]}...")
    print(f"  LLM API Key: {'已设置' if loader.get('llm.api_key') else '未设置'}")
    print(f"  LLM Model: {loader.get('llm.model')}")
    print(f"  LLM Base URL: {loader.get('llm.base_url')}")
    print(f"  代理设置: {loader.get_proxy_settings() or '未设置'}")

    print("\n🔍 验证配置:")
    loader.validate()

    # 提示如何设置
    if not loader.validate():
        print("\n💡 配置方法:")
        print("1. 复制 .env.example 为 .env 并填入你的配置")
        print("2. 或运行 python auth_setup.py 自动获取认证信息")


if __name__ == "__main__":
    main()