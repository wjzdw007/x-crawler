**dotey 今日分享解读（2026-11-26）**

**新工具/技术**
- **Cindy /artifacts**：基于开源项目 Open Artifact，可生成文档、slides、白板、网页等，插件机制可自定义窗口与功能，Artifacts 既能存本地也能部署到自己的服务器，即将集成。
- **UI SDK（shadcn/ui 团队）**：把弹层、方向键移焦点等交互拆成 Agent 可调用的“行为原语”，因此与组件无关，可跨 React、Vue、Svelte、Solid 复用。
- **Lemo-opuscar**：开源视频风格库，发布两周破 20K star，含 99 种风格与“改变风格”玩法，2.1 版计划用 Opus 5.6 重做旧风格并适配 Gemini。

**核心观点/方法论**
- **提示词从“约束”转向“释放”**：他转的 Opus 5.6 演示网页提示词明确要求 no anchor bias、强调“你有审美也有能力”，说明高质量产出更依赖给足自由度与品味引导，而非堆砌限制。
- **平台合规边界趋严**：仅接入 ACP 并不等于拿到免死金牌，还必须保持 thin-client editor 定位，否则照样封号，套壳式集成的风险正在上升。
- **年度叙事判断**：23 LLM→24 Agent→25 RL→26 continual learning，2027 属于 USER；当 verifiable reward 被吃尽，人心里模糊的判断和对用户的理解才是最稀缺资源。
- **GPT-6.2 计费“朝四暮三”**：修正折扣后名义价未变，但同样的活会多耗额度——Astra 快 40%、Sol 快 25% 触顶，用户需重算成本预期。

**实践经验/案例**
- **AI 视频工作流**：用 Antigravity + Gemini TTS + OpenArtifact Motion 给 shadcn 的 UI SDK 英文讲解加中文配音，显著降低观看门槛。
- **薅额度时机**：感恩节 Antigravity 重置全体用户 Gemini 配额，适合集中跑实验或批量任务。
- **先核实再传播**：转发图片前溯源（指出他人盗图），以及 Denny's 铭牌“摘了又挂、店员说法矛盾”的品牌公关乌龙，都说明信息链未闭环前不宜下结论。