#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
クエリ検出システムのデバッグ
"""

import sys
import os
from pathlib import Path

# パス設定
sys.path.append(str(Path(__file__).parent))

def debug_query_detection():
    """クエリ検出の詳細デバッグ"""
    print("=== クエリ検出システムデバッグ ===")
    
    try:
        from core.conversation_context_builder import ConversationContextBuilder
        
        builder = ConversationContextBuilder()
        
        # 問題の入力をテスト
        test_input = "じゃあ アドベンチャーは"
        
        print(f"🔍 デバッグ対象: '{test_input}'")
        
        # ステップ1: キーワード抽出
        print("\n【ステップ1: キーワード抽出】")
        keywords = builder._extract_keywords(test_input)
        print(f"抽出キーワード: {keywords}")
        
        # ステップ2: クエリ検出
        print("\n【ステップ2: クエリ検出】")
        queries = builder.detect_video_queries(test_input)
        print(f"検出クエリ数: {len(queries)}")
        for i, query in enumerate(queries):
            print(f"  {i+1}. {query}")
        
        # ステップ3: 具体性チェック（キーワードごと）
        print("\n【ステップ3: 具体性チェック】")
        for keyword in keywords:
            is_specific = builder._is_specific_query(keyword)
            print(f"  '{keyword}' → {'具体的' if is_specific else '一般的'}")
        
        # ステップ4: 実際の検索テスト
        print("\n【ステップ4: 検索テスト】")
        search_results = builder.knowledge_manager.search_videos("アドベンチャー")
        print(f"'アドベンチャー'検索結果: {len(search_results)}件")
        for result in search_results[:3]:
            title = result['data']['metadata'].get('title', '不明')
            print(f"  - {title[:60]}... (スコア: {result['score']})")
        
        # ステップ5: 代替入力パターンテスト
        print("\n【ステップ5: 代替入力パターンテスト】")
        alternative_inputs = [
            "アドベンチャーは",
            "アドベンチャーって曲",
            "アドベンチャーの動画",
            "YOASOBIのアドベンチャー"
        ]
        
        for alt_input in alternative_inputs:
            alt_queries = builder.detect_video_queries(alt_input)
            print(f"  '{alt_input}' → {len(alt_queries)}件のクエリ")
        
    except Exception as e:
        print(f"❌ デバッグ失敗: {e}")
        import traceback
        traceback.print_exc()

def debug_chat_integration():
    """チャット統合でのコンテキスト生成デバッグ"""
    print("\n=== チャット統合デバッグ ===")
    
    try:
        from core.conversation_context_builder import ConversationContextBuilder
        
        builder = ConversationContextBuilder()
        
        test_input = "じゃあ アドベンチャーは"
        print(f"🔍 チャット統合テスト: '{test_input}'")
        
        # process_user_inputの完全な流れを追跡
        context_result = builder.process_user_input(test_input)
        
        if context_result:
            print("✅ コンテキスト生成成功")
            print(f"生成コンテキスト:\n{context_result}")
        else:
            print("❌ コンテキスト生成失敗")
            print("→ この場合、OpenAI GPTが一般知識で回答してしまう")
        
    except Exception as e:
        print(f"❌ チャット統合デバッグ失敗: {e}")
        import traceback
        traceback.print_exc()

def main():
    """メインデバッグ実行"""
    print("🔧 クエリ検出システム詳細デバッグ開始\n")
    
    debug_query_detection()
    debug_chat_integration()
    
    print("\n" + "="*60)
    print("📝 デバッグ結果分析")
    print("="*60)
    print("上記の結果から、以下を確認してください：")
    print("1. キーワード抽出で「アドベンチャー」が抽出されているか")
    print("2. クエリ検出パターンが「じゃあ アドベンチャーは」をキャッチしているか")
    print("3. 具体性チェックで「アドベンチャー」が具体的と判定されているか")
    print("4. 直接検索では「アドベンチャー」が見つかるか")

if __name__ == "__main__":
    main()