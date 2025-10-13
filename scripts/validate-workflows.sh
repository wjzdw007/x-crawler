#!/bin/bash

# GitHub Actions Workflow 验证脚本
# 用于在推送前本地检查 workflow 文件的语法

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 图标
CHECK="✓"
CROSS="✗"
WARN="⚠"
INFO="ℹ"

echo ""
echo "========================================"
echo "  GitHub Actions Workflow 验证工具"
echo "========================================"
echo ""

# 检查是否在项目根目录
if [ ! -d ".github/workflows" ]; then
    echo -e "${RED}${CROSS} 错误: 未找到 .github/workflows 目录${NC}"
    echo -e "${YELLOW}${INFO} 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 计数器
total_files=0
passed_files=0
failed_files=0
warnings=0

# 检查 actionlint 是否安装
check_actionlint() {
    if command -v actionlint &> /dev/null; then
        echo -e "${GREEN}${CHECK} actionlint 已安装${NC}"
        return 0
    else
        echo -e "${YELLOW}${WARN} actionlint 未安装${NC}"
        echo ""
        echo "actionlint 是一个强大的 GitHub Actions 语法检查工具"
        echo ""
        echo "安装方法:"
        echo "  macOS:   brew install actionlint"
        echo "  Linux:   下载自 https://github.com/rhysd/actionlint/releases"
        echo ""
        read -p "是否继续进行基础检查? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        return 1
    fi
}

# 基础 YAML 语法检查
basic_yaml_check() {
    local file=$1

    # 检查文件是否为空
    if [ ! -s "$file" ]; then
        echo -e "${RED}  ${CROSS} 文件为空${NC}"
        return 1
    fi

    # 检查基本缩进（2空格或4空格）
    if grep -q $'^\t' "$file"; then
        echo -e "${YELLOW}  ${WARN} 检测到 Tab 字符，YAML 应该使用空格缩进${NC}"
        ((warnings++))
    fi

    # 检查常见的 GitHub Actions 必需字段
    if ! grep -q "^name:" "$file"; then
        echo -e "${YELLOW}  ${WARN} 缺少 'name' 字段${NC}"
        ((warnings++))
    fi

    if ! grep -q "^on:" "$file" && ! grep -q "^'on':" "$file"; then
        echo -e "${RED}  ${CROSS} 缺少 'on' 触发器定义${NC}"
        return 1
    fi

    if ! grep -q "^jobs:" "$file"; then
        echo -e "${RED}  ${CROSS} 缺少 'jobs' 定义${NC}"
        return 1
    fi

    # 检查常见的语法错误
    # 1. secrets 在 if 条件中未包裹（检查没有 ${{ }} 包裹的情况）
    if grep -E "^[[:space:]]*if:[[:space:]]+[^$]*secrets\." "$file" | grep -qv '\${{'; then
        echo -e "${RED}  ${CROSS} 发现错误: secrets 在 if 条件中未使用 \${{ }}${NC}"
        echo -e "${BLUE}     修复: if: \${{ failure() && secrets.TOKEN != '' }}${NC}"
        return 1
    fi

    # 2. 检查未定义的 step id 引用
    local step_ids=$(grep -o 'id: [a-zA-Z_][a-zA-Z0-9_]*' "$file" | cut -d' ' -f2 || true)
    local step_refs=$(grep -o 'steps\.[a-zA-Z_][a-zA-Z0-9_]*\.outputs' "$file" | cut -d'.' -f2 || true)

    for ref in $step_refs; do
        if ! echo "$step_ids" | grep -q "^$ref$"; then
            echo -e "${YELLOW}  ${WARN} 可能引用了未定义的 step: steps.$ref${NC}"
            ((warnings++))
        fi
    done

    return 0
}

# 检查敏感信息泄露
check_secrets_leak() {
    local file=$1

    # 检查是否直接打印 secrets
    if grep -qE 'echo.*\$\{\{ secrets\.' "$file"; then
        echo -e "${RED}  ${CROSS} 危险: 检测到可能泄露 secrets 的 echo 命令${NC}"
        grep -n "echo.*\${{ secrets\." "$file" | while read line; do
            echo -e "${YELLOW}     $line${NC}"
        done
        return 1
    fi

    # 检查是否将 secrets 发送到外部
    if grep -qE 'curl.*\$\{\{ secrets\.' "$file"; then
        echo -e "${YELLOW}  ${WARN} 警告: 检测到 curl 使用 secrets，请确认目标地址安全${NC}"
        ((warnings++))
    fi

    return 0
}

