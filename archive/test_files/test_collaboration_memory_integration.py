#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CollaborationMemory統合テスト
SetsunaChat への統合後の動作確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.setsuna_chat import SetsunaChat
from enhanced_memory.collaboration_memory import CollaborationMemory

def test_collaboration_memory_integration():
    """CollaborationMemory統合テスト"""
    
    print("=" * 60)
    print("🤝 CollaborationMemory統合テスト開始")
    print("=" * 60)
    
    try:
        # SetsunaChat初期化（テストモード）
        print("\n--- SetsunaChat初期化（テストモード） ---")
        setsuna = SetsunaChat(memory_mode="test")
        
        # 協働記憶システムが正常に初期化されているか確認
        if setsuna.collaboration_memory:
            print("✅ CollaborationMemoryシステム初期化成功")
            print(f"記憶モード: {setsuna.collaboration_memory.memory_mode}")
        else:
            print("❌ CollaborationMemoryシステム初期化失敗")
            return False
        
        # 初期統計情報
        print("\n--- 初期統計情報 ---")
        stats = setsuna.get_collaboration_memory_stats()
        print(f"初期統計: {stats}")
        
        # テスト会話 1: 創作活動
        print("\n--- テスト会話 1: 創作活動 ---")
        user_input1 = "一緒に音楽を作ってみませんか？"
        response1 = setsuna.get_response(user_input1, mode="fast_response")
        print(f"ユーザー: {user_input1}")
        print(f"せつな: {response1}")
        
        # テスト会話 2: ディスカッション
        print("\n--- テスト会話 2: ディスカッション ---")
        user_input2 = "このプロジェクトについてどう思いますか？"
        response2 = setsuna.get_response(user_input2, mode="fast_response")
        print(f"ユーザー: {user_input2}")
        print(f"せつな: {response2}")
        
        # テスト会話 3: レビュー活動
        print("\n--- テスト会話 3: レビュー活動 ---")
        user_input3 = "作品の改善点を教えてください"
        response3 = setsuna.get_response(user_input3, mode="fast_response")
        print(f"ユーザー: {user_input3}")
        print(f"せつな: {response3}")
        
        # 手動で作業セッション記録
        print("\n--- 手動作業セッション記録テスト ---")
        work_id = setsuna.record_work_session(
            activity_type="creation",
            duration_minutes=60,
            user_satisfaction="high",
            outcome_quality="excellent",
            notes="統合テストでの音楽制作セッション"
        )
        print(f"記録された作業セッションID: {work_id}")
        
        # 手動で成功パターン記録
        print("\n--- 手動成功パターン記録テスト ---")
        success_id = setsuna.record_success(
            success_type="creative_breakthrough",
            context="統合テスト中の創作活動",
            key_factors=["良い環境", "集中", "協力"],
            outcome="効果的な協働システム構築",
            replicability="high"
        )
        print(f"記録された成功パターンID: {success_id}")
        
        # 会話後の統計情報
        print("\n--- 会話後の統計情報 ---")
        final_stats = setsuna.get_collaboration_memory_stats()
        print(f"最終統計: {final_stats}")
        
        # 協働洞察確認
        print("\n--- 協働洞察 ---")
        insights = setsuna.get_collaboration_insights()
        print(f"洞察:")
        for key, value in insights.items():
            print(f"  {key}: {value}")
        
        # 協働記憶コンテキスト確認
        print("\n--- 協働記憶コンテキスト ---")
        if setsuna.collaboration_memory:
            context = setsuna.collaboration_memory.get_collaboration_context_for_prompt()
            print(f"コンテキスト:\n{context}")
        
        # パートナーシップ進化状態確認
        print("\n--- パートナーシップ進化状態 ---")
        if setsuna.collaboration_memory:
            evolution = setsuna.collaboration_memory.collaboration_data["partnership_evolution"]
            print(f"信頼レベル: {evolution['trust_level']:.2f}")
            print(f"同期効率: {evolution['sync_efficiency']:.2f}")
            print(f"創作適合性: {evolution['creative_compatibility']:.2f}")
            print(f"コミュニケーション明確性: {evolution['communication_clarity']:.2f}")
        
        print("\n✅ CollaborationMemory統合テスト完了")
        return True
        
    except Exception as e:
        print(f"\n❌ 統合テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dual_memory_integration():
    """PersonalityMemory + CollaborationMemory 連携テスト"""
    
    print("\n" + "=" * 60)
    print("🧠🤝 デュアル記憶システム連携テスト")
    print("=" * 60)
    
    try:
        # SetsunaChat初期化（通常モード）
        print("\n--- SetsunaChat初期化（通常モード） ---")
        setsuna = SetsunaChat(memory_mode="normal")
        
        # 両方のシステムが初期化されているか確認
        if setsuna.personality_memory and setsuna.collaboration_memory:
            print("✅ 両方の記憶システム初期化成功")
        else:
            print(f"❌ 記憶システム初期化失敗: personality={bool(setsuna.personality_memory)}, collaboration={bool(setsuna.collaboration_memory)}")
            return False
        
        # 統合会話テスト
        print("\n--- 統合会話テスト ---")
        user_input = "今日はとても創作がはかどりました！"
        response = setsuna.get_response(user_input, mode="fast_response")
        print(f"ユーザー: {user_input}")
        print(f"せつな: {response}")
        
        # 両システムの統計確認
        print("\n--- 両システム統計 ---")
        personality_stats = setsuna.get_personality_memory_stats()
        collaboration_stats = setsuna.get_collaboration_memory_stats()
        
        print(f"個人記憶統計: {personality_stats}")
        print(f"協働記憶統計: {collaboration_stats}")
        
        # データ保存テスト
        print("\n--- 統合データ保存テスト ---")
        setsuna.save_all_data()
        
        print("\n✅ デュアル記憶システム連携テスト完了")
        return True
        
    except Exception as e:
        print(f"\n❌ 連携テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # テスト実行
    test1_success = test_collaboration_memory_integration()
    test2_success = test_dual_memory_integration()
    
    print("\n" + "=" * 60)
    print("📊 協働記憶統合テスト結果サマリー")
    print("=" * 60)
    print(f"CollaborationMemory統合テスト: {'✅ 成功' if test1_success else '❌ 失敗'}")
    print(f"デュアル記憶システム連携テスト: {'✅ 成功' if test2_success else '❌ 失敗'}")
    
    if test1_success and test2_success:
        print("\n🎉 CollaborationMemory統合完了！")
        print("Phase A-2完了：協働記憶システムが正常に統合されました")
    else:
        print("\n⚠️ 統合に問題があります。上記のエラーを確認してください。")