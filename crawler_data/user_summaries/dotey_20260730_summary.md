**新工具/技术**（如有）
- baoyu-slide-deck skill：以纯图片为主的 PPT 生成 Skill，适合快速产出视觉页。  
- baoyu-design：生成 HTML 可转原生 PPTX 的 Skill，定位为可编辑且美观的中间格式。  
- Opus（Claude Opus / Opus 4.8）：在生成 HTML/视觉设计方面效果优秀，常被用于提升美观度。  
- Claude Code / baoyu-image-gen / Codex：用于生成代码级 HTML/CSS 和插图/图像素材，配合设计模型输出完整 slides。

**核心观点/方法论**（如有）
- HTML 是最佳中间格式：AI 对 HTML/CSS 更熟悉，能直接产出好看的页面且便于编辑，是生成到 PPTX 的优选 IR。  
- 受限的 HTML+CSS 更利于转成原生 PPTX：加约束能在兼顾美观和可编辑性之间取得平衡，便于高保真还原。  
- 选用模型/格式应优先考虑 AI 训练熟悉度：发明冷门 JSON/XML IR 虽可行，但通常样式有限，效果不如 HTML。  
- 追求“所见即所得”与局部性：DSL/IR 要避免 CSS 那类“远程作用”导致的不可预料副作用，便于调试与模型生成。  
- 往返保真（round-trip fidelity）很重要：生成与解析保持一致，才能支持已有 PPT 修改与持续迭代。  
- 美观 vs 可编辑的权衡：直接生成图像最美但不可编辑，直接写 PPTX 可编辑但常难看，HTML 是折中解。

**实践经验/案例**（如有）
- baoyu-design 实测：作者用该 Skill 生成的 PPT 能做到几乎 1:1 还原成 PPTX，说明约束型 HTML→PPTX 路线可行。  
- 成本/时间对比：用 HTML 的方案在效果上比一些通用插件更漂亮，但调试成本与失败率更高；与 remio/guizang 比较时存在时间和成本差异。  
- 常见问题举例：CSS 选择器与层级导致的“浅色文字在浅色背景上不可见”、inline 元素 width/height 无效等问题，会让调试复杂化。  
- SVG 路线权衡：ppt master 用 SVG 作为 IR 优点是绝对定位、语法精炼，但文本排版难题与修改时需重算换行是硬伤；remio 花了约九个月做 IR/解析，工作量大。