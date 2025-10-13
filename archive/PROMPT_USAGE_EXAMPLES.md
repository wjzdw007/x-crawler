# 提示词模板使用指南

## 📝 可用模板

### 1. 简洁版本 (`simple`)
- **用途**：快速总结，适合API token限制场景
- **特点**：极简格式，直接列出推文要点
- **Token消耗**：约 3,000 tokens

### 2. 用户日报简洁版 (`user_daily`)  
- **用途**：日常用户总结，平衡详细度和效率
- **特点**：包含用户信息和关注点，保持简洁
- **Token消耗**：约 8,000 tokens

### 3. 用户日报详细版 (`user_daily_detailed`)
- **用途**：深度分析，包含完整的分析框架
- **特点**：结构化报告，包含行动建议和价值评级
- **Token消耗**：约 15,000 tokens

### 4. 自定义模板 (`custom`)
- **用途**：根据特定需求定制分析角度
- **特点**：支持自定义指令和分析重点
- **Token消耗**：约 10,000 tokens

## 🔧 使用方法

### 1. 基本使用

```python
from summarizer import TwitterSummarizer

# 初始化
summarizer = TwitterSummarizer()

# 使用简洁模板
result = summarizer.generate_summary(
    tweets=tweet_data,
    summary_type="user_daily",
    user_info={"screen_name": "elonmusk"},
    template_type="simple"  # 指定模板
)
```

### 2. 查看可用模板

```python
# 列出所有可用模板
summarizer.list_templates()
```

### 3. 创建自定义模板

```python
# 添加自定义模板
custom_template = '''
分析用户 @{username} 的推文内容：

## 基础信息
- 用户：{username} ({user_type})
- 分析日期：{date}
- 推文数量：{tweet_count} 条

## 推文内容
{tweets_data}

## 自定义分析要求
{custom_instructions}

请重点关注以下方面：
1. 技术趋势识别
2. 商业机会发现
3. 行业洞察提炼

生成简洁的中文总结。
'''

summarizer.set_custom_template(
    template_name="tech_focused",
    template_content=custom_template,
    description="技术趋势专用模板",
    max_tokens=6000
)
```

### 4. 使用自定义指令

```python
# 使用自定义模板并添加特定指令
result = summarizer.generate_summary(
    tweets=tweet_data,
    summary_type="user_daily", 
    user_info={"screen_name": "elonmusk"},
    template_type="custom",
    custom_instructions="重点关注AI和自动驾驶相关内容，忽略政治话题"
)
```

## 📊 模板对比

| 模板 | 长度 | 详细程度 | 适用场景 | Token消耗 |
|------|------|----------|----------|----------|
| simple | 极简 | ⭐ | API限制、快速浏览 | 3K |
| user_daily | 中等 | ⭐⭐⭐ | 日常总结 | 8K |
| user_daily_detailed | 详细 | ⭐⭐⭐⭐⭐ | 深度分析 | 15K |
| custom | 可变 | 自定义 | 特定需求 | 可调 |

## 💡 最佳实践

1. **根据用途选择模板**：
   - 快速浏览 → `simple`
   - 日常总结 → `user_daily`
   - 深度分析 → `user_daily_detailed`

2. **Token优化**：
   - API有限制时使用简洁模板
   - 批量处理时优先考虑效率

3. **自定义模板**：
   - 针对特定用户或场景创建专用模板
   - 使用变量占位符保持灵活性

4. **用户配置**：
   - 确保用户信息正确，影响个性化分析
   - 关键词和分析角度要与实际需求匹配

## 📁 文件结构

```
项目根目录/
├── prompt_templates.json      # 模板配置文件
├── user_analysis_profiles.json # 用户分析配置
├── prompts/                   # 生成的prompt文件
└── summaries/                 # 生成的总结文件
```

## 🔄 更新模板

修改 `prompt_templates.json` 文件后会自动加载新配置，或者通过代码动态添加：

```python
# 重新加载模板
summarizer.load_prompt_templates()

# 检查加载状态
summarizer.list_templates()
```