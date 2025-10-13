# GitHub Actions 完整部署指南

本文档将手把手教你如何将 X Crawler 部署到 GitHub，实现每天自动爬取和总结。

---

## 📋 部署前准备

### 需要准备的账号和资料

- [ ] GitHub 账号
- [ ] X (Twitter) 账号（已登录）
- [ ] OpenRouter API Key（用于 LLM 总结）
- [ ] 浏览器（Chrome/Firefox/Safari）

---

## 🚀 部署步骤

### 第一步：创建 GitHub 仓库

#### 1.1 新建仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   ```
   Repository name: x-crawler
   Description: X (Twitter) 推文爬虫和智能总结系统
   ```
3. 选择可见性：
   - **Public（公开）**: 无限 Actions 时长 ✅ 推荐
   - **Private（私有）**: 每月 2000 分钟免费
4. 不勾选 "Add a README file"（我们已有 README）
5. 点击 **Create repository**

#### 1.2 推送现有代码到 GitHub

```bash
# 在你的项目目录下执行
cd /Users/daweizheng/Desktop/ai/x1/x_crawler

# 初始化 Git（如果还没有）
git init

# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/x-crawler.git

# 添加所有文件
git add .

# 创建首次提交
git commit -m "Initial commit: X Crawler with GitHub Actions"

# 推送到 GitHub
git branch -M main
git push -u origin main
```

**注意**: 将 `YOUR_USERNAME` 替换为你的 GitHub 用户名。

---

### 第二步：提取 X 平台认证信息

#### 2.1 使用自动工具提取（推荐）

```bash
# 在本地运行
python auth_setup.py
```

这会：
1. 自动打开浏览器
2. 引导你登录 X
3. 提取认证信息保存到 `.env`

#### 2.2 手动提取（备选方案）

如果自动工具不工作，可以手动提取：

**步骤：**

1. **打开浏览器开发者工具**
   - Chrome/Edge: 按 `F12` 或 `Cmd+Option+I` (Mac)
   - Firefox: 按 `F12`
   - Safari: `Cmd+Option+I`

2. **登录 X 平台**
   - 访问 https://x.com
   - 登录你的账号

3. **提取 Cookies**
   - 进入开发者工具的 `Application` 标签页（Chrome）或 `Storage` 标签页（Firefox）
   - 左侧选择 `Cookies` → `https://x.com`
   - 找到并复制以下 Cookie 值：

   | Cookie 名称 | 说明 | 示例 |
   |------------|------|------|
   | `auth_token` | 认证令牌 | `a1b2c3d4e5f6...` |
   | `ct0` | CT0 令牌 | `1a2b3c4d5e6f...` |

4. **提取 Bearer Token**
   - 切换到 `Network` 标签页
   - 刷新页面（`F5`）
   - 在列表中找到任意一个 `graphql` 请求
   - 点击该请求，查看 `Headers` 区域
   - 找到 `Request Headers` 中的 `Authorization` 字段
   - 复制完整的值（包括 `Bearer` 前缀）

   示例：
   ```
   Authorization: Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA
   ```

5. **记录所有值**

   将提取的值记录到本地文件（不要提交到 Git）：

   ```
   X_AUTH_TOKEN=你的auth_token值
   X_CT0_TOKEN=你的ct0值
   X_BEARER_TOKEN=你的Bearer Token完整值
   ```

---

### 第三步：获取 OpenRouter API Key

#### 3.1 注册 OpenRouter

1. 访问 https://openrouter.ai/
2. 点击 **Sign In** → 使用 Google/GitHub 登录
3. 首次登录会赠送免费额度

#### 3.2 创建 API Key

1. 登录后访问 https://openrouter.ai/keys
2. 点击 **Create Key**
3. 设置密钥名称（如：`X Crawler`）
4. 复制生成的 API Key（以 `sk-or-v1-` 开头）
5. **重要**: 立即保存，关闭窗口后无法再次查看

