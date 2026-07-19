**新工具/技术**
- Claude Fable 5：将从7月20日纳入 Max / Team Premium（50% 限额），Pro/Team Standard 通过使用额度访问并获得一次性 $100 额度，提升可用算力和可预期性。  
- GPT 5.6 / Kimi 3：dotey 指出 GPT 5.6 在非 UI 的任务上表现很好，Kimi 3 的发布被用来说明模型生态的快速迭代。  
- Opus 4.8：在高保真 UI 原型和还原设计稿上优于 GPT，适合做前端/交互实现。  
- Claude Design / Claude Code / Claude Desktop：Claude Design 输出 HTML/CSS/React+data.js，利于 AI 驱动的设计到实现流水线；Claude Code 与 Desktop 版配合支持本地化开发与工具调用。  
- Codex（含 CloudFlare 插件）：用于自动实现大量代码和发布流程，显著降低人工编码量并加速交付。  
- Cursor + 本地 Skill：dotey 把 Claude Design 的能力本地化（用 Cursor + Skill 复现），用于在本地做标注/编辑和迭代。  
- Playwright / Agent 的 Computer Use：用于 GUI E2E 自动化测试；Agent 的 Computer Use 可做更复杂的自动化（成本和稳定性代价更高）。

**核心观点/方法论**
- 代码实现越来越由模型承担，工程师角色向产品经理 + QA 转变：定义需求、验收与架构比逐行写码更重要，因为高质量模型能写出超越多数人的代码。  
- 高保真可交互原型可以取代传统产品文档：设计稿可交互、有模拟数据，交给 AI 基本能还原 90%+，加速沟通与实现。  
- Agent 化与自动化测试是 QA 的关键：实现功能同时要同步写自动化测试，Agent 可承担大量测试生成与执行工作，人负责黑盒与边界/安全验证。  
- 团队代码将被 AI 维护，但前提是普及高质量模型（如 GPT 5.6+）；这改变了代码所有权与审美标准的考量。  
- AI 应用的第一性原理不是造 App 而是替代工种：优先考虑哪些岗位能被 AI 替代，再倒推出产品形态和落地路径。

**实践经验/案例**
- BaoCut 开发循环：先用 Claude Design/Opus 4.8 产出高保真原型→同会话用 Claude Code/Fable 实现→Codex + CloudFlare 发布，短循环迭代，反馈驱动改进。  
- 强制写测试的落地方式：对没有测试的项目提示“请帮我初始化自动化测试”，已有项目在 AGENTS.md 中加入“实现时同步写测试并用测试验证”。  
- QA 实施：用 Playwright 做常规 E2E，复杂场景用 Agent 的 Computer Use 代替人工（成本高、稳定性差但能覆盖传统 E2E 做不到的情况）；人做黑盒/极端/安全测试。  
- 开源替代风险：市面上被推荐的“开源 CapCut / OpenCut”可能只是壳或已不再维护，评估时需注意代码活跃度与实质实现。  
- 资源与限额影响开发节奏：Claude 等模型的额度调整（如临时提升 50%）会影响可用性与选型，需在团队流程中考虑配额波动。