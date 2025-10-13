# GitHub Actions Workflows

本目录包含项目的所有 GitHub Actions 工作流配置。

---

## 📋 Workflow 文件列表

### 1. `daily-crawler.yml` - 主工作流 ⭐

**功能:**
- 定时任务：每天北京时间 09:00 自动运行
- 爬取 X 推文数据
- 生成 LLM 智能总结
- 自动提交数据到仓库
- 失败时自动通知

**触发方式:**
- 定时：`0 1 * * *` (UTC 01:00 / 北京 09:00)
- 手动：Actions → Daily X Crawler → Run workflow

**参数:**
- `tweet_count`: 爬取数量（默认 500）
- `force_summary`: 强制重新生成总结（true/false）

**输出:**
- `crawler_data/daily_posts/` - 每日推文数据
- `crawler_data/users_daily/` - 按用户分组的推文
- `crawler_data/user_summaries/` - LLM 生成的总结
- `report.md` - 运行报告

---

### 2. `manual-summary.yml` - 手动总结工具

**功能:**
- 为历史数据生成总结
- 支持指定日期
- 强制覆盖已有总结

**触发方式:**
- 仅手动触发

**参数:**
- `date`: 日期（YYYYMMDD 格式，留空表示昨天）
- `force`: 强制覆盖（true/false）

**使用场景:**
- 补充历史数据总结
- 重新生成不满意的总结
- 测试新的提示词模板

---

### 3. `notifications.yml` - 通知示例（不运行）

**功能:**
- 展示多种通知方式的示例代码
- 包含 8 种通知方案

**说明:**
- 此文件仅作为参考，不会自动运行
- 实际通知配置已集成到 `daily-crawler.yml` 中

---

## 🚀 快速开始

### 首次使用

1. **配置 Secrets**
   ```
   Settings → Secrets and variables → Actions
   ```
   需要添加的 Secrets:
   - `X_AUTH_TOKEN`
   - `X_CT0_TOKEN`
   - `X_CSRF_TOKEN`
   - `X_BEARER_TOKEN`
   - `OPENROUTER_API_KEY`
   - `OPENAI_MODEL`

2. **启用 Actions 权限**
   ```
   Settings → Actions → General
   → Workflow permissions
   → 选择 "Read and write permissions"
   ```

3. **测试运行**
   ```
   Actions → Daily X Crawler → Run workflow
   ```

### 本地验证

在推送前验证 workflow 语法：

```bash
# 运行验证脚本
./scripts/validate-workflows.sh

# 或安装 actionlint
brew install actionlint
actionlint .github/workflows/*.yml
```

---

## 📊 运行监控

### 查看运行历史

```
仓库首页 → Actions 标签 → 选择 workflow
```

### 下载运行报告

```
Actions → 选择具体运行 → Artifacts → 下载 crawler-report
```

### 查看失败通知

失败时会：
1. 自动创建 GitHub Issue（含详细诊断信息）
2. 发送 Telegram 通知（如已配置）
3. 发送企业微信/钉钉通知（如已配置）

---

## ⚙️ 自定义配置

### 修改运行时间

编辑 `daily-crawler.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 13 * * *'  # 改为每天 21:00 北京时间
```

**常用时间：**
| 北京时间 | Cron 表达式 |
|---------|-----------|
| 06:00 | `0 22 * * *` |
| 09:00 | `0 1 * * *` |
| 12:00 | `0 4 * * *` |
| 18:00 | `0 10 * * *` |
| 21:00 | `0 13 * * *` |

**工具:** https://crontab.guru/

### 修改爬取数量

方法 1：手动触发时指定
```
Actions → Run workflow → tweet_count: 1000
```

方法 2：修改默认值
```yaml
inputs:
  tweet_count:
    default: '1000'  # 改为 1000
```

### 添加通知渠道

参考 `notifications.yml` 中的示例，复制相应代码到 `daily-crawler.yml`。

---

## 🐛 故障排查

### 常见问题

#### 1. Workflow 不运行

**检查项:**
- [ ] Actions 是否启用（Settings → Actions）
- [ ] Workflow 文件语法是否正确
- [ ] 定时任务可能延迟 5-15 分钟

**解决:**
```bash
# 本地验证语法
./scripts/validate-workflows.sh
```

#### 2. 认证失败

**症状:** `401 Unauthorized` 或 `403 Forbidden`

**原因:** X 认证 token 过期

**解决:**
1. 重新登录 X 平台
2. 提取新的认证信息
3. 更新 GitHub Secrets

#### 3. 数据未提交

**检查项:**
- [ ] Workflow permissions 是否为 Read and write
- [ ] 是否有新数据生成
- [ ] Git 配置是否正确

#### 4. LLM 总结失败

**检查项:**
- [ ] `OPENROUTER_API_KEY` 是否有效
- [ ] API 余额是否充足
- [ ] 模型名称是否正确

---

## 📚 相关文档

- [GITHUB_DEPLOYMENT.md](../../docs/GITHUB_DEPLOYMENT.md) - 完整部署指南
- [GITHUB_ACTIONS_BEST_PRACTICES.md](../../docs/GITHUB_ACTIONS_BEST_PRACTICES.md) - 最佳实践
- [NOTIFICATION_SETUP.md](../../docs/NOTIFICATION_SETUP.md) - 通知配置详解

---

## 🔒 安全说明

### Secrets 保护

- ✅ 所有敏感信息都存储在 GitHub Secrets 中
- ✅ Fork PR 无法访问 Secrets
- ✅ Secrets 在日志中自动隐藏
- ⚠️ 不要在代码中硬编码任何敏感信息

### 权限控制

- ✅ 只授予必需的最小权限
- ✅ 定期审查协作者列表
- ✅ 定期轮换 Secrets

### 审计

```
Settings → Audit log
```
查看所有 Actions 相关操作记录。

---

## 💡 提示

### 减少运行时间

```yaml
# 减少爬取数量
python run_crawler.py --count 200

# 减少运行频率
schedule:
  - cron: '0 1 * * 1,3,5'  # 只在周一、三、五
```

### 测试新功能

使用 `workflow_dispatch` 手动触发，避免影响定时任务：

```yaml
on:
  workflow_dispatch:
    inputs:
      test_mode:
        description: '测试模式'
        type: boolean
```

### 调试技巧

```yaml
# 添加调试步骤
- name: Debug info
  run: |
    echo "Event: ${{ github.event_name }}"
    echo "Ref: ${{ github.ref }}"
    echo "Actor: ${{ github.actor }}"
    ls -la crawler_data/
```

---

## 🎯 最佳实践清单

部署前检查：

- [ ] 所有必需的 Secrets 已配置
- [ ] Workflow 语法验证通过
- [ ] 手动测试运行成功
- [ ] 权限配置正确
- [ ] 通知渠道已测试（可选）
- [ ] 定时任务时间正确
- [ ] `.gitignore` 配置正确
- [ ] 文档已更新

---

*最后更新: 2025-10-10*
*如有问题，请参考完整文档或创建 Issue*
