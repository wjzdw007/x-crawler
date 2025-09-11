#!/usr/bin/env python3
"""
X爬虫命令行工具 - 支持灵活参数配置
"""

import argparse
import json
from daily_report_generator import DailyReportGenerator

def main():
    parser = argparse.ArgumentParser(description='X推文爬虫 - 生成每日报告')
    
    # 添加命令行参数
    parser.add_argument(
        '-c', '--count',
        type=int,
        default=None,
        help='指定要抓取的推文数量 (默认使用config.json中的设置)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='指定配置文件路径 (默认: config.json)'
    )
    
    parser.add_argument(
        '--timeline',
        type=str,
        default='recommended',
        choices=['recommended', 'following'],
        help='时间线类型 (默认: recommended)'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='最大爬取页数 (默认: 10)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='测试模式 - 只验证数据质量，不生成完整报告'
    )
    
    args = parser.parse_args()
    
    print("🚀 X推文爬虫系统")
    print(f"📋 配置文件: {args.config}")
    if args.count:
        print(f"🎯 目标数量: {args.count} 条")
    print(f"📍 时间线类型: {args.timeline}")
    
    try:
        # 创建报告生成器
        generator = DailyReportGenerator(args.config)
        
        if args.test:
            # 测试模式
            print("\n🧪 测试模式 - 验证数据质量")
            from test_crawler_with_validation import test_crawler_with_validation
            test_crawler_with_validation()
        else:
            # 正常模式
            result = generator.generate_daily_report(tweet_count=args.count)
            
            if result["success"]:
                print(f"\n🎉 报告生成成功！")
                print(f"📄 报告位置: {result['report_file']}")
                print(f"📊 推文数量: {result['tweet_count']} 条")
                print(f"🏆 数据质量: {result['data_quality_score']:.1f}/100")
            else:
                print(f"\n❌ 报告生成失败: {result.get('error', '未知错误')}")
                
    except FileNotFoundError:
        print(f"\n❌ 配置文件不存在: {args.config}")
        print("💡 请先运行认证配置:")
        print("   python working_auth.py")
        
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        print("💡 建议:")
        print("   1. 检查网络连接")
        print("   2. 验证认证信息是否有效")
        print("   3. 查看详细日志信息")

def show_examples():
    """显示使用示例"""
    print("""
🎯 使用示例:

# 使用默认配置
python run_crawler.py

# 指定抓取200条推文
python run_crawler.py --count 200

# 抓取50条following时间线推文
python run_crawler.py --count 50 --timeline following

# 使用自定义配置文件
python run_crawler.py --config my_config.json --count 150

# 测试模式 - 只验证数据质量
python run_crawler.py --test

# 高级配置 - 限制最大页数
python run_crawler.py --count 100 --max-pages 3
""")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 2 and sys.argv[1] in ['--help', '-h', 'help']:
        show_examples()
    else:
        main()