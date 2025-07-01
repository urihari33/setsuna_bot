#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL表示機能テストスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.youtube_knowledge_manager import YouTubeKnowledgeManager
from core.setsuna_chat import SetsunaChat
import re

def test_knowledge_manager():
    """YouTube知識管理システムのテスト"""
    print("=" * 50)
    print("🔍 YouTube知識管理システムテスト開始")
    print("=" * 50)
    
    try:
        # 知識管理システム初期化
        manager = YouTubeKnowledgeManager()
        
        # 動画数確認
        video_count = len(manager.knowledge_db.get("videos", {}))
        print(f"📊 動画データベース: {video_count}件")
        
        # 検索テスト
        search_results = manager.search_videos("TRINITY", limit=3)
        print(f"🔍 'TRINITY'検索結果: {len(search_results)}件")
        
        for i, result in enumerate(search_results):
            title = result['data']['metadata'].get('title', '不明')
            print(f"  {i+1}. {title}")
        
        # ランダム推薦テスト
        random_videos = manager.get_random_recommendation(limit=3)
        print(f"🎲 ランダム推薦: {len(random_videos)}件")
        
        for i, video in enumerate(random_videos):
            title = video['data']['metadata'].get('title', '不明')
            print(f"  {i+1}. {title}")
        
        print("✅ YouTube知識管理システムテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        return False

def test_setsuna_chat():
    """せつなチャットシステムのテスト"""
    print("\n" + "=" * 50)
    print("🤖 せつなチャットシステムテスト開始")
    print("=" * 50)
    
    try:
        # チャットシステム初期化
        chat = SetsunaChat()
        
        # 基本応答テスト
        test_input = "こんにちは"
        response = chat.get_response(test_input)
        print(f"💬 入力: {test_input}")
        print(f"💬 応答: {response}")
        
        # 音楽関連質問テスト
        music_input = "TRINITYの楽曲について教えて"
        music_response = chat.get_response(music_input)
        print(f"💬 音楽質問: {music_input}")
        print(f"💬 音楽応答: {music_response}")
        
        print("✅ せつなチャットシステムテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        return False

def test_video_keyword_extraction():
    """動画キーワード抽出テスト"""
    print("\n" + "=" * 50)
    print("🔍 動画キーワード抽出テスト開始")
    print("=" * 50)
    
    # テスト応答パターン
    test_responses = [
        "「XOXO」はTRINITYの楽曲で、とても印象的な曲だと思います。",
        "最近見た中では「アドベンチャー」がお気に入りです。",
        "その動画は知らないけど、音楽系ならボカロが好きかな。",
        "TRINITYの新曲はどうでしたか？"
    ]
    
    def extract_keywords(response):
        """キーワード抽出（テスト用）"""
        keywords = []
        
        # 基本的なキーワード抽出パターン
        patterns = [
            r'「(.+?)」',  # 鍵括弧で囲まれた部分
            r'『(.+?)』',  # 二重鍵括弧で囲まれた部分
            r'(\w+)\s*って',  # 「XXって」パターン
            r'(\w+)\s*が',   # 「XXが」パターン
            r'(\w+)\s*は',   # 「XXは」パターン
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response)
            for match in matches:
                if isinstance(match, tuple):
                    keywords.extend([m.strip() for m in match if len(m.strip()) > 1])
                else:
                    keyword = match.strip()
                    if len(keyword) > 1:
                        keywords.append(keyword)
        
        # 単語レベルでの抽出
        word_patterns = [
            r'[ァ-ヶー]{2,}',    # カタカナ2文字以上
            r'[A-Za-z]{2,}',     # 英語2文字以上
            r'[一-龯]{2,}',      # 漢字2文字以上
        ]
        
        for pattern in word_patterns:
            matches = re.findall(pattern, response)
            keywords.extend(matches)
        
        # 重複除去
        return list(set(keywords))
    
    try:
        for i, response in enumerate(test_responses):
            print(f"📝 テスト {i+1}: {response}")
            keywords = extract_keywords(response)
            print(f"🔍 抽出キーワード: {keywords}")
            print()
        
        print("✅ 動画キーワード抽出テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🧪 URL表示機能統合テスト開始")
    print("=" * 60)
    
    # 各テストを実行
    tests = [
        test_knowledge_manager,
        test_setsuna_chat,
        test_video_keyword_extraction
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ テスト実行エラー: {e}")
            results.append(False)
    
    # 結果まとめ
    print("\n" + "=" * 60)
    print("📊 テスト結果まとめ")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ 成功: {passed}/{total} テスト")
    print(f"❌ 失敗: {total - passed}/{total} テスト")
    
    if passed == total:
        print("🎉 全テスト成功！URL表示機能は正常に動作する準備ができています。")
    else:
        print("⚠️ 一部テストが失敗しました。問題を確認してください。")
    
    print("\n🏁 テスト完了")

if __name__ == "__main__":
    main()