# X推文爬虫系统 🚀

极简的X(Twitter)推文采集和LLM智能总结系统。

## ✨ 核心特性

- 🔥 **推文爬取** - 基于HTTP API的数据采集
- 🤖 **LLM总结** - 支持OpenRouter多模型智能分析
- 📝 **用户模板** - 可自定义的提示词模板系统

## 🚀 快速开始

### 1. 安装依赖
```bash
./setup.sh
# 或手动安装
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置

#### 方法1：使用.env文件（推荐）
```bash
cp .env.example .env
# 编辑.env文件，填入你的配置
```

#### 方法2：自动提取认证
```bash
python auth_setup.py
```
自动打开浏览器登录X平台，提取认证信息并保存到 `.env` 和 `config.json`

#### 方法3：使用config.json
```bash
cp config_template.json config.json
# 编辑config.json填入配置
```

**优先级**: `.env` > `config.json` > 默认值

### 3. 环境变量说明
```bash
# X平台认证
X_AUTH_TOKEN=your_auth_token
X_CT0_TOKEN=your_ct0_token

# LLM配置（腾讯云 DeepSeek，不是 OpenRouter）
TENCENT_DEEPSEEK_API_KEY=your_tencent_deepseek_api_key
OPENAI_BASE_URL=https://api.lkeap.cloud.tencent.com/v1
OPENAI_MODEL=deepseek-v3.2

# 代理配置（可选）
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

### 4. 验证配置
```bash
python test_config.py
```

### 5. 运行爬虫
```bash
# 爬取推文并生成用户总结
python run_crawler.py --count 500 --user-summaries

# 仅为已有数据生成总结
python run_crawler.py --user-summaries

# 强制覆盖已有总结
python run_crawler.py --user-summaries --force
```

## 📋 项目结构

```
x_crawler/
├── crawler.py              # 爬虫引擎
├── summarizer.py           # LLM总结生成器
├── run_crawler.py          # 命令行入口
├── config.json             # API认证配置
├── user_prompt_templates.json # 用户提示词模板
└── crawler_data/           # 数据存储目录
```

## 📝 自定义提示词

编辑 `user_prompt_templates.json` 添加用户专属模板：

```json
{
  "username": {
    "template": "你的提示词模板，支持{user_info}和{tweet_content}变量",
    "description": "模板描述"
  }
}
```

## 📊 数据输出

- **爬虫数据**: `crawler_data/users_daily/username_YYYYMMDD.json`
- **LLM总结**: `crawler_data/user_summaries/username_YYYYMMDD_summary.md`
- **提示词缓存**: `prompts/user_daily_username_*.txt`

## 🔧 环境变量

- `TENCENT_DEEPSEEK_API_KEY`: 腾讯云 DeepSeek / LKEAP API Key（生产必填；别名 `LKEAP_API_KEY`）
- `OPENAI_BASE_URL`: OpenAI 兼容地址（默认 `https://api.lkeap.cloud.tencent.com/v1`；TokenHub 可改为 `https://tokenhub.tencentmaas.com/v1`）
- `OPENAI_MODEL`: 模型 ID（默认 `deepseek-v3.2`，同家族还可设 `deepseek-v3.1-terminus` / `deepseek-v3-0324` / `deepseek-r1-0528`）
- 生产环境未配置密钥或 LLM 调用失败会**非零退出**，不会把「模拟内容」当成功提交

### GitHub Actions Secrets（Daily Summary）

仓库 Settings → Secrets and variables → Actions 需要：

| Secret | 必填 | 说明 |
|--------|------|------|
| `TENCENT_DEEPSEEK_API_KEY` | 是 | 腾讯云 LKEAP / TokenHub API Key（老板单独写入，不要提交到仓库） |
| `LKEAP_API_KEY` | 否 | 与上一行二选一即可 |
| `OPENAI_MODEL` | 否 | 默认 `deepseek-v3.2` |
| `OPENAI_BASE_URL` | 否 | 默认 LKEAP；已迁 TokenHub 时再覆盖 |

文档：https://cloud.tencent.com/document/product/1772/115969

## 📄 许可

MIT License