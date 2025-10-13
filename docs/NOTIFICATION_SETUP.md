# 通知配置指南

本文档介绍如何配置各种失败通知方案。

---

## 🎯 推荐方案对比

| 方案 | 难度 | 成本 | 实时性 | 推荐度 |
|-----|------|------|--------|--------|
| **GitHub Issue** | ⭐ 最简单 | 免费 | 即时 | ⭐⭐⭐⭐ |
| **GitHub Email** | ⭐ 无需配置 | 免费 | 延迟 | ⭐⭐⭐ |
| **Telegram** | ⭐⭐ 简单 | 免费 | 即时 | ⭐⭐⭐⭐⭐ |
| **Bark (iOS)** | ⭐⭐ 简单 | 免费 | 即时 | ⭐⭐⭐⭐ |
| **企业微信** | ⭐⭐ 中等 | 免费 | 即时 | ⭐⭐⭐⭐ |
| **钉钉** | ⭐⭐ 中等 | 免费 | 即时 | ⭐⭐⭐⭐ |
| **Discord** | ⭐⭐ 简单 | 免费 | 即时 | ⭐⭐⭐ |
| **Slack** | ⭐⭐⭐ 复杂 | 收费 | 即时 | ⭐⭐ |

---

## 方案 1: GitHub Issue (已内置，无需配置) ⭐⭐⭐⭐

### 优势
- ✅ **无需任何配置**，开箱即用
- ✅ 自动创建 Issue，便于跟踪问题
- ✅ 包含详细的运行信息和快速链接
- ✅ 可以直接在 Issue 中讨论和标记完成

### 使用方式
已经集成在 `daily-crawler.yml` 中，无需额外操作。

失败时会自动创建一个 Issue，包含：
- 📅 失败时间
- 🔗 运行日志链接
- ✅ 常见问题检查清单
- 🏷️ 自动打上 `bot`、`crawler-failure` 标签

### 查看通知
访问仓库的 `Issues` 标签页，查看自动创建的失败报告。

### 关闭 Issue
问题解决后手动关闭 Issue 即可。

---

## 方案 2: GitHub Email 通知 (默认启用) ⭐⭐⭐

### 优势
- ✅ 完全免费，无需配置
- ✅ GitHub 默认功能

### 配置方式

1. **检查邮箱设置**
   - 进入 GitHub 个人 Settings → Notifications
   - 确保勾选了 Actions 相关通知

2. **自定义通知规则**
   ```
   Settings → Notifications → Actions
   → ✅ Send notifications for failed workflows
   → ✅ Only notify for workflows I subscribe to (可选)
   ```

3. **针对特定仓库配置**
   ```
   仓库页面 → Watch → Custom
   → ✅ Issues
   → ✅ Actions (workflows)
   ```

### 缺点
- ⚠️ 可能有延迟
- ⚠️ 容易被淹没在其他邮件中

---

## 方案 3: Telegram Bot (强烈推荐) ⭐⭐⭐⭐⭐

### 优势
- ✅ 完全免费
- ✅ 推送及时（秒级）
- ✅ 支持 Markdown 格式
- ✅ 跨平台（iOS/Android/桌面）

### 配置步骤

#### 1. 创建 Telegram Bot

1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示设置 Bot 名称和用户名
4. 获取 **Bot Token**（形如 `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`）

#### 2. 获取 Chat ID

**方法 A: 使用现有 Bot**
1. 向你的 Bot 发送任意消息
2. 访问: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. 在返回的 JSON 中找到 `chat.id` 字段

**方法 B: 使用 @userinfobot**
1. 在 Telegram 中搜索 `@userinfobot`
2. 发送 `/start`
3. Bot 会回复你的 Chat ID

#### 3. 配置 GitHub Secrets

在仓库中添加两个 Secrets:
- `TELEGRAM_BOT_TOKEN`: 你的 Bot Token
- `TELEGRAM_CHAT_ID`: 你的 Chat ID

#### 4. 测试

手动触发一次 workflow，失败时会收到 Telegram 推送。

### 进阶配置：创建通知群组

如果想让多人接收通知：

