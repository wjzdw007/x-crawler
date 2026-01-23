**新工具/技术**（如有）
- Gemini App 的 SAT 模拟考试功能：Google for Education 联手 Princeton Review，在 Gemini App 内提供全长 SAT 练习题并给即时反馈，表明大模型开始直接嵌入教学评测场景。  
- Claude Skills / Claude Project：Anthropic 的 Skills 机制，可把可复用的提示/脚本封装为 Skill，并在 Project 中直接调用，便于构建工作流。  
- Claude Code + Opus 4.5：作为底层模型与代码能力组合，用于生成 HTML/代码演示，但能力上限和交互流畅度仍有限。  
- baoyu-xhs-images Skill：dotey 演示的自动图片生成 Skill，用于快速产图并嵌入工作流。  
- Remotion Skill（示例引用）：将现有工具的文档与关键参数作为 References，方便 Skill 调用和复用。  
- Postgres Agent Skills：预计大量开源/闭源项目会发布对应的 Agent Skills，形成“skills stack”。  
- Electron .asar 逆向：有人通过解包 .asar 查看 prompt 和 schema 定义，便于复用/学习内部实现细节。

**核心观点/方法论**（如有）
- 确定性任务交给脚本、不确定性交给大模型：把可确定化的步骤用脚本实现，复杂模糊的决策留给 LLM，能让流程更清晰且可复现。  
- Skills = 工作流组成单元：把重复的提示/模版/脚本封装成 Skills，可像管理代码库一样管理技能，提高效率与复用。  
- 工作目录与技能分层管理：每个项目目录下维护 .claude/skills，公共 Skills 放到 ~/.claude/skills，配合 git 管理，便于版本回滚与协作。  
- 避免上下文膨胀，及时回滚重做：当会话卡住多半是思路问题，借助 Git 回到上一个靠谱快照比在原会话继续补上下文更干净。  
- 从别人的 SKILL.MD 学习复用：大量有价值的实现细节和 references 都写在 Skill 文档里，阅读它们是学习最佳实践的捷径。

**实践经验/案例**（如有）
- 避免 Claude Code 上下文占满的实用技巧：dotey 分享了自己避免上下文用满的经验（具体细节见贴），以减少等待和压缩问题。  
- 用 Skill 自动化图片产出：dotey 用 baoyu-xhs-images Skill 自动生成配图，说明 Skill 能把常见制作流程一键化。  
- Project 中调用 Skill 的简化提示：提示词可以很简洁，只要指明 Skill 名称，Project 会按指令去调用，降低使用门槛。  
- 对演示视频的冷静评估：视频演示很酷，但实际修改流程可能没有那么顺滑，提示底层模型能力（如生成实时可编辑 HTML）仍有限。