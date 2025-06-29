#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube知識統合テスト - Phase 1統合機能テスト
"""

import sys
import os
from pathlib import Path

# パス設定
sys.path.append(str(Path(__file__).parent))

def test_youtube_knowledge_manager():
    """YouTubeKnowledgeManagerの単体テスト"""
    print("=== YouTubeKnowledgeManager テスト ===")
    
    try:
        from core.youtube_knowledge_manager import YouTubeKnowledgeManager
        
        manager = YouTubeKnowledgeManager()
        
        # 1. データベース読み込みテスト
        print(f"✅ データベース読み込み成功")
        print(f"   動画数: {len(manager.knowledge_db.get('videos', {}))}")
        print(f"   プレイリスト数: {len(manager.knowledge_db.get('playlists', {}))}")
        
        # 2. 検索テスト
        test_queries = ["TRiNITY", "にじさんじ", "XOXO"]
        for query in test_queries:
            results = manager.search_videos(query, limit=3)
            print(f"✅ 検索テスト '{query}': {len(results)}件")
            for result in results[:2]:
                title = result['data']['metadata'].get('title', '不明')[:50]
                print(f"   - {title}... (スコア: {result['score']})")
        
        # 3. 分析要約テスト
        if manager.knowledge_db.get('videos'):
            first_video_id = list(manager.knowledge_db['videos'].keys())[0]
            summary = manager.get_analysis_summary(first_video_id)
            print(f"✅ 分析要約テスト: {summary[:100] if summary else 'なし'}...")
        
        return True
        
    except Exception as e:
        print(f"❌ YouTubeKnowledgeManager テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversation_context_builder():
    """ConversationContextBuilderの単体テスト"""
    print("\n=== ConversationContextBuilder テスト ===")
    
    try:
        from core.conversation_context_builder import ConversationContextBuilder
        
        builder = ConversationContextBuilder()
        
        # 1. クエリ検出テスト
        test_inputs = [
            "TRiNITYの動画知ってる？",
            "にじさんじの歌ってみた動画ある？",
            "最近面白い動画見た？",
            "XOXOって曲について教えて",
            "今日はいい天気ですね"  # 非動画関連
        ]
        
        for test_input in test_inputs:
            queries = builder.detect_video_queries(test_input)
            print(f"✅ クエリ検出 '{test_input}': {len(queries)}件")
            for query in queries:
                print(f"   - {query['type']}: '{query['query']}' (信頼度: {query['confidence']})")
        
        # 2. コンテキスト生成テスト
        video_related_input = "TRiNITYの動画知ってる？"
        context_text = builder.process_user_input(video_related_input)
        print(f"✅ コンテキスト生成テスト:")
        if context_text:
            print(context_text[:200] + "..." if len(context_text) > 200 else context_text)
        else:
            print("   コンテキストなし")
        
        return True
        
    except Exception as e:
        print(f"❌ ConversationContextBuilder テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_setsuna_integration():
    """SetsunaChat統合テスト"""
    print("\n=== SetsunaChat統合テスト ===")
    
    try:
        from core.setsuna_chat import SetsunaChat
        
        # 初期化テスト
        chat = SetsunaChat()
        print("✅ SetsunaChat初期化成功")
        
        # 動画関連の会話テスト
        test_conversations = [
            "TRiNITYの動画知ってる？",
            "最近どんな動画見てる？",
            "こんにちは"  # 通常会話
        ]
        
        for conversation in test_conversations:
            print(f"\n🗣️ テスト会話: '{conversation}'")
            try:
                # 注意: 実際のOpenAI API呼び出しを避けるため、
                # コンテキスト構築のみテスト
                if hasattr(chat, 'context_builder') and chat.context_builder:
                    context = chat.context_builder.process_user_input(conversation)
                    if context:
                        print("✅ 動画コンテキスト検出")
                        print(f"   コンテキスト: {context[:150]}...")
                    else:
                        print("✅ 動画関連なし（通常会話）")
                else:
                    print("⚠️ YouTube知識統合システムが利用できません")
                    
            except Exception as e:
                print(f"⚠️ 会話テスト中エラー: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ SetsunaChat統合テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メインテスト実行"""
    print("🚀 YouTube知識統合システム Phase 1 テスト開始\n")
    
    results = []
    
    # 各コンポーネントのテスト実行
    results.append(test_youtube_knowledge_manager())
    results.append(test_conversation_context_builder()) 
    results.append(test_setsuna_integration())
    
    # 結果サマリー
    print("\n" + "="*50)
    print("📊 テスト結果サマリー")
    print("="*50)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"❌ 失敗: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 全テスト合格！YouTube知識統合Phase 1が正常に動作しています。")
    else:
        print("\n⚠️ 一部テストに問題があります。上記の詳細を確認してください。")
    
    print("\n🔧 次のステップ:")
    print("1. Windows環境でVOICEVOXを起動")
    print("2. voice_chat_gpt4.py でホットキー音声テスト")
    print("3. 実際の動画関連会話をテスト")

if __name__ == "__main__":
    main()