# 检查权限配置
check_permissions() {
    local file=$1

    if grep -q "permissions:" "$file"; then
        echo -e "${GREEN}  ${CHECK} 已配置权限${NC}"
    else
        echo -e "${YELLOW}  ${WARN} 未显式配置权限，将使用默认权限${NC}"
        ((warnings++))
    fi
}

# 检查超时配置
check_timeouts() {
    local file=$1

    if grep -q "timeout-minutes:" "$file"; then
        echo -e "${GREEN}  ${CHECK} 已配置超时${NC}"
    else
        echo -e "${YELLOW}  ${INFO} 未配置超时（将使用默认 360 分钟）${NC}"
    fi
}

# 使用 actionlint 检查
actionlint_check() {
    local file=$1

    if command -v actionlint &> /dev/null; then
        echo -e "${BLUE}  → 运行 actionlint...${NC}"
        if output=$(actionlint "$file" 2>&1); then
            echo -e "${GREEN}  ${CHECK} actionlint 检查通过${NC}"
            return 0
        else
            echo -e "${RED}  ${CROSS} actionlint 发现问题:${NC}"
            echo "$output" | sed 's/^/    /'
            return 1
        fi
    fi
    return 0
}

# 验证单个文件
validate_file() {
    local file=$1
    local filename=$(basename "$file")

    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}检查: $filename${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    ((total_files++))

    local file_passed=true

    # 基础检查
    if ! basic_yaml_check "$file"; then
        file_passed=false
    fi

    # 安全检查
    if ! check_secrets_leak "$file"; then
        file_passed=false
    fi

    # 权限检查
    check_permissions "$file"

    # 超时检查
    check_timeouts "$file"

    # actionlint 检查
    if ! actionlint_check "$file"; then
        file_passed=false
    fi

    # 统计结果
    if [ "$file_passed" = true ]; then
        echo -e "${GREEN}${CHECK} $filename 验证通过${NC}"
        ((passed_files++))
    else
        echo -e "${RED}${CROSS} $filename 验证失败${NC}"
        ((failed_files++))
    fi
}

# 主函数
main() {
    # 检查工具
    has_actionlint=false
    if check_actionlint; then
        has_actionlint=true
    fi

    echo ""
    echo "开始检查 workflow 文件..."

    # 查找所有 workflow 文件
    workflow_files=(.github/workflows/*.yml .github/workflows/*.yaml)

    if [ ${#workflow_files[@]} -eq 0 ]; then
        echo -e "${RED}${CROSS} 未找到任何 workflow 文件${NC}"
        exit 1
    fi

    # 验证每个文件
    for file in "${workflow_files[@]}"; do
        if [ -f "$file" ]; then
            validate_file "$file"
        fi
    done

    # 输出总结
    echo ""
    echo -e "${BLUE}========================================"
    echo "  验证总结"
    echo -e "========================================${NC}"
    echo ""
    echo "总文件数: $total_files"
    echo -e "${GREEN}通过: $passed_files${NC}"
    echo -e "${RED}失败: $failed_files${NC}"
    echo -e "${YELLOW}警告: $warnings${NC}"
    echo ""

    # 建议
    if [ "$has_actionlint" = false ]; then
        echo -e "${YELLOW}${INFO} 建议: 安装 actionlint 以获得更全面的检查${NC}"
        echo "   brew install actionlint"
        echo ""
    fi

    if [ $warnings -gt 0 ]; then
        echo -e "${YELLOW}${WARN} 有 $warnings 个警告，建议修复${NC}"
        echo ""
    fi

    # 返回状态
    if [ $failed_files -eq 0 ]; then
        echo -e "${GREEN}${CHECK} 所有检查通过！${NC}"
        exit 0
    else
        echo -e "${RED}${CROSS} 有 $failed_files 个文件未通过验证${NC}"
        exit 1
    fi
}

# 运行主函数
main
