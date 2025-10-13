#!/usr/bin/env python3
"""
隐身认证提取工具 - 绕过自动化检测的认证信息提取
"""

import json
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def stealth_extract():
    """使用隐身模式提取认证信息，绕过Google安全检测"""
    print("🥷 隐身模式：绕过自动化检测")
    print("这个版本专门针对Google登录优化")
    
    async with async_playwright() as p:
        # 使用Chrome，添加大量反检测参数
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=1000,  # 减慢操作速度，更像人类
            args=[
                '--disable-blink-features=AutomationControlled',
                '--exclude-switches=enable-automation',
                '--disable-extensions-except',
                '--disable-plugins-discovery',
                '--disable-plugins',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-popup-blocking',
                '--disable-translate',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-field-trial-config',
                '--disable-back-forward-cache',
                '--disable-background-networking',
                '--disable-features=TranslateUI,VizDisplayCompositor',
                '--disable-ipc-flooding-protection',
                '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        )
        
        # 创建上下文，添加更多真实浏览器特征
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN,zh',
            timezone_id='Asia/Shanghai',
            extra_http_headers={
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        page = await context.new_page()
        
        # 注入反检测脚本
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en'],
            });
            
            window.chrome = {
                runtime: {},
            };
            
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: () => Promise.resolve({ state: 'granted' }),
                }),
            });
        """)
        
        auth_info = {}
        
        # 监听请求
        async def handle_request(request):
            if any(domain in request.url for domain in ['api.x.com', 'twitter.com', 'x.com']):
                headers = request.headers
                if 'authorization' in headers:
                    auth_info['authorization'] = headers['authorization']
                    print(f"✅ 获取到 Authorization")
                if 'x-csrf-token' in headers:
                    auth_info['x-csrf-token'] = headers['x-csrf-token']
                    print(f"✅ 获取到 CSRF Token")
        
        page.on('request', handle_request)
        
        try:
            print("\n🌐 正在打开X登录页面...")
            await page.goto('https://x.com/login', wait_until='domcontentloaded')
            
            # 等待页面完全加载
            await page.wait_for_timeout(3000)
            
            print("\n💡 登录提示:")
            print("1. 现在可以正常使用Google登录")
            print("2. 如果仍提示不安全，可以:")
            print("   - 点击'了解详情' → '转到x.com（不安全）'")
            print("   - 或者直接用X用户名密码登录")
            print("3. 登录成功后，这个窗口会自动检测并提取认证信息")
            
            print("\n⏳ 等待登录完成...")
            
            # 检测登录状态
            login_success = False
            check_count = 0
            max_checks = 300  # 5分钟超时
            
            while not login_success and check_count < max_checks:
                try:
                    current_url = page.url
                    
                    # 检测URL变化表示登录成功
                    if '/home' in current_url or '/timeline' in current_url:
                        login_success = True
                        break
                    
                    # 检测页面元素
                    try:
                        await page.wait_for_selector('[data-testid="AppTabBar_Home_Link"]', timeout=1000)
                        login_success = True
                        break
                    except:
                        pass
                    
                    check_count += 1
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    await asyncio.sleep(1)
                    continue
            
            if login_success:
                print("🎉 检测到登录成功！")
                print("🔄 正在提取认证信息...")
                
                # 确保在主页
                if '/home' not in page.url:
                    await page.goto('https://x.com/home')
                
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(5000)  # 等待API请求
                
                # 获取cookies
                cookies = await context.cookies()
                cookie_dict = {}
                for cookie in cookies:
                    if cookie['name'] in ['auth_token', 'ct0']:
                        cookie_dict[cookie['name']] = cookie['value']
                        print(f"✅ 获取到 {cookie['name']}")
                
                # 检查是否获取到完整认证信息
                if (cookie_dict.get('auth_token') and 
                    cookie_dict.get('ct0') and 
                    auth_info.get('authorization')):
                    
                    config = {
                        "authentication": {
                            "cookies": {
                                "auth_token": cookie_dict['auth_token'],
                                "ct0": cookie_dict['ct0']
                            },
                            "headers": {
                                "Authorization": auth_info['authorization'],
                                "X-Csrf-Token": auth_info.get('x-csrf-token', cookie_dict['ct0'])
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
                    
                    print("\n🎉 认证信息提取成功！")
                    print("💾 已保存到 config.json")
                    print("\n🚀 现在可以运行:")
                    print("python daily_report_generator.py")
                    
                    return True
                else:
                    print("\n⚠️ 认证信息不完整:")
                    print(f"   auth_token: {'✅' if cookie_dict.get('auth_token') else '❌'}")
                    print(f"   ct0: {'✅' if cookie_dict.get('ct0') else '❌'}")
                    print(f"   authorization: {'✅' if auth_info.get('authorization') else '❌'}")
                    print("\n💡 建议:")
                    print("1. 尝试刷新页面或浏览几条推文")
                    print("2. 然后重新运行这个工具")
                    return False
            else:
                print("\n⏰ 登录检测超时")
                print("请确保已完成登录，然后重新运行工具")
                return False
                
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            return False
        finally:
            # 询问是否关闭浏览器
            print("\n❓ 是否关闭浏览器？(y/n，默认5秒后自动关闭)")
            try:
                await asyncio.wait_for(asyncio.get_event_loop().run_in_executor(None, input), timeout=5.0)
            except asyncio.TimeoutError:
                pass
            await browser.close()

def show_troubleshooting():
    """显示故障排除指南"""
    print("""
🛠️ Google登录故障排除:

1. 如果看到"此浏览器或应用可能不安全"：
   ✅ 点击 "了解详情"
   ✅ 点击 "转到x.com（不安全）"
   ✅ 或者点击 "继续"

2. 如果仍然无法登录Google：
   ✅ 尝试直接用X用户名/密码登录
   ✅ 或者用手机号登录

3. 如果提取失败：
   ✅ 登录后在X上浏览几条推文
   ✅ 确保看到主页时间线
   ✅ 重新运行工具

4. 终极解决方案：
   ✅ 正常浏览器登录X
   ✅ F12 → Network → 找HomeTimeline请求
   ✅ 复制认证信息到config.json
""")

if __name__ == "__main__":
    print("🥷 X认证隐身提取工具")
    print("专门解决Google登录安全检测问题")
    
    try:
        show_troubleshooting()
        print("\n🚀 开始自动提取...")
        asyncio.run(stealth_extract())
    except KeyboardInterrupt:
        print("\n👋 已取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n建议使用手动配置方式")