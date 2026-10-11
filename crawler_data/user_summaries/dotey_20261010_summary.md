**新工具/技术**
- Carbon（Google 内部新模型）：Google 在 Jetski（内部 AI 编程工具）上测试的新模型，有员工称其“编码感觉像 Opus 5.5”，具体跑分和发布时间未公开，可能用于提升 Gemini 的编程能力。  
- Claude Dashboards / Claude Motion（Anthropic）：Dashboards 能把公司数据接到 BigQuery/Snowflake 等并生成自动更新看板；Motion 把报告/图表生成几十秒的动画讲解，适合汇报和产品演示。  
- REA（Reverse Engineer Anything）：把反汇编/逆向工具接入 Claude Code 等智能体的项目，能在本机分析原生程序、Electron、APK、固件、以太坊字节码等并把结果交给智能体，强调合规与本地分析。  
- Codex（上下文设定）：公开信息显示 Codex 的默认上下文长度被选为 ~300k token，权衡了成本与效用。  
- magpie（本地 agent 可观测性与调优）：提供本地回放和观测，按真实调用自动为每个 agent/模型调优压缩阈值和缓存策略，做到千人千面。

**核心观点/方法论**
- 编程仍是 Gemini 的短板，需要用基准（如 Terminal Bench）和第三方跑分对比，来驱动模型改进和产品选择；可直接影响开发者的生产力。  
- 团队规模在 AI 时代趋向小而精（two-slice）：“海盗”快速试错、“架构师”负责稳健扩展，能降低沟通成本并提高迭代速度。  
- 把 UI/交互类修改从写详尽技术方案转为原型驱动，利用 agent 的浏览器标记与评论实现快速反馈和同步代码，强调原型优先的工程流程。  
- AI 生成的高质量草稿会把校验成本转移给审查者；因此必须建立更严格的审查与验证流程，而非单纯禁止使用 AI。  
- 上下文压缩与缓存策略直接影响成本与体验，默认策略可能“太晚”触发压缩，主动提前压缩/调整 cache TTL 可显著省 token。

**实践经验/案例**
- 用 Claude Dashboard 分析 X（Twitter）数据：下载 Artifacts/各 Tab 导出的数据，作为附件上传到 Dashboard，给出“帮我分析哪些推文更受欢迎、怎么优化”的提示即可获得可视化看板与建议。  
- 原型到代码的实际工作流：先用 Fable 做原型，再用 Agent 内置浏览器的“标记”工具标注修改点，交给 Opus 执行，最后由 Fable 验收；适合以 UI 改动为主的迭代。  
- REA 的三个示例验证效果：DX-Ball（还原并通过测试）、Notion 桌面版（追踪进程间通信链路）、PC-98 游戏 TH04（从 16 位指令还原弹幕算法），显示逆向能生成可验证的证据链。  
- 节省 token 的实操建议：对含大上下文的会话提前触发 auto-compact（如 /autocompact 400k 或在配置里设置 autoCompactWindow），并调整 promptCacheTtl/subagentPromptCacheTtl。  
- 用 magpie 做个性化调优：在本地用真实请求回放不同压缩阈值与缓存时长，自动找出对你最省 token 且效果最好的配置。