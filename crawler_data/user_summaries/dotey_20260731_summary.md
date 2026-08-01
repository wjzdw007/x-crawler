**新工具/技术**（如有）
- Agentic Coding Round / AI Coding Agent：面试环节要求用 AI agent 在现有代码库上完成复杂任务，反映“以 agent 驱动开发”成为考核点。  
- DeepSeek V4-Flash（正式 API，Responses 原生适配 Codex）：284B 混合专家模型，优化后训练提升智能体能力，直接兼容 Codex 客户端。  
- Codex（OpenAI 的编程助手）与 Responses API：DeepSeek 支持后可一键切换 Codex 的 CLI/桌面/VS Code 流程，降低接入门槛。  
- PI / Claude Code SDK（替代后端方案）：可用来快速复刻 Codex 体验，说明底层接入多模型已成实战路径。  

**核心观点/方法论**（如有）
- 面试重点从纯算法向分布式系统与 agent 协作转移：说明工程师需具备大规模系统设计和 AI 工具协作能力，而非仅靠刷题。  
- “会驾驭 AI 工具写代码”正在成为基本功：企业开始考察如何拆问题、编排 Agent、监督循环与成本控制。  
- 后训练对智能体场景的提升显著：DeepSeek 的例子表明调优能在 Agent 任务上超过参数/架构带来的差异。  
- 成本与上下文窗口成为关键设计变量：大上下文（1M tokens）与低 Token 价差能重塑 Agent 循环的可行性与架构选择。  
- 产品层面要把 Stop 设计为“中断 run 非清空记忆”：流式输出需要 session 化与半截 tool_call 的恢复策略。  

**实践经验/案例**（如有）
- 候选人面试流程详解：招聘电话→两轮 60min 技术面（KV 存储与任务调度）→48h take-home（分布式 webhook，重试/死信队列）→四轮现场（编程、系统、行为）→可选 Agentic Round。  
- 48 小时 take-home 要交付可运行系统且逐行审查，强调设计决策需能逐条解释。  
- 现场编程考察偏系统底层（Python 生成器/异步/并发）与渐进式多阶段题，系统设计题聚焦 GPU 分配、自动扩缩容与分布式协调（如“设计 ChatGPT”）。  
- Agentic Round 实操提示：遇到手写难以解决的大问题，需把任务拆给 Agent、设计验证与恢复流程，并能衡量 Token 成本与循环效率。  
- 流式中断恢复实作要点（来自 xiongchun007）：每个 Task 对应一个 Session，停止时保存上下文；对半截的 tool_call 需补 recovery result 以恢复合法状态。