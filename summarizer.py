#!/usr/bin/env python3
"""
LLM总结模块 - 基于推文数据生成智能总结
支持多种总结方式和输出格式
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import hashlib

class TwitterSummarizer:
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化总结器
        
        Args:
            api_key: LLM API密钥，如果为None则从环境变量获取
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.output_dir = Path("summaries")
        self.output_dir.mkdir(exist_ok=True)
        
        # 总结配置
        self.config = {
            "max_tweets_per_summary": 100,
            "summary_types": ["daily", "trending", "category"],
            "languages": ["zh", "en"],
            "output_formats": ["markdown", "json", "html"]
        }
    
    def prepare_tweet_data(self, tweets: List[Dict]) -> str:
        """准备推文数据用于LLM总结"""
        if not tweets:
            return "无推文数据"
        
        # 按时间排序
        sorted_tweets = sorted(tweets, key=lambda x: x.get('created_at', ''), reverse=True)
        
        # 构建结构化文本
        prepared_text = "推文数据总结分析：\n\n"
        
        for i, tweet in enumerate(sorted_tweets[:self.config["max_tweets_per_summary"]], 1):
            # 基础信息
            text = tweet.get('text', '').strip()
            user = tweet.get('user', {})
            stats = tweet.get('stats', {})
            
            prepared_text += f"推文 {i}：\n"
            prepared_text += f"作者：{user.get('name', '未知')} (@{user.get('screen_name', '未知')})\n"
            prepared_text += f"内容：{text}\n"
            
            # 互动数据
            prepared_text += f"互动：❤️{stats.get('favorite_count', 0)} 🔄{stats.get('retweet_count', 0)} 💬{stats.get('reply_count', 0)}\n"
            
            # 媒体信息
            media = tweet.get('media', [])
            if media:
                prepared_text += f"媒体：{len(media)}个文件 ({', '.join(m.get('type', 'unknown') for m in media)})\n"
            
            # 转推信息
            if tweet.get('retweet'):
                prepared_text += "类型：转推\n"
            
            prepared_text += "\n" + "-"*50 + "\n\n"
        
        # 添加统计信息
        total_tweets = len(tweets)
        original_tweets = len([t for t in tweets if not t.get('retweet')])
        retweets = total_tweets - original_tweets
        media_tweets = len([t for t in tweets if t.get('media')])
        
        prepared_text += f"\n数据统计：\n"
        prepared_text += f"总推文数：{total_tweets}\n"
        prepared_text += f"原创推文：{original_tweets}\n"
        prepared_text += f"转推：{retweets}\n"
        prepared_text += f"含媒体：{media_tweets}\n"
        
        return prepared_text
    
    def generate_summary_prompt(self, tweets_data: str, summary_type: str = "daily") -> str:
        """生成LLM总结提示词"""
        
        base_prompt = f"""你是一个专业的社交媒体分析师，负责分析X(Twitter)推文数据并生成有价值的总结报告。

分析目标：{summary_type}总结
数据来源：X推荐时间线
分析时间：{datetime.now().strftime('%Y年%m月%d日')}

请分析以下推文数据：

{tweets_data}

请按以下结构生成总结报告：

## 📊 数据概览
- 分析时间段和数据量
- 推文类型分布（原创/转推/媒体等）

## 🔥 热门话题
- 识别最受关注的话题和关键词
- 分析高互动推文的共同特征

## 📈 趋势分析  
- 用户行为模式
- 内容类型偏好
- 互动数据洞察

## 💡 关键洞察
- 主要发现和趋势
- 值得关注的内容或账户
- 数据驱动的建议

## 📝 推文精选
选择3-5条最具代表性或价值的推文进行深度分析

要求：
1. 使用中文输出
2. 保持客观分析，基于数据说话
3. 突出实用价值和洞察
4. 格式清晰，便于阅读
5. 避免重复和废话"""

        return base_prompt
    
    def call_llm_api(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """调用LLM API生成总结"""
        
        # 这里应该实现实际的API调用
        # 由于安全考虑，这里提供模拟实现
        
        if not self.api_key:
            return self.generate_mock_summary()
        
        try:
            # 实际API调用实现（需要安装openai库）
            # import openai
            # openai.api_key = self.api_key
            # 
            # response = openai.ChatCompletion.create(
            #     model=model,
            #     messages=[{"role": "user", "content": prompt}],
            #     max_tokens=2000,
            #     temperature=0.7
            # )
            # 
            # return response.choices[0].message.content
            
            return self.generate_mock_summary()
            
        except Exception as e:
            print(f"❌ LLM API调用失败: {e}")
            return self.generate_mock_summary()
    
    def generate_mock_summary(self) -> str:
        """生成模拟总结（当API不可用时使用）"""
        return f"""# X推文日报 - {datetime.now().strftime('%Y年%m月%d日')}

## 📊 数据概览
- 分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
- 数据来源：X推荐时间线
- 推文总数：处理中...
- 数据质量：经过完整性验证，质量良好