#### 3.3 充值（可选）

- 免费额度: $1-5（足够测试）
- 推荐充值: $10-20（可用几个月）
- 充值方式: 信用卡、Crypto

#### 3.4 选择模型

推荐的性价比模型：

| 模型 | 价格 | 速度 | 质量 | 推荐 |
|-----|------|------|------|------|
| `openai/gpt-4o-mini` | $0.15/1M tokens | 快 | 优 | ⭐⭐⭐⭐⭐ |
| `anthropic/claude-3-haiku` | $0.25/1M tokens | 最快 | 优 | ⭐⭐⭐⭐ |
| `google/gemini-flash-1.5` | $0.075/1M tokens | 快 | 良 | ⭐⭐⭐ |
| `openai/gpt-4o` | $2.5/1M tokens | 中 | 极优 | ⭐⭐⭐ |

**推荐**: 使用 `openai/gpt-4o-mini`，性价比最高。

---

### 第四步：配置 GitHub Secrets

现在把所有敏感信息添加到 GitHub Secrets，保证安全。

#### 4.1 进入 Secrets 配置页面

```
你的仓库页面 → Settings → Secrets and variables → Actions
```

#### 4.2 添加必需的 Secrets

点击 **New repository secret**，逐个添加：

| Secret 名称 | 值来源 | 示例 |
|------------|-------|------|
| `X_AUTH_TOKEN` | 第二步提取的 auth_token | `a1b2c3d4e5f6...` |
| `X_CT0_TOKEN` | 第二步提取的 ct0 | `1a2b3c4d5e6f...` |
| `X_CSRF_TOKEN` | 与 ct0 相同 | `1a2b3c4d5e6f...` |
| `X_BEARER_TOKEN` | 第二步提取的 Bearer Token | `Bearer AAAAAAA...` |
| `OPENROUTER_API_KEY` | 第三步获取的 API Key | `sk-or-v1-...` |
| `OPENAI_MODEL` | 模型名称 | `openai/gpt-4o-mini` |

**添加步骤**：
1. 点击 **New repository secret**
2. **Name**: 输入 Secret 名称（如 `X_AUTH_TOKEN`）
3. **Value**: 粘贴对应的值
4. 点击 **Add secret**
5. 重复以上步骤添加所有 Secrets

#### 4.3 可选的 Secrets

如果需要代理或通知功能：

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `HTTP_PROXY` | HTTP 代理地址 | `http://127.0.0.1:7890` |
| `HTTPS_PROXY` | HTTPS 代理地址 | `http://127.0.0.1:7890` |
| `TELEGRAM_BOT_TOKEN` | Telegram 通知（可选） | `123456:ABC-DEF...` |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | `123456789` |

#### 4.4 验证 Secrets

配置完成后，你应该看到类似这样的列表：

```
✅ X_AUTH_TOKEN          Updated X seconds ago
✅ X_CT0_TOKEN           Updated X seconds ago
✅ X_CSRF_TOKEN          Updated X seconds ago
✅ X_BEARER_TOKEN        Updated X seconds ago
✅ OPENROUTER_API_KEY    Updated X seconds ago
✅ OPENAI_MODEL          Updated X seconds ago
```

---

### 第五步：启用 GitHub Actions 权限

#### 5.1 配置 Actions 权限

```
Settings → Actions → General
```

向下滚动到 **Workflow permissions** 区域：

1. 选择 **Read and write permissions** ✅
2. 勾选 **Allow GitHub Actions to create and approve pull requests** ✅
3. 点击 **Save** 保存

**为什么需要这些权限？**
- 写权限：自动提交爬取的数据
- 创建 PR 权限：自动创建失败通知 Issue

#### 5.2 允许 Actions 运行

在同一页面，确保：

```
Actions permissions: ✅ Allow all actions and reusable workflows
```

---

### 第六步：测试运行

#### 6.1 手动触发 Workflow

