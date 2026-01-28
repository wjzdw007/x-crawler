**新工具/技术**
- Manus Skills（ManusAI 的 Skill 机制）：把会话/能力打包成可复用的 Skill，社区可共享，dotey 的 baoyu-skills 已可一键安装并在 Manus 里运行，方便把工作流模块化。  
- baoyu-skills（jimliu/baoyu-skills）：dotey 发布的一组 Skill（如 baoyu-article-illustrator、baoyu-cover-image、baoyu-infographic），用于自动生成文章配图/封面和信息图，已在实际案例中验证效果。  
- OpenAI Prism：内置 GPT-5.2 的云端 LaTeX 科研工作区，支持文献检索、公式/图表识别与协作，面向科研写作的专项工具。  
- MCP 协议 + Agent Skills 概念：MCP 被视为“能力”接入协议，Agent Skills 则是“知识/规范”层，通过二者组合让 agent 能按需加载工具和知识。  
- Codex CLI / Codex agent SDK：将 Codex 作 CLI/agent 使用的路径（包括 codex-exec、ts 封装）被讨论为构建 coding agent 的实践方式。  
- Gemini 的 Google Doc 同步（Gem 与 Google Doc 绑定）：把持续更新的 Google 文档作为 Gem 的知识源，使 AI 能自动获取最新规则/内容，打造可成长的“第二大脑”。

**核心观点/方法论**
- Agent-first 编程范式正在形成：从手工编码过渡到以 agents 执行为主，人的角色从“写代码”变为“设定目标与评估产出”，这会改变工程流程与组织形态。重要性：它放大生产力但对流程、验证与责任提出新要求。  
- Skills（知识）和 MCP（能力）的分层设计：把“可用能力”和“知识/策略”分开能让 agent 更可组合、可扩展，对构建复杂自动化系统很有价值。  
- 人机角色重新定位：agents 可并行、多任务且“不知疲倦”，但会犯概念性错误、假设错误或“为你好”式替人决策，需人类在高风险情境中保留审查或设计更严格的验证。  
- 法律与责任边界正在收缩：Workday 案显示法院可能把做出筛选决策的算法视为代理人，从而使供应商承担责任—技术部署必须同步法律合规与问责设计。  
- 模型“人格”是产品/目标的反映：不同公司的训练目标与奖励函数会沉淀成不同风格（如 Gemini、ChatGPT、Claude），这影响模型在不同任务上的适配性与信任度。

**实践经验/案例**
- baoyu-skills 在 Manus 上成功把网站/公告自动生成信息图，workflow 可复用，实际产出质量被认可（视频/演示）。  
- 写作流程推荐：先让 ChatGPT 提供写作建议，再把建议交给 Claude 去实际修改，二者互补提高效果。  
- Codex 实际问题：速度较慢、编码之外任务能力有限、写作能力不足，需在模型与产品设计上同时优化（例如更通用的 CLI agent）。  
- OpenAI Prism 的实践场景：对科研写作、文献管理、LaTeX 编辑有明显提升作用，适合需要高正确性与格式化输出的学术工作流。  
- 安全/运营风险示例：开源项目改名（Clawdbot→Moltbot）导致旧账号被骗子抢注并推币诈骗，提醒社区治理与账号迁移风险需要防范。  
- 用例提醒：大量自动化生成内容会带来“slopacolypse”（质量泛滥）与技能退化（人类写码/写作能力逐步萎缩）的现实问题，需建立质量控制与长期能力维护机制。