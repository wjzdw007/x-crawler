#!/usr/bin/env python3
"""
爬虫集成测试 - 使用验证系统确保数据质量
"""

from crawler import XCrawler
from tools.validator import DataValidator
import json
from datetime import datetime

def test_crawler_with_validation():
    print("🧪 爬虫集成测试 - 包含数据质量验证")
    
    # 创建爬虫实例
    crawler = XCrawler()
    
    # 创建验证器
    validator = DataValidator()
    
    print("\n⚠️ 注意：此测试需要有效的认证信息")
    print("请确保已配置以下内容：")
    print("1. 有效的cookies (auth_token, ct0)")
    print("2. 正确的Bearer token")
    print("3. 其他必需的认证headers")
    
    # 模拟一个小规模的API响应来测试解析逻辑
    print("\n🔄 测试1: 解析逻辑验证")
    
    # 使用与黄金数据集相同的API响应文件进行测试
    test_response_file = "analysis_data/api_responses/response_213433_687388.json"
    
    try:
        with open(test_response_file, 'r', encoding='utf-8') as f:
            response_data = json.load(f)
        
        # 提取数据
        api_data = response_data.get('data', {})
        tweets = crawler.extract_tweets_from_response(api_data)
        
        print(f"✅ 成功提取 {len(tweets)} 条推文")
        
        # 显示前3条推文摘要
        for i, tweet in enumerate(tweets[:3]):
            print(f"  推文 {i+1}:")
            print(f"    ID: {tweet.get('id')}")
            print(f"    文本: {tweet.get('text', '')[:50]}...")
            print(f"    用户: {tweet.get('user', {}).get('name', 'N/A')} (@{tweet.get('user', {}).get('screen_name', 'N/A')})")
            print(f"    媒体: {len(tweet.get('media', []))} 个文件")
            
        # 验证数据质量
        print(f"\n🔍 数据质量验证:")
        golden_dataset = "golden_dataset/golden_dataset_20250911_220234.json"
        validation_results = validator.comprehensive_validation(tweets, golden_dataset)
        
        # 打印验证结果
        validator.print_validation_summary(validation_results)
        
        # 生成报告
        report_file = validator.generate_validation_report(validation_results, tweets)
        
        # 测试结果评估
        scores = [result.score for result in validation_results.values()]
        overall_score = sum(scores) / len(scores) if scores else 0
        
        print(f"\n📊 测试结果:")
        print(f"总体评分: {overall_score:.1f}/100")
        
        if overall_score >= 80:
            print("✅ 测试通过 - 爬虫解析逻辑工作正常")
        else:
            print("❌ 测试失败 - 需要修复解析逻辑")
            
        print(f"详细报告: {report_file}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n🔄 测试2: 认证状态检查")
    
    # 检查是否能进行实际的HTTP请求
    print("检查认证配置...")
    
    # 这里应该有实际的认证检查逻辑
    # 但目前我们没有真实的cookies，所以跳过
    print("⚠️ 跳过实际HTTP请求测试 - 需要有效认证")
    
    print("\n📋 后续步骤:")
    print("1. 配置有效的认证信息")
    print("2. 测试实际的时间线API请求")
    print("3. 验证分页和游标机制")
    print("4. 实现错误处理和重试逻辑")
    print("5. 建立监控和告警机制")

def extract_cookies_instruction():
    """提供提取cookies的指导"""
    print("\n🔑 认证信息配置指导:")
    print("1. 在浏览器中打开 https://x.com/home")
    print("2. 打开开发者工具 (F12)")
    print("3. 切换到Network标签")
    print("4. 刷新页面，找到时间线API请求")
    print("5. 复制请求头中的以下信息:")
    print("   - Cookie: auth_token=...; ct0=...")
    print("   - Authorization: Bearer ...")
    print("   - X-Csrf-Token: ...")
    print("6. 将这些信息配置到爬虫中")

if __name__ == "__main__":
    test_crawler_with_validation()
    extract_cookies_instruction()