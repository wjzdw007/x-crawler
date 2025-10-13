# 开源许可证选择指南

本项目使用 **MIT License**，这是最流行和宽松的开源许可证之一。

---

## 🤔 为什么选择 MIT License？

### ✅ 优势

1. **简单易懂**
   - 只有几段话，不到 200 字
   - 没有复杂的法律术语

2. **最大自由度**
   - 允许任何人使用、修改、分发
   - 允许商业使用
   - 允许私有化（闭源）使用

3. **广泛采用**
   - GitHub 上 55% 的项目使用
   - 大公司友好（Google、Facebook、Microsoft 等）
   - 与其他许可证兼容性好

4. **无负担**
   - 不强制衍生作品开源
   - 不要求贡献者签署 CLA
   - 不涉及专利条款

### ❌ 局限性

1. **无专利保护**
   - 不明确授予专利权利
   - 如需专利保护，考虑 Apache 2.0

2. **无商标保护**
   - 不保护项目名称和品牌

3. **免责声明**
   - 不提供任何保证
   - 作者不承担责任

---

## 📊 其他常见许可证对比

### Apache License 2.0

**特点：**
- 类似 MIT，但包含专利授权条款
- 要求注明修改内容
- 更详细的法律保护

**适用场景：**
- 涉及专利的项目
- 企业级开源项目
- 需要明确贡献者条款

**示例项目：**
- Android、Kubernetes、Apache Spark

---

### GNU GPL-3.0

**特点：**
- **Copyleft**：衍生作品必须开源
- 必须使用相同许可证
- 不能用于闭源商业软件

**适用场景：**
- 希望保持项目永久开源
- 防止被商业公司闭源使用
- 理念驱动的项目

**示例项目：**
- Linux、WordPress、Git

**注意：**
- 对商业应用有限制
- 许多公司避免使用 GPL 代码

---

### GNU AGPL-3.0

**特点：**
- 最严格的开源许可证
- **网络 Copyleft**：SaaS 服务也必须开源
- 即使不分发，只要提供网络服务就要开源

**适用场景：**
- 防止云服务商闭源使用
- 极度重视开源理念

**示例项目：**
- MongoDB（早期）、RocketChat

**警告：**
- 很多公司完全禁止使用 AGPL 代码
- 最不受企业欢迎的许可证

---

### BSD 2-Clause / BSD 3-Clause

**特点：**
- 类似 MIT，稍微详细一些
- 3-Clause 禁止使用项目名做背书

**适用场景：**
- 类似 MIT 的使用场景
- 需要禁止商标滥用

**示例项目：**
- FreeBSD、Redis、Flask

---

### Creative Commons (CC BY 4.0)

**特点：**
- 主要用于文档、数据、艺术作品
- 不推荐用于软件代码

**适用场景：**
- 文档、教程
- 数据集
- 设计资源

---

## 🎯 如何选择？

### 决策树

```
是否希望衍生作品也开源？
├─ 是 → GPL-3.0 或 AGPL-3.0
└─ 否 ↓

是否涉及专利技术？
├─ 是 → Apache 2.0
└─ 否 ↓

想要最简单宽松的许可证？
└─ 是 → MIT License ✅
```

### 按项目类型推荐

| 项目类型 | 推荐许可证 | 理由 |
|---------|-----------|------|
| **工具/脚本** | MIT | 简单、易用、广泛接受 |
| **库/框架** | MIT / Apache 2.0 | 商业友好，易于集成 |
| **应用软件** | MIT / GPL-3.0 | 看是否希望衍生作品开源 |
| **SaaS 服务** | AGPL-3.0 | 防止云服务商闭源使用 |
| **企业级项目** | Apache 2.0 | 专利保护、法律完善 |
| **数据/文档** | CC BY 4.0 | 专门为内容设计 |

---

## 📝 如何使用 MIT License

### 1. 创建 LICENSE 文件

在项目根目录创建 `LICENSE` 文件，内容如下：

```
MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**注意：**
- 替换 `[year]` 为当前年份（如 2025）
- 替换 `[fullname]` 为你的名字或 GitHub 用户名

### 2. 在 README 中声明

在 `README.md` 末尾添加：

```markdown
## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

或中文版本：

```markdown
## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件
```

### 3. 在源代码中添加（可选）

在每个源文件头部添加：

