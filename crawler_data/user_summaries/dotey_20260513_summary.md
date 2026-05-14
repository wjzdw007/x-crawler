**新工具/技术**
- Claude Agent SDK / Claude Code / claude -p — Anthropic 的 agent/编程化调用栈与终端工具，支持把大模型当作可编排的执行单元。  
- MCP connector（如 Ironclad、DocuSign、iManage、Everlaw、CourtListener、Trellis）— 把真实业务数据源接入 agent，消除手工复制粘贴。  
- Skills / Plugin 机制 — repo 中的 SKILL.md + .mcp.json + agents 的打包格式，便于把领域 playbook、agents 和 connectors 一起分发。  
- Whisper / WhisperKit — 用于生成带 word-level timestamps 的语音识别，配合大模型做断句和标点用于生成高质量 SRT。

**核心观点/方法论**
- Skills = 可读的“工作手册”，把如何做（步骤、判定、输出格式）显式化，便于可复用与审计。重要性：把领域知识从人脑转成可被 agent 理解的规范。  
- Agent 有三层：主 Agent（协调）、Subagent（并行隔离执行）和 Scheduled agent（定时后台任务），分别解决上下文爆炸、并行处理和持续监控问题。  
- Plugin 把 skills、scheduled agents、MCP 配置打包，一键装配整套业务能力，降低集成门槛并加速落地。  
- 数据连通比模型本身更关键：没有 MCP connector，再好的 skill 也没法处理真实业务。  
- 产品价值来自行业 know‑how 与体验设计：外包不懂业务会在需求传递中失真，内生的复合型人才更容易做出有用产品。  
- 商业/限额策略会改变技术可行性：Anthropic 的额度与 SDK credit 调整会直接影响自动化成本与第三方工具生态。

**实践经验/案例**
- NDA-review：在 commercial-legal 仓库里，nda-review 的 SKILL.md 规定先比对哪些条款、按 playbook 打绿黄红、何时升级、输出用 Word 修订模式——把审查流程模板化。  
- tabular-review 用 Subagent 为每份合同并行跑单文档处理，主对话只收汇总表，避免主上下文被几百份文件刷爆。  
- renewal-watcher（Scheduled agent）每周扫描合同库并把 90 天内到期合同推 Slack，实现自动提醒与低运维监控。  
- SRT 实操要点：先生成 word-level timestamps（或用 WhisperKit 本地），再用大模型补标点断句并重新对齐时间戳，分块时避免切中一句话；否则会出现超长 cue 或重复幻觉问题。  
- 商业影响实录：Claude Code 周额度短期上调 50% 对交互用户友好，但程序化调用被分配很小的月度 credit（不同套餐），重度自动化/第三方工具用户需转为按量 API 或承担额外费用。