#!/usr/bin/env python3
"""
X API分析工具 - 使用Playwright捕获和分析API请求
基于实际请求和响应数据进行分析，不做任何假设
"""

import json
import asyncio
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

class XAPIAnalyzer:
    def __init__(self, data_dir="analysis_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 创建分析数据子目录
        for subdir in ["api_responses", "baseline_tweets", "comparison_results", "problem_cases"]:
            (self.data_dir / subdir).mkdir(exist_ok=True)
            
        self.captured_requests = []
        self.analysis_results = {}
    
    async def setup_request_interception(self, page):
        """设置请求拦截，捕获所有XHR和fetch请求"""
        
        async def handle_request(request):
            # 只关注X的API请求
            if any(domain in request.url for domain in ["twitter.com", "x.com"]):
                if request.method in ["POST", "GET"] and "/api/" in request.url:
                    print(f"🔍 捕获请求: {request.method} {request.url}")
                    
                    # 记录请求信息
                    request_data = {
                        "timestamp": datetime.now().isoformat(),
                        "method": request.method,
                        "url": request.url,
                        "headers": await self.get_request_headers(request),
                        "post_data": request.post_data if request.method == "POST" else None
                    }
                    
                    self.captured_requests.append(request_data)
        
        async def handle_response(response):
            # 捕获API响应
            if any(domain in response.url for domain in ["twitter.com", "x.com"]):
                if "/api/" in response.url and response.status == 200:
                    try:
                        response_data = await response.json()
                        
                        # 保存响应数据
                        filename = f"response_{datetime.now().strftime('%H%M%S_%f')}.json"
                        filepath = self.data_dir / "api_responses" / filename
                        
                        analysis_data = {
                            "url": response.url,
                            "timestamp": datetime.now().isoformat(),
                            "status": response.status,
                            "headers": dict(response.headers),
                            "data": response_data
                        }
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
                        
                        print(f"💾 保存响应: {filename}")
                        
                        # 立即分析响应结构
                        await self.analyze_response_structure(response_data, response.url)
                        
                    except Exception as e:
                        print(f"❌ 解析响应失败: {e}")
        
        page.on("request", handle_request)
        page.on("response", handle_response)
    
    async def get_request_headers(self, request):
        """安全获取请求头"""
        try:
            return dict(request.headers)
        except:
            return {}
    
    async def analyze_response_structure(self, data, url):
        """实时分析响应数据结构"""
        print(f"\n📊 分析响应结构: {url}")
        
        # 检测推文数据
        tweets = self.extract_tweets_from_response(data)
        if tweets:
            print(f"  发现 {len(tweets)} 条推文")
            
            for i, tweet in enumerate(tweets[:3]):  # 只分析前3条
                analysis = self.analyze_single_tweet(tweet)
                print(f"  推文 {i+1}: {analysis}")
    
    def extract_tweets_from_response(self, data):
        """从响应中提取推文数据"""
        tweets = []
        
        # 尝试多种可能的数据结构
        possible_paths = [
            data.get('data', {}).get('home', {}).get('home_timeline_urt', {}).get('instructions', []),
            data.get('data', {}).get('user', {}).get('result', {}).get('timeline_v2', {}).get('timeline', {}).get('instructions', []),
            data.get('globalObjects', {}).get('tweets', {}),
            data.get('timeline', {}).get('instructions', [])
        ]
        
        for path in possible_paths:
            if isinstance(path, list):
                # GraphQL类型响应
                for instruction in path:
                    if instruction.get('type') == 'TimelineAddEntries':
                        entries = instruction.get('entries', [])
                        for entry in entries:
                            if 'tweet' in entry.get('entryId', ''):
                                tweet_data = entry.get('content', {}).get('itemContent', {}).get('tweet_results', {}).get('result', {})
                                if tweet_data:
                                    tweets.append(tweet_data)
            elif isinstance(path, dict):
                # 直接的tweets对象
                for tweet_id, tweet_data in path.items():
                    tweets.append(tweet_data)
        
        return tweets
    
    def analyze_single_tweet(self, tweet):
        """分析单条推文的完整性"""
        analysis = {
            'has_full_text': 'full_text' in tweet,
            'has_text': 'text' in tweet,
            'has_legacy': 'legacy' in tweet,
            'text_length': 0,
            'has_media': False,
            'has_retweet': False,
            'potential_issues': []
        }
        
        # 分析文本内容
        text_field = tweet.get('full_text') or tweet.get('text') or tweet.get('legacy', {}).get('full_text', '')
        analysis['text_length'] = len(text_field)
        
        # 检查截断指标
        if 'truncated' in tweet and tweet['truncated']:
            analysis['potential_issues'].append('text_truncated')
        
        # 检查媒体内容
        media = tweet.get('entities', {}).get('media', []) or tweet.get('legacy', {}).get('entities', {}).get('media', [])
        analysis['has_media'] = len(media) > 0
        
        # 检查转推
        if 'retweeted_status' in tweet or tweet.get('legacy', {}).get('retweeted_status_id_str'):
            analysis['has_retweet'] = True
        
        # 检查可能的数据缺失
        essential_fields = ['id_str', 'created_at', 'user']
        for field in essential_fields:
            if field not in tweet and field not in tweet.get('legacy', {}):
                analysis['potential_issues'].append(f'missing_{field}')
        
        return analysis
    
    async def start_analysis_session(self):
        """开始分析会话"""
        print("🚀 启动X API分析工具")
        print("📋 分析目标:")
        print("  1. 帖子内容完整性")
        print("  2. 文本截断问题")
        print("  3. 转推数据结构")
        print("  4. 媒体文件URL")
        print("  5. API请求模式")
        print("\n请在浏览器中登录X并访问推荐时间线...")
        
        # 使用绝对路径存储用户数据
        user_data_dir = os.path.join(os.getcwd(), "browser_data")
        
        async with async_playwright() as p:
            # 使用launch_persistent_context正确保持登录状态
            context = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # 获取或创建页面
            if context.pages:
                page = context.pages[0]
            else:
                page = await context.new_page()
            
            # 设置请求拦截
            await self.setup_request_interception(page)
            
            # 访问X主页
            print("\n🌐 正在访问 x.com...")
            await page.goto("https://x.com/home")
            
            print("\n✋ 请在浏览器中完成以下操作:")
            print("  1. 如未登录，请先登录")
            print("  2. 浏览推荐时间线")
            print("  3. 点击几条不同类型的推文（普通、转推、长文、媒体）")
            print("  4. 展开一些回复和评论")
            print("  5. 完成后在终端按 Ctrl+C 结束分析")
            
            try:
                # 等待用户操作
                await asyncio.sleep(300)  # 等待5分钟
            except KeyboardInterrupt:
                print("\n\n🛑 分析会话结束")
            
            await context.close()
            
            # 生成分析报告
            await self.generate_analysis_report()
    
    async def generate_analysis_report(self):
        """生成分析报告"""
        print(f"\n📈 生成分析报告...")
        print(f"  捕获请求数: {len(self.captured_requests)}")
        
        # 统计API响应文件
        response_files = list((self.data_dir / "api_responses").glob("*.json"))
        print(f"  保存响应数: {len(response_files)}")
        
        # 生成总结报告
        report = {
            "analysis_session": {
                "timestamp": datetime.now().isoformat(),
                "captured_requests": len(self.captured_requests),
                "response_files": len(response_files)
            },
            "api_endpoints": [],
            "data_structure_patterns": {},
            "potential_issues": []
        }
        
        # 分析API端点模式
        endpoints = set()
        for req in self.captured_requests:
            endpoint = req['url'].split('?')[0]  # 去掉查询参数
            endpoints.add(endpoint)
        
        report["api_endpoints"] = list(endpoints)
        
        # 保存报告
        report_file = self.data_dir / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 分析报告已保存: {report_file}")
        print(f"📁 数据目录: {self.data_dir.absolute()}")

if __name__ == "__main__":
    analyzer = XAPIAnalyzer()
    asyncio.run(analyzer.start_analysis_session())