```python
# Copyright (c) 2025 [Your Name]
# Licensed under the MIT License
```

---

## 🔄 如何更改许可证

### 情况 1: 项目刚创建，还没有贡献者

✅ 可以随意更改，只需：
1. 更新 `LICENSE` 文件
2. 更新 `README.md`
3. 提交并推送

### 情况 2: 已有外部贡献者

⚠️ **需要所有贡献者同意**

步骤：
1. 创建 Issue 说明更改理由
2. 联系所有贡献者获取同意
3. 记录同意证明
4. 更新许可证

---

## ⚖️ 许可证兼容性

### MIT 与其他许可证的兼容性

| 其他许可证 | 作为依赖 | 集成 MIT 代码 |
|-----------|---------|-------------|
| MIT | ✅ 兼容 | ✅ 兼容 |
| Apache 2.0 | ✅ 兼容 | ✅ 兼容 |
| BSD | ✅ 兼容 | ✅ 兼容 |
| GPL-3.0 | ⚠️ 单向兼容 | ✅ 兼容 |
| AGPL-3.0 | ⚠️ 单向兼容 | ✅ 兼容 |
| 专有软件 | ✅ 兼容 | ✅ 兼容 |

**说明：**
- ✅ 完全兼容：可以混合使用
- ⚠️ 单向兼容：MIT 代码可以用在 GPL 项目中，但 GPL 代码不能用在 MIT 项目中
- ❌ 不兼容：不能混合使用

---

## 🛡️ 法律保护建议

### MIT License 的免责声明

MIT License 包含 "AS IS" 免责声明，意味着：

- ✅ 你不承担任何责任
- ✅ 软件没有任何保证
- ⚠️ 用户自行承担风险

### 额外保护措施（可选）

1. **添加 NOTICE 文件**
   ```
   X Crawler
   Copyright 2025 [Your Name]

   This product includes software developed by...
   ```

2. **代码注释说明**
   ```python
   # WARNING: This is a web scraper for personal use only.
   # Use responsibly and comply with X's Terms of Service.
   ```

3. **README 中添加免责声明**
   ```markdown
   ## ⚠️ Disclaimer

   This tool is for educational and personal use only. Users are responsible
   for complying with X's Terms of Service and applicable laws.
   ```

---

## 📚 扩展阅读

### 官方资源

- [Choose a License](https://choosealicense.com/) - GitHub 官方许可证选择工具
- [Open Source Initiative](https://opensource.org/licenses) - 开源倡议组织
- [TLDRLegal](https://www.tldrlegal.com/) - 许可证简明解释

### 许可证全文

- [MIT License](https://opensource.org/licenses/MIT)
- [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)
- [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)
- [BSD-3-Clause](https://opensource.org/licenses/BSD-3-Clause)

---

## ❓ FAQ

### Q: 可以不用任何许可证吗？

**A**: 不推荐。没有许可证意味着：
- ⚠️ 默认保留所有权利（All Rights Reserved）
- ❌ 他人无法合法使用你的代码
- ❌ 失去开源的意义

### Q: MIT License 可以用于商业项目吗？

**A**: ✅ 可以，完全允许商业使用。

### Q: 我的代码被别人用了不给我钱怎么办？

**A**: 这是 MIT License 的特点，你已经授予了免费使用的权利。如果想要收费，应该：
- 使用双许可（Dual License）
- 或使用专有许可证

### Q: 如何保护我的品牌/名称？

**A**: MIT License 不保护商标，你需要：
- 单独注册商标
- 在 README 中声明商标权
- 考虑使用 Apache 2.0（包含商标条款）

### Q: GPL 代码可以放在 MIT 项目中吗？

**A**: ❌ 不可以。GPL 是 Copyleft，会"传染"整个项目。

---

## 🎯 总结

**对于本项目（X Crawler）：**

✅ **MIT License 是最佳选择**

**理由：**
1. 个人工具项目，不涉及专利
2. 希望他人可以自由使用和改进
3. 不强制衍生作品开源
4. 简单、流行、易于理解

**如果将来需要更改：**
- 需要专利保护 → 考虑 Apache 2.0
- 希望衍生作品开源 → 考虑 GPL-3.0
- 防止 SaaS 闭源 → 考虑 AGPL-3.0

---

*最后更新: 2025-10-10*
