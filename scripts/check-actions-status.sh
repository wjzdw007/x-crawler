#!/bin/bash

# GitHub Actions 状态检查脚本
# 需要 GitHub Personal Access Token

set -e

REPO="wjzdw007/x-crawler"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "========================================"
echo "  GitHub Actions 状态检查"
echo "========================================"
echo ""

# 检查是否安装 gh CLI
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠ GitHub CLI 未安装${NC}"
    echo ""
    echo "请安装 GitHub CLI:"
    echo "  macOS:   brew install gh"
    echo "  Linux:   https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    echo ""
    echo "安装后运行: gh auth login"
    exit 1
fi

# 检查是否已登录
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ 未登录 GitHub${NC}"
    echo ""
    echo "请先登录:"
    echo "  gh auth login"
    exit 1
fi

echo -e "${GREEN}✓ GitHub CLI 已就绪${NC}"
echo ""

# 获取最近的 workflow 运行
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "最近的 Workflow 运行记录:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

gh run list --repo "$REPO" --limit 5 --json status,conclusion,name,createdAt,headBranch,displayTitle | \
  jq -r '.[] | "\(.status) | \(.conclusion // "in_progress") | \(.name) | \(.displayTitle) | \(.createdAt)"' | \
  while IFS='|' read -r status conclusion name title created; do
    status=$(echo "$status" | xargs)
    conclusion=$(echo "$conclusion" | xargs)
    name=$(echo "$name" | xargs)
    title=$(echo "$title" | xargs)
    created=$(echo "$created" | xargs)

    # 状态图标
    if [ "$conclusion" = "success" ]; then
      icon="${GREEN}✓${NC}"
    elif [ "$conclusion" = "failure" ]; then
      icon="${RED}✗${NC}"
    elif [ "$status" = "in_progress" ]; then
      icon="${YELLOW}●${NC}"
    else
      icon="${BLUE}○${NC}"
    fi

    echo -e "$icon $name"
    echo "   标题: $title"
    echo "   时间: $created"
    echo ""
  done

# 检查最新一次运行的详细状态
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "最新运行详情:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

latest_run=$(gh run list --repo "$REPO" --limit 1 --json databaseId --jq '.[0].databaseId')

if [ -n "$latest_run" ]; then
  gh run view "$latest_run" --repo "$REPO"
else
  echo -e "${YELLOW}⚠ 暂无运行记录${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查 workflow 文件状态
echo "Workflow 文件状态:"
echo ""

workflow_file=".github/workflows/daily-crawler.yml"
if [ -f "$workflow_file" ]; then
  echo -e "${GREEN}✓${NC} $workflow_file 存在"

  # 检查是否有语法错误（简单检查）
  if grep -q "name:" "$workflow_file" && \
     grep -q "on:" "$workflow_file" && \
     grep -q "jobs:" "$workflow_file"; then
    echo -e "${GREEN}✓${NC} 基础语法正确"
  else
    echo -e "${RED}✗${NC} 基础语法可能有问题"
  fi
else
  echo -e "${RED}✗${NC} $workflow_file 不存在"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 提供快速操作链接
echo "快速操作:"
echo ""
echo "  查看所有运行:"
echo "    gh run list --repo $REPO"
echo ""
echo "  查看特定运行:"
echo "    gh run view <run-id> --repo $REPO"
echo ""
echo "  实时监控:"
echo "    gh run watch --repo $REPO"
echo ""
echo "  触发手动运行:"
echo "    gh workflow run daily-crawler.yml --repo $REPO"
echo ""
echo "  查看在线:"
echo "    https://github.com/$REPO/actions"
echo ""
