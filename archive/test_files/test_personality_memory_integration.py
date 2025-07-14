#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PersonalityMemory統合テスト
SetsunaChat への統合後の動作確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.setsuna_chat import SetsunaChat
from enhanced_memory.personality_memory import PersonalityMemory

def test_personality_memory_integration():
    """PersonalityMemory統合テスト"""
    
    print("=" * 60)
    print("🧠 PersonalityMemory統合テスト開始")
    print("=" * 60)
    
    try:
        # SetsunaChat初期化（テストモード）
        print("\n--- SetsunaChat初期化（テストモード） ---")
        setsuna = SetsunaChat(memory_mode="test")
        
        # 個人記憶システムが正常に初期化されているか確認
        if setsuna.personality_memory:
            print("✅ PersonalityMemoryシステム初期化成功")
            print(f"記憶モード: {setsuna.personality_memory.memory_mode}")
        else:
            print("❌ PersonalityMemoryシステム初期化失敗")
            return False
        
        # 初期統計情報
        print("\n--- 初期統計情報 ---")
        stats = setsuna.get_personality_memory_stats()
        print(f"初期統計: {stats}")
        
        # テスト会話: 学習体験
        print("\n--- テスト会話 1: 学習体験 ---")
        user_input1 = "Pythonプログラミングを教えてください"
        response1 = setsuna.get_response(user_input1, mode="fast_response")
        print(f"ユーザー: {user_input1}")
        print(f"せつな: {response1}")
        
        # テスト会話: 創作体験
        print("\n--- テスト会話 2: 創作体験 ---")
        user_input2 = "一緒に歌詞を作ってみましょう"
        response2 = setsuna.get_response(user_input2, mode="fast_response")
        print(f"ユーザー: {user_input2}")
        print(f"せつな: {response2}")
        
        # テスト会話: 挑戦体験
        print("\n--- テスト会話 3: 挑戦体験 ---")
        user_input3 = "新しいプロジェクトに挑戦したいです"
        response3 = setsuna.get_response(user_input3, mode="fast_response")
        print(f"ユーザー: {user_input3}")
        print(f"せつな: {response3}")
        
        # テスト会話: 会話体験
        print("\n--- テスト会話 4: 会話体験 ---")
        user_input4 = "今日の気持ちについて話しましょう"
        response4 = setsuna.get_response(user_input4, mode="fast_response")
        print(f"ユーザー: {user_input4}")
        print(f"せつな: {response4}")
        
        # 会話後の統計情報
        print("\n--- 会話後の統計情報 ---")
        final_stats = setsuna.get_personality_memory_stats()
        print(f"最終統計: {final_stats}")
        
        # 個人記憶コンテキスト確認
        print("\n--- 個人記憶コンテキスト ---")
        if setsuna.personality_memory:
            context = setsuna.personality_memory.get_personality_context_for_prompt()
            print(f"コンテキスト:\n{context}")
        
        # キャラクター進化状態確認
        print("\n--- キャラクター進化状態 ---")
        if setsuna.personality_memory:
            evolution = setsuna.personality_memory.personality_data["character_evolution"]
            print(f"自信レベル: {evolution['confidence_level']:.2f}")
            print(f"技術知識: {evolution['technical_knowledge']:.2f}")
            print(f"創作経験: {evolution['creative_experience']:.2f}")
            print(f"社交性: {evolution['social_comfort']:.2f}")
        
        # 最近の体験確認
        print("\n--- 最近の体験記録 ---")
        if setsuna.personality_memory:
            recent_experiences = setsuna.personality_memory.get_recent_experiences(days=1, limit=5)
            for i, exp in enumerate(recent_experiences, 1):
                print(f"{i}. {exp['description'][:50]}... (感情: {exp['emotion']}, 影響度: {exp['impact_level']})")
        
        # テストモードでは保存されないことを確認
        print("\n--- テストモード確認 ---")
        setsuna.save_personality_memory()
        print("テストモード: 個人記憶は永続保存されません")
        
        print("\n✅ PersonalityMemory統合テスト完了")
        return True
        
    except Exception as e:
        print(f"\n❌ 統合テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_normal_mode_integration():
    """通常モードでの統合テスト"""
    
    print("\n" + "=" * 60)
    print("🧠 通常モード統合テスト")
    print("=" * 60)
    
    try:
        # SetsunaChat初期化（通常モード）
        print("\n--- SetsunaChat初期化（通常モード） ---")
        setsuna = SetsunaChat(memory_mode="normal")
        
        # 個人記憶システムが正常に初期化されているか確認
        if setsuna.personality_memory:
            print("✅ PersonalityMemoryシステム初期化成功（通常モード）")
            print(f"記憶モード: {setsuna.personality_memory.memory_mode}")
        else:
            print("❌ PersonalityMemoryシステム初期化失敗")
            return False
        
        # 手動で体験記録テスト
        print("\n--- 手動体験記録テスト ---")
        exp_id = setsuna.personality_memory.record_personal_experience(
            event_description="統合テストでの動作確認",
            event_type="learning",
            emotion="curious",
            learning="システム統合の確認ができた",
            impact_level=0.7
        )
        print(f"記録された体験ID: {exp_id}")
        
        # 簡単な会話テスト
        print("\n--- 簡単な会話テスト ---")
        test_response = setsuna.get_response("テストです", mode="fast_response")
        print(f"応答: {test_response}")
        
        # データ保存テスト
        print("\n--- データ保存テスト ---")
        setsuna.save_personality_memory()
        
        print("\n✅ 通常モード統合テスト完了")
        return True
        
    except Exception as e:
        print(f"\n❌ 通常モード統合テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # テスト実行
    test1_success = test_personality_memory_integration()
    test2_success = test_normal_mode_integration()
    
    print("\n" + "=" * 60)
    print("📊 統合テスト結果サマリー")
    print("=" * 60)
    print(f"テストモード統合テスト: {'✅ 成功' if test1_success else '❌ 失敗'}")
    print(f"通常モード統合テスト: {'✅ 成功' if test2_success else '❌ 失敗'}")
    
    if test1_success and test2_success:
        print("\n🎉 PersonalityMemory統合完了！")
    else:
        print("\n⚠️ 統合に問題があります。上記のエラーを確認してください。")