#!/usr/bin/env python3
"""
数据完整性验证系统 - 确保抓取数据正确性和完整性
基于黄金数据集和多维度验证机制
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import requests
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    score: float  # 0-100分
    issues: List[str]
    details: Dict[str, Any]

class DataValidator:
    def __init__(self, data_dir="analysis_data", golden_dataset_dir="golden_dataset"):
        self.data_dir = Path(data_dir)
        self.golden_dir = Path(golden_dataset_dir)
        self.golden_dir.mkdir(exist_ok=True)
        
        # 创建验证数据目录
        for subdir in ["baseline_data", "validation_reports", "comparison_results"]:
            (self.golden_dir / subdir).mkdir(exist_ok=True)
        
        # 验证规则配置
        self.validation_rules = {
            "text_completeness": {
                "min_avg_length": 20,  # 推文平均长度不应过短
                "truncated_ratio_threshold": 0.05,  # 截断推文比例不超过5%
                "empty_text_threshold": 0.01  # 空文本比例不超过1%
            },
            "retweet_integrity": {
                "retweet_original_text_required": True,
                "nested_retweet_support": True,
                "retweet_user_info_required": True
            },
            "media_completeness": {
                "media_url_accessibility": True,
                "video_quality_variants": True,
                "image_url_format_check": True
            },
            "data_structure": {
                "required_fields": ["id", "text", "created_at", "user"],
                "user_required_fields": ["name", "screen_name"],
                "timestamp_format_check": True
            }
        }
    
    def create_golden_dataset(self, browser_visible_posts: List[Dict], api_response_file: str) -> str:
        """创建黄金数据集 - 人工验证的正确数据"""
        print("🏆 创建黄金数据集...")
        
        # 加载API响应数据
        with open(api_response_file, 'r', encoding='utf-8') as f:
            api_data = json.load(f)
        
        golden_dataset = {
            "creation_time": datetime.now().isoformat(),
            "source_api_file": api_response_file,
            "verification_method": "manual_browser_comparison",
            "posts": [],
            "validation_checkpoints": {
                "text_integrity": {},
                "media_files": {},
                "retweet_data": {},
                "user_info": {}
            }
        }
        
        for i, browser_post in enumerate(browser_visible_posts):
            # 创建验证检查点
            checkpoint = {
                "browser_visible_text": browser_post["text"],
                "browser_visible_media": browser_post.get("media", []),
                "browser_user_info": browser_post["user"],
                "browser_stats": browser_post.get("stats", {}),
                "api_extraction_path": browser_post.get("api_path", ""),
                "validation_status": "verified",
                "known_issues": browser_post.get("known_issues", [])
            }
            
            golden_dataset["posts"].append(checkpoint)
        
        # 保存黄金数据集
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        golden_file = self.golden_dir / f"golden_dataset_{timestamp}.json"
        
        with open(golden_file, 'w', encoding='utf-8') as f:
            json.dump(golden_dataset, f, ensure_ascii=False, indent=2)
        
        print(f"💾 黄金数据集已保存: {golden_file}")
        return str(golden_file)
    
    def validate_text_completeness(self, tweets: List[Dict]) -> ValidationResult:
        """验证文本完整性"""
        issues = []
        details = {}
        
        if not tweets:
            return ValidationResult(False, 0, ["没有推文数据"], {})
        
        # 统计文本长度
        text_lengths = [len(tweet.get('text', '')) for tweet in tweets]
        avg_length = sum(text_lengths) / len(text_lengths)
        
        empty_texts = sum(1 for length in text_lengths if length == 0)
        empty_ratio = empty_texts / len(tweets)
        
        # 检查截断标识
        truncated_count = sum(1 for tweet in tweets if tweet.get('truncated', False))
        truncated_ratio = truncated_count / len(tweets)
        
        details = {
            "total_tweets": len(tweets),
            "avg_text_length": avg_length,
            "empty_text_count": empty_texts,
            "empty_text_ratio": empty_ratio,
            "truncated_count": truncated_count,
            "truncated_ratio": truncated_ratio,
            "min_length": min(text_lengths) if text_lengths else 0,
            "max_length": max(text_lengths) if text_lengths else 0
        }
        
        score = 100
        
        # 评分规则
        if avg_length < self.validation_rules["text_completeness"]["min_avg_length"]:
            issues.append(f"平均文本长度过短: {avg_length:.1f}")
            score -= 30
        
        if empty_ratio > self.validation_rules["text_completeness"]["empty_text_threshold"]:
            issues.append(f"空文本比例过高: {empty_ratio:.3f}")
            score -= 40
        
        if truncated_ratio > self.validation_rules["text_completeness"]["truncated_ratio_threshold"]:
            issues.append(f"截断文本比例过高: {truncated_ratio:.3f}")
            score -= 25
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            score=max(0, score),
            issues=issues,
            details=details
        )
    
    def validate_retweet_integrity(self, tweets: List[Dict]) -> ValidationResult:
        """验证转推完整性"""
        issues = []
        details = {}
        
        retweets = [tweet for tweet in tweets if tweet.get('retweet')]
        details['total_retweets'] = len(retweets)
        details['retweet_ratio'] = len(retweets) / len(tweets) if tweets else 0
        
        if not retweets:
            return ValidationResult(True, 100, [], details)
        
        # 检查转推原文完整性
        missing_original_text = 0
        missing_original_user = 0
        nested_retweets = 0
        
        for tweet in retweets:
            retweet_data = tweet.get('retweet', {})
            
            # 检查原文
            if not retweet_data.get('text'):
                missing_original_text += 1
            
            # 检查原用户信息
            if not retweet_data.get('user'):
                missing_original_user += 1
            
            # 检查嵌套转推
            if retweet_data.get('retweet'):
                nested_retweets += 1
        
        details.update({
            "missing_original_text": missing_original_text,
            "missing_original_user": missing_original_user,
            "nested_retweets": nested_retweets
        })
        
        score = 100
        
        if missing_original_text > 0:
            issues.append(f"缺失转推原文: {missing_original_text} 条")
            score -= (missing_original_text / len(retweets)) * 50
        
        if missing_original_user > 0:
            issues.append(f"缺失转推原用户信息: {missing_original_user} 条")
            score -= (missing_original_user / len(retweets)) * 30
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            score=max(0, score),
            issues=issues,
            details=details
        )
    
    def validate_media_accessibility(self, tweets: List[Dict]) -> ValidationResult:
        """验证媒体文件可访问性"""
        issues = []
        details = {}
        
        media_tweets = [tweet for tweet in tweets if tweet.get('media')]
        all_media = []
        
        for tweet in media_tweets:
            all_media.extend(tweet.get('media', []))
        
        details['total_media_files'] = len(all_media)
        details['media_tweets'] = len(media_tweets)
        
        if not all_media:
            return ValidationResult(True, 100, [], details)
        
        # 检查媒体URL格式
        valid_urls = 0
        invalid_urls = 0
        accessible_urls = 0
        video_files = 0
        image_files = 0
        
        for media in all_media:
            url = media.get('url')
            media_type = media.get('type')
            
            if media_type == 'video':
                video_files += 1
            elif media_type in ['photo', 'animated_gif']:
                image_files += 1
            
            if not url:
                invalid_urls += 1
                continue
            
            # 检查URL格式
            if url.startswith('https://') and ('twimg.com' in url or 'twitter.com' in url):
                valid_urls += 1
                
                # 测试可访问性（采样检查，避免过多请求）
                if len(all_media) <= 10 or valid_urls <= 3:
                    try:
                        response = requests.head(url, timeout=5)
                        if response.status_code == 200:
                            accessible_urls += 1
                    except:
                        pass
            else:
                invalid_urls += 1
        
        details.update({
            "valid_urls": valid_urls,
            "invalid_urls": invalid_urls,
            "accessible_urls": accessible_urls,
            "video_files": video_files,
            "image_files": image_files
        })
        
        score = 100
        
        if invalid_urls > 0:
            invalid_ratio = invalid_urls / len(all_media)
            issues.append(f"无效媒体URL: {invalid_urls} 个 ({invalid_ratio:.2%})")
            score -= invalid_ratio * 60
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            score=max(0, score),
            issues=issues,
            details=details
        )
    
    def validate_data_structure(self, tweets: List[Dict]) -> ValidationResult:
        """验证数据结构完整性"""
        issues = []
        details = {}
        
        if not tweets:
            return ValidationResult(False, 0, ["没有推文数据"], {})
        
        required_fields = self.validation_rules["data_structure"]["required_fields"]
        user_required_fields = self.validation_rules["data_structure"]["user_required_fields"]
        
        missing_field_counts = {field: 0 for field in required_fields}
        missing_user_field_counts = {field: 0 for field in user_required_fields}
        
        valid_timestamps = 0
        
        for tweet in tweets:
            # 检查必需字段
            for field in required_fields:
                if field not in tweet or tweet[field] is None:
                    missing_field_counts[field] += 1
            
            # 检查用户字段
            user = tweet.get('user', {})
            if user:
                for field in user_required_fields:
                    if field not in user or user[field] is None:
                        missing_user_field_counts[field] += 1
            
            # 检查时间戳格式
            created_at = tweet.get('created_at')
            if created_at:
                try:
                    # X的时间格式: "Wed Oct 05 22:34:12 +0000 2011"
                    from dateutil.parser import parse
                    parse(created_at)
                    valid_timestamps += 1
                except:
                    pass
        
        details = {
            "total_tweets": len(tweets),
            "missing_fields": missing_field_counts,
            "missing_user_fields": missing_user_field_counts,
            "valid_timestamps": valid_timestamps,
            "timestamp_validity_ratio": valid_timestamps / len(tweets)
        }
        
        score = 100
        
        # 评分
        for field, count in missing_field_counts.items():
            if count > 0:
                ratio = count / len(tweets)
                issues.append(f"缺失{field}字段: {count} 条 ({ratio:.2%})")
                score -= ratio * 30
        
        for field, count in missing_user_field_counts.items():
            if count > 0:
                ratio = count / len(tweets)
                issues.append(f"缺失用户{field}字段: {count} 条 ({ratio:.2%})")
                score -= ratio * 20
        
        timestamp_invalid_ratio = 1 - (valid_timestamps / len(tweets))
        if timestamp_invalid_ratio > 0.1:  # 超过10%的时间戳无效
            issues.append(f"时间戳格式错误比例: {timestamp_invalid_ratio:.2%}")
            score -= timestamp_invalid_ratio * 25
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            score=max(0, score),
            issues=issues,
            details=details
        )
    
    def compare_with_golden_dataset(self, tweets: List[Dict], golden_dataset_file: str) -> ValidationResult:
        """与黄金数据集对比"""
        issues = []
        details = {}
        
        try:
            with open(golden_dataset_file, 'r', encoding='utf-8') as f:
                golden_data = json.load(f)
        except:
            return ValidationResult(False, 0, ["无法读取黄金数据集"], {})
        
        # 修正：我们的黄金数据集中字段名是baseline_tweets，不是posts
        golden_posts = golden_data.get('baseline_tweets', [])
        
        if len(tweets) < len(golden_posts) * 0.8:  # 允许20%的数据差异
            issues.append(f"推文数量显著减少: {len(tweets)} vs {len(golden_posts)}")
        
        # 文本相似度检查（采样前10条）
        text_match_count = 0
        sample_size = min(10, len(tweets), len(golden_posts))
        
        for i in range(sample_size):
            tweet_text = tweets[i].get('text', '').strip()
            # 修正：我们的黄金数据集中字段名是expected_text，不是browser_visible_text
            golden_text = golden_posts[i].get('expected_text', '').strip()
            
            # 简单相似度检查
            if tweet_text and golden_text:
                if tweet_text == golden_text:
                    text_match_count += 1
                elif tweet_text in golden_text or golden_text in tweet_text:
                    text_match_count += 0.5
        
        text_match_ratio = text_match_count / sample_size if sample_size > 0 else 0
        
        details = {
            "golden_posts_count": len(golden_posts),
            "current_posts_count": len(tweets),
            "sample_text_match_ratio": text_match_ratio,
            "sample_size": sample_size
        }
        
        score = 100
        
        if text_match_ratio < 0.8:
            issues.append(f"文本匹配率过低: {text_match_ratio:.2%}")
            score -= (1 - text_match_ratio) * 50
        
        return ValidationResult(
            is_valid=text_match_ratio >= 0.8,
            score=max(0, score),
            issues=issues,
            details=details
        )
    
    def comprehensive_validation(self, tweets: List[Dict], golden_dataset_file: Optional[str] = None) -> Dict[str, ValidationResult]:
        """综合验证"""
        print("🔍 开始综合数据验证...")
        
        results = {}
        
        # 文本完整性验证
        print("  1. 验证文本完整性...")
        results['text_completeness'] = self.validate_text_completeness(tweets)
        
        # 转推完整性验证
        print("  2. 验证转推完整性...")
        results['retweet_integrity'] = self.validate_retweet_integrity(tweets)
        
        # 媒体文件验证
        print("  3. 验证媒体文件...")
        results['media_accessibility'] = self.validate_media_accessibility(tweets)
        
        # 数据结构验证
        print("  4. 验证数据结构...")
        results['data_structure'] = self.validate_data_structure(tweets)
        
        # 黄金数据集对比
        if golden_dataset_file and os.path.exists(golden_dataset_file):
            print("  5. 对比黄金数据集...")
            results['golden_comparison'] = self.compare_with_golden_dataset(tweets, golden_dataset_file)
        
        return results
    
    def generate_validation_report(self, validation_results: Dict[str, ValidationResult], tweets: List[Dict]) -> str:
        """生成验证报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.golden_dir / "validation_reports" / f"validation_report_{timestamp}.json"
        
        # 计算总体分数
        scores = [result.score for result in validation_results.values()]
        overall_score = sum(scores) / len(scores) if scores else 0
        
        all_issues = []
        for category, result in validation_results.items():
            all_issues.extend([f"[{category}] {issue}" for issue in result.issues])
        
        report = {
            "validation_time": datetime.now().isoformat(),
            "tweet_count": len(tweets),
            "overall_score": overall_score,
            "overall_status": "PASS" if overall_score >= 80 else "FAIL",
            "category_results": {},
            "all_issues": all_issues,
            "recommendations": []
        }
        
        # 详细结果
        for category, result in validation_results.items():
            report["category_results"][category] = {
                "score": result.score,
                "is_valid": result.is_valid,
                "issues": result.issues,
                "details": result.details
            }
        
        # 生成建议
        if overall_score < 80:
            report["recommendations"] = self.generate_improvement_recommendations(validation_results)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 验证报告已保存: {report_file}")
        return str(report_file)
    
    def generate_improvement_recommendations(self, results: Dict[str, ValidationResult]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        for category, result in results.items():
            if result.score < 80:
                if category == 'text_completeness':
                    recommendations.append("检查文本提取路径，确保使用 legacy.full_text 字段")
                elif category == 'retweet_integrity':
                    recommendations.append("检查转推解析逻辑，确保提取 retweeted_status_result 数据")
                elif category == 'media_accessibility':
                    recommendations.append("检查媒体URL提取路径，确保从 extended_entities.media 获取")
                elif category == 'data_structure':
                    recommendations.append("检查必需字段的提取逻辑，确保数据结构完整")
        
        return recommendations
    
    def print_validation_summary(self, validation_results: Dict[str, ValidationResult]):
        """打印验证摘要"""
        print("\n📊 验证结果摘要:")
        print("=" * 50)
        
        scores = []
        for category, result in validation_results.items():
            status = "✅ PASS" if result.is_valid else "❌ FAIL"
            print(f"{category:20} {status:8} 分数: {result.score:5.1f}")
            scores.append(result.score)
        
        overall_score = sum(scores) / len(scores) if scores else 0
        overall_status = "✅ PASS" if overall_score >= 80 else "❌ FAIL"
        
        print("-" * 50)
        print(f"{'总体评分':20} {overall_status:8} 分数: {overall_score:5.1f}")
        
        # 显示主要问题
        all_issues = []
        for result in validation_results.values():
            all_issues.extend(result.issues)
        
        if all_issues:
            print(f"\n🚨 发现 {len(all_issues)} 个问题:")
            for issue in all_issues[:10]:  # 只显示前10个
                print(f"  • {issue}")
            
            if len(all_issues) > 10:
                print(f"  ... 还有 {len(all_issues) - 10} 个问题")

def main():
    """验证工具主函数"""
    print("🔍 数据完整性验证工具")
    
    validator = DataValidator()
    
    # 示例：创建黄金数据集
    print("\n1. 创建黄金数据集 (需要手动验证的浏览器数据)")
    print("请准备以下数据:")
    print("- browser_visible_posts: 浏览器中看到的推文数据")
    print("- api_response_file: 对应的API响应文件")
    
    # 示例：验证数据
    print("\n2. 数据验证示例")
    print("使用方法:")
    print("validator.comprehensive_validation(tweets, golden_dataset_file)")

if __name__ == "__main__":
    main()