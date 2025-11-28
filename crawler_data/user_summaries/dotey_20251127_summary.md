**新工具/技术**
- Nano Banana Pro: 强大图像编辑生成模型，支持简单prompt如“Upscale to 4K”+“上色”翻新老照片，无需复杂工程；GeminiApp免费试用。
- Claude Agent SDK: 用于企业级设计系统开发，dotey将在FEDAY 2025分享落地经验。
- Puppeteer MCP: 浏览器自动化工具，提升Agent端到端测试，如模拟用户操作claude.ai克隆版。
- Claude Opus 4.5: 新模型视觉/工具调用升级，支持effort参数调节智能/成本；配裁剪工具处理密集图像。

**核心观点/方法论**
- 长运行Agent需软件工程harness: 初始化Agent建JSON功能清单（200+项）、Git进度文件、每次只做一功能+浏览器验证；解决无记忆/过早停止问题，确保跨窗口协作。
- AI尽头是软件工程: Agent放大工程师技能，非取代；高级工程师prompt清晰、任务拆解、验证heuristics强，更敢采纳输出。
- Claude 4.5 prompting: 用effort调智能、温和工具指令防overtrigger、强制读代码防猜测、简洁spec防overengineer；迁移插件加速应用。
- System prompt缓存优化: 大用户体量下加{{SESSION_ID}}提升hit rate，避免全局一致溢出；反范式优先会话内缓存。

**实践经验/案例**
- 老照片翻新: Nano Banana Pro黑白照两步“1. Upscale to 4K 2. 上色”，无需复杂prompt，输出稳定4K。
- 宝宝认知图: 3D黏土风元prompt（8h后公布），特定场景先玩；调风格确保2-5岁质量。
- 电商作图: 以实物材质锚点+AI场景杠杆，用宝玉prompt可视化实践，平衡成本/效率/还原度。
- Pixar 3D群自拍prompt: 自定义人物/环境/性格，Nano Banana Pro生鲜艳动态场景；中英版通用，改名即用。