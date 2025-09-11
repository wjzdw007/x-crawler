#!/usr/bin/env python3
"""
黄金数据集构建工具 - 基于已有分析数据创建验证基准
通过分析API响应数据，自动生成验证检查点
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class GoldenDatasetBuilder:
    def __init__(self, analysis_data_dir="analysis_data", golden_dir="golden_dataset"):
        self.analysis_data_dir = Path(analysis_data_dir)
        self.golden_dir = Path(golden_dir)
        self.golden_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        for subdir in ["baseline_data", "verification_samples", "test_cases"]:
            (self.golden_dir / subdir).mkdir(exist_ok=True)
    
    def extract_tweets_from_api_response(self, response_file: str) -> List[Dict]:
        """从API响应中提取推文数据"""
        try:
            with open(response_file, 'r', encoding='utf-8') as f:
                response_data = json.load(f)
            
            data = response_data.get('data', {})
            tweets = []
            
            # 修正数据路径 - 基于调试发现的结构
            inner_data = data.get('data', {})
            home_timeline = inner_data.get('home', {}).get('home_timeline_urt', {})
            instructions = home_timeline.get('instructions', [])
            
            for instruction in instructions:
                if instruction.get('type') == 'TimelineAddEntries':
                    entries = instruction.get('entries', [])
                    
                    for entry in entries:
                        entry_id = entry.get('entryId', '')
                        
                        if 'tweet-' in entry_id:
                            content = entry.get('content', {})
                            item_content = content.get('itemContent', {})
                            tweet_results = item_content.get('tweet_results', {})
                            tweet_data = tweet_results.get('result', {})
                            
                            if tweet_data.get('__typename') == 'Tweet':
                                tweets.append(tweet_data)
            
            return tweets
            
        except Exception as e:
            print(f"❌ 提取推文失败: {e}")
            return []
    
    def create_baseline_tweet(self, tweet_data: Dict) -> Dict:
        """创建基准推文数据 - 正确的解析结果"""
        try:
            # 基础信息
            baseline = {
                "tweet_id": tweet_data.get('rest_id'),
                "source_data_path": "",
                "expected_text": "",
                "expected_created_at": tweet_data.get('legacy', {}).get('created_at'),
                "expected_lang": tweet_data.get('legacy', {}).get('lang'),
            }
            
            # 提取文本内容 - 处理长文推文和普通推文
            if 'note_tweet' in tweet_data:
                # 长文推文
                note_tweet_result = tweet_data.get('note_tweet', {}).get('note_tweet_results', {}).get('result', {})
                if note_tweet_result:
                    baseline["expected_text"] = note_tweet_result.get('text', '')
                    baseline["source_data_path"] = "note_tweet.note_tweet_results.result.text"
            
            if not baseline["expected_text"]:
                # 普通推文 - 使用 legacy.full_text
                baseline["expected_text"] = tweet_data.get('legacy', {}).get('full_text', '')
                baseline["source_data_path"] = "legacy.full_text"
            
            # 用户信息 - 修正字段路径
            user_results = tweet_data.get('core', {}).get('user_results', {}).get('result', {})
            if user_results:
                baseline["expected_user"] = {
                    "id": user_results.get('rest_id'),
                    "name": user_results.get('core', {}).get('name'),  # 修正：从core获取
                    "screen_name": user_results.get('core', {}).get('screen_name'),  # 修正：从core获取
                    "description": user_results.get('legacy', {}).get('description'),
                    "followers_count": user_results.get('legacy', {}).get('followers_count', 0),
                    "friends_count": user_results.get('legacy', {}).get('friends_count', 0),
                    "verified": user_results.get('verification', {}).get('verified', False),  # 修正路径
                    "is_blue_verified": user_results.get('is_blue_verified', False)
                }
            
            # 统计数据
            legacy_data = tweet_data.get('legacy', {})
            baseline["expected_stats"] = {
                "retweet_count": legacy_data.get('retweet_count', 0),
                "favorite_count": legacy_data.get('favorite_count', 0),
                "reply_count": legacy_data.get('reply_count', 0),
                "quote_count": legacy_data.get('quote_count', 0)
            }
            
            # 媒体文件
            extended_entities = legacy_data.get('extended_entities', {})
            if 'media' in extended_entities:
                baseline["expected_media"] = []
                for media_item in extended_entities['media']:
                    media_info = {
                        "type": media_item.get('type'),
                        "id": media_item.get('id_str'),
                    }
                    
                    if media_item['type'] == 'video':
                        variants = media_item.get('video_info', {}).get('variants', [])
                        # 找到最高质量的视频
                        best_variant = None
                        highest_bitrate = 0
                        for variant in variants:
                            if variant.get('content_type') == 'video/mp4':
                                bitrate = variant.get('bitrate', 0)
                                if bitrate > highest_bitrate:
                                    highest_bitrate = bitrate
                                    best_variant = variant
                        
                        if best_variant:
                            media_info["expected_url"] = best_variant['url']
                            media_info["expected_bitrate"] = best_variant.get('bitrate')
                    
                    elif media_item['type'] in ['photo', 'animated_gif']:
                        media_info["expected_url"] = media_item.get('media_url_https')
                    
                    baseline["expected_media"].append(media_info)
            
            # 转推数据
            if 'retweeted_status_result' in legacy_data:
                retweet_result = legacy_data['retweeted_status_result'].get('result', {})
                if retweet_result:
                    baseline["is_retweet"] = True
                    baseline["expected_retweet_text"] = retweet_result.get('legacy', {}).get('full_text', '')
                    
                    # 转推用户信息
                    retweet_user = retweet_result.get('core', {}).get('user_results', {}).get('result', {})
                    if retweet_user:
                        baseline["expected_retweet_user"] = {
                            "name": retweet_user.get('legacy', {}).get('name'),
                            "screen_name": retweet_user.get('legacy', {}).get('screen_name')
                        }
            else:
                baseline["is_retweet"] = False
            
            # 引用推文
            if 'quoted_status_result' in tweet_data:
                quoted_result = tweet_data['quoted_status_result'].get('result', {})
                if quoted_result:
                    baseline["is_quoted"] = True
                    baseline["expected_quoted_text"] = quoted_result.get('legacy', {}).get('full_text', '')
            else:
                baseline["is_quoted"] = False
            
            # 验证检查点
            baseline["validation_checkpoints"] = {
                "text_not_empty": len(baseline["expected_text"]) > 0,
                "has_user_info": "expected_user" in baseline,
                "timestamp_valid": baseline["expected_created_at"] is not None,
                "media_urls_valid": all(
                    m.get("expected_url", "").startswith("https://") 
                    for m in baseline.get("expected_media", [])
                ),
                "retweet_data_complete": (
                    not baseline["is_retweet"] or 
                    (len(baseline.get("expected_retweet_text", "")) > 0)
                )
            }
            
            return baseline
            
        except Exception as e:
            print(f"❌ 创建基准数据失败: {e}")
            return {}
    
    def build_golden_dataset_from_responses(self) -> str:
        """从API响应文件构建黄金数据集"""
        print("🏗️ 从API响应构建黄金数据集...")
        
        # 查找响应文件 - 检查多个可能位置
        possible_dirs = [
            self.analysis_data_dir / "api_responses",
            Path("."),  # 当前目录
            Path("analysis_data/api_responses")
        ]
        
        response_files = []
        for response_dir in possible_dirs:
            if response_dir.exists():
                found_files = list(response_dir.glob("response_*.json"))
                if found_files:
                    response_files.extend(found_files)
                    print(f"📂 在 {response_dir} 发现 {len(found_files)} 个响应文件")
                    break
        
        print(f"📂 总共发现 {len(response_files)} 个响应文件")
        
        all_baselines = []
        processed_tweet_ids = set()  # 避免重复
        
        # 过滤出真正的时间线API文件
        timeline_files = []
        for response_file in response_files:
            try:
                with open(response_file, 'r', encoding='utf-8') as f:
                    response_data = json.load(f)
                url = response_data.get('url', '')
                if 'HomeTimeline' in url or 'HomeLatestTimeline' in url:
                    timeline_files.append(response_file)
            except:
                continue
        
        print(f"📍 发现 {len(timeline_files)} 个时间线API文件")
        
        for response_file in timeline_files[:3]:  # 处理前3个时间线文件
            print(f"  处理: {response_file.name}")
            tweets = self.extract_tweets_from_api_response(str(response_file))
            
            for tweet_data in tweets:
                tweet_id = tweet_data.get('rest_id')
                if tweet_id and tweet_id not in processed_tweet_ids:
                    baseline = self.create_baseline_tweet(tweet_data)
                    if baseline:
                        baseline["source_file"] = response_file.name
                        all_baselines.append(baseline)
                        processed_tweet_ids.add(tweet_id)
        
        # 创建黄金数据集
        golden_dataset = {
            "creation_time": datetime.now().isoformat(),
            "description": "基于API响应数据自动生成的黄金数据集",
            "source_files": [f.name for f in response_files[:5]],
            "total_tweets": len(all_baselines),
            "baseline_tweets": all_baselines,
            "validation_rules": {
                "text_completeness": {
                    "description": "验证推文文本完整性",
                    "critical_fields": ["expected_text", "expected_created_at"]
                },
                "user_data_integrity": {
                    "description": "验证用户信息完整性",
                    "critical_fields": ["expected_user.name", "expected_user.screen_name"]
                },
                "media_accessibility": {
                    "description": "验证媒体文件URL有效性",
                    "critical_fields": ["expected_media[].expected_url"]
                },
                "retweet_completeness": {
                    "description": "验证转推数据完整性",
                    "critical_fields": ["expected_retweet_text", "expected_retweet_user"]
                }
            }
        }
        
        # 统计信息
        stats = {
            "total_tweets": len(all_baselines),
            "retweets": sum(1 for b in all_baselines if b.get("is_retweet")),
            "quoted_tweets": sum(1 for b in all_baselines if b.get("is_quoted")),
            "media_tweets": sum(1 for b in all_baselines if b.get("expected_media")),
            "valid_checkpoints": sum(
                1 for b in all_baselines 
                if all(b.get("validation_checkpoints", {}).values())
            )
        }
        
        golden_dataset["statistics"] = stats
        
        # 保存黄金数据集
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        golden_file = self.golden_dir / f"golden_dataset_{timestamp}.json"
        
        with open(golden_file, 'w', encoding='utf-8') as f:
            json.dump(golden_dataset, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 黄金数据集已创建: {golden_file}")
        print(f"📊 统计信息:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        return str(golden_file)
    
    def create_test_cases(self, golden_dataset_file: str) -> str:
        """创建测试用例"""
        print("🧪 创建测试用例...")
        
        try:
            with open(golden_dataset_file, 'r', encoding='utf-8') as f:
                golden_data = json.load(f)
        except:
            print("❌ 无法读取黄金数据集")
            return ""
        
        baselines = golden_data.get("baseline_tweets", [])
        
        test_cases = {
            "creation_time": datetime.now().isoformat(),
            "golden_dataset_source": golden_dataset_file,
            "test_scenarios": []
        }
        
        # 创建不同类型的测试用例
        scenarios = [
            {
                "name": "普通推文文本完整性测试",
                "description": "测试普通推文的文本是否完整提取",
                "filter": lambda b: not b.get("is_retweet") and not b.get("expected_media"),
                "key_validations": ["expected_text", "expected_user", "expected_created_at"]
            },
            {
                "name": "转推数据完整性测试",
                "description": "测试转推推文的原文和用户信息提取",
                "filter": lambda b: b.get("is_retweet"),
                "key_validations": ["expected_retweet_text", "expected_retweet_user"]
            },
            {
                "name": "媒体文件URL测试",
                "description": "测试图片和视频URL的提取",
                "filter": lambda b: b.get("expected_media"),
                "key_validations": ["expected_media"]
            }
        ]
        
        for scenario in scenarios:
            matching_baselines = [b for b in baselines if scenario["filter"](b)]
            
            if matching_baselines:
                test_case = {
                    "scenario_name": scenario["name"],
                    "description": scenario["description"],
                    "sample_count": len(matching_baselines[:10]),  # 每类取10个样本
                    "samples": matching_baselines[:10],
                    "key_validations": scenario["key_validations"]
                }
                test_cases["test_scenarios"].append(test_case)
        
        # 保存测试用例
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        test_file = self.golden_dir / "test_cases" / f"test_cases_{timestamp}.json"
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_cases, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 测试用例已创建: {test_file}")
        print(f"📋 创建了 {len(test_cases['test_scenarios'])} 个测试场景")
        
        return str(test_file)

def main():
    """主函数"""
    print("🏗️ 黄金数据集构建工具")
    
    builder = GoldenDatasetBuilder()
    
    # 构建黄金数据集
    golden_file = builder.build_golden_dataset_from_responses()
    
    if golden_file:
        # 创建测试用例
        test_file = builder.create_test_cases(golden_file)
        
        print(f"\n🎉 完成!")
        print(f"黄金数据集: {golden_file}")
        print(f"测试用例: {test_file}")
        
        print(f"\n📖 使用方法:")
        print(f"1. 使用黄金数据集验证爬虫输出:")
        print(f"   validator.comprehensive_validation(tweets, '{golden_file}')")
        print(f"2. 运行测试用例:")
        print(f"   使用测试用例文件进行自动化测试")
    else:
        print("❌ 构建失败，请检查API响应数据")

if __name__ == "__main__":
    main()