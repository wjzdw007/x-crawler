# 项目结构说明

## 📁 极简项目结构

```
x_crawler/
├── 🚀 核心文件 (3个)
│   ├── crawler.py              # X平台爬虫引擎
│   ├── summarizer.py           # LLM总结生成器
│   └── run_crawler.py          # 命令行入口
│
├── ⚙️ 配置 (2个)
│   ├── config.json             # API认证配置
│   └── user_prompt_templates.json # 用户提示词模板
│
├── 📊 数据目录 (统一在crawler_data)
│   └── crawler_data/           # 所有数据统一存储
│       ├── daily_posts/        # 每日推文原始数据
│       ├── users_daily/        # 按用户分类的数据
│       ├── raw_responses/      # API原始响应
│       ├── user_summaries/     # LLM生成的总结
│       └── prompts/            # 提示词缓存
│
├── 🔧 工具 (可选)
│   └── tools/                  # 分析验证工具
│
├── 📦 环境
│   ├── requirements.txt        # 依赖列表
│   ├── setup.sh                # 安装脚本
│   └── venv/                   # 虚拟环境
│
└── 📁 其他
    ├── README.md               # 使用说明
    └── archive/                # 历史文件存档
```

## 🚀 核心使用流程

1. **配置环境**: `./setup.sh`
2. **运行爬虫**: `python run_crawler.py`
3. **生成报告**: 自动调用 `summarizer.py`
4. **查看结果**: `summaries/` 和 `daily_reports/` 目录

## 📋 文件功能说明

### 核心组件
- `crawler.py`: X平台HTTP爬虫核心引擎，支持推荐时间线爬取
- `summarizer.py`: 集成OpenRouter+OpenAI的LLM总结生成系统
- `run_crawler.py`: 命令行接口，支持灵活参数配置

### 配置系统
- `config.json`: API认证、请求限制、目标配置
- `user_prompt_templates.json`: 用户自定义LLM提示词模板

### 数据流向
```
API请求 → 原始数据(crawler_data/) → LLM处理 → 总结文件(summaries/) → 日报(daily_reports/)
```

## 🗑️ 已清理内容

移动到 `archive/` 目录的废弃文件：
- 多个重复的认证模块（auth_extractor.py等）
- 调试和测试文件（debug_extraction.py等）
- 过时的配置和文档文件
- 重复的工具文件

保持项目简洁，专注核心功能。