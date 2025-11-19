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
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import random
from config_loader import ConfigLoader

class XCrawler:
    def __init__(self, data_dir="crawler_data", config_file="config.json"):
        # 使用环境变量或默认值
        self.data_dir = Path(os.getenv('DATA_DIR', data_dir))
        self.data_dir.mkdir(exist_ok=True)

        # 创建数据存储目录
        for subdir in ["daily_posts", "users_daily", "raw_responses", "user_summaries", "prompts"]:
            (self.data_dir / subdir).mkdir(exist_ok=True)

        # 使用新的配置加载器
        self.config_loader = ConfigLoader(config_file)
        self.config = self.config_loader.config
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

        # 确保requests会自动处理gzip解压
        self.session.trust_env = False

        # 设置代理（如果配置了）
        proxy_settings = self.config_loader.get_proxy_settings()
        if proxy_settings:
            self.session.proxies = proxy_settings
            print(f"🌐 使用代理: {proxy_settings}")

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
                # 检查响应内容类型和编码
                content_type = response.headers.get('Content-Type', '')
                print(f"📄 响应类型: {content_type}")

                # 尝试解码响应内容
                try:
                    response_data = response.json()
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"📝 响应长度: {len(response.text)} 字符")
                    print(f"📝 Content-Encoding: {response.headers.get('Content-Encoding', 'None')}")

                    # 检查响应是否为二进制内容（可能是gzip压缩的）
                    content_sample = response.content[:100]
                    is_binary = any(b < 32 or b > 126 for b in content_sample if b not in [9, 10, 13])

                    if is_binary:
                        print("🔧 检测到二进制内容，尝试解压...")
                        content_encoding = response.headers.get('Content-Encoding', '').lower()

                        try:
                            if 'br' in content_encoding:
                                print("🔧 使用Brotli解压...")
                                import brotli
                                decompressed = brotli.decompress(response.content)
                            elif 'gzip' in content_encoding:
                                print("🔧 使用Gzip解压...")
                                import gzip
                                decompressed = gzip.decompress(response.content)
                            else:
                                print("🔧 尝试自动解压...")
                                # 尝试多种解压方式
                                try:
                                    import brotli
                                    decompressed = brotli.decompress(response.content)
                                    print("✅ Brotli解压成功")
                                except:
                                    import gzip
                                    decompressed = gzip.decompress(response.content)
                                    print("✅ Gzip解压成功")

                            response_data = json.loads(decompressed.decode('utf-8'))
                            print("✅ 成功解压并解析JSON")
                        except Exception as decomp_e:
                            print(f"❌ 解压失败: {decomp_e}")
                            return None
                    else:
                        print(f"📝 响应前100字符: {repr(response.text[:100])}")
                        return None

                # 保存原始API响应用于分析
                self.save_raw_response(response, url, params, timeline_type)

                return response_data
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
    
    def save_raw_response(self, response, url: str, params: dict, timeline_type: str):
        """保存原始API响应用于分析"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            raw_dir = self.data_dir / "raw_responses"
            raw_dir.mkdir(exist_ok=True)

            filename = f"{timestamp}_{timeline_type}_response.json"
            filepath = raw_dir / filename

            raw_data = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "status": response.status_code,
                "headers": dict(response.headers),
                "params": params,
                "data": response.json() if response.status_code == 200 else {"error": response.text}
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, ensure_ascii=False, indent=2)

            print(f"💾 原始响应已保存: {filename}")

            # 保存后自动清理旧文件
            self.cleanup_old_raw_responses(days_to_keep=3)

        except Exception as e:
            print(f"⚠️ 保存原始响应失败: {e}")

    def cleanup_old_raw_responses(self, days_to_keep: int = 3):
        """清理旧的raw_responses文件，只保留最近N天的"""
        try:
            raw_dir = self.data_dir / "raw_responses"
            if not raw_dir.exists():
                return

            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)

            deleted_count = 0
            total_size = 0

            for filepath in raw_dir.glob("*.json"):
                # 从文件名提取时间戳（格式：YYYYMMDD_HHMMSS_mmm）
                try:
                    filename = filepath.stem
                    date_part = filename.split('_')[0]  # YYYYMMDD
                    file_date = datetime.strptime(date_part, '%Y%m%d')

                    if file_date < cutoff_time:
                        file_size = filepath.stat().st_size
                        filepath.unlink()
                        deleted_count += 1
                        total_size += file_size
                except (ValueError, IndexError):
                    # 文件名格式不符，跳过
                    continue

            if deleted_count > 0:
                print(f"🗑️  清理旧响应文件: {deleted_count} 个 ({total_size / 1024 / 1024:.1f} MB)")

        except Exception as e:
            print(f"⚠️ 清理raw_responses失败: {e}")
    
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
                        
                        # 推文条目 - 排除promoted-tweet广告
                        if entry_id.startswith('tweet-'):
                            content = entry.get('content', {})
                            item_content = content.get('itemContent', {})
                            tweet_results = item_content.get('tweet_results', {})
                            tweet_data = tweet_results.get('result', {})
                            
                            if tweet_data.get('__typename') == 'Tweet':
                                parsed_tweet = self.parse_tweet(tweet_data)
                                if parsed_tweet:
                                    tweets.append(parsed_tweet)
                        
                        # 对话模块 - 包含多条相关推文
                        elif entry_id.startswith('home-conversation-'):
                            content = entry.get('content', {})
                            if content.get('entryType') == 'TimelineTimelineModule':
                                items = content.get('items', [])
                                for item in items:
                                    item_content = item.get('item', {}).get('itemContent', {})
                                    if item_content.get('itemType') == 'TimelineTweet':
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
    
    def crawl_daily_posts(self, timeline_type: str = "recommended", max_pages: int = None, target_count: Optional[int] = None) -> List[Dict]:
        """爬取日推文 - 支持精确数量控制，实时去重"""
        if target_count is None:
            target_count = self.config.get("targets", {}).get("daily_tweet_count", 100)

        print(f"🚀 开始爬取 {timeline_type} 时间线...")
        print(f"🎯 目标推文数: {target_count} 条")

        # 使用字典存储推文，自动去重
        unique_tweets = {}
        cursor = None
        page = 0

        # 如果指定了max_pages就使用，否则无限制直到达到target_count或无更多数据
        while max_pages is None or page < max_pages:
            page += 1
            print(f"📄 爬取第 {page} 页...")

            response_data = self.make_timeline_request(timeline_type, cursor)
            if not response_data:
                print("❌ 请求失败，停止爬取")
                break

            tweets = self.extract_tweets_from_response(response_data)
            if not tweets:
                print("⚠️ 未找到推文数据，可能需要检查认证状态")
                break

            # 实时去重：只添加新推文
            new_count = 0
            for tweet in tweets:
                tweet_id = tweet.get('id')
                if tweet_id and tweet_id not in unique_tweets:
                    unique_tweets[tweet_id] = tweet
                    new_count += 1

            print(f"✅ 本页获取 {len(tweets)} 条推文 (新增: {new_count} 条, 重复: {len(tweets) - new_count} 条, 累计: {len(unique_tweets)} 条)")

            # 检查是否达到目标数量
            if len(unique_tweets) >= target_count:
                print(f"🎯 已达到目标数量 {target_count} 条，结束爬取")
                break

            # 更新cursor用于下一页
            cursor = getattr(self, 'last_cursor', None)
            if not cursor:
                print("📝 未找到下一页cursor，结束爬取")
                break

        # 转换为列表，按时间倒序排序，然后精确截取
        from dateutil.parser import parse as parse_date
        all_tweets = sorted(
            unique_tweets.values(),
            key=lambda t: parse_date(t.get('created_at', '1970-01-01')),
            reverse=True
        )[:target_count]

        # 保存数据
        if all_tweets:
            self.save_daily_data(all_tweets, timeline_type)
            # 按用户分组保存当天数据
            self.save_by_user_daily(all_tweets)

        print(f"🎉 总共爬取 {len(all_tweets)} 条唯一推文")
        return all_tweets
    
    def save_daily_data(self, tweets: List[Dict], timeline_type: str):
        """保存日数据 - 支持多次抓取合并去重"""
        today = datetime.now().strftime('%Y%m%d')
        filename = f"{today}_{timeline_type}_posts.json"
        filepath = self.data_dir / "daily_posts" / filename

        # 如果文件已存在，加载现有数据
        existing_tweets = []
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_tweets = existing_data.get('tweets', [])
                print(f"📂 加载现有数据: {len(existing_tweets)} 条推文")
            except Exception as e:
                print(f"⚠️ 读取现有文件失败: {e}")

        # 合并推文并去重（基于推文ID）
        all_tweets = existing_tweets + tweets
        unique_tweets = {}

        for tweet in all_tweets:
            tweet_id = tweet.get('id')
            if tweet_id and tweet_id not in unique_tweets:
                unique_tweets[tweet_id] = tweet

        # 按时间倒序排序（最新的在前）
        from dateutil.parser import parse as parse_date
        sorted_tweets = sorted(
            unique_tweets.values(),
            key=lambda t: parse_date(t.get('created_at', '1970-01-01')),
            reverse=True
        )

        # 保存合并后的数据
        data = {
            "date": today,
            "timeline_type": timeline_type,
            "last_crawl_time": datetime.now().isoformat(),
            "tweet_count": len(sorted_tweets),
            "unique_tweet_count": len(sorted_tweets),
            "total_crawled": len(all_tweets),
            "duplicates_removed": len(all_tweets) - len(sorted_tweets),
            "tweets": sorted_tweets
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        action = "更新" if existing_tweets else "创建"
        print(f"💾 数据已{action}: {filepath}")
        print(f"   本次抓取: {len(tweets)} 条, 累计: {len(sorted_tweets)} 条 (去重: {len(all_tweets) - len(sorted_tweets)} 条)")

        # 生成简要统计
        self.generate_stats(sorted_tweets, timeline_type)
    
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
    
    def save_by_user_daily(self, tweets: List[Dict]):
        """按用户和日期分组保存所有推文数据"""
        from dateutil.parser import parse as parse_date
        import os
        
        users_dir = self.data_dir / "users_daily"
        
        print(f"\n👥 按用户和日期分组保存推文...")
        
        # 按用户和日期双重分组 {user: {date: [tweets]}}
        user_date_tweets = {}
        total_processed = 0
        
        for tweet in tweets:
            try:
                tweet_date = parse_date(tweet.get('created_at', ''))
                tweet_date_str = tweet_date.strftime('%Y%m%d')
                
                # 获取用户信息
                user = tweet.get('user', {})
                screen_name = user.get('screen_name', 'unknown')
                
                # 初始化嵌套字典结构
                if screen_name not in user_date_tweets:
                    user_date_tweets[screen_name] = {}
                if tweet_date_str not in user_date_tweets[screen_name]:
                    user_date_tweets[screen_name][tweet_date_str] = []
                
                user_date_tweets[screen_name][tweet_date_str].append(tweet)
                total_processed += 1
                
            except Exception as e:
                print(f"⚠️ 解析推文时间失败: {e}")
                continue
        
        print(f"📅 处理推文: {total_processed}/{len(tweets)} 条")
        
        # 统计信息
        total_users = len(user_date_tweets)
        total_files = sum(len(date_tweets) for date_tweets in user_date_tweets.values())
        print(f"👤 涉及用户数: {total_users} 个")
        print(f"📂 将生成文件数: {total_files} 个")
        
        # 为每个用户的每个日期保存数据
        for screen_name, date_tweets in user_date_tweets.items():
            for date_str, user_tweet_list in date_tweets.items():
                self._save_user_tweets_by_date(screen_name, date_str, user_tweet_list, users_dir)
        
        print(f"✅ 用户分组保存完成")
    
    def _save_user_tweets(self, screen_name: str, new_tweets: List[Dict], users_dir: Path):
        """保存或合并用户的推文数据"""
        import os
        from dateutil.parser import parse as parse_date
        
        today = datetime.now().strftime('%Y%m%d')
        filename = f"{screen_name}_{today}.json"
        filepath = users_dir / filename
        
        # 如果文件已存在，加载现有数据
        existing_tweets = []
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_tweets = existing_data.get('tweets', [])
            except Exception as e:
                print(f"⚠️ 读取现有文件失败 {filepath}: {e}")
        
        # 合并推文并去重（基于推文ID）
        all_tweets = existing_tweets + new_tweets
        unique_tweets = {}
        
        # 先保存用户信息，再移除冗余字段
        user_info = {}
        for tweet in all_tweets:
            tweet_id = tweet.get('id')
            if tweet_id and tweet_id not in unique_tweets:
                # 保存最新的用户信息
                if tweet.get('user'):
                    user_info = tweet['user']
                
                # 移除冗余的用户信息，因为文件已经按用户分组
                clean_tweet = tweet.copy()
                clean_tweet.pop('user', None)  # 移除顶层user字段
                unique_tweets[tweet_id] = clean_tweet
        
        # 按时间正序排序
        sorted_tweets = sorted(
            unique_tweets.values(),
            key=lambda t: parse_date(t.get('created_at', '1970-01-01'))
        )
        
        # 构建保存数据
        save_data = {
            "user": {
                "screen_name": screen_name,
                "name": user_info.get('name', ''),
                "description": user_info.get('description', ''),
                "followers_count": user_info.get('followers_count', 0),
                "verified": user_info.get('verified', False),
                "is_blue_verified": user_info.get('is_blue_verified', False)
            },
            "date": today,
            "last_updated": datetime.now().isoformat(),
            "tweet_count": len(sorted_tweets),
            "tweets": sorted_tweets
        }
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        action = "更新" if existing_tweets else "创建"
        print(f"  📄 {action} @{screen_name}: {len(sorted_tweets)} 条推文 -> {filename}")
    
    def _save_user_tweets_by_date(self, screen_name: str, date_str: str, new_tweets: List[Dict], users_dir: Path):
        """按日期保存或合并用户的推文数据"""
        import os
        from dateutil.parser import parse as parse_date
        
        filename = f"{screen_name}_{date_str}.json"
        filepath = users_dir / filename
        
        # 如果文件已存在，加载现有数据
        existing_tweets = []
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_tweets = existing_data.get('tweets', [])
            except Exception as e:
                print(f"⚠️ 读取现有文件失败 {filepath}: {e}")
        
        # 合并推文并去重（基于推文ID）
        all_tweets = existing_tweets + new_tweets
        unique_tweets = {}
        
        # 先保存用户信息，再移除冗余字段
        user_info = {}
        for tweet in all_tweets:
            tweet_id = tweet.get('id')
            if tweet_id and tweet_id not in unique_tweets:
                # 保存最新的用户信息
                if tweet.get('user'):
                    user_info = tweet['user']
                
                # 移除冗余的用户信息，因为文件已经按用户分组
                clean_tweet = tweet.copy()
                clean_tweet.pop('user', None)  # 移除顶层user字段
                unique_tweets[tweet_id] = clean_tweet
        
        # 按时间正序排序
        sorted_tweets = sorted(
            unique_tweets.values(),
            key=lambda t: parse_date(t.get('created_at', '1970-01-01'))
        )
        
        # 构建保存数据
        save_data = {
            "user": {
                "screen_name": screen_name,
                "name": user_info.get('name', ''),
                "description": user_info.get('description', ''),
                "followers_count": user_info.get('followers_count', 0),
                "verified": user_info.get('verified', False),
                "is_blue_verified": user_info.get('is_blue_verified', False)
            },
            "date": date_str,
            "last_updated": datetime.now().isoformat(),
            "tweet_count": len(sorted_tweets),
            "tweets": sorted_tweets
        }
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        action = "更新" if existing_tweets else "创建"
        print(f"  📄 {action} @{screen_name}[{date_str}]: {len(sorted_tweets)} 条推文 -> {filename}")
    
    def generate_user_summaries_for_yesterday(self, force_overwrite: bool = False):
        """生成昨天所有用户的个人推文总结"""
        from datetime import datetime, timedelta
        from summarizer import TwitterSummarizer
        
        # 计算昨天日期
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y%m%d')
        
        print(f"\n🤖 开始生成昨天({yesterday_str})的用户总结...")
        
        users_dir = self.data_dir / "users_daily"
        summaries_dir = self.data_dir / "user_summaries"
        summaries_dir.mkdir(exist_ok=True)
        
        # 查找昨天的所有用户文件
        yesterday_files = list(users_dir.glob(f"*_{yesterday_str}.json"))
        
        if not yesterday_files:
            print(f"📭 未找到昨天({yesterday_str})的用户数据文件")
            return
        
        print(f"📂 发现 {len(yesterday_files)} 个用户文件")
        
        # 初始化总结器
        summarizer = TwitterSummarizer()
        summarized_count = 0
        skipped_count = 0
        
        for user_file in yesterday_files:
            try:
                # 解析文件名获取用户名
                username = user_file.stem.replace(f"_{yesterday_str}", "")
                summary_filename = f"{username}_{yesterday_str}_summary.json"
                summary_filepath = summaries_dir / summary_filename
                
                # 检查总结文件是否已存在
                if summary_filepath.exists() and not force_overwrite:
                    print(f"  ⏭️  跳过 @{username}: 总结已存在")
                    skipped_count += 1
                    continue
                # 读取用户推文数据
                with open(user_file, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                
                tweets = user_data.get('tweets', [])
                user_info = user_data.get('user', {})
                
                if summary_filepath.exists() and force_overwrite:
                    print(f"  🔄 强制覆盖 @{username} 总结 ({len(tweets)}条推文)...")
                else:
                    print(f"  🔄 生成 @{username} 总结 ({len(tweets)}条推文)...")
                
                if not tweets:
                    print(f"  ⚠️  跳过 @{username}: 无推文数据")
                    continue
                
                # 生成个人总结
                summary_result = summarizer.generate_summary(tweets, f"user_daily", user_info)
                
                # 直接保存大模型的回复为markdown文件
                md_filename = f"{username}_{yesterday_str}_summary.md"
                md_filepath = summaries_dir / md_filename

                # 判断是覆盖还是创建
                was_existing = md_filepath.exists()

                # 直接保存大模型的总结内容
                with open(md_filepath, 'w', encoding='utf-8') as f:
                    f.write(summary_result.get('summary', '暂无总结内容'))
                
                action = "覆盖" if (was_existing and force_overwrite) else "创建"
                print(f"  ✅ {action}完成 @{username}: {md_filename}")
                summarized_count += 1
                
            except Exception as e:
                print(f"  ❌ 处理 {user_file.name} 失败: {e}")
        
        print(f"\n📊 用户总结完成:")
        print(f"  ✅ 新生成: {summarized_count} 个")
        print(f"  ⏭️  已跳过: {skipped_count} 个")
        print(f"  📁 总结目录: {summaries_dir}")
    
    def generate_user_summaries_for_date(self, date_str: str, force_overwrite: bool = False):
        """为指定日期的用户数据生成总结"""
        from summarizer import TwitterSummarizer
        
        print(f"\n🤖 开始生成指定日期({date_str})的用户总结...")
        
        users_dir = self.data_dir / "users_daily"
        summaries_dir = self.data_dir / "user_summaries"
        summaries_dir.mkdir(exist_ok=True)
        
        # 查找指定日期的所有用户文件
        date_files = list(users_dir.glob(f"*_{date_str}.json"))
        
        if not date_files:
            print(f"📭 未找到指定日期({date_str})的用户数据文件")
            print(f"🔍 检查目录: {users_dir}")
            return
        
        print(f"📁 找到 {len(date_files)} 个用户数据文件")
        
        # 创建总结器
        summarizer = TwitterSummarizer()
        
        processed_count = 0
        skipped_count = 0
        
        for user_file in date_files:
            try:
                # 提取用户名
                user_name = user_file.stem.split('_')[0]  # filename: username_YYYYMMDD.json
                
                # 生成总结文件路径（改为markdown格式）
                summary_filename = f"{user_name}_{date_str}_summary.md"
                summary_path = summaries_dir / summary_filename
                
                # 检查是否已存在且不强制覆盖
                if summary_path.exists() and not force_overwrite:
                    print(f"  ⏭️  跳过 @{user_name} - 总结已存在")
                    skipped_count += 1
                    continue
                
                # 加载用户数据
                with open(user_file, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                
                tweets = user_data.get('tweets', [])
                user_info = user_data.get('user', {})
                
                if not tweets:
                    print(f"  ⚠️   @{user_name} - 无推文数据")
                    continue
                
                # 生成总结
                print(f"  🔄 处理 @{user_name} ({len(tweets)} 条推文)")
                summary_result = summarizer.generate_summary(tweets, 'user_daily', user_info)
                
                # 直接保存大模型的总结内容
                with open(summary_path, 'w', encoding='utf-8') as f:
                    f.write(summary_result.get('summary', '暂无总结内容'))
                
                print(f"  ✅ @{user_name} 总结完成")
                processed_count += 1
                
            except Exception as e:
                print(f"  ❌ @{user_name} 处理失败: {e}")
                continue
        
        print(f"\n📊 用户总结生成完成:")
        print(f"  ✅ 已处理: {processed_count} 个")
        print(f"  ⏭️  已跳过: {skipped_count} 个")
        print(f"  📁 总结目录: {summaries_dir}")

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