1. 进入仓库的 **Actions** 标签页
2. 左侧选择 **Daily X Crawler**
3. 点击右上角 **Run workflow** 按钮
4. 配置运行参数：
   ```
   tweet_count: 100        (测试用小数量)
   force_summary: false
   ```
5. 点击绿色的 **Run workflow** 按钮

#### 6.2 监控运行过程

运行开始后，你会看到：

```
● Daily X Crawler #1
  → 📥 Checkout repository
  → 🐍 Set up Python
  → 📦 Install system dependencies
  → 📚 Install dependencies
  → ⚙️ Configure environment
  → 🕷️ Run crawler
  → 📊 Generate report
  → 💾 Commit and push data
  → 📤 Upload report
  → 🐛 Create Issue on failure (如果失败)
```

点击任意步骤查看详细日志。

#### 6.3 预期结果

**成功的标志：**

✅ 所有步骤显示绿色 ✓
✅ 在 `crawler_data/` 目录看到新文件
✅ 自动创建了一个新的 commit
✅ Artifacts 中有运行报告

**运行时长预估：**
- 100 条推文: ~3-5 分钟
- 500 条推文: ~8-12 分钟

#### 6.4 查看爬取的数据

```
仓库首页 → crawler_data/
  ├── daily_posts/          # 每日推文原始数据
  ├── users_daily/          # 按用户分组的推文
  ├── user_summaries/       # LLM 生成的总结
  └── raw_responses/        # API 原始响应（不提交）
```

---

### 第七步：配置定时任务

#### 7.1 默认计划

项目已配置为：
```
每天北京时间 09:00 自动运行
```

对应的 cron 表达式：
```yaml
schedule:
  - cron: '0 1 * * *'  # UTC 01:00 = 北京时间 09:00
```

#### 7.2 自定义运行时间

如果想修改运行时间，编辑 `.github/workflows/daily-crawler.yml`：

**常用时间配置：**

| 北京时间 | Cron 表达式 | 说明 |
|---------|------------|------|
| 每天 06:00 | `0 22 * * *` | 早上 |
| 每天 09:00 | `0 1 * * *` | 默认 |
| 每天 12:00 | `0 4 * * *` | 中午 |
| 每天 18:00 | `0 10 * * *` | 傍晚 |
| 每天 21:00 | `0 13 * * *` | 晚上 |
| 每天 00:00 | `0 16 * * *` | 午夜 |
| 每 6 小时 | `0 */6 * * *` | 高频 |
| 每 12 小时 | `0 */12 * * *` | 中频 |
| 工作日 09:00 | `0 1 * * 1-5` | 周一到周五 |
| 周一 09:00 | `0 1 * * 1` | 每周一次 |

**时区转换公式：**
```
UTC 时间 = 北京时间 - 8
```

例如：北京时间 21:00 → UTC 13:00 → cron: `0 13 * * *`

#### 7.3 修改运行时间

```bash
# 编辑 workflow 文件
vim .github/workflows/daily-crawler.yml

# 找到并修改这一行
schedule:
  - cron: '0 13 * * *'  # 改为晚上 21:00

# 提交更改
git add .github/workflows/daily-crawler.yml
git commit -m "chore: 修改定时任务为每天 21:00"
git push
```

#### 7.4 在线 Cron 表达式工具

不确定表达式是否正确？使用这些工具：
- https://crontab.guru/ (英文)
- https://cron.qqe2.com/ (中文)

---

### 第八步：配置失败通知（可选）

#### 8.1 GitHub Issue 通知（已默认启用）

无需配置，失败时自动创建 Issue。

#### 8.2 Telegram 通知（推荐）

**优势：即时推送到手机**

**配置步骤：**

1. **创建 Telegram Bot**
   ```
   1. 在 Telegram 搜索 @BotFather
   2. 发送 /newbot
   3. 设置名称：X Crawler Bot
   4. 获取 Bot Token (保存)
   ```

