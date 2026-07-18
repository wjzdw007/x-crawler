**新工具/技术**（如有）
- Gemini Skills 原生菜单（传闻）：桌面端将支持上传/创建/编辑 Skills 并在所有对话使用，支持 Skill 文件夹，便于本地技能管理。
- Qwen3 ASR + Qwen3-ForcedAligner：本地语音识别与强制对齐，0.6b 就足够，能输出精确词级时间戳，资源占用低。
- Pyannote + WeSpeaker：开源说话人识别方案，多人或重叠说话时精度有限，建议与 Agent 上下文结合提升效果。
- 豆包录音文件识别模型 2.0（云端）：质量高、速度快，但需付费，适合要求严格的转录场景。
- baoyu-design skill：用于原型设计并在 Claude Code 内预览，配合模型快速迭代 UI 原型。
- Opus 4.8 / Fable 5 / GPT 5.6：Opus 4.8 在 UI 设计原型上表现优秀，Fable 5 在某些情境下更强，GPT 5.6 前端设计能力相对较弱。
- Codex CloudFlare Plugin：用于自动化发布更新/安装包到 CloudFlare，便于技能部署。
- 开源 Agent controller（手柄→Codex）：把手柄操作映射成 Codex 指令，实现低成本本地替代硬件控制器。
- MuonClip + QK-Clip（Kimi K2.5 组件）：MuonClip 提高数据利用率（等效扩充数据量），QK-Clip 防止注意力数值溢出以稳定训练。
- Kimi Linear (KDA) & Attention Residue：KDA 提供分通道线性注意力以高效利用超长上下文；Attention Residue 用注意力替代部分残差连接以选择性保留深层信息。

**核心观点/方法论**（如有）
- 专家能力决定上限，AI 放大下限：有设计/写作/剪辑能力的人会因 AI 更强，普通人更多是被 AI 提升基本能力而非创造顶尖作品。
- 开源模型要既开放又强：Kimi 的工作表明通过改基础组件（优化器/注意力/残差）能显著提升开源模型能力而非只靠规模堆叠。
- 有效利用数据比盲目扩数据更重要：MuonClip/Attention Residue 等方法通过提高 Token 利用效率应对高质量数据稀缺。
- 长上下文需“可用”而非仅“更长”：KDA 把固定遗忘机制拆细，混合线性与全注意力以在百万 Token 级别保持效率与效果。
- 多 Agent 并行优于单 Agent 串行：Agent Swarm 用任务拆解与多重奖励机制把复杂流程并行化，大幅缩短完成时间。

**实践经验/案例**（如有）
- 转录流程：Whisper 时间戳/中英混排/说话人识别存在不足；Qwen3 ASR + ForcedAligner 本地组合能显著提升准确率；复杂需求可选云端付费模型（豆包 2.0）。
- 开发迭代 loop（BaoCut 案例）：先用 baoyu-design + Opus 4.8 打磨原型，再用 Claude Code 或 Codex 实现与发布，AI 扮演设计-实现的加速器，人工负责验收与改进。
- 安全教训（Codex / GPT-5.6）：在开启 Full Access 并关闭沙盒/自动审查时存在删掉用户 $HOME 的风险，需更安全的权限模式与额外 Harness 检查。
- 运营/成本提醒：Claude Code 的 “Usage credits” 会自动消耗 API 额度，注意不要误开以免产生大额费用；开发者机器偏好 Mac，Agent 应用生态对 Mac 支持更好。