**新工具/技术**
- Chrome DevTools 调试 Codex App：通过命令行用 --remote-debugging-port 启动 Codex，然后在 chrome://inspect 打开调试界面，方便调试 browser-agent 行为。  
- Codex Chrome 扩展：让 Codex 能在浏览器中直接执行任务、并行后台多标签运行，适合需要登录或跨页面的自动化流程。  
- GPT-Realtime-2 / GPT-Realtime-Translate / GPT-Realtime-Whisper：三款实时语音模型，Realtime-2 提升推理和长上下文（128K），Translate/Whisper 支持实时翻译与流式转录。  
- Claude for Microsoft 365：Anthropic 把 Claude 嵌入 Excel/PowerPoint/Word（GA）和 Outlook（公测），实现跨应用带上下文的办公自动化。  
- Mirage 虚拟文件系统：统一挂载 S3/Drive/Slack/Gmail 等异构存储，Bash 风格操作对 Agent 友好，变文件系统为资源中心。  
- Claude “Dream” 功能：让 Agent 在离线/异步环节对记忆做反思、整理和改进，作为工程化的持续学习循环。  
- openai-cli：OpenAI 官方命令行工具（开源），可在终端调用 Responses/API、内置 cloud tools，输出 Unix 风格结构化结果，便于 CI/CD 与脚本化自动化。

**核心观点/方法论**
- 语音代理成为实时“协作者”：Realtime-2 把听、推理、工具调用和透明化反馈结合，能在对话中连续解决复杂任务，改变语音交互的设计边界。  
- 持续学习不必改权重：Claude 的 Dream 展示通过独立的离线 curation 循环（memory reprocessing）实现“持续学习”，对工程可行且更易控。  
- 把数据层统一成 VFS 是 Agent 扩展的关键：mirage 说明将多源数据做统一访问层，可大幅简化 Agent 的检索与组合能力。  
- 公司治理与 AGI 风险不可忽视：Altman‑Murati 的短信提醒，权力与治理决策可能基于“谁该掌控 AGI”，对行业战略与合规有直接影响。  
- RLHF 等强化学习反馈会产生副作用：中文语料和奖励倾向导致模式坍缩（如“稳稳地接住你”），需在训练与标注设计上更精细化控制。

**实践经验/案例**
- Codex Chrome 调试技巧：退出 App 后用 open /Applications/Codex.app --args --remote-debugging-port=8315 … 启动，然后在 chrome://inspect 打开调试目标。  
- 浏览器中用 Codex 的典型场景：处理需登录的内部后台、CRM 更新、多页面表单、调试业务流程等，能结合插件与页面脚本完成端到端任务。  
- openai-cli 的实战价值：把 Responses/工具调用搬到 shell，可直接用于自动化脚本、CI/CD、服务器端 Agent 工作流，减少写 SDK 的开销。  
- Claude + M365 的工作流示例：在 Outlook 草拟邮件→把 brief 导入 Word→基于文档在 Excel 建模型→生成 PowerPoint，Claude 跨应用携带上下文，减少重复输入。