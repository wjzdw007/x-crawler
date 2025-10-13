#!/usr/bin/env python3
"""
测试配置系统
"""

from config_loader import ConfigLoader
import os

def test_config():
    """测试配置加载"""
    print("🔧 测试配置系统\n")

    # 创建配置加载器
    loader = ConfigLoader()

    # 显示配置来源
    print("📋 配置检查:")
    print("-" * 50)

    # 检查 .env 文件
    if os.path.exists('.env'):
        print("✅ 发现 .env 文件")
    else:
        print("❌ 未发现 .env 文件")

    # 检查 config.json
    if os.path.exists('config.json'):
        print("✅ 发现 config.json 文件")
    else:
        print("❌ 未发现 config.json 文件")

    print("\n📊 当前配置值:")
    print("-" * 50)

    # X平台认证
    auth_token = loader.get('authentication.cookies.auth_token')
    ct0_token = loader.get('authentication.cookies.ct0')

    if auth_token and not auth_token.startswith('your_'):
        print(f"✅ Auth Token: {auth_token[:20]}...")
    else:
        print("❌ Auth Token: 未配置或使用默认值")

    if ct0_token and not ct0_token.startswith('your_'):
        print(f"✅ CT0 Token: {ct0_token[:20]}...")
    else:
        print("❌ CT0 Token: 未配置或使用默认值")

    # LLM配置
    api_key = loader.get('llm.api_key')
    model = loader.get('llm.model')

    if api_key:
        print(f"✅ LLM API Key: {'*' * 10}{api_key[-5:]}")
    else:
        print("⚠️ LLM API Key: 未配置（将使用模拟模式）")

    print(f"📝 LLM Model: {model}")

    # 代理配置
    proxy = loader.get_proxy_settings()
    if proxy:
        print(f"🌐 代理设置: {proxy}")
    else:
        print("🔄 代理设置: 未配置（直连）")

    # 爬虫设置
    print(f"\n⚙️ 爬虫设置:")
    print(f"  请求速率: {loader.get('settings.requests_per_hour')} 请求/小时")
    print(f"  重试次数: {loader.get('settings.retry_attempts')} 次")
    print(f"  超时时间: {loader.get('settings.timeout')} 秒")
    print(f"  目标数量: {loader.get('targets.daily_tweet_count')} 条/天")

    # 验证配置
    print("\n🔍 配置验证:")
    print("-" * 50)
    is_valid = loader.validate()

    if is_valid:
        print("\n✅ 配置正常，可以运行爬虫")
        print("\n🚀 运行命令:")
        print("  python run_crawler.py --user-summaries")
    else:
        print("\n⚠️ 请先完成配置")
        print("\n💡 配置方法:")
        print("  1. 运行: python auth_setup.py")
        print("  2. 或复制 .env.example 为 .env 并填入配置")
        print("  3. 或编辑 config.json 文件")

if __name__ == "__main__":
    test_config()