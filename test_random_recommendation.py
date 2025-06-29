#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ランダム推薦機能のテスト
"""

import sys
import os
from pathlib import Path

# パス設定
sys.path.append(str(Path(__file__).parent))

def test_random_recommendation():
    """ランダム推薦機能の直接テスト"""
    print("=== ランダム推薦機能テスト ===")
    
    try:
        from core.youtube_knowledge_manager import YouTubeKnowledgeManager
        
        manager = YouTubeKnowledgeManager()
        
        # ランダム推薦テスト
        print("🎲 ランダム推薦テスト開始")
        
        recommendations = manager.get_random_recommendation(
            context_hint="最近見た動画でおすすめ", 
            limit=2
        )
        
        if recommendations:
            print(f"✅ ランダム推薦成功: {len(recommendations)}件")
            for rec in recommendations:
                title = rec['data']['metadata'].get('title', '不明')[:60]
                print(f"  - {title}... (重み付きスコア: {rec['score']})")
        else:
            print("❌ ランダム推薦失敗")
        
        return len(recommendations) > 0
        
    except Exception as e:
        print(f"❌ ランダム推薦テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_context_builder():
    """ConversationContextBuilderでランダム推薦テスト"""
    print("\n=== コンテキストビルダーテスト ===")
    
    try:
        from core.conversation_context_builder import ConversationContextBuilder
        
        builder = ConversationContextBuilder()
        
        test_input = "最近見た動画でおすすめある"
        print(f"入力: '{test_input}'")
        
        # process_user_inputをテスト
        context_text = builder.process_user_input(test_input)
        
        if context_text:
            print("✅ コンテキスト生成成功")
            print(f"コンテキスト: {context_text[:200]}...")
        else:
            print("❌ コンテキスト生成失敗")
        
        return context_text is not None
        
    except Exception as e:
        print(f"❌ コンテキストビルダーテスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_query_check():
    """具体性チェック機能のテスト"""
    print("\n=== 具体性チェックテスト ===")
    
    try:
        from core.conversation_context_builder import ConversationContextBuilder
        
        builder = ConversationContextBuilder()
        
        test_queries = [
            "最近見た動画でおすすめある",  # 一般的
            "にじさんじの動画でおすすめある",  # 具体的
            "TRiNITYの動画知ってる",  # 具体的
            "面白い動画ある",  # 一般的
            "おすすめ動画"  # 一般的
        ]
        
        for query in test_queries:
            is_specific = builder._is_specific_query(query)
            print(f"'{query}' → {'具体的' if is_specific else '一般的'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 具体性チェックテスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メインテスト実行"""
    print("🔍 ランダム推薦機能デバッグ開始\n")
    
    results = []
    
    # 各テストの実行
    results.append(test_random_recommendation())
    results.append(test_context_builder())
    results.append(test_specific_query_check())
    
    # 結果サマリー
    print("\n" + "="*50)
    print("📊 テスト結果サマリー")
    print("="*50)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"❌ 失敗: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 全テスト合格！ランダム推薦機能は正常です。")
    else:
        print(f"\n⚠️ 問題があります。詳細は上記ログを確認してください。")

if __name__ == "__main__":
    main()