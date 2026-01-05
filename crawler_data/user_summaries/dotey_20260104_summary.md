**新工具/技术**（如有）
- Claude Code（Claude agent SDK）+ VM + tools + Web UI + data 的组合被称作“manus”，是一套可构建垂直领域代理的技术栈，便于把模型、执行环境和知识库打包成行业化产品。  
- Claude Code 的 Plan Mode：能自动生成开发 plan 文档，适合反复沟通与确认，实现“先有计划再实现”的闭环。  
- VSCode 的 Commit Message Generation（或 Copilot 提交消息扩展）：可以通过在 Settings 或项目根目录添加指令文件，强制 AI 生成符合 Conventional Commits 的提交信息。  
- dotey 分享了自定义 Prompt 的资源和示例（含截图/链接），方便工程团队统一提示词并复用到多项目中。

**核心观点/方法论**（如有）
- 反对重度 Spec-Driven Development（SDD）：SDD 会产生大量文档和维护成本，容易成为瀑布式负担，影响迭代速度。  
- 倡导小版本迭代（vibe coding）：用几句 prompt 直接生成可以运行的版本，快速验证，再逐步改进，这比先写详尽 spec 更高效。  
- “prompt -> 代码”成为主流路径：AI 降低了代码成本，prompt 可直接驱动生成实现，不满意再修改 prompt 重生成，代码也可视为运行时的文档。  
- 强调上下文管理优于生硬的 spec-kit：不要把一堆文档统统塞进上下文，应该按当前任务提供“刚刚好”的上下文片段。  
- 模型+Agent 带来“工程能力内化”：随着 Agent 与更强模型的迭代，自动化开发上限会超过仅靠模板化 SDD 的上限。  
- AI 共创是新常态：专业创作者借助 AI 搜集素材与填充细节，最终由人负责审美与风格把控，读者更关心作品本身价值。

**实践经验/案例**（如有）
- 使用 Claude Code 的 Plan Mode 写出 plan 后，可让模型像产品经理那样主动提问，澄清边界与异常情况，得到可执行的 spec。  
- 在让 Agent 实施开发时，新建干净 Session 并只提供代码库访问 + 刚生成的完整 spec，可避免旧上下文干扰，聚焦任务执行。  
- 实操案例：通过在 VSCode Settings 或在项目根创建 .copilot-commit-message-instructions.md，可以 100% 让 AI 输出符合 Conventional Commits 的提交格式。  
- 警示：把大量过时或不必要文档当作上下文会占用令牌并误导 Agent，务必保持知识库与工具链精简且实时更新。