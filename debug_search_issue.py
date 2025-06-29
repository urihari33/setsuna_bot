#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
検索問題のデバッグ - なぜ「にじさんじ」で検索がヒットしないのか調査
"""

import sys
import os
from pathlib import Path

# パス設定
sys.path.append(str(Path(__file__).parent))

def debug_keyword_extraction():
    """キーワード抽出のデバッグ"""
    print("=== キーワード抽出デバッグ ===")
    
    from core.conversation_context_builder import ConversationContextBuilder
    
    builder = ConversationContextBuilder()
    test_input = "最近見たにじさんじの動画でおすすめってある"
    
    print(f"入力: '{test_input}'")
    
    # 1. キーワード抽出
    keywords = builder._extract_keywords(test_input)
    print(f"抽出キーワード: {keywords}")
    
    # 2. クエリ検出
    queries = builder.detect_video_queries(test_input)
    print(f"検出クエリ: {len(queries)}件")
    for i, query in enumerate(queries):
        print(f"  {i+1}. {query['type']}: '{query['query']}' (信頼度: {query['confidence']})")
    
    return queries

def debug_video_search():
    """動画検索のデバッグ"""
    print("\n=== 動画検索デバッグ ===")
    
    from core.youtube_knowledge_manager import YouTubeKnowledgeManager
    
    manager = YouTubeKnowledgeManager()
    
    # 直接検索テスト
    test_queries = [
        "にじさんじ",
        "最近見たにじさんじ", 
        "nijisanji",
        "犬のおまわりさん"
    ]
    
    for query in test_queries:
        print(f"\n検索クエリ: '{query}'")
        results = manager.search_videos(query, limit=3)
        
        if results:
            print(f"✅ {len(results)}件ヒット")
            for result in results:
                title = result['data']['metadata'].get('title', '不明')[:60]
                print(f"  - {title}... (スコア: {result['score']})")
        else:
            print("❌ ヒットなし")

def debug_context_building():
    """コンテキスト構築のデバッグ"""
    print("\n=== コンテキスト構築デバッグ ===")
    
    from core.conversation_context_builder import ConversationContextBuilder
    
    builder = ConversationContextBuilder()
    
    # キーワード抽出
    test_input = "最近見たにじさんじの動画でおすすめってある"
    queries = debug_keyword_extraction()
    
    # 各クエリでの検索結果確認
    for query in queries:
        print(f"\nクエリ '{query['query']}' での検索:")
        search_results = builder.knowledge_manager.search_videos(query['query'], limit=3)
        
        if search_results:
            print(f"✅ {len(search_results)}件ヒット")
            for result in search_results:
                title = result['data']['metadata'].get('title', '不明')[:60]
                print(f"  - {title}... (スコア: {result['score']})")
        else:
            print("❌ ヒットなし")
    
    # build_video_context の動作確認
    print(f"\nbuild_video_context での処理:")
    context = builder.build_video_context(queries)
    
    if context:
        print(f"✅ コンテキスト構築成功: {len(context['videos'])}件")
        for video in context['videos']:
            print(f"  - {video['title'][:60]}... (スコア: {video['search_score']})")
    else:
        print("❌ コンテキスト構築失敗")

def debug_database_content():
    """データベース内容のデバッグ"""
    print("\n=== データベース内容デバッグ ===")
    
    from core.youtube_knowledge_manager import YouTubeKnowledgeManager
    
    manager = YouTubeKnowledgeManager()
    videos = manager.knowledge_db.get("videos", {})
    
    print(f"総動画数: {len(videos)}")
    
    # にじさんじ関連動画を探す
    nijisanji_videos = []
    for video_id, video_data in videos.items():
        metadata = video_data.get("metadata", {})
        title = metadata.get("title", "")
        channel = metadata.get("channel_title", "")
        
        if "にじさんじ" in title.lower() or "にじさんじ" in channel.lower():
            nijisanji_videos.append({
                "title": title,
                "channel": channel,
                "video_id": video_id
            })
    
    print(f"にじさんじ関連動画: {len(nijisanji_videos)}件")
    for video in nijisanji_videos[:5]:
        print(f"  - {video['title'][:60]}...")
        print(f"    チャンネル: {video['channel']}")

def main():
    """メインデバッグ実行"""
    print("🔍 検索問題デバッグ開始\n")
    
    # 各段階をデバッグ
    debug_database_content()
    debug_keyword_extraction()
    debug_video_search()
    debug_context_building()
    
    print("\n" + "="*60)
    print("📊 デバッグ完了")
    print("問題の原因が特定できましたか？")

if __name__ == "__main__":
    main()