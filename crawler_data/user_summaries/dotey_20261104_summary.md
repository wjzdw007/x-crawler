**dotey 2026年11月04日 AI 技术分享分析**

**新工具/技术**
- **Baoyu Design Skill · DeepSeek Harness 插件**：提供一个统一入口，用来查看 Slides、Design、Dashboard、Motion 的全部生成结果并发起会话；配合 baoyu-design 新增的 Motion，支持多人协作、内置编辑器，并可随时修改文字。
- **OpenAI 收购 Pierre**：将 Trees（文件树）、Diffs（diff 查看与就地编辑）、Highlights（流式语法高亮）、Code Storage（Git 式代码存储）并入 Codex，补上“看代码、审代码”环节。
- **quiet.md**：兼容飞书的开源富文本编辑器，Rust + GPUI 直接用 GPU 绘制、无 WebView，百万字符文档每帧约 5ms；本地 XML 文件可被 Claude Code 等 agent 读写。
- **Cicada（知了）**：开源原生 macOS 实时语音翻译与会议助手，提供双语字幕、AI 纪要、虚拟麦克风同声传译和说话人识别，适配 Zoom、飞书、YouTube 等。
- **OpenAI Images 2.6**：支持导出 SVG 矢量图与 GIF 动图，出图速度提升 50%，API 分 Flare（速度）和 Sunburst（画质一致性）两档，价格与 2.5 持平。

**核心观点/方法论**
- **“审代码”正成为 AI 编程的新瓶颈**：AI 写代码越来越快、可并行多路任务，人需要审查的改动量随之暴涨；OpenAI 收购 Pierre 意在把“建分支→审代码→上线”整条流程收进 Codex。
- **内容生产的三层分化**（转阑夕“三种书”框架）：纯人工以证明未用 AI、AI 创作但读者仍想读、读者按需让 AI 生成；Amazon 正走向第三种，该框架可迁移到出版之外。
- **别用 AI 编程逃避验证**（转 oran_ge）：不断派活给 Claude/Codex 会让产品更精致，却没解决“有没有人要”；真正的瓶颈是把东西拿给人看、发冷邮件找用户。
- **视频应先有 Beat Sheet 再动笔**（转 goshenggo）：按情绪重音和信息密度排好节拍，每个 beat 对应一个 scene，再交给 Claude Code + HyperFrames 渲染，避免逐字稿被平均切、做成“电子 PPT”。

**实践经验/案例**
- **Motion 的“边渲染边看”**：不必等整段视频渲染完，一开始就能看到渲染过程并随时改文字；dotey 也坦承效果一般，需配合擅长 Motion 的模型（如 Opus 5.5）与专用提示词/skill，方向是“简单编辑器 + 标记评论即可修改”。
- **从开源组件预判产品走向**：dotey 早在 5 月就发现 Codex App 的 TreeView/Diff View 来自 Pierre，此次收购验证了判断，说明跟踪开源生态能提前读懂大厂产品路线。
- **Rust 构建产物的 AI 时代管理**（转 huacnlee）：多 worktree、多 agent 并行反复 build 让 target 动辄几十 G；通过优化 cargo 不删 target 避免全量重编，把单项目控制在 20G 左右。
- **人力继续向 AI/云倾斜**：Google 在加、法、德、日、瑞五国推自愿离职补偿（每年工龄一个月工资、上限 12 个月），DeepMind 与 Cloud 不在名单；同时 DeepMind 正为 AI Studio 和 Gemini API 招工程师。