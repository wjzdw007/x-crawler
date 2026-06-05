**新工具/技术**
- Claude Design（生成 SVG icon）：让 Claude 直接输出矢量 SVG，便于设计/迭代和无损放大，适合快速出图标原型。  
- feishu-claude-code-bridge（Zara Zhang）：开源桥接，把飞书与本机 Claude Code/Codex 连接，能把消息转成 CLI 调用并把结果回写到飞书；支持改用 codex profile 避开 claude -p 独立计费风险。  
- Codex Build iOS Apps 插件：在 Codex 右侧嵌入 iOS Simulator 画面并建立控制通道，支持 SwiftUI preview 和热重载，实现读代码→改 UI→看结果的闭环开发。  
- Glimpse（即览）：离线、不联网的手机 Markdown/HTML 预览工具，专注在移动端优化 AI 产出物预览问题。  
- OpenAI “Dreaming” 内存系统（以及 Anthropic 的类似能力）：后台自动提炼、合并和时效化记忆，使助手跨会话更“懂用户”，并提供记忆摘要页供人工校正。  
- 非官方 X 客户端调试工具：用于实时查看客户端发出的 API 请求，以降低因 bug 导致封号的风险。

**核心观点/方法论**
- AI Agent 与 PC/手机是互补关系，不会完全取代，而是改变交互—很多操作可直接对 Agent 下指令，减少打开多个 App 的需要。  
- SaaS 产品趋势：同时提供 CLI + Skill，让 Agent 学会调用产品功能以保住客户，避免被 Agent OS 替代。  
- 模型选择策略：优先 2–3 个你能用上的“最聪明”模型，权衡成本与稳定性；复杂任务建议多模型并行生成方案以互相校验。  
- 时间成本优先：Token 贵但省时间，时间往往比 Token 更值钱（更倾向用更贵的模型节约开发/验证时间）。  
- 团队与开发节奏：短期封闭、高强度迭代能极大提升架构和产出速度，集体主义/团队效率对 Agent 类产品尤为重要。

**实践经验/案例**
- 用 feishu-claude-code-bridge 的典型流程：在飞书指令中抓取并翻译网页、让 Codex 画图并把文档+图片创建到飞书，实现端到端自动化文档生产；在 6 月 15 日 Claude 计费变更前可切换到 Codex。  
- 在开发 Mac/iOS 应用时，作者感觉 Claude Opus 4.8 对实战更稳定，GPT-5.5 在某些场景反而下降表现（建议对比输出并回退到更稳模型）。  
- Codex iOS 插件实操价值：能在同一界面查看模拟器画面、选取元素（用 Accessibility 信息映射），并热重载 SwiftUI preview，显著缩短 UI 调试循环。  
- 做非官方 X 客户端要防范意外大量请求导致封号，优先做能实时观察请求的 Debug 工具再上手开发。  
- 行业人力动态：Cursor 等团队在招设计工程师，强调 taste、systems thinking 和对高质量体验的追求；说明产品/设计岗位在 Agent 时代仍有强需求。