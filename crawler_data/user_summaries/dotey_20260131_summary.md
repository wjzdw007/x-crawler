**新工具/技术**（如有）
- Moltbook：一个大量自治 Agent 的社区/广场（当前约 15 万 Agent），展示了 Agent-to-Agent 交互的可能性，但噪声和安全风险高。  
- Clawdbot / OpenClaw：面向长期存在的 Agent 基础设施与记忆持久化方案，dotey 认为它更可能成为持久的产品形态。  
- Claude Code / CLAUDE MD：在 Claude 生态里常用的说明文档模板（实测约 2.5k tokens），用于收纳必要的操作、代码规范和流程。  
- Coding Agent（Codex/Claude 等）工作流：把现成的开源代码作为参考并让 Agent 自行验证，是提高效率的常见实践。  
- AI 应用数据引擎方案（Forma / 若石的思路）：EAV + JSON Schema（零 DDL）、Postgres CTE+JSON_AGG（解决 N+1）、DuckDB+Parquet 做冷热分离，用于适配频繁变更的数据结构。  

**核心观点/方法论**（如有）
- CLAUDE MD 要短：只放 AI 没训练过或必须的核心信息，其他内容用链接按需加载，能节省 token 并减少干扰。  
- 用好 Coding Agent 的两条秘诀：一，给它高质量的代码参考；二，明确告诉它如何自行验证结果，这样事半功倍。  
- 记忆与上下文按需加载比把一切塞进客户端更重要：把常规设计/规范只引用名称或放 Skills，避免 token 爆炸。  
- 大规模 Agent 网络带来不可预期的二阶风险（文本病毒、协同越狱、僵尸网络式行为），不要在主机上直接运行，应在隔离环境中实验。  
- 当前模型权重是“死的”，单靠把大量 Agent 互联并不能改变模型内部权重，涌现更多是系统级交互而非模型自我进化。  

**实践经验/案例**（如有）
- 让 Agent 自测的实践：给 Codex/Agent API Key + 文档，让它写完后用真实 Key 调用接口（例：发布微信草稿），可直接验证并减少人工反复测试。  
- 验证清单示例：先编译/跑单元测试，连真实 API 做端到端验证，用 Chrome DevTools MCP 或 Playwright MCP 检查前端错误与日志。  
- 记忆持久化注意：过大 token 会把客户端撑爆，推荐把长期记忆下沉到专门的存储/Skill 层并按需拉取。  
- 产品判断：Moltbook 的“热度”可能短暂（用户注意力驱动），而像 Clawdbot/OpenClaw 这样的 Infra 式产品更可能长期存在并成为行业范式。