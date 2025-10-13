# X API 深度分析结果

## 关键发现

### 1. X 时间线 GraphQL API

#### 推荐时间线 (For You)
```
https://x.com/i/api/graphql/xNGIIoXaz9DyeBXBfn3AjA/HomeLatestTimeline
```

#### 关注时间线 (Following)  
```
https://x.com/i/api/graphql/1_nms9JVtHQxTw8VwZJciQ/HomeTimeline
```

**关键参数**:
- `count`: 20 (每次获取推文数量)
- `includePromotedContent`: true (包含推广内容)
- `latestControlAvailable`: true
- `requestContext`: "launch"

**重要Features参数**:
- `longform_notetweets_consumption_enabled`: true (长文推文支持)
- `view_counts_everywhere_api_enabled`: true (查看次数)
- `responsive_web_edit_tweet_api_enabled`: true
- `longform_notetweets_rich_text_read_enabled`: true

### 2. 数据结构分析

#### 推文数据路径:
```
data.home.home_timeline_urt.instructions[].entries[].content.itemContent.tweet_results.result
```

#### 推文结构:
```json
{
  "__typename": "Tweet",
  "rest_id": "推文ID",
  "core": {
    "user_results": { "用户信息" }
  },
  "legacy": {
    "full_text": "完整推文内容",
    "display_text_range": [开始位置, 结束位置],
    "entities": { "实体数据" },
    "created_at": "创建时间"
  }
}
```

### 3. 文本完整性分析 ✅

**重大发现**: 推文文本存储在 `legacy.full_text` 字段中

**实际样本**:
1. 原文: `"full_text": "just talked. gemini 3 not this month but soon. 3.0 flash will be >2.5 pro. can't say more. buckle up!"`
2. 中文翻译: `"full_text": "小道消息：Gemini 3 Flash 能力超过 Gemini 2.5 Pro，本月不会发布 Gemini 3，但是很快了。"`

**关键结论**: 
- ✅ 文本内容是完整的，存储在 `legacy.full_text` 字段
- ✅ 没有发现文本截断问题
- ✅ `display_text_range` 字段标明了显示范围

### 4. 用户信息结构

用户数据在 `core.user_results.result`:
```json
{
  "__typename": "User", 
  "rest_id": "用户ID",
  "core": {
    "name": "显示名称",
    "screen_name": "用户名"
  },
  "legacy": {
    "description": "个人简介",
    "followers_count": "粉丝数",
    "friends_count": "关注数",
    "statuses_count": "推文数"
  }
}
```

## 已解决的核心问题

### ✅ 问题1: 帖子内容不完整
**根本原因**: 需要使用 `legacy.full_text` 字段，而非简单的 `text` 字段
**解决方案**: 从正确的JSON路径提取完整文本内容

### ✅ 问题2: 转推数据结构分析
**数据路径**: `legacy.retweeted_status_result.result`  
**结构**: 转推包含完整的原始推文数据，包括用户信息和文本内容
**示例**: 
```json
{
  "legacy": {
    "retweeted_status_result": {
      "result": {
        "__typename": "Tweet",
        "legacy": {
          "full_text": "原始推文完整文本"
        }
      }
    }
  }
}
```

### ✅ 问题3: 引用推文数据结构
**数据路径**: `quoted_status_result.result`
**特点**: 与转推类似，包含完整的被引用推文数据

### ✅ 问题4: 媒体文件URL获取
**视频数据路径**: `legacy.extended_entities.media[].video_info.variants[]`
**图片数据路径**: `legacy.extended_entities.media[].media_url_https`

**视频URL示例**:
```json
{
  "variants": [
    {
      "bitrate": 2176000,
      "content_type": "video/mp4", 
      "url": "https://video.twimg.com/amplify_video/.../vid/avc1/720x1280/xxx.mp4"
    }
  ]
}
```

**图片URL示例**:
```json
{
  "media_url_https": "https://pbs.twimg.com/amplify_video_thumb/.../img/xxx.jpg"
}
```

### 📋 待深入分析的问题

1. **嵌套转推处理** - 分析A转B，B转C的复杂情况
2. **分页机制** - 分析cursor和timeline指令
3. **长文推文(Note Tweet)** - 分析超长内容的数据结构

## 下一步分析计划

1. 查找转推(retweet)样本数据
2. 分析媒体文件的URL提取方法
3. 研究分页和游标机制
4. 验证长文推文(note_tweet)的处理方式

## API请求特征

- **认证方式**: Cookie-based认证
- **限流**: 500次/小时 (X-Rate-Limit-*)
- **响应格式**: 嵌套GraphQL结构
- **数据大小**: 大约157KB per响应 (20条推文)

---
*分析时间: 2025-09-11*
*数据来源: 实际X.com API响应*