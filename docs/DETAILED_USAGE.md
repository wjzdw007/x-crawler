# X 推文爬虫系统使用与功能详解

本指南覆盖安装、配置、运行模式、数据结构以及可扩展点，帮助你快速理解并使用本仓库的完整能力。

## 1. 架构概览
- **命令入口**：`run_crawler.py` 负责解析命令行参数并调用爬虫/总结流程。
- **爬虫核心**：`crawler.py` 提供 `XCrawler` 类，用于时间线抓取、数据去重存储、按用户拆分以及调用总结。
- **总结引擎**：`summarizer.py` 中的 `TwitterSummarizer` 负责生成提示词、调用 LLM（或模拟输出）、保存总结与 Prompt。
- **配置加载**：`config_loader.py` 统一合并 `.env`、`config.json` 与默认值，并提供代理、认证和通用设置。
- **辅助脚本**：`auth_setup.py` 自动从浏览器登录会话提取认证；`test_config.py` 验证配置有效性。

## 2. 环境准备
1. **安装依赖**
   ```bash
   ./setup.sh
   # 或
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **配置认证与模型**
   - 推荐：复制 `.env.example` 为 `.env`，填入 `X_AUTH_TOKEN`、`X_CT0_TOKEN`、`OPENROUTER_API_KEY`、`OPENAI_MODEL` 等。
   - 备选：复制 `config_template.json` 为 `config.json` 后手工填写；或运行 `python auth_setup.py` 自动生成。
   - 优先级：`.env` > `config.json` > 默认值，加载逻辑见 `config_loader.py`。
3. **验证配置**
   ```bash
   python test_config.py
   ```
   通过后再启动爬虫，避免因认证缺失导致请求失败。

## 3. 运行方式
`run_crawler.py` 暴露以下常用参数：
- `-c/--count`：指定抓取推文数量（默认读取 `config.json` 的 `targets.daily_tweet_count`）。
- `--timeline`：选择时间线类型 `recommended` 或 `following`，默认 `recommended`。
- `--max-pages`：限制翻页次数，防止无限爬取。
- `--user-summaries`：基于每日用户数据生成个人总结；配合 `--count` 可在抓取后立即生成。
- `--force`：覆盖已有总结文件（只在 `--user-summaries` 模式下生效）。

### 示例
```bash
# 使用默认配置抓取推荐时间线
python run_crawler.py

# 抓取 200 条并生成用户总结（不生成全局报告）
python run_crawler.py --count 200 --user-summaries

# 仅为昨天的用户数据生成总结（不抓取新数据）
python run_crawler.py --user-summaries

# 指定 following 时间线且限制翻页
python run_crawler.py --count 80 --timeline following --max-pages 3

