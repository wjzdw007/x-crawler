# API分析方法论

## 核心原则：认真分析，大胆假设，小心验证

### 已知问题清单
1. **帖子内容不完整** ← 新发现的关键问题
2. 转帖的原帖获取不到
3. 嵌套转帖处理问题
4. 图片视频地址获取失败
5. 数据错误和不完整

## 分析方法论

### 1. 帖子内容不完整问题分析

#### 假设1：文本截断问题
**假设**：X API可能返回截断的文本内容
**验证方法**：
- 对比浏览器显示内容 vs API返回内容
- 检查是否有`text` vs `full_text`字段差异
- 分析字符数限制和截断规则

#### 假设2：字段选择不当
**假设**：可能没有请求完整的字段集合
**验证方法**：
- 分析GraphQL查询参数
- 对比不同字段集合的返回结果
- 查看X前端实际使用的字段列表

#### 假设3：分页加载问题
**假设**：长内容可能通过后续请求加载
**验证方法**：
- 分析thread展开的API调用
- 检查reply链和续文的加载机制
- 对比单独获取帖子详情的接口

### 2. 数据结构深度分析

#### 基于实际请求的分析流程
```python
# 分析工具框架
def analyze_api_request(url, headers, payload):
    """分析单个API请求"""
    # 1. 记录完整请求信息
    request_info = {
        'url': url,
        'headers': dict(headers),
        'payload': payload,
        'timestamp': datetime.now()
    }
    
    # 2. 发送请求并记录响应
    response = requests.post(url, headers=headers, json=payload)
    response_info = {
        'status_code': response.status_code,
        'headers': dict(response.headers),
        'data': response.json(),
        'size': len(response.content)
    }
    
    # 3. 结构化分析响应数据
    analysis = analyze_response_structure(response_info['data'])
    
    return {
        'request': request_info,
        'response': response_info,
        'analysis': analysis
    }

def analyze_response_structure(data):
    """深度分析响应数据结构"""
    return {
        'tweet_fields': extract_tweet_fields(data),
        'user_fields': extract_user_fields(data), 
        'media_fields': extract_media_fields(data),
        'retweet_structure': analyze_retweet_structure(data),
        'missing_fields': detect_missing_fields(data),
        'truncation_indicators': detect_truncation(data)
    }
```

### 3. 分步验证策略

#### 阶段1：单帖子完整性验证
1. 选择明确知道内容的帖子（如自己发的长帖）
2. 分析API返回 vs 实际内容的差异
3. 记录所有缺失内容的模式

#### 阶段2：批量数据模式分析
1. 收集50-100个不同类型的帖子
2. 分类分析：普通帖、长帖、转帖、回复、媒体帖
3. 统计各类问题的出现频率

#### 阶段3：对比验证
1. 同时使用多个不同的API endpoint
2. 对比GraphQL vs REST API的差异
3. 分析X官方网页的请求模式

### 4. 具体验证检查点

#### 文本内容验证
- [ ] 检查text字段长度限制
- [ ] 验证full_text字段存在性
- [ ] 分析display_text_range参数
- [ ] 检查entities字段对内容的影响

#### 转推结构验证
- [ ] 分析retweeted_status结构
- [ ] 验证quoted_status的完整性
- [ ] 检查转推链的深度限制
- [ ] 对比不同转推类型的数据结构

#### 媒体内容验证
- [ ] 验证media_url vs media_url_https
- [ ] 检查video_info的完整性
- [ ] 分析不同尺寸图片的URL格式
- [ ] 验证媒体文件的可访问性

#### API参数实验
```python
# 系统化测试不同参数组合
PARAMETER_EXPERIMENTS = {
    'tweet_mode': ['extended', 'compat'],
    'include_entities': [True, False],
    'include_ext_media': [True, False],
    'include_cards': [True, False],
    'count': [20, 50, 100, 200],
    'result_type': ['recent', 'popular', 'mixed']
}
```

### 5. 数据记录和对比

#### 建立基准数据集
```
analysis_data/
├── baseline_tweets/       # 已知完整内容的帖子
├── api_responses/        # 各种API请求的响应
├── comparison_results/   # 对比分析结果
├── field_mapping/       # 字段结构分析
└── problem_cases/       # 问题案例收集
```

#### 自动化对比工具
```python
def compare_content_completeness(browser_content, api_content):
    """对比浏览器显示内容与API返回内容"""
    differences = {
        'missing_text': find_missing_text(browser_content, api_content),
        'truncated_fields': find_truncated_fields(api_content),
        'missing_media': find_missing_media(browser_content, api_content),
        'incomplete_threads': find_incomplete_threads(api_content)
    }
    return differences
```

### 6. 验证优先级

**高优先级**（影响内容完整性）：
1. 文本内容截断问题
2. 转推原文获取问题  
3. 媒体URL完整性问题

**中优先级**（影响数据质量）：
1. 用户信息完整性
2. 时间戳和统计数据准确性
3. 标签和mention的完整性

**低优先级**（优化相关）：
1. 请求效率优化
2. 数据格式标准化
3. 冗余数据清理

## 实施计划

1. **准备阶段**：创建分析工具和数据收集框架
2. **数据收集**：系统化收集各类API响应数据
3. **模式识别**：分析数据缺失和错误的规律
4. **假设验证**：逐一验证各类假设
5. **解决方案**：基于验证结果设计解决方案

**绝对不允许**：
- ❌ 基于猜测编写代码
- ❌ 不验证就采用网上的解决方案
- ❌ 忽略边缘案例
- ❌ 只测试单一场景