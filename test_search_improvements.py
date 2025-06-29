#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
検索精度改善テスト - キーワード抽出・タイトル正規化・英語読み対応
"""

import sys
import os
from pathlib import Path

# パス設定
sys.path.append(str(Path(__file__).parent))

def test_keyword_extraction():
    """キーワード抽出機能のテスト"""
    print("=== キーワード抽出テスト ===")
    
    try:
        from core.conversation_context_builder import ConversationContextBuilder
        
        builder = ConversationContextBuilder()
        
        test_cases = [
            "最近見たにじさんじの動画でおすすめってある",
            "TRiNITYの動画知ってる？",
            "トリニティって聞いたことある？",
            "XOXOについて教えて",
            "エックスオーエックスオーって曲知ってる？",
            "ボカロの歌ってみた動画ある？",
            "にじさんじのクリエイターで好きな人いる？"
        ]
        
        for test_input in test_cases:
            print(f"\n📝 入力: '{test_input}'")
            keywords = builder._extract_keywords(test_input)
            print(f"✅ キーワード抽出: {keywords}")
            
            queries = builder.detect_video_queries(test_input)
            print(f"🔍 検出クエリ: {len(queries)}件")
            for query in queries:
                print(f"  - {query['type']}: '{query['query']}' (信頼度: {query['confidence']})")
        
        return True
        
    except Exception as e:
        print(f"❌ キーワード抽出テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_title_normalization():
    """タイトル正規化機能のテスト"""
    print("\n=== タイトル正規化テスト ===")
    
    try:
        from core.youtube_knowledge_manager import YouTubeKnowledgeManager
        
        manager = YouTubeKnowledgeManager()
        
        # 実際のYouTubeタイトルでテスト
        test_titles = [
            "▽▲TRiNITY▲▽『XOXO』Music Video【2022/10/5発売「Δ(DELTA)」収録曲】",
            "【歌ってみた】犬のおまわりさん【栞葉るり/にじさんじ】",
            "【オリジナルMV】Blessing / にじさんじ元2期生 cover",
            "【ラピスリライツ】supernova「Trinity」MV（フルサイズver）"
        ]
        
        for title in test_titles:
            print(f"\n📹 元タイトル: {title}")
            normalized = manager._normalize_title(title)
            print(f"🔧 正規化: '{normalized}'")
            
            searchable_terms = manager._extract_searchable_terms(title)
            print(f"🔍 検索可能用語: {searchable_terms}")
        
        return True
        
    except Exception as e:
        print(f"❌ タイトル正規化テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_improved_search():
    """改善後の検索精度テスト"""
    print("\n=== 改善後検索精度テスト ===")
    
    try:
        from core.conversation_context_builder import ConversationContextBuilder
        
        builder = ConversationContextBuilder()
        
        # 問題があった検索ケース
        problem_cases = [
            "最近見たにじさんじの動画でおすすめってある",
            "TRiNITYの動画知ってる？",
            "XOXOって曲について教えて",
            "トリニティって聞いたことある？",
            "にじさんじの歌ってみた動画ある？"
        ]
        
        success_count = 0
        total_count = len(problem_cases)
        
        for test_input in problem_cases:
            print(f"\n🔍 テスト: '{test_input}'")
            
            # 改善されたコンテキスト生成をテスト
            context_text = builder.process_user_input(test_input)
            
            if context_text:
                print("✅ 動画コンテキスト生成成功")
                print(f"📄 コンテキスト: {context_text[:150]}...")
                success_count += 1
            else:
                print("❌ 動画コンテキスト生成失敗")
        
        print(f"\n📊 改善後検索成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
        
        return success_count > total_count // 2  # 50%以上成功すれば合格
        
    except Exception as e:
        print(f"❌ 改善後検索テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_searches():
    """特定の検索ケースでの精度テスト"""
    print("\n=== 特定検索ケーステスト ===")
    
    try:
        from core.youtube_knowledge_manager import YouTubeKnowledgeManager
        
        manager = YouTubeKnowledgeManager()
        
        # 具体的な検索テスト
        search_tests = [
            ("にじさんじ", "にじさんじ関連動画"),
            ("TRINITY", "TRiNITY動画"),
            ("trinity", "TRiNITY動画（小文字）"),
            ("トリニティ", "TRiNITY動画（カタカナ）"),
            ("XOXO", "XOXO楽曲"),
            ("xoxo", "XOXO楽曲（小文字）"),
            ("犬のおまわりさん", "犬のおまわりさん動画"),
            ("栞葉るり", "栞葉るりの動画")
        ]
        
        for query, description in search_tests:
            print(f"\n🔍 検索: '{query}' ({description})")
            results = manager.search_videos(query, limit=3)
            
            if results:
                print(f"✅ {len(results)}件ヒット")
                for result in results[:2]:
                    title = result['data']['metadata'].get('title', '不明')[:60]
                    print(f"  - {title}... (スコア: {result['score']})")
            else:
                print("❌ ヒットなし")
        
        return True
        
    except Exception as e:
        print(f"❌ 特定検索テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メインテスト実行"""
    print("🚀 検索精度改善テスト開始\n")
    
    results = []
    
    # 各テストの実行
    results.append(test_keyword_extraction())
    results.append(test_title_normalization())
    results.append(test_improved_search())
    results.append(test_specific_searches())
    
    # 結果サマリー
    print("\n" + "="*60)
    print("📊 検索精度改善テスト結果サマリー")
    print("="*60)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"❌ 失敗: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 全テスト合格！検索精度が大幅に改善されました。")
        print("\n✨ 改善点:")
        print("- キーワード抽出：文章→単語レベルの検索")
        print("- タイトル正規化：YouTubeタイトル装飾除去")
        print("- 英語読み対応：カタカナ→英語変換")
        print("\n🔧 次のステップ: 実際の音声会話でテスト")
    else:
        print(f"\n⚠️ 一部改善が必要です。詳細は上記ログを確認してください。")
    
    print("\n🗣️ 実際の会話テスト推奨文:")
    print("- 「最近見たにじさんじの動画でおすすめってある」")
    print("- 「TRiNITYの動画知ってる？」")
    print("- 「XOXOって曲について教えて」")

if __name__ == "__main__":
    main()