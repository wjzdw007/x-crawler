#!/usr/bin/env python3
"""
基于analyzer.py成功经验的认证提取工具
使用launch_persistent_context保持登录状态
"""

import json
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def extract_auth_like_analyzer():
    """使用和analyzer.py相同的方式提取认证信息"""
    print("🎯 使用analyzer.py的成功方法")
    print("这种方式已经验证可以正常登录Google账号")
    
    # 使用和analyzer.py完全相同的设置
    user_data_dir = os.path.join(os.getcwd(), "browser_data")
    
    async with async_playwright() as p:
        print(f"📂 使用用户数据目录: {user_data_dir}")
        
        # 完全复制analyzer.py的配置
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # 获取或创建页面，和analyzer.py一样
        if context.pages:
            page = context.pages[0]
        else:
            page = await context.new_page()
        
        # 存储认证信息
        auth_info = {'cookies': {}, 'headers': {}}
        
        # 监听请求获取认证信息
        async def handle_request(request):
            if any(domain in request.url for domain in ['api.x.com', 'twitter.com', 'x.com']):
                headers = request.headers
                if 'authorization' in headers:
                    auth_info['headers']['authorization'] = headers['authorization']
                    print(f"✅ 获取到Authorization")
                if 'x-csrf-token' in headers:
                    auth_info['headers']['x-csrf-token'] = headers['x-csrf-token']
                    print(f"✅ 获取到X-Csrf-Token")
        
        page.on('request', handle_request)
        
        try:
            print("\n🌐 正在访问 x.com...")
            await page.goto("https://x.com/home")
            
            print("\n💡 操作说明:")
            print("1. 如果需要登录，现在可以正常使用Google登录了")
            print("2. 登录成功后，浏览几条推文来触发API请求")
            print("3. 看到认证信息获取成功后，按任意键继续")
            
            # 等待用户登录和操作
            print("\n⏳ 等待获取认证信息...")
            print("（系统会自动监听API请求并提取认证信息）")
            
            # 检测认证信息获取情况
            wait_time = 0
            max_wait = 180  # 3分钟超时
            
            while wait_time < max_wait:
                # 获取cookies
                cookies = await context.cookies()
                for cookie in cookies:
                    if cookie['name'] in ['auth_token', 'ct0']:
                        auth_info['cookies'][cookie['name']] = cookie['value']
                        if cookie['name'] == 'auth_token':
                            print(f"✅ 获取到 auth_token")
                        if cookie['name'] == 'ct0':
                            print(f"✅ 获取到 ct0")
                
                # 检查是否获取到所有必需信息
                has_auth_token = bool(auth_info['cookies'].get('auth_token'))
                has_ct0 = bool(auth_info['cookies'].get('ct0'))
                has_authorization = bool(auth_info['headers'].get('authorization'))
                
                if has_auth_token and has_ct0 and has_authorization:
                    print("\n🎉 成功获取所有认证信息！")
                    break
                
                await asyncio.sleep(2)
                wait_time += 2
            
            # 提示用户确认
            print(f"\n📊 获取状态:")
            print(f"  auth_token: {'✅' if auth_info['cookies'].get('auth_token') else '❌'}")
            print(f"  ct0: {'✅' if auth_info['cookies'].get('ct0') else '❌'}")
            print(f"  authorization: {'✅' if auth_info['headers'].get('authorization') else '❌'}")
            
            if (auth_info['cookies'].get('auth_token') and 
                auth_info['cookies'].get('ct0') and 
                auth_info['headers'].get('authorization')):
                
                # 构建配置
                config = {
                    "authentication": {
                        "cookies": {
                            "auth_token": auth_info['cookies']['auth_token'],
                            "ct0": auth_info['cookies']['ct0']
                        },
                        "headers": {
                            "Authorization": auth_info['headers']['authorization'],
                            "X-Csrf-Token": auth_info['headers'].get('x-csrf-token', auth_info['cookies']['ct0'])
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
                
                # 保存配置
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                
                print("\n🎉 认证配置完成!")
                print("💾 已保存到 config.json")
                print("\n🚀 现在可以运行:")
                print("python daily_report_generator.py")
                
                return True
            else:
                print("\n⚠️ 认证信息不完整")
                print("建议:")
                print("1. 确保已完全登录X")
                print("2. 尝试刷新页面或浏览更多推文")
                print("3. 重新运行此工具")
                return False
                
        except KeyboardInterrupt:
            print("\n👋 用户取消")
            return False
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            return False
        finally:
            # 保持浏览器开启，就像analyzer.py一样
            print("\n💡 保持浏览器开启状态以便调试...")
            print("按 Ctrl+C 退出")
            try:
                await asyncio.sleep(30)  # 30秒后自动关闭
            except KeyboardInterrupt:
                pass
            await context.close()

if __name__ == "__main__":
    print("🔑 X认证提取工具 - 基于analyzer.py成功经验")
    print("使用和分析工具相同的浏览器配置，支持Google登录")
    
    try:
        asyncio.run(extract_auth_like_analyzer())
    except KeyboardInterrupt:
        print("\n👋 退出")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("如果问题持续，可以:")
        print("1. 删除 browser_data 目录后重试")
        print("2. 或使用手动配置方式")