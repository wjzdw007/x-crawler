#!/usr/bin/env python3
"""
每日推文报告生成器 - 完整的端到端系统
集成爬虫数据采集、数据验证和LLM智能总结
"""

import json
import os
from datetime import datetime
from pathlib import Path
from crawler import XCrawler
from summarizer import TwitterSummarizer
from realtime_validator import RealtimeValidator

class DailyReportGenerator:
    def __init__(self, config_file: str = "config.json"):
        """
        初始化每日报告生成器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self.load_config()
        
        # 初始化组件
        self.crawler = XCrawler(config_file=config_file)
        self.summarizer = TwitterSummarizer()
        self.validator = RealtimeValidator()
        
        # 创建输出目录
        self.output_dir = Path("daily_reports")
        self.output_dir.mkdir(exist_ok=True)
        
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"⚠️ 配置文件 {self.config_file} 不存在，使用默认设置")
            return {
                "targets": {
                    "daily_tweet_count": 100,
                    "timeline_types": ["recommended"]
                }
            }
    
    def generate_daily_report(self, tweet_count: int = None) -> dict:
        """
        生成每日报告
        
        Args:
            tweet_count: 目标推文数量，默认使用配置文件设置
        
        Returns:
            包含所有结果的字典
        """
        print("📊 开始生成每日推文报告")
        
        # 使用配置文件中的设置或参数覆盖
        target_count = tweet_count or self.config.get("targets", {}).get("daily_tweet_count", 100)
        
        # 步骤1: 数据采集
        print(f"\n🔍 步骤1: 采集 {target_count} 条推文...")
        tweets = self.crawler.crawl_daily_posts(
            timeline_type="recommended", 
            max_pages=10,  # 增加页数以确保能抓到足够数量
            target_count=target_count
        )
        
        if not tweets:
            print("❌ 数据采集失败，无法生成报告")
            return {"success": False, "error": "数据采集失败"}
        
        print(f"✅ 成功采集 {len(tweets)} 条推文")
        
        # 步骤2: 数据质量验证
        print(f"\n🔍 步骤2: 数据质量验证...")
        validation_results = self.validate_data_quality(tweets)
        
        # 步骤3: 生成智能总结
        print(f"\n🤖 步骤3: 生成智能总结...")
        summary_result = self.summarizer.generate_summary(tweets, "daily")
        
        # 步骤4: 生成多种格式的报告
        print(f"\n📄 步骤4: 生成完整报告...")
        report_data = self.create_comprehensive_report(
            tweets, validation_results, summary_result
        )
        
        # 保存报告
        report_file = self.save_report(report_data)
        
        print(f"\n✅ 每日报告生成完成")
        print(f"📁 报告位置: {report_file}")
        print(f"📊 数据质量评分: {validation_results.get('overall_score', 'N/A')}")
        print(f"🤖 智能总结: {len(summary_result.get('summary', ''))} 字符")
        
        return {
            "success": True,
            "report_file": report_file,
            "tweet_count": len(tweets),
            "data_quality_score": validation_results.get("overall_score"),
            "summary": summary_result
        }
    
    def validate_data_quality(self, tweets: list) -> dict:
        """验证数据质量"""
        try:
            # 使用实时验证器进行验证
            golden_dataset = "golden_dataset/golden_dataset_20250911_220234.json"
            if os.path.exists(golden_dataset):
                validation_results = self.validator.comprehensive_validation_realtime(tweets, golden_dataset)
                
                # 转换ValidationResult对象为可序列化的字典
                serializable_results = {}
                for key, result in validation_results.items():
                    serializable_results[key] = {
                        "is_valid": result.is_valid,
                        "score": result.score,
                        "issues": result.issues,
                        "details": result.details
                    }
                
                # 计算总分 - 排除参考项目
                core_categories = ['text_completeness', 'retweet_integrity', 'media_accessibility', 'data_structure']
                scores = [result.score for key, result in validation_results.items() if key in core_categories]
                overall_score = sum(scores) / len(scores) if scores else 0
                
                return {
                    "overall_score": overall_score,
                    "details": serializable_results,
                    "validation_passed": overall_score >= 80
                }
            else:
                print("⚠️ 黄金数据集不存在，跳过对比验证")
                return {"overall_score": "N/A", "validation_passed": True}
        except Exception as e:
            print(f"⚠️ 数据验证失败: {e}")
            return {"overall_score": "ERROR", "validation_passed": False}
    
    def create_comprehensive_report(self, tweets: list, validation: dict, summary: dict) -> dict:
        """创建综合报告"""
        timestamp = datetime.now()
        
        # 基础统计
        stats = self.calculate_statistics(tweets)
        
        # 构建完整报告数据
        report = {
            "metadata": {
                "generation_time": timestamp.isoformat(),
                "report_type": "daily_comprehensive",
                "data_source": "X推荐时间线",
                "tweet_count": len(tweets),
                "data_quality_score": validation.get("overall_score", "N/A")
            },
            "data_quality": validation,
            "statistics": stats,
            "ai_summary": summary,
            "raw_tweets": tweets[:10],  # 只保存前10条作为样例
            "full_data_reference": f"完整数据包含 {len(tweets)} 条推文"
        }
        
        return report
    
    def calculate_statistics(self, tweets: list) -> dict:
        """计算推文统计数据"""
        stats = {
            "total_tweets": len(tweets),
            "original_tweets": 0,
            "retweets": 0,
            "quoted_tweets": 0,
            "media_tweets": 0,
            "total_media_files": 0,
            "avg_text_length": 0,
            "top_users": {},
            "media_types": {"photo": 0, "video": 0, "animated_gif": 0}
        }
        
        text_lengths = []
        user_counts = {}
        
        for tweet in tweets:
            # 基础分类
            if tweet.get('retweet'):
                stats["retweets"] += 1
            elif tweet.get('quoted'):
                stats["quoted_tweets"] += 1
            else:
                stats["original_tweets"] += 1
            
            # 媒体统计
            media = tweet.get('media', [])
            if media:
                stats["media_tweets"] += 1
                stats["total_media_files"] += len(media)
                
                for media_item in media:
                    media_type = media_item.get('type', 'unknown')
                    if media_type in stats["media_types"]:
                        stats["media_types"][media_type] += 1
            
            # 文本长度
            text = tweet.get('text', '')
            text_lengths.append(len(text))
            
            # 用户统计
            user = tweet.get('user', {})
            username = user.get('screen_name', 'unknown')
            user_counts[username] = user_counts.get(username, 0) + 1
        
        # 计算平均值
        stats["avg_text_length"] = sum(text_lengths) / len(text_lengths) if text_lengths else 0
        
        # Top 5 活跃用户
        stats["top_users"] = dict(
            sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        )
        
        return stats
    
    def save_report(self, report_data: dict) -> str:
        """保存完整报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON格式详细报告
        json_file = self.output_dir / f"daily_report_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        # Markdown格式用户友好报告
        md_file = self.output_dir / f"daily_report_{timestamp}.md"
        markdown_content = self.generate_markdown_report(report_data)
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"💾 详细报告 (JSON): {json_file}")
        print(f"📝 用户报告 (Markdown): {md_file}")
        
        return str(json_file)
    
    def generate_markdown_report(self, report_data: dict) -> str:
        """生成Markdown格式的用户友好报告"""
        metadata = report_data["metadata"]
        stats = report_data["statistics"]
        quality = report_data["data_quality"]
        summary = report_data["ai_summary"]
        
        md_content = f"""# X推文每日报告
*生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}*

## 📊 数据概览
- **采集时间**: {metadata['generation_time'][:10]}
- **数据来源**: {metadata['data_source']}
- **推文总数**: {metadata['tweet_count']} 条
- **数据质量**: {quality.get('overall_score', 'N/A')} 分

## 📈 内容分析
- **原创推文**: {stats['original_tweets']} 条 ({stats['original_tweets']/stats['total_tweets']*100:.1f}%)
- **转推**: {stats['retweets']} 条 ({stats['retweets']/stats['total_tweets']*100:.1f}%)
- **引用推文**: {stats['quoted_tweets']} 条 ({stats['quoted_tweets']/stats['total_tweets']*100:.1f}%)
- **含媒体推文**: {stats['media_tweets']} 条
- **平均文本长度**: {stats['avg_text_length']:.0f} 字符

## 🎯 活跃用户 (Top 5)
"""
        
        for username, count in stats['top_users'].items():
            md_content += f"- @{username}: {count} 条推文\n"
        
        md_content += f"""
## 🖼️ 媒体内容
- **图片**: {stats['media_types']['photo']} 个
- **视频**: {stats['media_types']['video']} 个  
- **动图**: {stats['media_types']['animated_gif']} 个

## 🤖 AI智能总结
{summary.get('summary', '总结生成中...')}

## 📋 数据质量报告
"""
        if quality.get('overall_score') != 'N/A':
            md_content += f"- **总体评分**: {quality['overall_score']:.1f}/100\n"
            md_content += f"- **验证状态**: {'✅ 通过' if quality.get('validation_passed') else '❌ 未通过'}\n"
        else:
            md_content += "- 数据质量验证未执行\n"
        
        md_content += f"""
---
*本报告由X爬虫系统自动生成，包含数据采集、质量验证和AI智能分析*  
*技术栈: Python + Playwright + LLM + 数据验证系统*
"""
        
        return md_content

