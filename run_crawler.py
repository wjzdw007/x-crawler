#!/usr/bin/env python3
"""
X爬虫命令行工具 - 支持灵活参数配置
"""

import argparse
import json
import sys

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
        default=None,
        help='最大爬取页数 (可选安全上限，默认由target_count自然终止)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='测试模式 - 只验证数据质量，不生成完整报告'
    )
    
    parser.add_argument(
        '--user-summaries',
        action='store_true',
        help='生成用户个人总结 - 如果指定--count则抓取新数据后生成总结，否则只处理已有数据'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制覆盖已存在的总结文件 (仅与--user-summaries配合使用)'
    )
    
    
    args = parser.parse_args()
    
    print("🚀 X推文爬虫系统")
    print(f"📋 配置文件: {args.config}")
    if args.count:
        print(f"🎯 目标数量: {args.count} 条")
    print(f"📍 时间线类型: {args.timeline}")
    if args.max_pages:
        print(f"📄 页数限制: {args.max_pages} 页")
    
    try:
        if args.user_summaries and not args.count:
            # 纯用户总结模式 - 只处理昨天的数据
            mode_text = "生成昨天的个人总结"
            if args.force:
                mode_text += " (强制覆盖模式)"
            print(f"\n🤖 用户总结模式 - {mode_text}")
            from crawler import XCrawler
            crawler = XCrawler()
            crawler.generate_user_summaries_for_yesterday(force_overwrite=args.force)
        elif args.test:
            # 测试模式
            print("\n🧪 测试模式已废弃，请使用正常模式")
        else:
            # 正常模式 - 抓取新数据
            if args.user_summaries:
                # 只抓取数据并生成用户总结，不生成全局报告
                print(f"\n📡 抓取数据并生成用户总结...")
                from crawler import XCrawler
                crawler = XCrawler()
                
                # 直接使用爬虫抓取数据
                tweets = crawler.crawl_daily_posts(
                    timeline_type='recommended', 
                    target_count=args.count,
                    max_pages=args.max_pages
                )
                
                if tweets:
                    print(f"\n✅ 数据抓取完成：{len(tweets)} 条推文")
                    
                    # 为前一天的数据生成用户总结
                    print(f"🔄 为前一天的数据生成用户总结...")
                    
                    crawler.generate_user_summaries_for_yesterday(force_overwrite=args.force)
                else:
                    print(f"\n❌ 数据抓取失败")
                    sys.exit(1)
            else:
                # 标准模式：只抓取数据
                print(f"\n📡 抓取数据...")
                from crawler import XCrawler
                crawler = XCrawler()

                tweets = crawler.crawl_daily_posts(
                    timeline_type='recommended',
                    target_count=args.count,
                    max_pages=args.max_pages
                )

                if tweets:
                    print(f"\n✅ 数据抓取完成：{len(tweets)} 条推文")
                    print(f"📁 数据保存在 crawler_data/daily_posts/ 目录")
                else:
                    print(f"\n❌ 数据抓取失败")
                    sys.exit(1)
                
    except FileNotFoundError:
        print(f"\n❌ 配置文件不存在: {args.config}")
        print("💡 请先运行认证配置:")
        print("   python working_auth.py")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        print("💡 建议:")
        print("   1. 检查 TENCENT_DEEPSEEK_API_KEY / OPENAI_MODEL / OPENAI_BASE_URL 是否已配置且有效")
        print("   2. 检查昨天的 users_daily 数据文件是否存在")
        print("   3. 查看上方失败用户列表与 LLM 错误")
        sys.exit(1)

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

# 生成用户个人总结 (昨天的数据)
python run_crawler.py --user-summaries

# 强制覆盖已存在的总结文件 (用于测试)
python run_crawler.py --user-summaries --force
# 生成用户总结（提示词完全由配置文件决定）
python run_crawler.py --user-summaries

# 抓取500条新数据并生成今天的用户总结 (不生成全局报告)
python run_crawler.py --count 500 --user-summaries

# 抓取新数据并强制覆盖用户总结
python run_crawler.py --count 300 --user-summaries --force

# 标准模式：抓取数据并生成全局分析报告
python run_crawler.py --count 500

# 高级配置 - 限制最大页数
python run_crawler.py --count 100 --max-pages 3
""")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 2 and sys.argv[1] in ['help']:
        show_examples()
    else:
        main()