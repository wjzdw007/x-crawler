**新工具/技术**（如有）
- Claude Code From Scratch：开源电子书 + ~4300 行 TypeScript/Python 代码，逐章复现 Claude Code 的核心架构，适合手把手学习 coding agent 实现细节。  
- Orca（开源 IDE）：跨平台 coding IDE，集成并行 worktree、嵌入浏览器、远程控制等功能，定位为 Codex 类工具的替代/升级。  
- Claude Sonnet 5：Anthropic 新的 agentic 模型，Agent 能力与 Opus 接近且成本更低，内建实时安全防护，但换了分词器可能提高 token 消耗。  
- Claude Science：面向科研的 AI 工作台，整合 60+ 科学数据库、可本地运算与可复现的产物（含生成代码与环境），用于加速生命科学工作流。  
- Kimi Code 招人（社区招聘/扩散信息）。

**核心观点/方法论**（如有）
- 上下文质量 + 验证闭环是 Agent 成败关键：高质量、按需加载的上下文与自动化的测试/验证链能显著降低误判和回归风险。  
- 用用户价值而不是工程指标衡量 AI：部署次数/PR 占比等只是效率指标，真正重要的是用户体验和产品质量。  
- 技能与方法优于具体工具：强调培养 Agent 使用的“技能集”和敏捷维护流程，比押宝单一工具更有长期价值。  
- 文档按层次与索引管理：根级 AGENTS.md 作为索引，服务目录写清 bounded context，Agent 先定位再加载细节。  
- 契约测试优于手写说明：OpenAPI/Pact/contract tests 可作为“活文档”，更可靠地描述服务间协议并供 Agent 理解与验证。

**实践经验/案例**（如有）
- 微服务场景实操建议：推荐 monorepo 或“虚拟 monorepo”，配合根索引、每服务职责文档、mock server 与基于契约的本地测试，形成“写代码→跑测试→自我修正”的闭环。  
- 宣传指标与产品感知差距（Spotify 案例）：大量工程指标并未带来可感知的用户体验提升，提醒不要用产出量作为唯一成功标准。  
- 安全/信任风险示例（Claude Code 隐蔽信道指控）：逆向报告称在 system prompt 用几乎不可见的 Unicode 标记通过代理的用户，该做法引发审计与隐私担忧，需要公开解释与独立验证。  
- Sonnet 5 与成本注意点：模型在 agent 基准上进步明显，但新分词器导致 token 消耗上升，短期推广价对冲后仍需关注长期成本。  
- Claude Science 早期反馈：Gladstone、UCSF、Allen、MIT 等案例显示工作流整合与可复现性能显著提速科研，但仍需关注领域适配与数据合规。