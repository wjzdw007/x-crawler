**新工具/技术**
- Claude Opus 4.6（Anthropic）+ 新版本上线，Pro/Max 用户可领取限时 50 美元额外额度（需在规定时间前开启 Extra Usage，额度 60 天内有效）。  
- Extra Usage（Anthropic 功能）+ 开启后可额外计费并领取赠送额度；手机端 App 无法设置，需网页版操作。  
- Claude Code 的 /insights 命令 + 在本地生成完整 HTML 报告，分析过去交互、项目复盘与优化建议，数据不出本地。  
- xhs-images skill（小红书图片生成）+ 用于生成推文配图（dotey 指出图片来自该 skill）。  
- YouMind 0.8 + 新三栏布局、海量 Skills，用于收集和学习他人提示词与技能库。  
- Auto-reload（自动充值）+ 与 Extra Usage 共同作用，开启会在额度用尽后按标准费率继续扣费，要谨慎配置。

**核心观点/方法论**
- Agent 设计要“说清楚要求并告诉 Agent 怎么验证”+ 验证流程是使 Agent 稳定完成任务的关键（类型/编译/测试等都是验证手段）。  
- TypeScript 更适合构建 Coding Agent + 提供类型层面的自动校验，能让 Agent 在生成-验证-修复循环中更可靠。  
- AI 编程类似“高级语言 + 编译器”+ 未来人类用自然语言描述需求，AI 将翻译成可执行代码，用户主要负责验收结果。  
- 对于赠送额度要保持谨慎态度+ 社区提醒 Extra Usage 可能有“token/计费陷阱”，务必确认 Auto-reload 与计费策略。

**实践经验/案例**
- /insights 本地运行可完整复盘使用习惯并给出工作流改进建议，适合把常用流程抽成 Skills。  
- 对 Agent 流程的实践要结合编译、自动化测试和截图对比等验证手段，减少反复迭代的盲目成本。  
- 在 Anthropic 活动中：若已开启 Extra Usage 无需操作，未开启需在 2/16 前打开并留意资格（非 Team/Enterprise/API）。  
- 使用 YouMind 学习他人提示词有收获，但 dotey 本人更偏好本地 markdown 管理个人知识。  
- 领取免费额度时要注意有效期（60 天）和后续付费逻辑，不想继续用应手动关闭自动充值。