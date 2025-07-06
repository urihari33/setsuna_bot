#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL表示管理システム
音声チャットからのURL表示機能統合
"""

import webbrowser
import re
from typing import List, Dict, Any

def show_recommended_urls(context_data: Dict[str, Any], setsuna_response: str):
    """
    推薦動画URLを表示（せつな応答フィルター付き）
    
    Args:
        context_data: 知識システムからのコンテキストデータ
        setsuna_response: せつなの応答文
    """
    try:
        if not context_data or 'videos' not in context_data:
            return
        
        videos = context_data['videos']
        if not videos:
            return
        
        # せつなの応答から関連動画をフィルタリング
        filtered_videos = filter_videos_by_response(videos, setsuna_response)
        
        if filtered_videos:
            print("\n" + "="*60)
            print("🔗 推薦動画URL (せつなが言及した動画のみ)")
            print("="*60)
            
            for i, video in enumerate(filtered_videos[:5], 1):
                title = video.get('title', '不明な動画')
                channel = video.get('channel', '不明なチャンネル')
                video_id = video.get('video_id', '')
                url = f"https://www.youtube.com/watch?v={video_id}"
                
                print(f"{i}. {title}")
                print(f"   チャンネル: {channel}")
                print(f"   URL: {url}")
                print()
            
            print("💡 ブラウザで開くには上記URLをコピーしてください")
            print("="*60)
        else:
            print("🔍 [URL表示] せつなの応答に関連する動画が見つかりませんでした")
    
    except Exception as e:
        print(f"❌ [URL表示] エラー: {e}")

def filter_videos_by_response(videos: List[Dict[str, Any]], response: str) -> List[Dict[str, Any]]:
    """
    せつなの応答に言及された動画のみをフィルタリング
    
    Args:
        videos: 動画リスト
        response: せつなの応答文
        
    Returns:
        フィルタリングされた動画リスト
    """
    filtered_videos = []
    response_lower = response.lower()
    
    print(f"🔍 [フィルター] 応答分析: {response[:100]}...")
    
    for video in videos:
        title = video.get('title', '')
        channel = video.get('channel', '')
        
        # タイトルの部分的な言及をチェック
        title_mentioned = check_title_mention(title, response_lower)
        channel_mentioned = check_channel_mention(channel, response_lower)
        
        if title_mentioned or channel_mentioned:
            filtered_videos.append(video)
            reason = "タイトル言及" if title_mentioned else "チャンネル言及"
            print(f"🎯 [フィルター] 選択: {title} ({reason})")
    
    return filtered_videos

def check_title_mention(title: str, response: str) -> bool:
    """
    タイトルが応答に言及されているかチェック
    """
    if not title:
        return False
    
    title_lower = title.lower()
    
    # 直接的な言及
    if title_lower in response:
        return True
    
    # 部分的な言及（3文字以上の部分）
    title_parts = extract_meaningful_parts(title)
    for part in title_parts:
        if len(part) >= 3 and part.lower() in response:
            return True
    
    # 引用符での言及
    quoted_patterns = [
        r'「(.+?)」',  # 鍵括弧
        r'『(.+?)』',  # 二重鍵括弧
        r'"(.+?)"',   # ダブルクォート
    ]
    
    for pattern in quoted_patterns:
        matches = re.findall(pattern, response)
        for match in matches:
            if match.lower() in title_lower or title_lower in match.lower():
                return True
    
    return False

def check_channel_mention(channel: str, response: str) -> bool:
    """
    チャンネル名が応答に言及されているかチェック
    """
    if not channel:
        return False
    
    channel_lower = channel.lower()
    
    # 直接的な言及
    if channel_lower in response:
        return True
    
    # アーティスト名としての言及
    artist_patterns = [
        r'(\w+)の楽曲',
        r'(\w+)の曲',
        r'アーティスト.*?(\w+)',
    ]
    
    for pattern in artist_patterns:
        matches = re.findall(pattern, response)
        for match in matches:
            if match.lower() in channel_lower:
                return True
    
    return False

def extract_meaningful_parts(text: str) -> List[str]:
    """
    テキストから意味のある部分を抽出
    """
    # 括弧内の内容を除去
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = re.sub(r'【[^】]*】', '', text)
    
    # 記号を除去
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # 単語に分割
    parts = []
    
    # カタカナ（3文字以上）
    katakana_parts = re.findall(r'[ァ-ヶー]{3,}', text)
    parts.extend(katakana_parts)
    
    # 英語（3文字以上）
    english_parts = re.findall(r'[A-Za-z]{3,}', text)
    parts.extend(english_parts)
    
    # 漢字（2文字以上）
    kanji_parts = re.findall(r'[一-龯]{2,}', text)
    parts.extend(kanji_parts)
    
    return parts

# テスト用関数
def test_url_display_manager():
    """URL表示管理システムのテスト"""
    print("🧪 URL表示管理システムテスト開始")
    print("="*50)
    
    # テストデータ
    test_context = {
        'videos': [
            {
                'video_id': 'test1',
                'title': 'XOXO - TRiNITY',
                'channel': 'TRiNITY Official'
            },
            {
                'video_id': 'test2', 
                'title': 'アドベンチャー',
                'channel': 'ボカロチャンネル'
            },
            {
                'video_id': 'test3',
                'title': '関係ない動画',
                'channel': '他のチャンネル'
            }
        ]
    }
    
    test_responses = [
        "「XOXO」はTRiNITYの代表的な楽曲です。",
        "アドベンチャーという曲をご存知ですか？",
        "音楽について一般的にお話ししましょう。"
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"\n📝 テスト {i}: {response}")
        show_recommended_urls(test_context, response)
    
    print("✅ テスト完了")

if __name__ == "__main__":
    test_url_display_manager()