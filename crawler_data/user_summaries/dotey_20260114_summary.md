**新工具/技术**  
- PixVerse R1：首个实时生成视频的大模型，输入文本/指令即可即时改变画面帧，支持复杂交互与视角切换。  
- agent-browser（配套补丁/使用方法讨论）：用浏览器驱动读取 HTML 的爬虫/自动化方式，能节省 token，但默认无头/登录会受限。  
- Chrome CDP（Chrome DevTools Protocol）：通过 WebSocket 控制真实 Chromium 的底层调试协议，dotey 用它替代 Playwright MCP 以降低 token 成本并固化登录状态。  
- Claude Agent SDK / Claude Code + Skills：用少量代码搭建 Agent、运行 Skill，实现多平台自动化发布与协同工作。  
- gemini-web / 多平台发布 Skill：社区改造出的 Skill 集合（含 LinkedIn、微信公众号、画图等），可联动完成多平台稿件生成与发布草稿。

**核心观点/方法论**  
- 实时生成视频是一个类别级突破：视频从“先做后看”变成“你说了算”的交互世界，能把直播、游戏、教育、互动影视等边界模糊化。  
- 用脚本+浏览器协议（CDP）做自动化比用大型模型在线渲染更省 token：把“动作”交给浏览器而不是让 LLM 处理所有界面步骤。  
- Agent + Skill 的组合能把多平台发布、审稿、图文处理等流程自动化，但会有集成/授权/稳定性等工程坑需要踩平。  
- 快速复制（copycat）并跟进爆点能带来流量红利：产品增长上“跟得上爆发的渠道”有时比原创更高效。

**实践经验/案例**  
- dotey 的微信公众号自动发布 Skill：用 Chrome CDP 操作浏览器，支持 Markdown→HTML、单图粘贴进编辑器、记住登录状态、不直接发布只生成草稿；需 Claude Code/Node 环境。  
- agent-browser 登录 Google 的解决思路：用 “channel” 启动系统 Chrome + 指定 --user-data-dir 固化登录，或按社区方法（kill Chrome → 复制 Profile → 启动带 --remote-debugging-port 和 --user-data-dir）让 agent-browser 通过 CDP 登录。  
- 社区互助示例：BadUncle、orz99 等给出补丁和命令行流程，结合 oracle agent/多模型协作（Gemini/Codex）能解决复杂集成问题。  
- 成长案例：monica 跟进热门作品/话题（copycat）后，通过 Instagram 板块流量导入实现地区榜单冲顶，说明渠道时机与执行力的重要性。