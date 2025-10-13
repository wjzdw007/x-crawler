#!/usr/bin/env python3
"""
LLM API 设置和测试脚本
"""

import os
from summarizer import TwitterSummarizer

def main():
    print("🤖 LLM API 设置和测试")
    print("=" * 50)
    
    # 检查当前状态
    print("\n📋 当前环境检查:")
    summarizer = TwitterSummarizer()
    
    print("\n💡 使用步骤:")
    print("1. 获取 OpenRouter API Key:")
    print("   - 访问: https://openrouter.ai/")
    print("   - 注册账号并获取API密钥")
    print("")
    print("2. 设置环境变量:")
    print("   export OPENROUTER_API_KEY='your_api_key_here'")
    print("   export LLM_MODEL='openai/gpt-4o-mini'  # 可选，指定模型")
    print("")
    print("3. 测试API连接:")
    print("   python setup_llm.py --test")
    print("")
    print("4. 运行完整爬虫:")
    print("   python run_crawler.py --count 500 --user-summaries --force")
    
    # 显示可用模型
    summarizer.list_available_models()
    
    print(f"\n📊 已配置的用户分析类型:")
    for username, profile in summarizer.user_analysis_profiles.items():
        if username != 'default':
            print(f"   👤 @{username}: {profile['focus']}")
        else:
            print(f"   🔧 {username}: {profile['focus']}")

def test_api(model=None):
    """测试API连接"""
    print("🧪 测试API连接...")
    
    summarizer = TwitterSummarizer(model=model)
    if not summarizer.api_key:
        print("❌ 请先设置 OPENROUTER_API_KEY 环境变量")
        return
    
    test_prompt = "请用中文回复：你好，这是一个API连接测试。请简短回复。"
    
    try:
        result = summarizer.call_llm_api(test_prompt)
        print(f"\n✅ API测试成功!")
        print(f"📄 响应预览: {result[:200]}...")
        return True
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def test_multiple_models():
    """测试多个模型的响应"""
    print("🧪 测试多个模型...")
    
    models_to_test = [
        "openai/gpt-4o-mini",
        "anthropic/claude-3-haiku", 
        "openai/gpt-4o"
    ]
    
    test_prompt = "用一句话回答：AI的未来发展方向是什么？"
    
    for model in models_to_test:
        print(f"\n🤖 测试模型: {model}")
        try:
            summarizer = TwitterSummarizer(model=model)
            if not summarizer.api_key:
                print("❌ 请先设置 OPENROUTER_API_KEY 环境变量")
                break
                
            result = summarizer.call_llm_api(test_prompt)
            print(f"✅ 响应: {result[:150]}...")
        except Exception as e:
            print(f"❌ 失败: {e}")

def show_model_usage():
    """显示模型使用方法"""
    print("\n🎯 模型指定方法:")
    print("1. 环境变量 (全局):")
    print("   export LLM_MODEL='anthropic/claude-3-haiku'")
    print("")
    print("2. 代码中指定:")
    print("   from summarizer import TwitterSummarizer")
    print("   summarizer = TwitterSummarizer(model='openai/gpt-4o-mini')")
    print("")  
    print("3. 动态切换:")
    print("   summarizer.set_model('meta-llama/llama-3.1-8b-instruct')")
    print("")
    print("4. 优先级: 代码参数 > 环境变量 > 默认配置")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_api()
    else:
        main()