1. 创建一个 Telegram 群组
2. 把 Bot 添加到群组
3. 获取群组 Chat ID（通常是负数，如 `-1001234567890`）
4. 更新 `TELEGRAM_CHAT_ID` Secret

---

## 方案 4: Bark (iOS 推送，极简方案) ⭐⭐⭐⭐

### 优势
- ✅ **超级简单**，只需一个 Key
- ✅ 推送到 iOS 通知中心
- ✅ 支持自定义铃声、角标

### 配置步骤

#### 1. 安装 Bark App
在 App Store 搜索并安装 [Bark](https://apps.apple.com/cn/app/bark/id1403753865)

#### 2. 获取 Bark Key
打开 App，复制你的推送 Key（形如 `xxxxxxxxxx`）

#### 3. 配置 GitHub Secret
添加 Secret: `BARK_KEY`

#### 4. 添加 Workflow 步骤

在 `daily-crawler.yml` 中添加：

```yaml
- name: 📱 Send Bark notification
  if: failure() && secrets.BARK_KEY != ''
  run: |
    curl -s "https://api.day.app/${{ secrets.BARK_KEY }}/X%20Crawler%20失败/$(TZ='Asia/Shanghai' date '+%Y-%m-%d%20%H:%M:%S')?group=crawler&sound=alarm&url=${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
```

### 自定义配置

```bash
# 基础推送
https://api.day.app/YOUR_KEY/标题/内容

# 带铃声
?sound=alarm

# 带分组
?group=crawler

# 带跳转链接
?url=https://example.com

# 自动保存
?automaticallyCopy=1&copy=内容
```

**可用铃声**: `alarm`, `anticipate`, `bell`, `birdsong`, `bloom`, `calypso`, `chime`, `choo`, `descent`, `electronic`, `fanfare`, `glass`, `gotosleep`, `healthnotification`, `horn`, `ladder`, `mailsent`, `minuet`, `multiwayinvitation`, `newmail`, `newsflash`, `noir`, `paymentsuccess`, `shake`, `sherwoodforest`, `silence`, `spell`, `suspense`, `telegraph`, `tiptoes`, `typewriters`, `update`

---

## 方案 5: 企业微信群机器人 ⭐⭐⭐⭐

### 优势
- ✅ 企业内部通知首选
- ✅ 支持 Markdown
- ✅ 可 @ 特定成员

### 配置步骤

#### 1. 创建群机器人

1. 在企业微信中创建一个群
2. 群设置 → 群机器人 → 添加机器人
3. 设置机器人名称和头像
4. 复制 **Webhook 地址**

#### 2. 配置 GitHub Secret

添加 Secret: `WECHAT_WEBHOOK`（完整的 Webhook URL）

#### 3. Workflow 已集成

`daily-crawler.yml` 已包含企业微信通知代码，配置 Secret 后自动生效。

### 进阶：@ 特定成员

```yaml
- name: 📢 Send WeChat Work notification with mention
  run: |
    curl -s -X POST "${{ secrets.WECHAT_WEBHOOK }}" \
      -H "Content-Type: application/json" \
      -d '{
        "msgtype": "text",
        "text": {
          "content": "🚨 X Crawler 运行失败\n请 @张三 处理",
          "mentioned_list": ["zhangsan"],
          "mentioned_mobile_list": ["13800138000"]
        }
      }'
```

---

## 方案 6: 钉钉群机器人 ⭐⭐⭐⭐

### 配置步骤

#### 1. 创建群机器人

1. 钉钉群设置 → 智能群助手 → 添加机器人 → 自定义
2. 设置机器人名称
3. **安全设置**选择 "自定义关键词"，输入：`Crawler`
4. 复制 **Webhook 地址**

#### 2. 配置 GitHub Secret

添加 Secret: `DINGTALK_WEBHOOK`

#### 3. 添加 Workflow 步骤

```yaml
- name: 📢 Send DingTalk notification
  if: failure() && secrets.DINGTALK_WEBHOOK != ''
  run: |
    curl -s -X POST "${{ secrets.DINGTALK_WEBHOOK }}" \
      -H "Content-Type: application/json" \
      -d '{
        "msgtype": "markdown",
        "markdown": {
          "title": "X Crawler 运行失败",
          "text": "## 🚨 X Crawler 运行失败\n\n- 时间: '"$(TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S')"'\n- 仓库: ${{ github.repository }}\n\n[查看详情](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})"
        }
      }'
```

### 进阶：@ 所有人

```json
{
  "msgtype": "text",
  "text": {
    "content": "🚨 X Crawler 运行失败，请及时处理"
  },
  "at": {
    "isAtAll": true
  }
}
```

---

## 方案 7: Discord Webhook ⭐⭐⭐

### 配置步骤

#### 1. 创建 Webhook

1. Discord 服务器设置 → 整合 → Webhooks
2. 点击 "新建 Webhook"
3. 设置名称、选择频道
4. 复制 **Webhook URL**

#### 2. 配置 GitHub Secret

添加 Secret: `DISCORD_WEBHOOK`

#### 3. 添加 Workflow 步骤

查看 `notifications.yml` 中的 Discord 示例。

---

## 🎯 推荐组合方案

### 个人开发者
```
GitHub Issue (已启用) + Telegram
```
- Issue 用于问题跟踪
- Telegram 用于即时通知

### 团队协作
```
GitHub Issue + 企业微信/钉钉
```
- Issue 记录历史
- 企业通讯工具通知团队

### iOS 用户
```
GitHub Issue + Bark
```
- 最简单的推送方案

---

## 📝 配置检查清单

完成配置后，按照以下步骤测试：

- [ ] 已添加必要的 GitHub Secrets
- [ ] 已更新 `daily-crawler.yml` 添加通知步骤
- [ ] 手动触发一次失败的 workflow 测试通知
  ```bash
  # 在 workflow 中临时添加一个失败步骤
  - run: exit 1
  ```
- [ ] 确认收到通知
- [ ] 移除测试失败步骤

---

## 🔧 故障排查

### Telegram 没收到通知

**检查项:**
1. Bot Token 和 Chat ID 是否正确
2. 是否向 Bot 发送过至少一条消息
3. Bot 是否被 Telegram 封禁（很少见）

**测试命令:**
```bash
# 手动测试推送
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "<YOUR_CHAT_ID>",
    "text": "测试消息"
  }'
```

### 企业微信/钉钉没收到

**检查项:**
1. Webhook URL 是否完整
2. 是否设置了安全关键词（钉钉）
3. 消息内容是否包含关键词

### GitHub Issue 没创建

**检查项:**
1. Actions 权限是否启用写权限
2. 是否有 `github-script` action 报错

---

## 💡 最佳实践

### 1. 避免通知疲劳

**只在重要失败时通知:**
```yaml
- name: 🚨 Notify only on critical failures
  if: failure() && contains(github.event.head_commit.message, '[critical]')
```

### 2. 分级通知

```yaml
# 连续失败 3 次才通知
- name: Check failure count
  id: check
  run: |
    FAIL_COUNT=$(gh api repos/${{ github.repository }}/actions/runs --jq '[.workflow_runs[] | select(.conclusion=="failure")] | length')
    if [ $FAIL_COUNT -ge 3 ]; then
      echo "notify=true" >> $GITHUB_OUTPUT
    fi

- name: Send notification
  if: steps.check.outputs.notify == 'true'
  run: # 发送通知
```

### 3. 成功恢复通知

```yaml
- name: ✅ Notify on recovery
  if: success() && github.event.before != ''
  run: |
    # 检查上一次运行是否失败
    PREV_STATUS=$(gh api repos/${{ github.repository }}/actions/runs/${{ github.event.before }} --jq .conclusion)
    if [ "$PREV_STATUS" = "failure" ]; then
      # 发送恢复通知
    fi
```

---

## 📚 更多资源

- [Telegram Bot API 文档](https://core.telegram.org/bots/api)
- [企业微信机器人文档](https://developer.work.weixin.qq.com/document/path/91770)
- [钉钉机器人文档](https://open.dingtalk.com/document/robots/custom-robot-access)
- [Bark 使用文档](https://github.com/Finb/Bark)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

---

需要帮助？在 Issues 中提问，或查看项目文档。