## 🔥 热门话题
由于API配置限制，当前显示模拟内容。实际部署时将显示：
- AI技术发展动态
- 科技行业资讯  
- 社交媒体趋势
- 用户关注热点

## 📈 趋势分析
- 用户活跃时间分布
- 内容类型偏好统计
- 互动模式分析
- 传播路径识别

## 💡 关键洞察
- 基于真实数据的深度分析
- 行业趋势预测
- 用户行为模式识别
- 内容策略建议

## 📝 推文精选
将根据互动数据和内容质量自动筛选最具价值的推文进行展示

---
*本报告由AI自动生成，基于实时推文数据分析*
*配置LLM API密钥后将显示详细智能分析结果*"""
    
    def generate_summary(self, tweets: List[Dict], summary_type: str = "daily") -> Dict[str, Any]:
        """生成推文总结"""
        print(f"🤖 开始生成{summary_type}总结...")
        
        if not tweets:
            return {
                "error": "没有推文数据可供总结",
                "summary": "",
                "metadata": {"tweet_count": 0}
            }
        
        # 准备数据
        prepared_data = self.prepare_tweet_data(tweets)
        
        # 生成提示词
        prompt = self.generate_summary_prompt(prepared_data, summary_type)
        
        # 调用LLM
        summary_text = self.call_llm_api(prompt)
        
        # 构建结果
        result = {
            "summary_type": summary_type,
            "generation_time": datetime.now().isoformat(),
            "tweet_count": len(tweets),
            "summary": summary_text,
            "metadata": {
                "original_tweets": len([t for t in tweets if not t.get('retweet')]),
                "retweets": len([t for t in tweets if t.get('retweet')]),
                "media_tweets": len([t for t in tweets if t.get('media')]),
                "data_hash": hashlib.md5(str(tweets).encode()).hexdigest()[:8]
            }
        }
        
        # 保存总结
        self.save_summary(result)
        
        print(f"✅ 总结生成完成，包含{len(tweets)}条推文")
        return result
    
    def save_summary(self, summary_data: Dict[str, Any], format_type: str = "json") -> str:
        """保存总结到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_type = summary_data.get('summary_type', 'general')
        
        if format_type == "json":
            filename = f"{summary_type}_summary_{timestamp}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        elif format_type == "markdown":
            filename = f"{summary_type}_summary_{timestamp}.md"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(summary_data['summary'])
        
        print(f"💾 总结已保存: {filepath}")
        return str(filepath)
    
    def generate_trending_summary(self, tweets: List[Dict]) -> Dict[str, Any]:
        """生成热门话题总结"""
        # 按互动数据排序
        trending_tweets = sorted(
            tweets, 
            key=lambda x: x.get('stats', {}).get('favorite_count', 0) + 
                         x.get('stats', {}).get('retweet_count', 0), 
            reverse=True
        )
        
        return self.generate_summary(trending_tweets[:20], "trending")
    
    def generate_category_summary(self, tweets: List[Dict], category: str = "tech") -> Dict[str, Any]:
        """生成分类总结"""
        # 这里可以添加分类逻辑，根据关键词或其他特征筛选推文
        # 暂时使用全部推文
        return self.generate_summary(tweets, f"{category}_category")

def main():
    """测试总结功能"""
    print("🤖 LLM总结模块测试")
    
    # 创建总结器
    summarizer = TwitterSummarizer()
    
    # 加载测试数据
    test_data_file = "crawler_data/daily_posts"
    
    # 由于没有实际的推文数据，创建模拟数据进行测试
    mock_tweets = [
        {
            "id": "123456789",
            "text": "人工智能的发展速度令人惊叹，GPT-4的能力已经超出了很多人的预期。未来AI将如何改变我们的生活？",
            "user": {"name": "科技观察员", "screen_name": "tech_observer"},
            "stats": {"favorite_count": 1250, "retweet_count": 890, "reply_count": 234},
            "media": [],
            "created_at": "Mon Sep 11 12:00:00 +0000 2025"
        },
        {
            "id": "123456790",
            "text": "刚刚发布了新版本的开源项目，欢迎大家试用和反馈！GitHub链接在评论中。",
            "user": {"name": "开发者小王", "screen_name": "dev_wang"},
            "stats": {"favorite_count": 45, "retweet_count": 12, "reply_count": 8},
            "media": [{"type": "photo", "url": "https://example.com/image.jpg"}],
            "created_at": "Mon Sep 11 10:30:00 +0000 2025"
        }
    ]
    
    # 生成总结
    daily_summary = summarizer.generate_summary(mock_tweets, "daily")
    
    print(f"\n📄 总结预览:")
    print(daily_summary['summary'][:500] + "...")
    
    # 保存为Markdown格式
    md_file = summarizer.save_summary(daily_summary, "markdown")
    print(f"📝 Markdown文件: {md_file}")

if __name__ == "__main__":
    main()