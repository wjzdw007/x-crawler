**新工具/技术**（如有）
- Claude Design — 将设计直接交付为 HTML/CSS/React/data.js 等文本格式，便于 AI 分析组件/数据结构并纳入代码仓库版本控制。  
- CLAUDE.md — 在 Claude Design/Code 中的持久化提示/配置文件，用来保存反复叮嘱的约定和上下文。  
- Claude Code + Fable 5 工作流 — 用模型+代码替代传统非编软件，实现自动化视频制作与工具调用（如 ffmpeg、Remotion 等）。  
- Whisper（本地） — 全量语音转写并输出毫秒级单词时间戳，支持精确“卡点”与自动片段选择。  
- Subagents / Agent Harness 概念 — 子智能体用于自动挑片、过滤停顿词等；同时有公司招聘“Agent Harness 研究员”表明这是重点方向。  
- Remotion（React 动画） — 把视觉元素做成 React 组件，结合时间戳实现精确触发动画，替代 After Effects 的部分流程。  
- FFmpeg 自动化 + AI 生成 LUT（色彩查找表） — 通过代码调用 ffmpeg 做粗剪，AI 手写 LUT 并提供 HTML 滑块供人工微调回写参数。  
- baoyu-design skill — 本地运行的 Claude Design Skill，支持导入本地 Figma (.fig) 文件，重建设计系统以便脱网或私有化使用。

**核心观点/方法论**（如有）
- 设计结果要版本管理 — 把设计当文本交付并提交到 git，用 git diff 让 AI 清晰理解设计变更，降低同步成本。  
- 把 Claude Design 作为唯一设计源（单向同步 Claude Design -> Code）——先改设计稿再改代码，避免设计与实现长期不同步。  
- AI 放大了软件工程的重要性 —— AI 没有重新定义工程，而是把工程流程、上下文管理、版本控制、Harness 等做得更重要。  
- 要在模型强度与成本间权衡 —— Fable 5 等强模型会带来更长的“思考/验证”时间和高 token 消耗，需要路由与使用策略。  
- 用 CLAUDE.md 维护长期约定/上下文 —— 把常用规则和约束写进文件，保证多次交互和多任务场景下一致性。

**实践经验/案例**（如有）
- 版本管理实操：每次把 Claude Design 导出的 zip 解压到项目中替换旧版本，配合 git 提交与 diff 跟踪设计变更。  
- 全代码视频制作流水线：示例包含本地 Whisper 转写（含时间戳）→ Subagents 挑片 → ffmpeg 粗剪 → AI 生成 LUT + HTML 调色 → Remotion 制作动画 → Figma MCP 人机协作 → 回写代码并渲染 4K 成片。  
- baoyu-design skill 实战：能把本地 Figma 文件导入到本地 Claude Design，重建设计系统，便于在私有环境中复用设计资产。  
- 长任务与中断策略：用 /goal 让长任务更稳定，AI 停下时常用发一句“继续”或重启目标来恢复；但对高强度模型要控制频次以节省 token。