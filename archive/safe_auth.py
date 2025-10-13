#!/usr/bin/env python3
"""
安全认证配置工具 - 使用真实用户浏览器配置文件
"""

import json
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def extract_with_real_browser():
    """使用真实浏览器配置文件提取认证信息"""
    print("🔒 安全模式：使用真实浏览器配置")
    print("这种方式更安全，Google登录应该可以正常使用")
    
    # 检测用户的Chrome配置路径
    chrome_paths = [
        Path.home() / "Library/Application Support/Google/Chrome/Default",  # macOS
        Path.home() / ".config/google-chrome/default",  # Linux
        Path.home() / "AppData/Local/Google/Chrome/User Data/Default",  # Windows
    ]
    
    user_data_dir = None
    for path in chrome_paths:
        if path.exists():
            user_data_dir = str(path.parent.parent)
            break
    
    async with async_playwright() as p:
        auth_info = {}
        
        # 配置浏览器上下文
        if user_data_dir:
            print(f"📂 使用Chrome配置: {user_data_dir}")
            context = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            page = context.pages[0] if context.pages else await context.new_page()
        else:
            print("📂 使用新的浏览器配置")
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security'
                ]
            )
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()
        
        # 监听请求
        async def handle_request(request):
            if any(domain in request.url for domain in ['api.x.com', 'twitter.com', 'x.com']):
                headers = request.headers
                if 'authorization' in headers:
                    auth_info['authorization'] = headers['authorization']
                if 'x-csrf-token' in headers:
                    auth_info['x-csrf-token'] = headers['x-csrf-token']
        
        page.on('request', handle_request)
        
        try:
            print("\n🌐 正在打开X...")
            await page.goto('https://x.com/login', wait_until='networkidle')
            
            print("📋 请在浏览器中完成登录")
            print("登录成功后，按任意键继续...")
            input()
            
            print("🔄 正在获取认证信息...")
            await page.goto('https://x.com/home')
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(3000)
            
            # 获取cookies
            cookies = await context.cookies()
            cookie_dict = {}
            for cookie in cookies:
                if cookie['name'] in ['auth_token', 'ct0']:
                    cookie_dict[cookie['name']] = cookie['value']
            
            if cookie_dict.get('auth_token') and auth_info.get('authorization'):
                config = {
                    "authentication": {
                        "cookies": {
                            "auth_token": cookie_dict.get('auth_token', ''),
                            "ct0": cookie_dict.get('ct0', '')
                        },
                        "headers": {
                            "Authorization": auth_info.get('authorization', ''),
                            "X-Csrf-Token": auth_info.get('x-csrf-token', cookie_dict.get('ct0', ''))
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
                        "timeline_types": ["recommended"]
                    }
                }
                
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                
                print("🎉 认证信息提取成功！")
                print("💾 已保存到 config.json")
                print("\n✅ 现在可以运行: python daily_report_generator.py")
                return True
            else:
                print("❌ 认证信息不完整，请检查是否完全登录")
                print(f"获取到的信息: auth_token={bool(cookie_dict.get('auth_token'))}, authorization={bool(auth_info.get('authorization'))}")
                return False
                
        finally:
            await context.close()

def manual_guide():
    """手动配置指导"""
    print("""
📖 手动配置指导:

1. 🌐 正常浏览器打开 https://x.com/home 并登录

2. 🔧 按F12打开开发者工具 → Network标签

3. 🔄 刷新页面，在Network中找到包含 'HomeTimeline' 的请求

4. 📋 右键该请求 → Copy → Copy as cURL

5. ✂️ 从cURL中提取以下信息:
   • Cookie中的: auth_token=xxx; ct0=xxx  
   • Header中的: Authorization: Bearer xxx
   • Header中的: X-Csrf-Token: xxx

6. 📝 编辑config.json，替换对应的占位符

示例配置:
{
  "authentication": {
    "cookies": {
      "auth_token": "你的auth_token",
      "ct0": "你的ct0值"
    },
    "headers": {
      "Authorization": "Bearer 你的bearer_token",
      "X-Csrf-Token": "你的csrf_token"
    }
  }
}
""")

def alternative_method():
    """备用方法：使用现有浏览器会话"""
    print("""
🔧 备用方法 - 使用现有浏览器会话:

1. 正常打开Chrome/Firefox，登录X
2. 在浏览器中按F12 → Console标签
3. 粘贴以下代码并回车:

document.cookie.split(';').forEach(c => {
  const [name, value] = c.trim().split('=');
  if(['auth_token','ct0'].includes(name)) {
    console.log(`${name}: ${value}`);
  }
});

fetch('/i/api/graphql/homeTimeline').then(r => {
  console.log('Authorization:', r.headers.get('authorization'));
  console.log('X-Csrf-Token:', r.headers.get('x-csrf-token'));
}).catch(e => console.log('需要在X页面执行'));

4. 复制输出的认证信息到config.json
""")

if __name__ == "__main__":
    print("🔐 X认证配置工具 - 安全版")
    print("\n选择配置方式:")
    print("1 - 安全自动提取（推荐）")
    print("2 - 手动配置指导") 
    print("3 - 备用方法（浏览器Console）")
    print("4 - 退出")
    
    try:
        choice = input("\n请选择 [1-4]: ").strip()
        
        if choice == '1':
            asyncio.run(extract_with_real_browser())
        elif choice == '2':
            manual_guide()
        elif choice == '3':
            alternative_method()
        elif choice == '4':
            print("👋 退出")
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n👋 已取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("请尝试手动配置方式")