**dotey 2026年10月22日分享内容分析**

**新工具/技术**
- Claude Code 云端任务卡片：项目提交到 GitHub 并通过 connector 连接后，可把部分任务放云端执行，便于多任务并行，但本地工具更丰富。
- 1Password for Agents：Agent 登录时向密码库请求凭据，用户批准后由 1Password 自动填充，Agent 看不到密码；dotey 对主要账号仍持谨慎态度。
- Agent Skills 标准化：Claude 把 Agent Skills 捐给 Agentic AI Foundation；dotey 希望 Claude Code 直接读取 `.agents/skills`，而不是另立 `.claude/skills`。
- Marathon Fusion 聚变中子炼金：用聚变中子把汞变成金，但真正商业价值在钼-99、锕-225 等医用同位素，炼金更多是叙事和补贴收入。

**核心观点/方法论**
- 安全更新要追到语言运行时层：Node.js 22/24/26 修复 Brotli 越界写入、HTTPS 证书校验、DNS NUL 截断等漏洞，并内置 eMudhra 坏证书黑名单；20/25 已无补丁，服务端应尽快升级。
- 浏览器之外也要有证书拉黑机制：Node 内置 CA 名单却缺少浏览器式动态吊销，旧版可能放行坏中间证书签出的假证书；基础设施层需要补“吊销链”。
- AI 语音书应先做“发音导演”：用大模型标注多音字拼音、停顿和情感，再驱动 TTS；并用 Kaldi 解码音素序列核验实际读音，比人工试听更可规模化。
- Agent 协作可设 advisor：外出时让主 Agent 有问题找 advisor 确认，如 `/advisor fable` 或让 Opus 当 advisor；把监督权交给更强模型，自己只处理关键决策。
- 订阅额度可能被“重置节奏”掩盖：dotey 猜测 Codex 28 天重置活动与额度变少、频繁重置维持旧用量有关，说明模型“耐用量”仍是产品竞争点。

**实践经验/案例**
- TTS 多音字校验：把 TTS 音频交给 Kaldi 识别，不看识别出的汉字，而看解码路径上的音素序列，再与目标字正确读音逐项比对。
- AI 语音书选型：高质量真人朗读仍优于 AI，AI 适合自制且需先做发音标注；付费 TTS 普遍好于开源，但性价比难统一推荐。
- eMudhra 事件响应：8 枚中间证书私钥过弱，Chrome/Firefox 当天拉黑，Apple/Microsoft 跟进，Node.js 10 月 21 日发版内置黑名单，生态响应以天计。
- 账号安全案例：晚点News 的 X 账号被黑、卡普空 CAPCOM ID 遭攻击影响 1177 万账户；品牌账号与游戏账户都要重视凭据和会话安全。
- 资本与基建：DeepSeek 新一轮融资约 1000 亿元，腾讯、宁德时代出资最多；dotey 转推的 AI 半导体长文认为开源不会打穿旗舰 token 毛利，需求仍看阶跃式增长。