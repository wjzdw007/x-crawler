#!/bin/bash
# X爬虫项目环境设置脚本

echo "🚀 设置X爬虫项目环境..."

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "⚡ 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "🔄 升级pip..."
pip install --upgrade pip

# 安装依赖
echo "📚 安装Python依赖..."
pip install -r requirements.txt

# 安装Playwright浏览器
echo "🌐 安装Playwright浏览器..."
playwright install chromium

echo "✅ 环境设置完成！"
echo ""
echo "使用方法："
echo "1. 激活环境: source venv/bin/activate"
echo "2. 运行分析器: python tools/analyzer.py"
echo "3. 退出环境: deactivate"