# 强制覆盖已有总结
python run_crawler.py --user-summaries --force
```

## 4. 爬虫流程（`crawler.py`）
1. **会话配置**：启动时加载认证 cookie/header、代理，设置类浏览器 UA，并执行限流与随机延迟。
2. **抓取**：
   - 使用 GraphQL 端点请求时间线，支持 `recommended` 与 `following`。
   - 自动检测压缩/编码问题并保存原始响应到 `crawler_data/raw_responses/` 以便排查。
3. **解析与去重**：
   - 完整提取长文 `note_tweet`、转推、引用、媒体信息以及互动数据。
   - 通过字典缓存实时去重，按创建时间排序后截取精确数量。
4. **存储**：
   - 日汇总：`crawler_data/daily_posts/{YYYYMMDD}_{timeline}_posts.json`（含抓取统计与去重信息）。
   - 按用户：`crawler_data/users_daily/{username}_{YYYYMMDD}.json` 便于后续生成个人总结。
   - 原始响应：`crawler_data/raw_responses/` 自动清理 3 天前文件。
5. **统计**：完成后在控制台输出原创、转推、媒体等基础分布统计。

## 5. 总结流程（`summarizer.py`）
1. **配置与模板**：
   - 自动读取 `OPENROUTER_API_KEY`/`OPENAI_API_KEY` 与 `OPENAI_MODEL`，缺失时降级为模拟总结。
   - 支持用户级提示词模板 `user_prompt_templates.json`，可为特定用户名设定分析角度。
   - 维护用户分析画像（如 `elonmusk`、`dotey` 等）并支持自定义持久化。
2. **数据准备**：
   - 将推文转为结构化嵌套格式（原创/转推/引用关系、媒体类型），并生成用于 LLM 的 JSON 片段与统计说明。
   - 同时提供简化版本，仅包含前 20 条核心内容以控制上下文长度。
3. **提示词与调用**：
   - `generate_simple_prompt` 根据模板注入用户信息与推文 JSON；`save_prompt_to_file` 将完整 Prompt 存到 `crawler_data/prompts/` 便于复现。
   - `call_llm_api` 通过 OpenRouter 按主模型+后备模型链路调用；失败时自动切换或输出模拟总结。
4. **输出**：
   - 用户总结：`crawler_data/user_summaries/{username}_{YYYYMMDD}_summary.md`。
   - 其他模式：`generate_summary`/`generate_trending_summary`/`generate_category_summary` 可输出 JSON 或 Markdown，默认保存于 `crawler_data/user_summaries/`。

## 6. 数据目录与文件说明
```
crawler_data/
├── daily_posts/         # 按日期+时间线的去重推文合集
├── users_daily/         # 按用户拆分的每日推文（用于个人总结）
├── raw_responses/       # 原始 GraphQL 响应，自动清理
├── user_summaries/      # 生成的 Markdown/JSON 总结
└── prompts/             # 保存下发给 LLM 的完整 Prompt 记录
```

## 7. 常见问题排查
- **无认证/403**：确认 `.env` 或 `config.json` 的 cookie/header 已填写且未过期；必要时重新运行 `auth_setup.py`。
- **返回空数据**：可能是限流或账户状态变化，可降低 `--count`、增加 `--max-pages` 或检查代理。
- **LLM 失败**：缺少 API Key 或网络受限时会降级为模拟总结；检查 `OPENROUTER_API_KEY`、`OPENAI_MODEL` 及网络。
- **重复数据**：抓取结果会自动去重并合并到当日文件，可直接重跑，无需手动清理。

## 8. 快速扩展
- **新增用户模板**：在 `user_prompt_templates.json` 添加用户名键，定义 `template` 与 `description`。
- **自定义分析画像**：调用 `TwitterSummarizer.add_user_profile` 或直接编辑 `user_analysis_profiles.json`，可持久化新的关注点与关键词。
- **调整限流策略**：通过环境变量 `REQUESTS_PER_HOUR`、`RETRY_ATTEMPTS`、`RETRY_DELAY`、`TIMEOUT` 修改请求节奏。
- **添加时间线类型**：在 `XCrawler.api_endpoints` 中补充 GraphQL 端点，并更新 `get_timeline_params` 以匹配参数需求。

## 9. 最佳实践
- 先运行 `python test_config.py` 确认认证与代理，再进行大规模抓取。
- 使用 `--max-pages` 防止无限循环，尤其在目标数量较大时。
- 保存的 Prompt 能复现实验过程，建议版本化管理 `crawler_data/prompts/`（排除敏感 cookie）。
- 长期运行时关注 `crawler_data/raw_responses/` 的清理策略，默认仅保留 3 天。

## 10. GitHub Actions 自动化运行
仓库提供一套 Workflow 方便定时或手动执行爬虫/总结任务（详见 `.github/workflows/README.md`）：

- **`daily-crawler.yml`（主工作流）**：每天 09:00（北京时间）定时抓取、总结并推送数据，支持 `tweet_count` 和 `force_summary` 参数；可在 Actions 界面手动触发。
- **`hourly-crawler.yml`**：按小时抓取更高频的时间线数据，可调整 cron 以匹配自定义频率。
- **`daily-summary.yml`**：针对已有数据的每日总结流程，适合对历史抓取数据批量补充报告。
- **`manual-summary.yml`**：仅手动触发，接受 `date`（默认昨天）和 `force` 参数，用于补跑或重生成指定日期总结。
- **`notifications.yml`**：通知示例集合，展示 Telegram/企业微信/钉钉等集成方式，实际通知逻辑已包含在主工作流中。

### 初始配置
1. 仓库 Settings → Secrets and variables → Actions 中添加认证与模型相关 Secrets：`X_AUTH_TOKEN`、`X_CT0_TOKEN`、`X_CSRF_TOKEN`、`X_BEARER_TOKEN`、`OPENROUTER_API_KEY`、`OPENAI_MODEL`。
2. Settings → Actions → General → Workflow permissions 选择 **Read and write permissions**，以允许工作流提交数据。
3. 推送前可执行 `./scripts/validate-workflows.sh` 或使用 `actionlint .github/workflows/*.yml` 验证语法。

### 常见用法
- 定时运行：保持默认 cron（`daily-crawler` 每天 09:00，北京时间），或根据需要修改工作流文件中的 `schedule.cron`。
- 手动运行：在 Actions 页选择相应 Workflow，点击 **Run workflow**，按需填写输入参数（如 `tweet_count`、`date` 或 `force_summary`）。
- 报告下载：完成后在对应 Run 的 Artifacts 下载 `crawler-report` 或在仓库新增的 `report.md` 查看摘要。

> 提示：若 Workflow 未执行，先确认仓库开启 Actions 权限、Secrets 填写完整且 cron 允许 5-15 分钟的触发延迟。

以上内容覆盖从配置到扩展的完整路径，便于落地运行与二次开发。
