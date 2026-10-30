**dotey 2026年10月29日分享整理**

**新工具/技术**
- baoyu-design v2（开源）：把 Claude Design、Claude Slides、Claude Dashboard 移植成可在任意 Agent、任意模型上运行的技能，不再依赖 Claude Artifacts；支持在本地项目内运行、双向同步编辑、导出 PDF/HTML/PNG、多屏预览。
- 四个技能需用新名字：claude-design-system（做设计前先导入或生成设计系统）、claude-design、claude-slides、claude-dashboard；旧版不能直接升级。
- 前端逆向方法：用 REA 逆向 Claude Slides 的混淆代码，再用 Claude Code 重写为结构清晰、类型完整的实现。

**核心观点/方法论**
- Worktree 在并行任务多时绕不开：云端并行虽能隔离任务，但环境不齐全、很多功能无法验证，且成本更高，本机验证仍不可少。
- Claude“自我评估”机制：每轮回答后追加短指令让模型自查安全，借 KV cache 把增量算力控制在 2% 以内；只做事后标记、不当场拦截。
- 该机制在 1% 误报率下可召回 78% 的可疑对话，高优先级达 94%，能覆盖传统分类器未预设的违规蒸馏、提示词注入、越权操作；局限是挡不住定向绕过，也不适合监督模型自身。
- OpenAI 同日将 Pro 100/200/500 与 Business Premium 用量上限翻倍，取消 Pro 200 原定降额；按倍数推算 Pro 100 由 5 倍升至 10 倍、Pro 500 由 25 倍升至 50 倍，老用户 Pro 200 维持 20 倍。
- 语音交互降低了儿童使用 AI 的门槛，孩子更愿意提问，也更信任 AI 给出的答案。

**实践经验/案例**
- 逆向流程可复用：下载核心脚本与样式→按 REA 说明安装→用 REA Skill 逆向→Claude Code 重写；提示词不必直接逆，改为让模型“做一个同样好的 slides skill”，成品效果接近。
- 7 岁孩子靠语音输入在 ChatGPT 里从画图、生成视频做到小游戏，再边玩边提需求迭代，全程几乎不打字。
- API 积分按到续订日的间隔比例发放（如当月仅 $75），需先在 ChatGPT 账单领取，再到 ChatGPT 或 Codex 创建 API 密钥使用。