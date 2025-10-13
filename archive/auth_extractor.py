#!/usr/bin/env python3
"""
认证信息提取工具 - 自动从浏览器中提取X的认证信息
"""

import json
import os
from playwright.sync_api import sync_playwright
from pathlib import Path

def extract_auth_info():
    """自动提取认证信息"""
    print("🔑 X认证信息自动提取工具")
    print("请按照以下步骤操作：")
    print("1. 浏览器将自动打开")
    print("2. 请登录你的X账号")
    print("3. 登录成功后，按回车键继续")
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # 用于捕获请求的认证信息
        auth_headers = {}
        cookies = {}
        
        def handle_request(request):
            """处理请求，提取认证信息"""
            if 'x.com' in request.url or 'twitter.com' in request.url:
                headers = request.headers
                
                # 提取关键认证头
                if 'authorization' in headers:
                    auth_headers['authorization'] = headers['authorization']
                if 'x-csrf-token' in headers:
                    auth_headers['x-csrf-token'] = headers['x-csrf-token']
        
        # 监听请求
        page.on('request', handle_request)
        
        try:
            # 打开X登录页面
            print("\n🌐 正在打开X登录页面...")
            page.goto("https://x.com/login")
            page.wait_for_load_state('networkidle')
            
            print("\n⏳ 请在浏览器中完成登录...")
            print("登录成功后，请在终端中按回车键继续")
            input()
            
            # 导航到主页以触发API请求
            print("\n🔄 正在获取认证信息...")
            page.goto("https://x.com/home")
            page.wait_for_load_state('networkidle')
            
            # 等待几秒让API请求完成
            page.wait_for_timeout(3000)
            
            # 获取cookies
            cookies_data = context.cookies()
            for cookie in cookies_data:
                if cookie['name'] in ['auth_token', 'ct0']:
                    cookies[cookie['name']] = cookie['value']
            
            # 检查是否成功获取认证信息
            if cookies.get('auth_token') and auth_headers.get('authorization'):
                print("✅ 成功提取认证信息!")
                
                # 构建配置
                config = {
                    "authentication": {
                        "cookies": {
                            "auth_token": cookies.get('auth_token', ''),
                            "ct0": cookies.get('ct0', '')
                        },
                        "headers": {
                            "Authorization": auth_headers.get('authorization', ''),
                            "X-Csrf-Token": auth_headers.get('x-csrf-token', cookies.get('ct0', ''))
                        }
                    },
                    "settings": {
                        "requests_per_hour": 400,
                        "retry_attempts": 3,
                        "retry_delay": 5,
                        "timeout": 30
                    },
                    "targets": {
                        "daily_tweet_count": 100,
                        "timeline_types": ["recommended", "following"]
                    }
                }
                
                # 保存配置文件
                config_file = "config.json"
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                
                print(f"💾 配置已保存到: {config_file}")
                print("\n🎉 现在你可以运行:")
                print("python daily_report_generator.py")
                
                return True
            else:
                print("❌ 未能提取到完整的认证信息")
                print("可能的原因：")
                print("1. 未完全登录")
                print("2. 需要刷新页面触发更多API请求")
                return False
                
        except Exception as e:
            print(f"❌ 提取过程中出错: {e}")
            return False
        finally:
            browser.close()

def manual_config_guide():
    """手动配置指导"""
    print("\n📋 手动配置指导:")
    print("1. 打开浏览器，访问 https://x.com/home")
    print("2. 按F12打开开发者工具")
    print("3. 切换到Network标签") 
    print("4. 刷新页面")
    print("5. 找到timeline相关的API请求")
    print("6. 复制以下信息：")
    print("   - Cookie中的 auth_token 和 ct0")
    print("   - Headers中的 Authorization 和 X-Csrf-Token")
    print("7. 编辑config.json文件填入这些信息")

def check_config():
    """检查配置文件是否存在和有效"""
    if os.path.exists("config.json"):
        try:
            with open("config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            auth = config.get('authentication', {})
            cookies = auth.get('cookies', {})
            headers = auth.get('headers', {})
            
            if (cookies.get('auth_token') and 
                cookies.get('ct0') and 
                headers.get('Authorization') and
                headers.get('X-Csrf-Token')):
                print("✅ 配置文件有效，包含所有必需的认证信息")
                return True
            else:
                print("⚠️ 配置文件存在但缺少认证信息")
                return False
        except Exception as e:
            print(f"❌ 配置文件格式错误: {e}")
            return False
    else:
        print("⚠️ 配置文件不存在")
        return False

def main():
    """主函数"""
    print("🔧 X爬虫认证配置工具")
    
    # 检查现有配置
    if check_config():
        print("当前配置有效，如需重新配置请删除config.json后重试")
        return
    
    print("\n选择配置方式:")
    print("1. 自动提取（需要你登录X账号）")
    print("2. 手动配置指导")
    print("3. 退出")
    
    choice = input("\n请选择 (1/2/3): ").strip()
    
    if choice == '1':
        print("\n🚀 开始自动提取认证信息...")
        success = extract_auth_info()
        if not success:
            print("\n自动提取失败，显示手动配置指导:")
            manual_config_guide()
    elif choice == '2':
        manual_config_guide()
    elif choice == '3':
        print("👋 退出配置")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()