**新工具/技术**
- Microsoft Copilot Agent Mode（Word/Excel/PowerPoint 默认体验）：把“智能体”直接放到文档/表格/幻灯片画布上，支持多步操作与上下文推理，面向已订阅 Microsoft 365 的用户即时可用。  
- ChatGPT for Google Sheets / ChatGPT for Excel 插件：在表格内用自然语言建表、写公式、分析数据，官方插件提升稳定性和工作流整合。  
- GPT-5.5（含 Codex 升级）：OpenAI 宣布能力显著提升且延迟不增，Codex 也支持 GPT-5.5；API 很快跟进，提供更大上下文窗口与新的定价档。  
- Codex 的浏览器/电脑操控与 Auto-review：能在网页上点击、填表、截图并迭代执行，遇高风险操作自动触发审查智能体；并与 gpt-image-2 集成用于原型/演示配图。  
- Anthropic Claude Managed Agents 的记忆功能（公测）：基于文件系统的跨会话记忆，支持权限控制、并发访问与审计日志，便于多智能体共享与回滚管理。  
- Claude Code vs Codex 使用 Skills 的差异：使用的基础模型、可用工具与运行环境（harness）不同，编写 Skills 需针对 agent 的能力与限制做定制化。

**核心观点/方法论**
- Agent = Model + Harness：模型负责推理生成，harness 提供工具接入、权限、记忆、审计、沙箱与验收等，使“会说话”的模型变成“能做事”的智能体；这是实现可靠自动化的关键。  
- AI 从聊天窗口走向工作画布：竞争重心从纯对话界面转移到办公工具/工作流内嵌（Office、Sheets 等），谁能深度嵌入日常工作流谁就更有护城河。  
- “控制权不可谈判”：在增强自动化的同时必须保留用户预览、回退与人为审批机制，以维护合规性、可解释性与信任。

**实践经验/案例**
- Microsoft 内测数据：Agent Mode 令 Excel 用户参与度 +67%、满意度 +65%，Word 参与度 +52%，PowerPoint 新用户留存 +36%，表明画布化智能体能显著提升采纳。  
- GPT-5.5 基准表现：在多项基准（如 Terminal-Bench、FrontierMath）上大幅提升，但在部分工程化编码基准仍有竞品优势，体现总体能力上升同时存在领域差异。  
- Anthropic 记忆落地效果：Rakuten 首次出错率下降 97%；Wisedocs 文档验证流程提速 30%；Netflix 将多轮对话中的人工纠正带入后续会话，降低重复工作。  
- Codex 应用示例：自动化注册流程测试、在 Office/Drive 里生成并预览文档/表格/演示、用图像生成功能做原型配图，工作流从“建议”向“自动执行并验证”演进。  
- Skills／Harness 开发教训：写 Skills 时需先检测 agent 当前能力与权限，针对不同模型/环境定制提示、权限与回退策略，避免“聪明但没办法行动”的空转。