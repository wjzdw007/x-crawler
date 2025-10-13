#!/usr/bin/env python3
"""
调试推文提取逻辑
"""

import json
from pathlib import Path

def debug_tweet_extraction():
    # 读取一个时间线API文件
    test_file = "analysis_data/api_responses/response_213337_350313.json"
    
    print(f"🔍 调试文件: {test_file}")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        response_data = json.load(f)
    
    print(f"📄 文件URL: {response_data.get('url', 'unknown')}")
    
    data = response_data.get('data', {})
    print(f"🔢 data keys: {list(data.keys())}")
    
    # 检查data.data的结构
    inner_data = data.get('data', {})
    print(f"🔢 inner data keys: {list(inner_data.keys())}")
    
    home = inner_data.get('home', {})
    print(f"🏠 home keys: {list(home.keys())}")
    
    home_timeline = home.get('home_timeline_urt', {})
    print(f"📈 home_timeline_urt keys: {list(home_timeline.keys())}")
    
    instructions = home_timeline.get('instructions', [])
    print(f"📋 instructions count: {len(instructions)}")
    
    for i, instruction in enumerate(instructions):
        print(f"  指令 {i}: {instruction.get('type')}")
        
        if instruction.get('type') == 'TimelineAddEntries':
            entries = instruction.get('entries', [])
            print(f"    条目数: {len(entries)}")
            
            for j, entry in enumerate(entries[:5]):  # 只看前5个
                entry_id = entry.get('entryId', '')
                print(f"    条目 {j}: {entry_id}")
                
                if 'tweet-' in entry_id:
                    content = entry.get('content', {})
                    print(f"      content keys: {list(content.keys())}")
                    
                    item_content = content.get('itemContent', {})
                    print(f"      itemContent keys: {list(item_content.keys())}")
                    
                    tweet_results = item_content.get('tweet_results', {})
                    print(f"      tweet_results keys: {list(tweet_results.keys())}")
                    
                    tweet_data = tweet_results.get('result', {})
                    print(f"      result keys: {list(tweet_data.keys())}")
                    print(f"      __typename: {tweet_data.get('__typename')}")
                    print(f"      rest_id: {tweet_data.get('rest_id')}")
                    
                    # 检查文本内容
                    legacy = tweet_data.get('legacy', {})
                    full_text = legacy.get('full_text', '')
                    print(f"      legacy.full_text: {full_text[:50]}...")
                    
                    # 检查长文推文
                    note_tweet = tweet_data.get('note_tweet', {})
                    if note_tweet:
                        note_result = note_tweet.get('note_tweet_results', {}).get('result', {})
                        note_text = note_result.get('text', '')
                        print(f"      note_tweet text: {note_text[:50]}...")
                    
                    print("      ---")

if __name__ == "__main__":
    debug_tweet_extraction()