2. **获取 Chat ID**
   ```
   1. 给你的 Bot 发送任意消息
   2. 访问: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   3. 在 JSON 中找到 "chat":{"id": 数字}
   4. 记下这个数字
   ```

3. **添加 GitHub Secrets**
   ```
   TELEGRAM_BOT_TOKEN: 你的 Bot Token
   TELEGRAM_CHAT_ID: 你的 Chat ID
   ```

完成！下次失败会推送到 Telegram。

**详细配置见**: `docs/NOTIFICATION_SETUP.md`

---

## 📊 数据管理策略

### 策略 A: 提交数据到 Git（默认，适合小规模）

**优势:**
- ✅ 简单，无需额外配置
- ✅ 数据自动备份
- ✅ 版本控制

**劣势:**
- ⚠️ 仓库体积会增长

**适用场景:**
- 每天爬取 < 500 条推文
- 保留 < 30 天数据

**当前配置:**
```gitignore
# .gitignore 已配置
crawler_data/raw_responses/   # 不提交原始响应
crawler_data/users_daily/     # 提交用户数据
crawler_data/user_summaries/  # 提交总结文件
```

### 策略 B: 上传到云存储（适合大规模）

如果数据量大，可以配置上传到云存储。

**支持的存储服务:**
- AWS S3
- Cloudflare R2（免费 10GB）
- Azure Blob Storage
- Google Cloud Storage

**配置示例（Cloudflare R2）:**

1. **获取 R2 凭证**
   ```
   Cloudflare Dashboard → R2 → Manage R2 API Tokens
   ```

2. **添加 GitHub Secrets**
   ```
   R2_ACCESS_KEY_ID: 你的 Access Key
   R2_SECRET_ACCESS_KEY: 你的 Secret Key
   R2_BUCKET: crawler-data
   R2_ENDPOINT: https://你的账号ID.r2.cloudflarestorage.com
   ```

3. **修改 workflow**（在 daily-crawler.yml 中添加）：
   ```yaml
   - name: 📤 Upload to R2
     run: |
       pip install boto3
       python << EOF
       import boto3
       s3 = boto3.client('s3',
         endpoint_url='${{ secrets.R2_ENDPOINT }}',
         aws_access_key_id='${{ secrets.R2_ACCESS_KEY_ID }}',
         aws_secret_access_key='${{ secrets.R2_SECRET_ACCESS_KEY }}'
       )
       # 上传文件
       import os
       for root, dirs, files in os.walk('crawler_data'):
         for file in files:
           filepath = os.path.join(root, file)
           s3.upload_file(filepath, '${{ secrets.R2_BUCKET }}', filepath)
       EOF
   ```

---

## 🔧 故障排查

### 问题 1: Actions 运行失败

**症状**: workflow 显示红色 ❌

**排查步骤:**

1. **查看详细日志**
   ```
   Actions → 失败的运行 → 点击失败的步骤 → 查看日志
   ```

2. **常见错误和解决方法:**

   | 错误信息 | 原因 | 解决方法 |
   |---------|------|---------|
   | `401 Unauthorized` | X 认证失败 | 重新提取 X 认证信息，更新 Secrets |
   | `403 Forbidden` | Token 过期 | 重新登录 X，更新 auth_token |
   | `429 Too Many Requests` | 请求过频 | 减少 `--count` 数量或增加间隔 |
   | `OpenAI API error` | API Key 无效或余额不足 | 检查 OpenRouter 账户 |
   | `Permission denied` | Actions 权限不足 | 检查 Settings → Actions → Workflow permissions |

### 问题 2: 没有生成数据文件

**可能原因:**

1. **认证信息错误**
   - 检查所有 Secrets 是否正确配置
   - 特别注意 Bearer Token 要包含 `Bearer` 前缀

2. **网络问题**
   - GitHub Actions 可能无法访问 X
   - 考虑配置代理（添加 HTTP_PROXY Secret）

3. **X 账号问题**
   - 账号被限制或封禁
   - 换一个 X 账号重试

