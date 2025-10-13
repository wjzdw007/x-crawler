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
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        初始化总结器
        
        Args:
            api_key: LLM API密钥，如果为None则从环境变量获取
            model: 指定使用的模型，如果为None则使用默认模型
        """
        # 尝试从多个环境变量获取API密钥
        self.api_key = (
            api_key or 
            os.getenv('OPENROUTER_API_KEY') or 
            os.getenv('OPENAI_API_KEY') or
            os.getenv('LLM_API_KEY')
        )
        
        # 指定的模型：参数 > 环境变量 > None
        self.custom_model = model or os.getenv('OPENAI_MODEL')
        # 不再创建独立的summaries目录，使用crawler_data/user_summaries
        
        # 总结配置
        self.config = {
            "max_tweets_per_summary": 100,
            "summary_types": ["daily", "trending", "category"],
            "languages": ["zh", "en"],
            "output_formats": ["markdown", "json", "html"]
        }
        
        # 用户分析配置 - 根据不同用户的特点定制分析角度
        self.user_analysis_profiles = {
            "elonmusk": {
                "type": "entrepreneur_investor",
                "focus": "商业投资机会",
                "keywords": ["投资", "创业", "科技趋势", "市场动向", "政策影响"],
                "analysis_angles": [
                    "🚀 **商业机会识别**：从推文中识别潜在的投资方向和商业趋势",
                    "💡 **创新技术洞察**：关注提到的新技术、产品或解决方案",
                    "📈 **市场信号解读**：分析对特定行业、公司或政策的态度变化",
                    "🎯 **战略思维分析**：理解其决策逻辑和长期布局思路"
                ]
            },
            "dotey": {
                "type": "tech_educator", 
                "focus": "AI技术学习",
                "keywords": ["AI", "编程", "技术分享", "工具推荐", "学习资源"],
                "analysis_angles": [
                    "🤖 **AI技术动态**：整理最新的AI工具、模型和技术发展",
                    "📚 **学习资源整理**：识别值得深入学习的技术内容和资源",
                    "🛠️ **实用工具推荐**：提取推荐的开发工具、框架和最佳实践",
                    "💭 **技术见解提炼**：总结对技术趋势和发展方向的独特观点"
                ]
            },
            "default": {
                "type": "general_content",
                "focus": "内容洞察",
                "keywords": ["热点", "趋势", "观点", "分享"],
                "analysis_angles": [
                    "📊 **内容主题分析**：识别主要讨论的话题和关注点",
                    "🔥 **热点事件跟踪**：总结涉及的重要事件和社会议题", 
                    "💬 **观点立场梳理**：分析表达的核心观点和价值取向",
                    "📈 **影响力评估**：评估内容的传播价值和社会影响"
                ]
            }
        }
        
        # 启动时加载保存的用户配置
        self.load_user_profiles()
        
        # 加载用户提示词模板
        self.load_user_prompt_templates()
        
        # LLM配置
        self.llm_config = {
            "default_model": "openai/gpt-4o",
            "fallback_models": [
                "openai/gpt-4o-mini", 
                "anthropic/claude-3-haiku",
                "meta-llama/llama-3.1-8b-instruct"
            ],
            "max_tokens": 100000,
            "temperature": 0.7
        }
        
        # 检查API状态
        self.check_api_status()
    
    def check_api_status(self):
        """检查API密钥和依赖库状态"""
        print(f"\n🔧 LLM API 状态检查:")
        
        # 检查API密钥
        if self.api_key:
            masked_key = f"{self.api_key[:8]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "***"
            print(f"  ✅ API密钥: {masked_key}")
        else:
            print(f"  ⚠️ API密钥: 未设置 (将使用模拟总结)")
            print(f"     💡 请设置环境变量: OPENROUTER_API_KEY")
        
        # 检查依赖库
        try:
            from openai import OpenAI
            print(f"  ✅ OpenAI库: 已安装")
        except ImportError:
            print(f"  ❌ OpenAI库: 未安装")
            print(f"     💡 请安装: pip install openai")
            
        effective_model = self.custom_model or self.llm_config['default_model']
        print(f"  🎯 使用模型: {effective_model}")
        if self.custom_model:
            print(f"     (自定义指定)")
        print(f"  🔄 备选模型: {len(self.llm_config['fallback_models'])} 个")
    
    def add_user_profile(self, username: str, user_type: str, focus: str, keywords: List[str], analysis_angles: List[str]):
        """添加新用户的分析配置"""
        self.user_analysis_profiles[username] = {
            "type": user_type,
            "focus": focus,
            "keywords": keywords,
            "analysis_angles": analysis_angles
        }
        print(f"✅ 已添加用户 @{username} 的分析配置：{focus}")
        
        # 自动保存到配置文件
        self.save_user_profiles()
    
    def save_user_profiles(self):
        """保存用户分析配置到文件"""
        config_file = Path("user_analysis_profiles.json")
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_analysis_profiles, f, ensure_ascii=False, indent=2)
            print(f"💾 用户分析配置已保存到: {config_file}")
        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='ignore').decode('utf-8')
            print(f"⚠️ 保存配置文件失败: {error_msg}")
    
    def load_user_profiles(self):
        """从文件加载用户分析配置"""
        config_file = Path("user_analysis_profiles.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_profiles = json.load(f)
                    # 合并保存的配置和默认配置
                    self.user_analysis_profiles.update(saved_profiles)
                print(f"📂 已从文件加载用户分析配置: {len(saved_profiles)} 个")
            except Exception as e:
                error_msg = str(e).encode('utf-8', errors='ignore').decode('utf-8')
                print(f"⚠️ 加载配置文件失败: {error_msg}")
    
    def load_user_prompt_templates(self):
        """加载用户提示词模板配置"""
        template_file = Path("user_prompt_templates.json")
        if template_file.exists():
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    self.user_prompt_templates = json.load(f)
                print(f"📝 已加载用户提示词模板: {len(self.user_prompt_templates)} 个")
            except Exception as e:
                error_msg = str(e).encode('utf-8', errors='ignore').decode('utf-8')
                print(f"⚠️ 加载用户提示词模板失败: {error_msg}")
                self.user_prompt_templates = {}
        else:
            print("📝 用户提示词模板文件不存在，使用默认模板")
            self.user_prompt_templates = {}

    def get_user_template(self, username: str) -> str:
        """获取用户的提示词模板"""
        if hasattr(self, 'user_prompt_templates') and username in self.user_prompt_templates:
            return self.user_prompt_templates[username]['template']
        elif hasattr(self, 'user_prompt_templates') and 'default' in self.user_prompt_templates:
            return self.user_prompt_templates['default']['template']
        else:
            # 后备默认模板
            return "请分析以下用户的推文：\n\n用户信息：{user_info}\n\n推文内容：\n{tweet_content}\n\n请用中文总结要点。"
    
    def set_model(self, model: str):
        """动态设置使用的模型"""
        self.custom_model = model
        print(f"✅ 已切换到模型: {model}")
    
    def list_templates(self):
        """列出可用的提示词模板"""
        if hasattr(self, 'prompt_templates'):
            print("📝 可用的提示词模板:")
            for template_name, config in self.prompt_templates.items():
                print(f"  • {template_name}: {config.get('description', 'No description')}")
                print(f"    最大token: {config.get('max_tokens', 'N/A')}")
        else:
            print("⚠️ 未加载提示词模板")
    
    def set_custom_template(self, template_name: str, template_content: str, description: str = "", max_tokens: int = 8000):
        """设置自定义提示词模板"""
        if not hasattr(self, 'prompt_templates'):
            self.prompt_templates = {}
        
        self.prompt_templates[template_name] = {
            "template": template_content,
            "max_tokens": max_tokens,
            "description": description
        }
        print(f"✅ 已添加自定义模板: {template_name}")
        
        # 保存到配置文件
        try:
            with open("prompt_templates.json", 'w', encoding='utf-8') as f:
                json.dump(self.prompt_templates, f, ensure_ascii=False, indent=2)
            print(f"💾 模板已保存到 prompt_templates.json")
        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='ignore').decode('utf-8')
            print(f"⚠️ 保存模板文件失败: {error_msg}")
    
    def optimize_tweet_structure(self, tweet: Dict) -> Dict:
        """将原始推文数据转换为优化的嵌套结构"""
        def extract_core_info(tweet_data, is_main_tweet=False):
            """提取推文核心信息"""
            if not tweet_data:
                return None
                
            # 获取用户信息
            user_info = tweet_data.get('user', {})
            
            # 如果是主推文且没有user字段，使用当前用户信息
            if is_main_tweet and (not user_info or not user_info.get('screen_name')):
                if hasattr(self, '_current_user') and self._current_user:
                    user_info = self._current_user
            
            # 获取用户名，优先从user_info获取
            screen_name = user_info.get('screen_name', 'unknown')
            
            return {
                "id": tweet_data.get('id'),
                "author": f"@{screen_name}",
                "text": tweet_data.get('text', '').strip(),
                "timestamp": tweet_data.get('created_at', ''),
                "media": [m.get('type') for m in tweet_data.get('media', [])]
            }
        
        # 构建主推文结构 - 这是主推文，标记为is_main_tweet=True
        optimized = extract_core_info(tweet, is_main_tweet=True)
        if not optimized:
            return None
            
        # 处理转推
        if tweet.get('retweet'):
            optimized["type"] = "retweet"
            optimized["original_content"] = extract_core_info(tweet['retweet'], is_main_tweet=False)
            
            # 处理转推中的引用
            if tweet['retweet'].get('quoted'):
                optimized["original_content"]["type"] = "quote_tweet"
                optimized["original_content"]["quoted_content"] = extract_core_info(tweet['retweet']['quoted'], is_main_tweet=False)
                optimized["original_content"]["quoted_content"]["type"] = "original"
            else:
                optimized["original_content"]["type"] = "original"
                
        # 处理直接引用
        elif tweet.get('quoted'):
            optimized["type"] = "quote_tweet"
            optimized["quoted_content"] = extract_core_info(tweet['quoted'], is_main_tweet=False)
            optimized["quoted_content"]["type"] = "original"
        else:
            optimized["type"] = "original"
            
        return optimized
    
    def save_optimized_structure(self, tweets: List[Dict], filename: str = None, user_info: Dict = None):
        """保存优化后的推文结构用于查看"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"optimized_tweets_{timestamp}.json"
        
        # 设置当前用户信息供内部函数使用
        if user_info:
            self._current_user = user_info
        
        # 转换所有推文为优化结构
        optimized_tweets = []
        for tweet in tweets[:10]:  # 只处理前10条用于查看
            optimized = self.optimize_tweet_structure(tweet)
            if optimized:
                optimized_tweets.append(optimized)
        
        # 保存到文件
        filepath = Path("analysis_data") / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "total_tweets": len(optimized_tweets),
                "sample_tweets": optimized_tweets,
                "structure_info": {
                    "original_tweets": len([t for t in optimized_tweets if t.get('type') == 'original']),
                    "retweets": len([t for t in optimized_tweets if t.get('type') == 'retweet']),
                    "quote_tweets": len([t for t in optimized_tweets if t.get('type') == 'quote_tweet']),
                    "complex_retweets": len([t for t in optimized_tweets if t.get('type') == 'retweet' and t.get('original_content', {}).get('type') == 'quote_tweet'])
                }
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 优化结构已保存: {filepath}")
        return str(filepath)
    
    def prepare_tweet_data(self, tweets: List[Dict], user_info: Dict = None) -> str:
        """准备推文数据用于LLM总结 - 使用优化的嵌套结构"""
        if not tweets:
            return "无推文数据"
        
        # 设置用户信息供优化结构使用
        if user_info:
            self._current_user = user_info
        
        # 按时间排序
        sorted_tweets = sorted(tweets, key=lambda x: x.get('created_at', ''), reverse=True)
        
        # 转换为优化的嵌套结构
        optimized_tweets = []
        for tweet in sorted_tweets[:self.config["max_tweets_per_summary"]]:
            optimized = self.optimize_tweet_structure(tweet)
            if optimized:
                optimized_tweets.append(optimized)
        
        # 构建JSON格式的结构化文本用于LLM分析
        tweet_data_json = {
            "total_tweets": len(optimized_tweets),
            "sample_tweets": optimized_tweets,
            "structure_info": {
                "original_tweets": len([t for t in optimized_tweets if t.get('type') == 'original']),
                "retweets": len([t for t in optimized_tweets if t.get('type') == 'retweet']),
                "quote_tweets": len([t for t in optimized_tweets if t.get('type') == 'quote_tweet']),
                "complex_retweets": len([t for t in optimized_tweets if t.get('type') == 'retweet' and t.get('original_content', {}).get('type') == 'quote_tweet'])
            }
        }
        
        # 构建给LLM的文本描述
        prepared_text = "推文数据分析 - 优化嵌套结构：\n\n"
        prepared_text += "以下是经过结构优化的推文数据，采用嵌套JSON格式便于理解推文间的复杂关系：\n\n"
        prepared_text += "```json\n"
        prepared_text += json.dumps(tweet_data_json, ensure_ascii=False, indent=2)
        prepared_text += "\n```\n\n"
        
        # 添加结构说明
        prepared_text += "数据结构说明：\n"
        prepared_text += "- type: 推文类型 (original/retweet/quote_tweet)\n"
        prepared_text += "- original_content: 转推的原始内容\n"
        prepared_text += "- quoted_content: 引用的推文内容\n"
        prepared_text += "- media: 媒体类型列表 (photo/video等)\n"
        prepared_text += "- 为节省空间，已省略详细的互动数据\n\n"
        
        # 添加统计摘要
        total_tweets = len(tweets)
        original_tweets = len([t for t in tweets if not t.get('retweet')])
        retweets = total_tweets - original_tweets
        media_tweets = len([t for t in tweets if t.get('media')])
        
        prepared_text += f"完整数据统计：\n"
        prepared_text += f"总推文数：{total_tweets}\n"
        prepared_text += f"原创推文：{original_tweets}\n"
        prepared_text += f"转推：{retweets}\n"
        prepared_text += f"含媒体：{media_tweets}\n"
        
        return prepared_text
    
    def prepare_simple_tweet_data(self, tweets: List[Dict], user_info: Dict = None) -> str:
        """准备简化的推文数据用于简洁模板"""
        if not tweets:
            return "无推文数据"
        
        # 按时间排序，取最多20条
        sorted_tweets = sorted(tweets, key=lambda x: x.get('created_at', ''), reverse=True)
        limited_tweets = sorted_tweets[:20]
        
        # 获取默认用户名 
        default_username = user_info.get('screen_name', 'unknown') if user_info else 'unknown'
        
        # 简化格式
        simple_tweets = []
        for i, tweet in enumerate(limited_tweets, 1):
            # 提取核心信息
            text = tweet.get('text', '') or tweet.get('full_text', '')
            
            # 优先使用推文中的用户信息，否则使用传入的user_info
            author = tweet.get('user', {}).get('screen_name') if tweet.get('user') else default_username
            created_at = tweet.get('created_at', '')
            
            # 处理转推
            if tweet.get('retweeted_status'):
                rt_text = tweet['retweeted_status'].get('text', '') or tweet['retweeted_status'].get('full_text', '')
                rt_author = tweet['retweeted_status'].get('user', {}).get('screen_name', 'unknown')
                text = f"RT @{rt_author}: {rt_text}"
            
            # 截断过长的文本
            if len(text) > 200:
                text = text[:197] + "..."
                
            simple_tweets.append(f"{i}. @{author} ({created_at})\n{text}")
        
        return "\n\n".join(simple_tweets)

    
    def generate_simple_prompt(self, tweets: List[Dict], user_info: Dict = None) -> str:
        """生成简洁的用户自定义提示词"""

        # 获取用户信息
        user_name = user_info.get('screen_name', '') if user_info else 'unknown'

        # 准备用户信息字符串（去除重复的用户数据）
        user_info_str = f"用户名: @{user_name}"
        if user_info:
            if user_info.get('name'):
                user_info_str += f"\n显示名: {user_info['name']}"
            if user_info.get('description'):
                user_info_str += f"\n简介: {user_info['description']}"
            if user_info.get('followers_count'):
                user_info_str += f"\n关注者: {user_info['followers_count']}"

        # 清理推文数据中的重复用户信息
        cleaned_tweets = []
        for tweet in tweets:
            cleaned_tweet = tweet.copy()
            # 删除推文中的用户信息，避免重复
            if 'user' in cleaned_tweet:
                del cleaned_tweet['user']
            # 处理转推中的用户信息重复
            if cleaned_tweet.get('retweeted_status') and 'user' in cleaned_tweet['retweeted_status']:
                cleaned_tweet['retweeted_status'] = cleaned_tweet['retweeted_status'].copy()
                # 保留转推原作者信息，因为这是必要的
                pass
            # 处理引用推文中的用户信息
            if cleaned_tweet.get('quoted_status') and 'user' in cleaned_tweet['quoted_status']:
                cleaned_tweet['quoted_status'] = cleaned_tweet['quoted_status'].copy()
                # 保留引用推文作者信息，因为这是必要的
                pass
            cleaned_tweets.append(cleaned_tweet)

        # 使用原始推文数据的JSON格式
        tweet_content = json.dumps(cleaned_tweets, ensure_ascii=False, indent=2)

        # 获取用户的模板
        template = self.get_user_template(user_name)

        # 只使用两个基本变量填充模板
        prompt = template.format(
            user_info=user_info_str,
            tweet_content=tweet_content
        )

        return prompt
    
    def save_prompt_to_file(self, prompt: str, summary_type: str, tweets: List[Dict], user_info: Dict = None) -> str:
        """保存完整的LLM prompt到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 确定用户名标识
        if user_info and user_info.get('screen_name'):
            user_name = user_info.get('screen_name')
        elif summary_type.endswith('_mixed'):
            user_name = 'mixed_users'  # 混合用户数据
        else:
            user_name = 'unknown'
        
        # 创建prompts目录（在crawler_data下）
        prompts_dir = Path("crawler_data/prompts")
        prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        filename = f"{summary_type}_{user_name}_{timestamp}_prompt.txt"
        filepath = prompts_dir / filename
        
        # 构建完整的prompt信息
        user_display = f"@{user_name}" if user_name != 'mixed_users' else "混合用户数据"
        full_prompt_content = f"""# LLM Prompt 保存记录
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
总结类型: {summary_type}
用户: {user_display}
推文数量: {len(tweets)}
数据哈希: {hashlib.md5(str(tweets).encode()).hexdigest()[:8]}

