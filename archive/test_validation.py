#!/usr/bin/env python3
"""
测试数据验证系统
"""

from tools.validator import DataValidator
import json

def test_validation():
    print("🧪 测试数据验证系统")
    
    # 使用修正后的黄金数据集
    golden_file = "golden_dataset/golden_dataset_20250911_220234.json"
    
    # 加载黄金数据集
    with open(golden_file, 'r', encoding='utf-8') as f:
        golden_data = json.load(f)
    
    baseline_tweets = golden_data.get('baseline_tweets', [])
    print(f"📊 黄金数据集包含 {len(baseline_tweets)} 条基准推文")
    
    # 创建模拟的爬虫输出数据 - 基于黄金数据集
    mock_tweets = []
    for i, baseline in enumerate(baseline_tweets[:10]):  # 测试前10条
        tweet = {
            'id': baseline['tweet_id'],
            'text': baseline['expected_text'],
            'created_at': baseline['expected_created_at'],
            'user': baseline.get('expected_user', {}),
            'stats': baseline.get('expected_stats', {}),
            'media': [],  # 修正：正确复制媒体信息
            'retweet': None,
            'quoted': None
        }
        
        # 正确复制媒体信息
        expected_media = baseline.get('expected_media', [])
        for media_item in expected_media:
            tweet['media'].append({
                'type': media_item.get('type'),
                'id': media_item.get('id'),
                'url': media_item.get('expected_url')
            })
        
        # 添加转推数据
        if baseline.get('is_retweet'):
            tweet['retweet'] = {
                'text': baseline.get('expected_retweet_text', ''),
                'user': baseline.get('expected_retweet_user', {})
            }
        
        # 添加引用数据
        if baseline.get('is_quoted'):
            tweet['quoted'] = {
                'text': baseline.get('expected_quoted_text', '')
            }
        
        mock_tweets.append(tweet)
    
    print(f"🔧 创建了 {len(mock_tweets)} 条模拟爬虫数据")
    
    # 执行验证
    validator = DataValidator()
    results = validator.comprehensive_validation(mock_tweets, golden_file)
    
    # 打印结果
    validator.print_validation_summary(results)
    
    # 生成报告
    report_file = validator.generate_validation_report(results, mock_tweets)
    print(f"📄 验证报告: {report_file}")

if __name__ == "__main__":
    test_validation()