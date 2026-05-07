**新工具/技术**
- MRC（Multipath Reliable Connection）｜OpenAI 等联合开源的网络协议，将训练数据包拆分并走多路径、采用 SRv6 源路由；用于大规模 GPU 集群以降低链路抖动和故障影响。
- Colossus 1（SpaceX/xAI 数据中心算力）｜Anthropic 与 SpaceX 的算力合作，短期内释放大量 GPU 资源，直接提高 Claude 的使用上限。
- TRAE SOLO Mobile（三端 Agent 平台）｜移动、Web、桌面三端同步的 Agent 工具，支持定时任务、飞书 CLI 等企业协作接入，定位为“意图路由器”。
- Cursor 3.3 的 Context 可视化｜可以查看 Agent/Skills/MCP 等在上下文里消耗的 token，便于排查与优化。
- Warp 的 Oz Skills（开源 Skill 集）｜Warp 团队开源的一组 Agent Skills，覆盖 Git/GitHub 流程、web 审计、dbt 模板等工作流加速模块。
- Plannotator（插件）｜可评论/编辑/共享的 Plan 评审工具，支持 agent 迭代 plan，类似 code-review 的计划评审流程。

**核心观点/方法论**
- 网络与基础设施决定训练可用性：MRC 用多路径与源路由把“网络”从瓶颈变成可控因素，能显著提高大规模训练的鲁棒性与成本效率。
- 算力供给决定产品开门槛：Anthropic 获得 Colossus 1 即能立刻放开使用限额，说明算力可用性直接影响产品体验与商业扩张速度。
- Agent 正从“工具”变成“助手/工作流中枢”：TRAE 与 Claude 的实践表明，Agent 不再仅是编码助手，而是写作、报表、监控等日常办公流程的自动化执行者。
- 手机是“意图路由器”而非远程桌面：用手机下发指令、语音触发、确认结果，比在手机上精细操作更符合移动场景的效率和交互逻辑。
- 观察与度量是优化前提：Cursor 的 context 统计、定时 Loop 与技能拆分都是把复杂系统可观测化，从而可定量优化的实践方法。

**实践经验/案例**
- MRC 部署效果：OpenAI 在多站点的 GB200 超算上部署后，重启交换机与链路抖动对训练基本无感知，节省了重跑与等待时间。
- Claude + Colossus 1：短期内放开 Claude Code/Claude API 限额，直接提升用户体验，显示出“有算力就能放量”的事实逻辑。
- TRAE SOLO 使用感：作者用手机下发任务、语音交互、定时任务（Loop）把重复且不紧急的工作交给 Agent，手机只负责意图与验收，极大降低了门槛与上下文切换成本。
- Plan-review 流程改进：Plannotator 把 plan 的生成—评审—迭代流程产品化，能把 agent 输出纳入人类 code-review 式的质量控制闭环，适合团队协作场景。