### 问题 3: Secrets 未生效

**检查方法:**

在 workflow 中添加调试步骤：

```yaml
- name: 🔍 Debug secrets
  run: |
    echo "AUTH_TOKEN 长度: ${#X_AUTH_TOKEN}"
    echo "CT0_TOKEN 长度: ${#X_CT0_TOKEN}"
    echo "API_KEY 存在: ${{ secrets.OPENROUTER_API_KEY != '' }}"
```

**注意**: 不要直接 echo Secret 值，会泄露！

### 问题 4: 定时任务没有触发

**可能原因:**

1. **Actions 未启用**
   - 确认 Settings → Actions → General 允许 Actions

2. **GitHub Actions 延迟**
   - GitHub 定时任务可能延迟 5-15 分钟
   - 高峰期可能延迟更久

3. **Workflow 文件错误**
   - 检查 `.github/workflows/daily-crawler.yml` 语法
   - 使用 https://crontab.guru/ 验证 cron 表达式

### 问题 5: 数据未提交到仓库

**排查步骤:**

1. **检查 Actions 权限**
   ```
   Settings → Actions → General → Workflow permissions
   → 确认选择 "Read and write permissions"
   ```

2. **查看提交步骤日志**
   ```
   Actions → 运行记录 → 💾 Commit and push data
   → 查看是否有错误
   ```

3. **本地测试**
   ```bash
   git status
   git add crawler_data/
   git commit -m "test"
   git push
   ```

### 问题 6: Playwright 安装失败

**错误信息:**
```
Error: browserType.launch: Executable doesn't exist
```

**解决方法:**

已在 workflow 中配置系统依赖安装，如果仍失败，可以添加：

```yaml
- name: 📦 Install Playwright browsers
  run: |
    playwright install --with-deps chromium
```

---

## 💡 最佳实践

### 1. Token 定期更新

X 的 auth_token 通常 30-60 天过期，建议：

- 📅 每月检查一次
- 🔔 配置失败通知（Telegram）
- 📝 在日历中设置提醒

### 2. 数据定期清理

避免仓库过大：

```bash
# 定期清理旧数据（本地执行）
find crawler_data/daily_posts -name "*.json" -mtime +30 -delete
git add crawler_data/
git commit -m "chore: 清理 30 天前的数据"
git push
```

或在 workflow 中自动清理：

```yaml
- name: 🧹 Clean old data
  run: |
    find crawler_data/daily_posts -name "*.json" -mtime +30 -delete
    find crawler_data/raw_responses -name "*.json" -mtime +7 -delete
```

### 3. 成本控制

**GitHub Actions:**
- 公开仓库：无限免费 ✅
- 私有仓库：2000 分钟/月

**OpenRouter API:**
- 监控用量: https://openrouter.ai/usage
- 设置预算提醒
- 选择性价比模型（gpt-4o-mini）

**预估成本（私有仓库）:**
```
每天运行一次，每次 10 分钟
= 300 分钟/月
= 完全在免费额度内 ✅

LLM 成本（gpt-4o-mini）:
500 条推文 × 每条 200 tokens × $0.15/1M tokens
= 约 $0.015/天
= 约 $0.45/月
```

### 4. 安全建议

✅ **应该做:**
- 使用 GitHub Secrets 存储敏感信息
- 定期更新认证 Token
- 启用 2FA（GitHub 和 X）
- 公开仓库时检查 .gitignore

❌ **不要做:**
- 不要在代码中硬编码 Token
- 不要提交 `.env` 文件
- 不要在 Issue/PR 中泄露 Secret
- 不要分享 auth_token

### 5. 监控和维护

**每周检查:**
- [ ] Actions 运行状态
- [ ] 数据文件生成情况
- [ ] OpenRouter 余额

**每月检查:**
- [ ] X 认证是否过期
- [ ] 清理旧数据
- [ ] 检查仓库大小

