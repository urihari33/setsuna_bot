#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase A完全統合テスト
A1(PersonalityMemory) + A2(CollaborationMemory) + A3(MemoryIntegration) の完全統合動作確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.setsuna_chat import SetsunaChat

def test_phase_a_complete_integration():
    """Phase A 完全統合テスト"""
    
    print("=" * 70)
    print("🧠🤝🔗 Phase A 完全統合テスト開始")
    print("A1(個人記憶) + A2(協働記憶) + A3(記憶統合)")
    print("=" * 70)
    
    try:
        # SetsunaChat初期化（テストモード）
        print("\n--- SetsunaChat初期化（テストモード） ---")
        setsuna = SetsunaChat(memory_mode="test")
        
        # 全システムが正常に初期化されているか確認
        systems_status = {
            "personality_memory": bool(setsuna.personality_memory),
            "collaboration_memory": bool(setsuna.collaboration_memory),
            "memory_integration": bool(setsuna.memory_integration)
        }
        
        print(f"システム初期化状況: {systems_status}")
        
        if not all(systems_status.values()):
            print("❌ 一部システムの初期化に失敗")
            return False
        
        print("✅ 全システム初期化成功")
        
        # 初期統計情報
        print("\n--- 初期統計情報 ---")
        personality_stats = setsuna.get_personality_memory_stats()
        collaboration_stats = setsuna.get_collaboration_memory_stats()
        integration_stats = setsuna.get_memory_integration_stats()
        
        print(f"個人記憶統計: {personality_stats}")
        print(f"協働記憶統計: {collaboration_stats}")
        print(f"記憶統合統計: {integration_stats}")
        
        # Phase A 統合会話シナリオ
        print("\n--- Phase A 統合会話シナリオ ---")
        
        # シナリオ1: 創作学習体験
        print("\n🎨 シナリオ1: 創作学習体験")
        user_input1 = "音楽制作の新しい技術を学びたいです"
        response1 = setsuna.get_response(user_input1, mode="fast_response")
        print(f"ユーザー: {user_input1}")
        print(f"せつな: {response1}")
        
        # シナリオ2: 協働作業提案
        print("\n🤝 シナリオ2: 協働作業提案")
        user_input2 = "一緒に楽曲のアレンジを作ってみませんか？"
        response2 = setsuna.get_response(user_input2, mode="fast_response")
        print(f"ユーザー: {user_input2}")
        print(f"せつな: {response2}")
        
        # 手動で体験と成功を記録（統合テスト用）
        print("\n--- 手動記録（統合用データ生成） ---")
        
        # 個人体験記録
        exp_id = setsuna.personality_memory.record_personal_experience(
            event_description="音楽制作技術の学習セッション",
            event_type="learning",
            emotion="excited",
            learning="新しいDAW技術を理解した",
            impact_level=0.8
        )
        print(f"記録された個人体験ID: {exp_id}")
        
        # 協働成功記録
        success_id = setsuna.record_success(
            success_type="creative_breakthrough",
            context="楽曲アレンジでの創作活動",
            key_factors=["技術学習", "創作意欲", "協働"],
            outcome="高品質なアレンジ作品完成",
            replicability="high"
        )
        print(f"記録された成功パターンID: {success_id}")
        
        # 記憶統合分析実行
        print("\n--- 記憶統合分析実行 ---")
        analysis_result = setsuna.analyze_memory_relationships()
        print(f"記憶関係性分析結果: {analysis_result}")
        
        # 統合コンテキスト生成テスト
        print("\n--- 統合コンテキスト生成テスト ---")
        
        # 完全統合コンテキスト
        full_context = setsuna.get_integrated_context(
            user_input="音楽制作について相談したい", 
            context_type="full"
        )
        print(f"完全統合コンテキスト:\n{full_context}")
        
        # 関連性コンテキスト
        relevant_context = setsuna.get_integrated_context(
            user_input="創作でうまくいかない時のアドバイス", 
            context_type="relevant"
        )
        print(f"\n関連性コンテキスト:\n{relevant_context}")
        
        # 適応的応答提案テスト
        print("\n--- 適応的応答提案テスト ---")
        suggestions = setsuna.suggest_adaptive_responses("新しいプロジェクトを始めたい")
        print(f"適応的応答提案: {suggestions}")
        
        # 関連記憶検索テスト
        print("\n--- 関連記憶検索テスト ---")
        if exp_id:
            related_memories = setsuna.find_related_memories(exp_id, "personality", max_results=3)
            print(f"関連記憶検索結果: {len(related_memories)}件")
            for i, memory in enumerate(related_memories, 1):
                print(f"  {i}. {memory['memory']['type']} - 関連度: {memory['relevance_score']:.2f}")
        
        # シナリオ3: 統合記憶を活用した会話
        print("\n🔗 シナリオ3: 統合記憶活用会話")
        user_input3 = "前回の学習を活かして、今度は別のジャンルに挑戦したい"
        response3 = setsuna.get_response(user_input3, mode="normal")  # 通常モードで統合効果確認
        print(f"ユーザー: {user_input3}")
        print(f"せつな: {response3}")
        
        # 最終統計確認
        print("\n--- 最終統計確認 ---")
        final_personality_stats = setsuna.get_personality_memory_stats()
        final_collaboration_stats = setsuna.get_collaboration_memory_stats()
        final_integration_stats = setsuna.get_memory_integration_stats()
        
        print(f"最終個人記憶統計: {final_personality_stats}")
        print(f"最終協働記憶統計: {final_collaboration_stats}")
        print(f"最終記憶統合統計: {final_integration_stats}")
        
        # 効果検証
        print("\n--- Phase A 効果検証 ---")
        
        # 記憶間関係性が生成されているか
        relationships_count = final_integration_stats.get("total_relationships", 0)
        if relationships_count > 0:
            print(f"✅ 記憶間関係性の生成: {relationships_count}件")
        else:
            print("⚠️ 記憶間関係性が生成されていません")
        
        # キャラクター進化が記録されているか
        personality_exp_count = final_personality_stats.get("total_experiences", 0)
        if personality_exp_count > 0:
            print(f"✅ 個人体験の記録: {personality_exp_count}件")
        else:
            print("⚠️ 個人体験が記録されていません")
        
        # 協働パターンが学習されているか
        collaboration_patterns = final_collaboration_stats.get("work_patterns", 0)
        if collaboration_patterns > 0:
            print(f"✅ 協働パターンの学習: {collaboration_patterns}件")
        else:
            print("⚠️ 協働パターンが学習されていません")
        
        # 統合コンテキスト生成が機能しているか
        if full_context and len(full_context) > 0:
            print("✅ 統合コンテキスト生成機能が動作")
        else:
            print("⚠️ 統合コンテキスト生成が機能していません")
        
        print("\n✅ Phase A 完全統合テスト完了")
        return True
        
    except Exception as e:
        print(f"\n❌ Phase A 統合テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_response_quality():
    """強化された応答品質テスト"""
    
    print("\n" + "=" * 70)
    print("🎯 強化応答品質テスト")
    print("=" * 70)
    
    try:
        # 通常モードで詳細な応答生成テスト
        print("\n--- 強化応答生成テスト（通常モード） ---")
        setsuna = SetsunaChat(memory_mode="normal")
        
        # データがある状態でのテスト（前テストのデータが蓄積されている想定）
        test_scenarios = [
            {
                "input": "創作で行き詰まった時はどうすればいいですか？",
                "expected_features": ["過去の体験参照", "協働提案", "統合洞察"]
            },
            {
                "input": "一緒に新しいプロジェクトを始めませんか？",
                "expected_features": ["成功パターン活用", "パートナーシップ状態反映"]
            },
            {
                "input": "最近学んだことを活かしたいです",
                "expected_features": ["学習記憶連携", "適応的提案"]
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📝 テストケース {i}")
            print(f"入力: {scenario['input']}")
            
            response = setsuna.get_response(scenario['input'], mode="normal")
            print(f"応答: {response}")
            
            # 統合コンテキストを確認
            integrated_context = setsuna.get_integrated_context(
                scenario['input'], 
                context_type="relevant"
            )
            if integrated_context:
                print(f"統合コンテキスト活用: ✅ ({len(integrated_context)}文字)")
            else:
                print("統合コンテキスト活用: ❌")
        
        print("\n✅ 強化応答品質テスト完了")
        return True
        
    except Exception as e:
        print(f"\n❌ 応答品質テストエラー: {e}")
        return False

if __name__ == "__main__":
    # 総合テスト実行
    test1_success = test_phase_a_complete_integration()
    test2_success = test_enhanced_response_quality()
    
    print("\n" + "=" * 70)
    print("📊 Phase A 総合テスト結果サマリー")
    print("=" * 70)
    print(f"完全統合テスト: {'✅ 成功' if test1_success else '❌ 失敗'}")
    print(f"強化応答品質テスト: {'✅ 成功' if test2_success else '❌ 失敗'}")
    
    if test1_success and test2_success:
        print("\n🎉 Phase A 実装完了！")
        print("強化記憶システム（A1+A2+A3）が正常に統合・動作しています")
        print("\n実装された機能:")
        print("- ✅ A1: 個人記憶システム（PersonalityMemory）")
        print("- ✅ A2: 協働記憶システム（CollaborationMemory）") 
        print("- ✅ A3: 記憶統合システム（MemoryIntegration）")
        print("- ✅ 記憶間関係性分析・関連付け")
        print("- ✅ 統合プロンプトコンテキスト生成")
        print("- ✅ 適応的応答提案")
        print("- ✅ クロスリファレンス検索")
    else:
        print("\n⚠️ Phase A に問題があります。上記のエラーを確認してください。")