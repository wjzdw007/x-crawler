# 用户提示词自定义指南

## 🎯 设计理念

系统现在完全简化，只负责提供两个核心数据：
1. **用户信息**：用户名、显示名、简介、关注者数等
2. **推文内容**：包含完整的转推、引用推文信息，按时间排序

提示词完全由配置文件决定，用户可以完全自定义分析角度和输出格式。

## 📁 配置文件

### 主配置文件：`user_prompt_templates.json`

```json
{
  "用户名": {
    "template": "提示词模板内容，支持 {user_info} 和 {tweet_content} 两个变量",
    "description": "模板描述"
  }
}
```

### 可用变量

模板中只有两个变量：

1. **{user_info}** - 用户信息字符串，包含：
   - 用户名: @username
   - 显示名: Display Name
   - 简介: User Bio
   - 关注者: 123456

2. **{tweet_content}** - 完整的推文内容，包含：
   - 推文ID和时间
   - 完整的转推信息（包含原作者和时间）
   - 嵌套的引用推文（转推的引用推文）
   - 媒体类型标识

## 📊 推文数据格式

系统直接使用爬虫的原始JSON数据，避免重复处理。数据结构包含：

### 基本推文字段
```json
{
  "id": "1234567890",
  "text": "推文内容",
  "created_at": "时间戳",
  "lang": "语言代码",
  "media": [{"type": "photo"}],
  "stats": {"retweet_count": 100, "favorite_count": 500}
}
```

### 转推结构
```json
{
  "id": "1234567891",
  "text": "RT @original: ...",
  "retweeted_status": {
    "id": "1234567888",
    "text": "原推文内容",
    "user": {"screen_name": "original", "name": "Original Author"},
    "created_at": "时间戳"
  }
}
```

### 引用推文结构
```json
{
  "id": "1234567892",
  "text": "评论内容",
  "quoted_status": {
    "id": "1234567889",
    "text": "被引用的推文内容",
    "user": {"screen_name": "quoted_author"},
    "created_at": "时间戳"
  }
}
```

## 🛠️ 自定义模板示例

### 1. 商业分析模板（适合企业家、投资人）
```json
"elonmusk": {
  "template": "请分析以下推文，重点关注商业机会和技术趋势：\n\n用户信息：{user_info}\n\n推文内容：\n{tweet_content}\n\n请提供：\n1. 主要观点总结\n2. 商业机会识别\n3. 技术趋势分析\n4. 投资启示",
  "description": "商业投资分析"
}
```

### 2. 技术学习模板（适合开发者、技术爱好者）
```json
"dotey": {
  "template": "分析这位技术专家的分享内容：\n\n{user_info}\n\n{tweet_content}\n\n请整理：\n- 技术要点\n- 工具推荐\n- 学习资源\n- 实践建议",
  "description": "技术学习资源"
}
```

### 3. 极简模板（适合快速浏览）
```json
"anyone": {
  "template": "简洁总结：\n\n用户：{user_info}\n内容：{tweet_content}\n\n用3句话概括要点。",
  "description": "极简总结"
}
```

### 4. 深度分析模板（适合研究、分析）
```json
"researcher": {
  "template": "深度分析推文数据：\n\n## 用户背景\n{user_info}\n\n## 推文数据\n```json\n{tweet_content}\n```\n\n## 分析维度\n1. 内容主题分类\n2. 观点立场分析\n3. 信息可信度评估\n4. 社会影响预测\n5. 相关领域连接\n\n要求：客观、专业、深入",
  "description": "学术研究分析"
}
```

## 🚀 使用方式

### 1. 编辑配置文件
编辑 `user_prompt_templates.json`，为不同用户设置不同的分析模板。

### 2. 运行系统
```bash
# 激活虚拟环境
source venv/bin/activate

# 生成用户总结（使用配置文件中的模板）
python run_crawler.py --user-summaries

# 强制覆盖现有总结
python run_crawler.py --user-summaries --force
```

### 3. 查看结果
- **Prompt 文件**：`prompts/` 目录下查看完整的提示词
- **总结文件**：`crawler_data/user_summaries/` 目录下查看生成的总结

## 💡 最佳实践

### 1. 模板设计原则
- **明确目标**：每个模板都应该有清晰的分析目标
- **简洁有效**：避免过于复杂的提示词
- **结构化输出**：使用编号、标题等结构化元素
- **灵活适配**：考虑不同长度和类型的推文内容

### 2. 用户分类建议
- **商业类**：企业家、投资人、行业专家
- **技术类**：开发者、研究员、技术博主
- **内容类**：媒体人、作家、评论家
- **通用类**：普通用户、个人博主

### 3. 提示词优化技巧
- **具体指令**：使用具体的动词和要求
- **输出格式**：明确指定输出的结构和格式
- **重点突出**：强调需要特别关注的内容
- **语言风格**：指定使用的语言和风格

## 📋 模板变量详细说明

### {user_info} 包含的信息：
```
用户名: @actual_username
显示名: User Display Name
简介: User bio description
关注者: 1234567
```

### {tweet_content} 的结构：
- 每条推文独立编号
- 包含推文ID、时间戳
- 完整的转推链条信息
- 媒体内容类型标识
- 按时间倒序排列（最新的在前）

## 🎯 系统优势

1. **完全自定义**：用户可以完全控制分析角度和输出格式
2. **数据完整**：系统确保推文内容的完整性，包括复杂的转推结构
3. **简洁高效**：只有两个变量，易于理解和使用
4. **灵活扩展**：可以为不同用户类型创建专门的分析模板

现在你可以完全自定义提示词，系统只负责提供干净、完整的数据！