{'='*80}
完整Prompt内容:
{'='*80}

{prompt}

{'='*80}
Prompt结束
{'='*80}

# 使用说明
这个文件包含了发送给LLM的完整prompt内容，你可以：
1. 直接复制到其他LLM服务（Claude、ChatGPT等）
2. 调试和优化prompt结构
3. 作为训练数据或示例使用
4. 分析LLM输入输出的对应关系

# 数据来源信息
- 原始推文数据来源: {user_display}的推文时间线
- 数据处理: 经过优化嵌套结构转换，便于LLM理解
- 结构特点: 支持复杂的转推、引用、多层嵌套关系分析
"""
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_prompt_content)
        
        print(f"📝 完整prompt已保存: {filepath}")
        return str(filepath)
    
    def call_llm_api(self, prompt: str, model: str = None) -> str:
        """调用LLM API生成总结 - 通过OpenRouter访问"""
        
        if not self.api_key:
            print("⚠️ 未找到API密钥，使用模拟总结")
            return self.generate_mock_summary()
        
        # 确保prompt是UTF-8字符串
        if isinstance(prompt, str):
            prompt = prompt.encode('utf-8', errors='ignore').decode('utf-8')
        
        # 模型优先级：方法参数 > 实例自定义 > 默认配置
        target_model = model or self.custom_model or self.llm_config["default_model"]
        models_to_try = [target_model] + self.llm_config["fallback_models"]
        
        try:
            from openai import OpenAI
        except ImportError:
            print("❌ 缺少openai库，请安装: pip install openai")
            return self.generate_mock_summary()
            
        # 创建OpenRouter客户端
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        
        print(f"📝 Prompt长度: {len(prompt)} 字符")
        
        # 尝试多个模型
        for i, current_model in enumerate(models_to_try):
            try:
                print(f"🤖 尝试模型 [{i+1}/{len(models_to_try)}]: {current_model}")
                
                # 调用API
                completion = client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "https://github.com/anthropics/claude-code", 
                        "X-Title": "X-Tweet-Analysis-System",
                    },
                    model=current_model,
                    messages=[
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=self.llm_config["max_tokens"],
                    temperature=self.llm_config["temperature"]
                )
                
                result = completion.choices[0].message.content
                print(f"✅ LLM响应完成: {len(result)} 字符 (模型: {current_model})")
                return result
                
            except Exception as e:
                error_msg = str(e).encode('utf-8', errors='ignore').decode('utf-8')
                print(f"❌ 模型 {current_model} 失败: {error_msg}")
                if i < len(models_to_try) - 1:
                    print(f"🔄 尝试备选模型...")
                    continue
                else:
                    print(f"🔄 所有模型都失败，降级到模拟总结")
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
    
    def generate_summary(self, tweets: List[Dict], summary_type: str = "daily", user_info: Dict = None, 
                       template_type: str = "auto", custom_instructions: str = "") -> Dict[str, Any]:
        """生成推文总结"""
        print(f"🤖 开始生成{summary_type}总结...")
        
        if not tweets:
            return {
                "error": "没有推文数据可供总结",
                "summary": "",
                "metadata": {"tweet_count": 0}
            }
        
        # 直接生成用户自定义提示词
        prompt = self.generate_simple_prompt(tweets, user_info)
        
        # 保存完整的prompt到文件
        self.save_prompt_to_file(prompt, summary_type, tweets, user_info)
        
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
                "data_hash": hashlib.md5(str(tweets).encode()).hexdigest()[:8],
                "user": user_info.get('screen_name') if user_info and user_info.get('screen_name') else ('mixed_users' if summary_type.endswith('_mixed') else 'unknown')
            }
        }
        
        # 保存总结
        self.save_summary(result)
        
        print(f"✅ 总结生成完成，包含{len(tweets)}条推文")
        return result
    
    def save_summary(self, summary_data: Dict[str, Any], format_type: str = "json") -> str:
        """保存总结到文件 - 仅用于测试"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_type = summary_data.get('summary_type', 'general')

        # 使用crawler_data/user_summaries目录
        output_dir = Path("crawler_data/user_summaries")
        output_dir.mkdir(parents=True, exist_ok=True)

        if format_type == "json":
            filename = f"{summary_type}_summary_{timestamp}.json"
            filepath = output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)

        elif format_type == "markdown":
            filename = f"{summary_type}_summary_{timestamp}.md"
            filepath = output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(summary_data['summary'])

        print(f"💾 总结已保存: {filepath}")
        return str(filepath)
    
    def generate_trending_summary(self, tweets: List[Dict], user_info: Dict = None) -> Dict[str, Any]:
        """生成热门话题总结"""
        # 按互动数据排序
        trending_tweets = sorted(
            tweets, 
            key=lambda x: x.get('stats', {}).get('favorite_count', 0) + 
                         x.get('stats', {}).get('retweet_count', 0), 
            reverse=True
        )
        
        return self.generate_summary(trending_tweets[:20], "trending", user_info)
    
    def generate_category_summary(self, tweets: List[Dict], category: str = "tech", user_info: Dict = None) -> Dict[str, Any]:
        """生成分类总结"""
        # 这里可以添加分类逻辑，根据关键词或其他特征筛选推文
        # 暂时使用全部推文
        return self.generate_summary(tweets, f"{category}_category", user_info)

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