**设置自动提醒:**
```
GitHub → Settings → Notifications → Email
→ ✅ Actions: Workflow failures
```

---

## 📚 相关文档

- [NOTIFICATION_SETUP.md](./NOTIFICATION_SETUP.md) - 失败通知配置
- [DEPLOYMENT.md](../DEPLOYMENT.md) - 其他部署方案对比
- [README.md](../README.md) - 项目使用说明

---

## 🎯 快速检查清单

部署完成后，确认以下所有项目：

### GitHub 配置
- [ ] 仓库已创建并推送代码
- [ ] Actions 已启用
- [ ] Workflow permissions 设置为 Read and write

### Secrets 配置
- [ ] X_AUTH_TOKEN
- [ ] X_CT0_TOKEN
- [ ] X_CSRF_TOKEN
- [ ] X_BEARER_TOKEN
- [ ] OPENROUTER_API_KEY
- [ ] OPENAI_MODEL

### 测试运行
- [ ] 手动触发 workflow 成功
- [ ] 数据文件正确生成
- [ ] 自动提交到仓库
- [ ] （可选）收到 Telegram 通知

### 定时任务
- [ ] 定时任务已配置
- [ ] 时间设置正确（考虑时区）
- [ ] 等待首次自动运行

---

## ❓ 常见问题 FAQ

### Q1: 公开仓库安全吗？

**A**: 是的，只要：
- ✅ 所有敏感信息都在 Secrets 中
- ✅ 没有提交 `.env` 和 `config.json`
- ✅ `.gitignore` 配置正确

公开仓库的好处：
- 无限 Actions 时长
- 可以分享给他人
- 社区可以贡献代码

### Q2: 如何备份数据？

**方法 1: Git 历史**（自动）
- 每次提交都是备份
- 可以回滚到任意版本

**方法 2: 定期下载**
```bash
git clone https://github.com/YOUR_USERNAME/x-crawler.git backup
```

**方法 3: GitHub Actions Artifacts**
- 每次运行的报告保留 30 天
- 在 Actions → 运行记录 → Artifacts 下载

### Q3: 可以同时爬取多个账号吗？

**A**: 可以，有两种方法：

**方法 1: 多个 workflow**
- 复制 `daily-crawler.yml`
- 创建 `daily-crawler-account2.yml`
- 使用不同的 Secrets（如 `X_AUTH_TOKEN_2`）

**方法 2: 切换账号**
- 定期手动更新 Secrets
- 适合不需要同时监控的场景

### Q4: 如何增加爬取数量？

修改 workflow 中的 `--count` 参数：

```yaml
# 从 500 改为 1000
python run_crawler.py --count 1000 --user-summaries
```

**注意**: 数量越大，运行时间越长，LLM 成本越高。

### Q5: 认证 Token 多久过期？

**经验数据:**
- `auth_token`: 30-60 天
- `ct0`: 随 auth_token 同步
- `Bearer Token`: 很长时间（但可能变更）

**建议**: 每月检查一次，配置失败通知以便及时发现。

---

## 🆘 获取帮助

**遇到问题？**

1. 📖 查看本文档的 [故障排查](#故障排查) 部分
2. 🔍 在项目 Issues 中搜索类似问题
3. 💬 创建新 Issue 描述你的问题（包含日志）
4. 📧 查看 GitHub Actions 日志中的错误信息

**提 Issue 时请包含:**
- 操作系统和浏览器版本
- 完整的错误日志（移除敏感信息）
- 已尝试的解决方法
- workflow 运行链接

---

## 🎉 部署完成！

恭喜！如果你完成了所有步骤，你的 X Crawler 现在应该：

✅ 每天自动运行
✅ 爬取并保存推文数据
✅ 生成 LLM 智能总结
✅ 失败时自动通知
✅ 数据安全存储在 GitHub

享受自动化的乐趣吧！🚀

---

*最后更新: 2025-10-10*
*如有问题或建议，欢迎提 Issue*
