#!/usr/bin/env python3
"""
快速认证配置工具 - 一键配置X认证信息
"""

import json
import asyncio
from playwright.async_api import async_playwright

async def extract_auth():
    print("🚀 自动提取X认证信息")
    print("1. 浏览器将打开X登录页面")
    print("2. 请登录你的X账号") 
    print("3. 登录成功后工具会自动提取认证信息")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        auth_info = {}
        
        # 监听请求获取认证信息
        async def handle_request(request):
            if 'api.x.com' in request.url or 'twitter.com' in request.url:
                headers = request.headers
                if 'authorization' in headers:
                    auth_info['authorization'] = headers['authorization']
                if 'x-csrf-token' in headers:
                    auth_info['x-csrf-token'] = headers['x-csrf-token']
        
        page.on('request', handle_request)
        
        try:
            # 打开X并等待登录
            await page.goto('https://x.com/login')
            print("\n⏳ 等待登录...")
            
            # 等待用户登录完成（检测URL变化）
            while True:
                current_url = page.url
                if '/home' in current_url or '/timeline' in current_url:
                    break
                await asyncio.sleep(1)
            
            print("✅ 检测到登录成功！")
            print("🔄 正在提取认证信息...")
            
            # 导航到首页触发API请求
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
                return True
            else:
                print("❌ 认证信息不完整")
                return False
                
        finally:
            await browser.close()

def manual_method():
    print("\n📋 手动配置方法：")
    print("1. 打开 https://x.com/home 并登录")
    print("2. 按F12 → Network标签 → 刷新页面")
    print("3. 找到timeline API请求，复制以下信息：")
    print("   • Cookie: auth_token=xxx; ct0=xxx")
    print("   • Authorization: Bearer xxx")
    print("   • X-Csrf-Token: xxx")
    print("4. 编辑config.json填入这些值")

if __name__ == "__main__":
    print("🔑 X认证配置工具")
    print("\n选择方式:")
    print("1 - 自动提取（推荐）")
    print("2 - 手动配置指导")
    
    try:
        choice = input("\n请选择 [1/2]: ").strip()
        
        if choice == '1':
            asyncio.run(extract_auth())
        elif choice == '2':
            manual_method()
        else:
            print("无效选择")
    except KeyboardInterrupt:
        print("\n👋 已取消")