def main():
    """主函数 - 演示每日报告生成"""
    print("🚀 X推文每日报告生成器")
    
    # 检查配置
    if not os.path.exists("config.json"):
        print("⚠️ 未找到config.json配置文件")
        print("请复制 config_template.json 为 config.json 并配置认证信息")
        print("\n📋 当前将使用测试数据进行演示...")
        
        # 使用测试数据演示功能
        generator = DailyReportGenerator()
        
        # 模拟加载真实爬取的数据进行演示
        test_file = "analysis_data/api_responses/response_213433_687388.json"
        if os.path.exists(test_file):
            print(f"📁 使用测试数据: {test_file}")
            
            # 直接使用爬虫解析测试数据
            with open(test_file, 'r', encoding='utf-8') as f:
                api_response = json.load(f)
            
            # 提取推文数据
            api_data = api_response.get('data', {})
            tweets = generator.crawler.extract_tweets_from_response(api_data)
            
            if tweets:
                print(f"✅ 解析得到 {len(tweets)} 条测试推文")
                
                # 生成完整报告
                result = generator.create_comprehensive_report(
                    tweets,
                    generator.validate_data_quality(tweets),
                    generator.summarizer.generate_summary(tweets, "daily")
                )
                
                report_file = generator.save_report(result)
                print(f"\n🎉 演示报告生成完成!")
                print(f"📄 查看报告: {report_file}")
            else:
                print("❌ 测试数据解析失败")
        else:
            print(f"❌ 测试数据文件不存在: {test_file}")
    else:
        # 正常流程
        generator = DailyReportGenerator()
        result = generator.generate_daily_report()
        
        if result["success"]:
            print("\n🎉 每日报告生成成功!")
        else:
            print(f"\n❌ 报告生成失败: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    main()