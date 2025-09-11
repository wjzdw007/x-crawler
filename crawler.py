#!/usr/bin/env python3
"""
X HTTP爬虫 - 基于深度分析结果实现
解决了所有已知核心问题：
1. ✅ 帖子内容完整性 - 使用 legacy.full_text
2. ✅ 转推原帖获取 - 使用 retweeted_status_result
3. ✅ 媒体文件URL - 使用 extended_entities.media
4. ✅ 数据准确性 - 正确的GraphQL路径
"""

import json
import requests
import time
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import random

class XCrawler:
    def __init__(self, data_dir="crawler_data", config_file="config.json"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 创建数据存储目录
        for subdir in ["daily_posts", "media", "summaries", "logs"]:
            (self.data_dir / subdir).mkdir(exist_ok=True)
        
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.session = requests.Session()
        self.setup_session()
        
        # API端点 - 基于分析结果
        self.api_endpoints = {
            "recommended": "xNGIIoXaz9DyeBXBfn3AjA/HomeLatestTimeline",
            "following": "1_nms9JVtHQxTw8VwZJciQ/HomeTimeline"
        }
        
        # 基础URL
        self.base_url = "https://x.com/i/api/graphql"
        
        # 请求计数和限流
        self.request_count = 0
        self.last_request_time = 0
        self.rate_limit = self.config.get('settings', {}).get('requests_per_hour', 400)
    
    def load_config(self) -> Dict:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 配置文件加载失败: {e}")
        
        # 返回默认配置
        return {
            "authentication": {"cookies": {}, "headers": {}},
            "settings": {"requests_per_hour": 400, "retry_attempts": 3, "timeout": 30}
        }
        
    def setup_session(self):
        """设置HTTP会话"""
        # 基础headers - 模拟真实浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://x.com/home',
            'Origin': 'https://x.com',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })
        
        # 从配置文件加载认证信息
        self.load_authentication()
    
    def load_authentication(self):
        """从配置文件加载认证信息"""
        auth_config = self.config.get('authentication', {})
        
        # 加载cookies
        cookies = auth_config.get('cookies', {})
        for key, value in cookies.items():
            if value and value != f"YOUR_{key.upper()}_HERE":
                self.session.cookies.set(key, value)
        
        # 加载headers
        headers = auth_config.get('headers', {})
        for key, value in headers.items():
            if value and not value.startswith("YOUR_"):
                self.session.headers[key] = value
        
        # 检查认证是否配置
        has_auth = any(
            v and not str(v).startswith("YOUR_") 
            for v in {**cookies, **headers}.values()
        )
        
        if not has_auth:
            print("⚠️ 未检测到认证配置")
            print("请复制 config_template.json 为 config.json 并填入正确的认证信息")
    
    def rate_limit_check(self):
        """检查和执行限流"""
        current_time = time.time()
        
        # 每小时重置计数
        if current_time - self.last_request_time > 3600:
            self.request_count = 0
        
        # 检查限流
        if self.request_count >= self.rate_limit:
            wait_time = 3600 - (current_time - self.last_request_time)
            if wait_time > 0:
                print(f"⏰ 达到限流上限，等待 {wait_time:.0f} 秒...")
                time.sleep(wait_time)
                self.request_count = 0
        
        # 随机延迟防止检测
        delay = random.uniform(1.0, 3.0)
        time.sleep(delay)
        
        self.request_count += 1
        self.last_request_time = current_time
    
    def get_timeline_params(self, timeline_type: str = "recommended", cursor: Optional[str] = None) -> Dict:
        """获取时间线请求参数"""
        variables = {
            "count": 20,
            "includePromotedContent": True,
            "latestControlAvailable": True,
            "requestContext": "launch",
            "withCommunity": True
        }
        
        if cursor:
            variables["cursor"] = cursor
        
        features = {
            "rweb_video_screen_enabled": False,
            "payments_enabled": False,
            "profile_label_improvements_pcf_label_in_post_enabled": True,
            "rweb_tipjar_consumption_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "premium_content_api_read_enabled": False,
            "communities_web_enable_tweet_community_results_fetch": True,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
            "responsive_web_grok_analyze_post_followups_enabled": True,
            "responsive_web_jetfuel_frame": True,
            "responsive_web_grok_share_attachment_enabled": True,
            "articles_preview_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "responsive_web_grok_show_grok_translated_post": False,
            "responsive_web_grok_analysis_button_from_backend": True,
            "creator_subscriptions_quote_tweet_preview_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_grok_image_annotation_enabled": True,
            "responsive_web_grok_imagine_annotation_enabled": True,
            "responsive_web_grok_community_note_auto_translation_is_enabled": False,
            "responsive_web_enhance_cards_enabled": False
        }
        
        return {
            "variables": json.dumps(variables),
            "features": json.dumps(features)
        }
    
    def make_timeline_request(self, timeline_type: str = "recommended", cursor: Optional[str] = None) -> Optional[Dict]:
        """发起时间线请求"""
        self.rate_limit_check()
        
        endpoint = self.api_endpoints[timeline_type]
        url = f"{self.base_url}/{endpoint}"
        params = self.get_timeline_params(timeline_type, cursor)
        
        try:
            print(f"🔄 请求 {timeline_type} 时间线...")
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print("⚠️ 触发限流，等待后重试...")
                time.sleep(60)
                return None
            else:
                print(f"❌ 请求失败: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None
    
    def parse_tweet(self, tweet_data: Dict) -> Optional[Dict]:
        """解析推文数据 - 基于分析结果的完整实现"""
        try:
            # 基础推文信息
            tweet = {
                'id': tweet_data.get('rest_id'),
                'text': '',
                'created_at': tweet_data.get('legacy', {}).get('created_at'),
                'lang': tweet_data.get('legacy', {}).get('lang'),
                'media': [],
                'retweet': None,
                'quoted': None,
                'user': None,
                'stats': {
                    'retweet_count': tweet_data.get('legacy', {}).get('retweet_count', 0),
                    'favorite_count': tweet_data.get('legacy', {}).get('favorite_count', 0),
                    'reply_count': tweet_data.get('legacy', {}).get('reply_count', 0),
                    'quote_count': tweet_data.get('legacy', {}).get('quote_count', 0)
                }
            }
            
            # 提取文本内容 - 处理长文推文和普通推文
            if 'note_tweet' in tweet_data:
                # 长文推文
                note_tweet_result = tweet_data.get('note_tweet', {}).get('note_tweet_results', {}).get('result', {})
                if note_tweet_result:
                    tweet['text'] = note_tweet_result.get('text', '')
            
            if not tweet['text']:
                # 普通推文 - 使用 legacy.full_text
                tweet['text'] = tweet_data.get('legacy', {}).get('full_text', '')
            
            # 解析用户信息 - 修正字段路径
            user_results = tweet_data.get('core', {}).get('user_results', {}).get('result', {})
            if user_results:
                tweet['user'] = {
                    'id': user_results.get('rest_id'),
                    'name': user_results.get('core', {}).get('name'),  # 修正：从core获取
                    'screen_name': user_results.get('core', {}).get('screen_name'),  # 修正：从core获取
                    'description': user_results.get('legacy', {}).get('description'),
                    'followers_count': user_results.get('legacy', {}).get('followers_count', 0),
                    'friends_count': user_results.get('legacy', {}).get('friends_count', 0),
                    'verified': user_results.get('verification', {}).get('verified', False),  # 修正路径
                    'is_blue_verified': user_results.get('is_blue_verified', False)
                }
            
            # 解析媒体文件 - 基于分析结果
            extended_entities = tweet_data.get('legacy', {}).get('extended_entities', {})
            if 'media' in extended_entities:
                for media_item in extended_entities['media']:
                    media_entry = {
                        'type': media_item.get('type'),
                        'id': media_item.get('id_str'),
                        'url': None
                    }
                    
                    if media_item['type'] == 'video':
                        # 视频处理 - 选择最高质量
                        variants = media_item.get('video_info', {}).get('variants', [])
                        best_variant = None
                        highest_bitrate = 0
                        
                        for variant in variants:
                            if variant.get('content_type') == 'video/mp4':
                                bitrate = variant.get('bitrate', 0)
                                if bitrate > highest_bitrate:
                                    highest_bitrate = bitrate
                                    best_variant = variant
                        
                        if best_variant:
                            media_entry['url'] = best_variant['url']
                            media_entry['bitrate'] = best_variant.get('bitrate')
                    
                    elif media_item['type'] in ['photo', 'animated_gif']:
                        # 图片处理
                        media_entry['url'] = media_item.get('media_url_https')
                    
                    if media_entry['url']:
                        tweet['media'].append(media_entry)
            
            # 处理转推 - 基于分析结果，支持TweetWithVisibilityResults结构
            if 'retweeted_status_result' in tweet_data.get('legacy', {}):
                retweet_result = tweet_data['legacy']['retweeted_status_result'].get('result')
                if retweet_result:
                    # 处理TweetWithVisibilityResults结构
                    if retweet_result.get('__typename') == 'TweetWithVisibilityResults':
                        # 数据嵌套在tweet字段中
                        actual_tweet = retweet_result.get('tweet')
                        if actual_tweet:
                            tweet['retweet'] = self.parse_tweet(actual_tweet)
                    else:
                        # 普通Tweet结构
                        tweet['retweet'] = self.parse_tweet(retweet_result)
            
            # 处理引用推文
            if 'quoted_status_result' in tweet_data:
                quoted_result = tweet_data['quoted_status_result'].get('result')
                if quoted_result:
                    tweet['quoted'] = self.parse_tweet(quoted_result)
            
            return tweet
            
        except Exception as e:
            print(f"❌ 解析推文失败: {e}")
            return None
    
    def extract_tweets_from_response(self, data: Dict) -> List[Dict]:
        """从响应中提取推文数据 - 基于分析结果"""
        tweets = []
        
        try:
            # 基于分析结果的数据路径
            home_timeline = data.get('data', {}).get('home', {}).get('home_timeline_urt', {})
            instructions = home_timeline.get('instructions', [])
            
            for instruction in instructions:
                if instruction.get('type') == 'TimelineAddEntries':
                    entries = instruction.get('entries', [])
                    
                    for entry in entries:
                        entry_id = entry.get('entryId', '')
                        
                        # 推文条目
                        if 'tweet-' in entry_id:
                            content = entry.get('content', {})
                            item_content = content.get('itemContent', {})
                            tweet_results = item_content.get('tweet_results', {})
                            tweet_data = tweet_results.get('result', {})
                            
                            if tweet_data.get('__typename') == 'Tweet':
                                parsed_tweet = self.parse_tweet(tweet_data)
                                if parsed_tweet:
                                    tweets.append(parsed_tweet)
                        
                        # 游标处理 - 用于分页
                        elif 'cursor-' in entry_id:
                            cursor_content = entry.get('content', {})
                            if cursor_content.get('cursorType') == 'Bottom':
                                cursor_value = cursor_content.get('value')
                                # 保存cursor用于下次请求
                                self.last_cursor = cursor_value
                                print(f"🔗 找到下一页cursor: {cursor_value[:50]}...")
        
        except Exception as e:
            print(f"❌ 提取推文数据失败: {e}")
        
        return tweets
    
    def crawl_daily_posts(self, timeline_type: str = "recommended", max_pages: int = 5, target_count: Optional[int] = None) -> List[Dict]:
        """爬取日推文 - 支持精确数量控制"""
        if target_count is None:
            target_count = self.config.get("targets", {}).get("daily_tweet_count", 100)
        
        print(f"🚀 开始爬取 {timeline_type} 时间线...")
        print(f"🎯 目标推文数: {target_count} 条")
        
        all_tweets = []
        cursor = None
        
        for page in range(max_pages):
            print(f"📄 爬取第 {page + 1} 页...")
            
            response_data = self.make_timeline_request(timeline_type, cursor)
            if not response_data:
                print("❌ 请求失败，停止爬取")
                break
            
            tweets = self.extract_tweets_from_response(response_data)
            if not tweets:
                print("⚠️ 未找到推文数据，可能需要检查认证状态")
                break
            
            all_tweets.extend(tweets)
            print(f"✅ 本页获取 {len(tweets)} 条推文 (累计: {len(all_tweets)} 条)")
            
            # 检查是否达到目标数量
            if len(all_tweets) >= target_count:
                print(f"🎯 已达到目标数量 {target_count} 条，结束爬取")
                all_tweets = all_tweets[:target_count]  # 精确截取
                break
            
            # 更新cursor用于下一页
            cursor = getattr(self, 'last_cursor', None)
            if not cursor:
                print("📝 未找到下一页cursor，结束爬取")
                break
        
        # 保存数据
        if all_tweets:
            self.save_daily_data(all_tweets, timeline_type)
        
        print(f"🎉 总共爬取 {len(all_tweets)} 条推文")
        return all_tweets
    
    def save_daily_data(self, tweets: List[Dict], timeline_type: str):
        """保存日数据"""
        today = datetime.now().strftime('%Y%m%d')
        filename = f"{today}_{timeline_type}_posts.json"
        filepath = self.data_dir / "daily_posts" / filename
        
        data = {
            "date": today,
            "timeline_type": timeline_type,
            "crawl_time": datetime.now().isoformat(),
            "tweet_count": len(tweets),
            "tweets": tweets
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 数据已保存: {filepath}")
        
        # 生成简要统计
        self.generate_stats(tweets, timeline_type)
    
    def generate_stats(self, tweets: List[Dict], timeline_type: str):
        """生成统计信息"""
        stats = {
            "总推文数": len(tweets),
            "原创推文": len([t for t in tweets if not t.get('retweet')]),
            "转推": len([t for t in tweets if t.get('retweet')]),
            "包含媒体": len([t for t in tweets if t.get('media')]),
            "包含视频": len([t for t in tweets if any(m.get('type') == 'video' for m in t.get('media', []))]),
            "包含图片": len([t for t in tweets if any(m.get('type') == 'photo' for m in t.get('media', []))]),
        }
        
        print(f"\n📊 {timeline_type} 时间线统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

def main():
    """主函数"""
    print("🤖 X HTTP爬虫启动")
    print("基于深度API分析结果实现")
    
    crawler = XCrawler()
    
    # 检查认证状态
    print("\n⚠️ 重要提醒:")
    print("请确保已完成以下步骤:")
    print("1. 在浏览器中登录X账号")
    print("2. 手动提取并配置必要的认证cookies")
    print("3. 包括: auth_token, ct0, bearer_token等")
    print("\n如未完成认证配置，请先运行 tools/analyzer.py 获取cookies")
    
    # 开始爬取
    input("\n按回车键开始爬取...")
    
    # 爬取推荐时间线
    tweets = crawler.crawl_daily_posts("recommended", max_pages=3)
    
    if tweets:
        print(f"\n🎉 爬取完成！获得 {len(tweets)} 条推文")
        print("数据保存在 crawler_data/daily_posts/ 目录")
    else:
        print("\n❌ 爬取失败，请检查认证配置")

if __name__ == "__main__":
    main()