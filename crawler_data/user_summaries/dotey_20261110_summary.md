**2026年11月10日 dotey 推文要点**

**新工具/技术**
- **Gemini 4 Carbon + /swarm**：面向长任务的最强模型，付费 API 引入价 2/10 美元每百万 token（12月1日翻倍），Ultra 订阅 99.99 美元起；Antigravity 里输入 /swarm 就能让多个 Agent 分工，由协调员拆任务，每 2-4 个执行 Agent 配一个验证员，共享留言板，可给不同 Agent 指定不同模型，没活干的 Agent 休眠不耗 token。
- **Claude 白板/表格/Claude Data**：付费套餐测试版，对话里直接说需求就生成白板和带公式的表格，团队可实时共改；交互式连接器能在对话旁打开 Confluence、Box、Adobe、Notion 等直接修改，变更需你批准。
- **BaoCut 虚拟主播 skill**：皮影戏式拆层（改 11 次图、逐像素比对拆 27 层）、罩网变形转头、按读音选口型（嘴比声音早 0.03 秒），基于开源 LivLiv Player，19 位内置主播或自制角色，装给 Agent 三步出片。
- **Segment Audio**：BGM 分离利器，专门解决 Seedance 2.5 怎么强调都会生成 BGM 的毛病，可整理成 skill 让 codex 跑。

**核心观点/方法论**
- **《苦涩的教训》纠偏**：Sutton 本人强调暴力计算不够、需要巧妙新方法；dotey 把“错误的聪明”（硬编码人类棋谱、语法树、if-else 规则）与“正确的聪明”（Transformer、MCTS、TD Learning 这类能随算力扩展的架构创新）区分开，同时引 NoaX 的反驳提醒：CNN 本身就是人类先验，两者是光谱而非二分，且 Sutton 并不买 LLM 的账。
- **软件开发瓶颈已转移**：不再是造出专业软件，而是①让 Agent 用好软件（cli、MCP、代码远优于 GUI 操作）②让人低成本预览微调（播放器+标记评论足够，复杂 Timeline 对 Agent 没价值，点名 Manus 新版仍在做）③满足个性化长尾（功能原子化，Agent 用脚本当胶水按需组合）。
- **视频结果尽早确认的三级机制**：脚本（可升级为可视化 HTML 分镜）→ HTML 版预览（BaoCut 用兼容 html 的类 hyperframe 格式，部分生成即可播，不必等截屏录制）→ 最终导出。
- **招聘标准转向“与 AI 协作”**：Manus 内部取消前后端角色、PM 提交代码、设计师写代码，面试改为用 Manus 四小时解题并复盘全程记录；彭博社 AI codebase 面试则暴露工具边界模糊、边读生成内容边沟通几乎不可能、one-shot 照样被拒。

**实践经验/案例**
- **AI 短片流水线**：Seedance 2.5 的 480P 样片模式大幅降低抽卡成本、终稿已不用 Topaz，样片只留 7 天反而倒逼甲方确认，正片 4K 竟比 1080P 便宜；音乐上用 Opus 5.5 写主题旋律、Suno 扩展成各场 BGM，音效也在同一 key 上。
- **Carbon 鹈鹕骑车演示**：一个 Agent 用 Blender + Three.js 建模构建，另一个 Agent 审查自己的渲染结果，产出浏览器里可玩的 3D 游戏。
- **就业数据**：PM 开放岗位四年最高（7303 个），工程师开放岗位首次停涨（+2.5%），设计创新低（1924 个），FDE 涨 4.6 倍；PM 招聘启事里 LLM 已超 SQL 成第一技能。
- **Fable 5.2 one-shot 游戏**：约 550 美元 API 成本、8 小时做出浏览器可玩的射击游戏，dotey 亲测“有点 Call of Duty 的感觉”。