# Prompt 优化指南

## 📊 对比

### 优化前（冗长版）
- 长度：66行，4.2KB
- 结构：一、二、三、四（学术报告风格）
- 问题：重复内容多，客套话多，不够直接

### 优化后（极简版）✨
- 长度：预计10-15行，~1KB
- 结构：bullet points
- 优点：直击要点，快速浏览

## 🎯 当前配置（极简版）

已应用到 `user_prompt_templates.json`

### elonmusk
```
输出示例：
• Grok 4.1发布 - LMArena排名第一，速度和质量大幅提升
• SpaceX完成第500次火箭复用飞行
• 调侃Bezos新AI项目"抄袭"
```

### dotey
```
输出示例：
• 新工具/技术：Claude Code新功能演示
• 值得关注的观点：AI工作流应该注重迭代速度而非完美
• 实践经验：使用Cursor提升开发效率的5个技巧
```

## 🔄 如何切换版本

### 切换到详细版
```bash
# 备份当前极简版
mv user_prompt_templates.json user_prompt_templates_minimal.json

# 使用详细版
mv user_prompt_templates_detailed.json user_prompt_templates.json
```

### 切换回极简版
```bash
# 恢复极简版
mv user_prompt_templates_minimal.json user_prompt_templates.json
```

## ✏️ 自定义Prompt

### 添加新用户
编辑 `user_prompt_templates.json`：

```json
{
  "your_username": {
    "template": "你的prompt模板\n\n推文数据：\n```json\n{tweet_content}\n```\n\n你的要求...",
    "description": "描述"
  }
}
```

### Prompt变量
可用变量：
- `{user_info}` - 用户信息（用户名、简介等）
- `{tweet_content}` - 推文JSON数据

### 优化技巧

1. **控制长度**
   ```
   ❌ 请详细分析...
   ✅ 只列出3-5个要点，每条不超过2行
   ```

2. **明确格式**
   ```
   ❌ 请总结内容
   ✅ 用bullet points列出要点
   ```

3. **去除冗余**
   ```
   ❌ 请用中文生成分析报告，包括...
   ✅ 直接给出要点，不要客套话和总结
   ```

4. **针对性指令**
   ```
   针对技术博主：
   • 新工具/技术：
   • 实践经验：

   针对创业者：
   • 核心观点：
   • 可行建议：
   ```

## 🧪 测试新Prompt

测试单个用户的总结：
```bash
# 只生成一个用户的总结（用于测试）
python run_crawler.py --user-summaries --force
```

查看生成的总结：
```bash
# 查看最新总结
ls -lt crawler_data/user_summaries/*.md | head -1
cat $(ls -t crawler_data/user_summaries/*.md | head -1)
```

## 💡 Prompt最佳实践

### 极简版（快速浏览）
适合：日常快速了解动态
```
• 要点1
• 要点2
• 要点3
```

### 结构化简洁版（平衡）
适合：需要一定分类但不要太长
```
## 核心动态
- 要点1
- 要点2

## 值得关注
- 细节1
```

### 问答式（学习型）
适合：技术/知识型内容
```
Q: 今天最重要的技术是什么？
A: ...

Q: 有什么实践建议？
A: ...
```

## 📈 效果对比

| 维度 | 冗长版 | 极简版 |
|------|--------|--------|
| 阅读时间 | 3-5分钟 | 30秒 |
| 信息密度 | 低（重复多） | 高 |
| 可扫读性 | 差 | 优秀 |
| 适合场景 | 深度研究 | 日常浏览 |

## 🚀 下次优化方向

1. **添加标签系统**
   ```
   #技术 #产品发布
   • Grok 4.1发布
   ```

2. **重要性标记**
   ```
   🔥 [高优先级] SpaceX里程碑
   💡 [有趣] 调侃竞争对手
   ```

3. **链接提取**
   ```
   • Grok 4.1发布 → [链接]
   ```

---

**当前版本**：极简版 v1.0
**更新时间**：2025-11-19
