# GitHub Actions 部署指南

## 📋 部署步骤

### 1. 配置 GitHub Secrets

在你的 GitHub 仓库中设置以下 Secrets:

**路径**: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

#### 必需的 Secrets:

| Secret 名称 | 说明 | 获取方式 |
|------------|------|---------|
| `X_AUTH_TOKEN` | X平台认证令牌 | 浏览器登录 X 后从 Cookie 提取 `auth_token` |
| `X_CT0_TOKEN` | X平台 CT0 令牌 | 浏览器 Cookie 中的 `ct0` |
| `X_CSRF_TOKEN` | X平台 CSRF 令牌 | 可选，部分接口需要 |
| `X_BEARER_TOKEN` | X平台 Bearer Token | 从网络请求头提取 `Authorization` |
| `OPENROUTER_API_KEY` | OpenRouter API 密钥 | https://openrouter.ai/keys |
| `OPENAI_MODEL` | 使用的模型名称 | 例如: `openai/gpt-4o-mini` |

#### 可选的 Secrets:

| Secret 名称 | 说明 |
|------------|------|
| `HTTP_PROXY` | HTTP 代理地址 (如需要) |
| `HTTPS_PROXY` | HTTPS 代理地址 (如需要) |
| `SLACK_WEBHOOK` | Slack 通知 Webhook (失败通知) |

---

### 2. 提取 X 平台认证信息

**方法 1: 使用项目自带工具**

```bash
python auth_setup.py
```

这会自动打开浏览器并提取认证信息到 `.env` 文件，然后手动将这些值添加到 GitHub Secrets。

**方法 2: 手动提取**

1. 在浏览器中登录 https://x.com
2. 打开开发者工具 (F12)
3. 进入 `Application` → `Cookies` → `https://x.com`
4. 复制以下 Cookie 值:
   - `auth_token`
   - `ct0`
5. 进入 `Network` 标签，刷新页面
6. 找到任意 GraphQL 请求，复制请求头中的 `Authorization` 值

---

### 3. 获取 OpenRouter API Key

1. 访问 https://openrouter.ai/
2. 注册/登录账号
3. 前往 https://openrouter.ai/keys
4. 点击 `Create Key` 创建新密钥
5. 复制密钥到 GitHub Secret `OPENROUTER_API_KEY`

**推荐模型** (性价比):
- `openai/gpt-4o-mini` - 便宜高效 ($0.15/1M tokens)
- `anthropic/claude-3-haiku` - 快速准确 ($0.25/1M tokens)

---

### 4. 启用 GitHub Actions

1. 进入仓库 `Settings` → `Actions` → `General`
2. 勾选 `Allow all actions and reusable workflows`
3. 在 `Workflow permissions` 中选择:
   - ✅ `Read and write permissions`
   - ✅ `Allow GitHub Actions to create and approve pull requests`

---

### 5. 测试运行

**手动触发测试:**

1. 进入 `Actions` 标签
2. 选择 `Daily X Crawler` workflow
3. 点击 `Run workflow` → `Run workflow`
4. 可以自定义参数:
   - `tweet_count`: 爬取数量 (默认 500)
   - `force_summary`: 是否强制重新生成总结

**查看运行结果:**

- 实时日志: Actions 运行页面查看
- 数据文件: 自动提交到 `crawler_data/` 目录
- 下载报告: 在 Artifacts 中下载

---

## 🕐 定时任务说明

### 默认计划

```yaml
# 每天北京时间早上 9:00 运行
schedule:
  - cron: '0 1 * * *'  # UTC 01:00
```

### 自定义时间

修改 `.github/workflows/daily-crawler.yml` 中的 cron 表达式:

| 时间 (北京) | Cron 表达式 |
|-----------|-----------|
| 每天 09:00 | `0 1 * * *` |
| 每天 12:00 | `0 4 * * *` |
| 每天 21:00 | `0 13 * * *` |
| 每 6 小时 | `0 */6 * * *` |
| 每周一 09:00 | `0 1 * * 1` |

**注意**: GitHub Actions cron 使用 UTC 时区，北京时间需要 -8 小时。

---

## 📊 Workflows 说明

### 1. Daily X Crawler (主工作流)

**功能:**
- ✅ 定时爬取推文
- ✅ 生成用户总结
- ✅ 自动提交数据
- ✅ 生成运行报告

**触发方式:**
- 定时: 每天北京时间 09:00
- 手动: Actions → Run workflow

### 2. Manual Summary Generator (手动总结)

**功能:**
- ✅ 为历史数据生成总结
- ✅ 指定日期生成
- ✅ 强制覆盖模式

**使用场景:**
- 补充历史数据总结
- 重新生成不满意的总结
- 测试新的提示词模板

---

## 💡 最佳实践

### 1. 数据存储策略

**选项 A: 提交到 Git (小规模数据)**
- ✅ 优点: 简单，自动备份，版本控制
- ❌ 缺点: 仓库体积增长快
- 🎯 适用: 每天 < 100MB 数据

**选项 B: 上传到云存储 (大规模数据)**
- ✅ 优点: 不占用仓库空间
- ❌ 缺点: 需要额外配置
- 🎯 适用: 每天 > 100MB 数据

如需使用云存储，可以添加以下步骤到 workflow:

```yaml
- name: 📤 Upload to S3
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1

- name: 💾 Sync to S3
  run: |
    aws s3 sync crawler_data/ s3://your-bucket/crawler_data/
```

### 2. 成本优化

**免费额度:**
- 公开仓库: **无限制** ✅
- 私有仓库: 2000 分钟/月

**减少运行时间:**
```yaml
# 调整爬取数量
python run_crawler.py --count 200  # 而不是 500

# 减少运行频率
schedule:
  - cron: '0 1 * * 1,3,5'  # 只在周一、三、五运行
```

### 3. 错误处理

**自动重试:**
```yaml
- name: 🕷️ Run crawler
  uses: nick-fields/retry@v2
  with:
    timeout_minutes: 30
    max_attempts: 3
    command: python run_crawler.py --count 500 --user-summaries
```

**失败通知:**
- Slack: 配置 `SLACK_WEBHOOK` Secret
- Email: 在 GitHub Settings → Notifications 配置

---

## 🔍 故障排查

### 问题 1: Secrets 未生效

**检查:**
```bash
# 在 workflow 中添加调试步骤
- name: Debug secrets
  run: |
    echo "AUTH_TOKEN length: ${#X_AUTH_TOKEN}"
    echo "API_KEY set: ${{ secrets.OPENROUTER_API_KEY != '' }}"
```

### 问题 2: 认证失败

**原因:**
- X 认证 token 过期 (通常 30-60 天)
- Cookie 被刷新

**解决:**
1. 重新登录 X
2. 提取新的认证信息
3. 更新 GitHub Secrets

### 问题 3: 超出免费额度

**查看用量:**
- `Settings` → `Billing and plans` → `Plans and usage`

**优化:**
- 减少运行频率
- 降低爬取数量
- 使用 `continue-on-error: true` 避免重复运行

---

## 📚 更多资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Cron 表达式生成器](https://crontab.guru/)
- [OpenRouter API 文档](https://openrouter.ai/docs)

---

## 🎯 快速开始清单

- [ ] 添加所有必需的 GitHub Secrets
- [ ] 启用 Actions 写权限
- [ ] 手动触发测试运行
- [ ] 检查数据是否正确提交
- [ ] 验证定时任务设置
- [ ] (可选) 配置失败通知

**完成后，你的爬虫将每天自动运行！** 🎉
