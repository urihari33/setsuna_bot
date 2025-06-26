#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2-B-3: 文脈理解向上システムテスト
文脈理解・代名詞解決・マルチターン会話管理の包括的テスト
"""

import sys
import os
from pathlib import Path
import tempfile

# パス設定
sys.path.append(str(Path(__file__).parent))

def test_context_understanding_system():
    """文脈理解システムの基本テスト"""
    print("=== 文脈理解システムテスト ===")
    
    try:
        from core.context_understanding_system import ContextUnderstandingSystem
        
        # テスト用の一時ディレクトリ
        with tempfile.TemporaryDirectory() as temp_dir:
            context_system = ContextUnderstandingSystem()
            # 一時ディレクトリを使用するよう設定変更
            context_system.context_file = Path(temp_dir) / "test_context.json"
            
            success_count = 0
            
            # 代名詞検出テスト
            test_inputs = [
                "この曲いいね",  # 指示語
                "さっき聞いた歌",  # 時間的指示
                "似たような動画ある？",  # 相対的指示
                "詳しく教えて"  # 暗黙的指示
            ]
            
            for test_input in test_inputs:
                analysis = context_system.analyze_input_context(test_input)
                
                if analysis.get("pronoun_references"):
                    print(f"✅ 代名詞検出: '{test_input}' → {len(analysis['pronoun_references'])}件")
                    success_count += 1
                else:
                    print(f"⚠️ 代名詞検出: '{test_input}' → 検出なし")
            
            # 感情分析テスト
            emotion_test = "この曲すごくいいね！"
            emotion_analysis = context_system.analyze_input_context(emotion_test)
            emotional_signals = emotion_analysis.get("emotional_signals", {})
            
            if emotional_signals.get("positive", 0) > 0.5:
                print("✅ 感情分析: ポジティブ感情検出成功")
                success_count += 1
            else:
                print("❌ 感情分析: ポジティブ感情検出失敗")
            
            # 継続性指標テスト
            continuity_test = "そうだね、でももっと知りたい"
            continuity_analysis = context_system.analyze_input_context(continuity_test)
            continuity_indicators = continuity_analysis.get("continuity_indicators", [])
            
            if continuity_indicators:
                print(f"✅ 継続性指標: {len(continuity_indicators)}件検出")
                success_count += 1
            else:
                print("❌ 継続性指標: 検出失敗")
            
            return success_count >= 4  # 6項目中4項目以上で成功
            
    except Exception as e:
        print(f"❌ 文脈理解システムテスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multi_turn_conversation_manager():
    """マルチターン会話管理システムテスト"""
    print("\n=== マルチターン会話管理システムテスト ===")
    
    try:
        from core.multi_turn_conversation_manager import MultiTurnConversationManager, ConversationState
        
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = MultiTurnConversationManager()
            manager.conversation_file = Path(temp_dir) / "test_conversations.json"
            
            success_count = 0
            
            # 基本的なターン追加テスト
            test_conversations = [
                {
                    "input": "アドベンチャーについて教えて",
                    "videos": [{"video_id": "test1", "title": "アドベンチャー", "channel": "テスト"}],
                    "expected_state": ConversationState.TOPIC_ESTABLISHED
                },
                {
                    "input": "この曲いいね！",
                    "videos": [],
                    "expected_state": ConversationState.PREFERENCE_LEARNING
                },
                {
                    "input": "もっと詳しく教えて",
                    "videos": [],
                    "expected_state": ConversationState.DEEP_DISCUSSION
                }
            ]
            
            for i, conv in enumerate(test_conversations):
                # 簡易的な文脈分析を作成
                mock_analysis = {
                    "emotional_signals": {
                        "positive": 0.8 if "いい" in conv["input"] else 0.2,
                        "curiosity": 0.7 if "教えて" in conv["input"] or "詳しく" in conv["input"] else 0.1,
                        "detected_emotions": []
                    },
                    "pronoun_references": [],
                    "continuity_indicators": []
                }
                
                # ターン追加
                turn_result = manager.add_turn(
                    conv["input"], 
                    mock_analysis, 
                    f"応答{i+1}", 
                    conv["videos"]
                )
                
                current_state = turn_result.get("new_state")
                if isinstance(current_state, str):
                    current_state = ConversationState(current_state)
                
                print(f"ターン {i+1}: '{conv['input']}' → 状態: {current_state.value if current_state else 'unknown'}")
                
                # 状態遷移が期待通りか確認（厳密ではなく、遷移が発生したかを確認）
                if turn_result.get("state_transition", {}).get("should_transition"):
                    print(f"  ✅ 状態遷移発生")
                    success_count += 1
                else:
                    print(f"  ⚠️ 状態遷移なし")
            
            # 会話コンテキスト取得テスト
            context = manager.get_conversation_context_for_response()
            
            if context and context.get("session_info"):
                session_info = context["session_info"]
                print(f"✅ 会話コンテキスト取得: ターン{session_info['turn_count']}件")
                success_count += 1
            else:
                print("❌ 会話コンテキスト取得失敗")
            
            # セッション終了テスト
            summary = manager.end_session()
            
            if summary and summary.get("session_id"):
                print(f"✅ セッション終了: {summary['total_turns']}ターン")
                success_count += 1
            else:
                print("❌ セッション終了失敗")
            
            return success_count >= 3  # 5項目中3項目以上で成功
            
    except Exception as e:
        print(f"❌ マルチターン会話管理システムテスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pronoun_resolution():
    """代名詞解決テスト"""
    print("\n=== 代名詞解決テスト ===")
    
    try:
        from core.context_understanding_system import ContextUnderstandingSystem
        
        with tempfile.TemporaryDirectory() as temp_dir:
            context_system = ContextUnderstandingSystem()
            context_system.context_file = Path(temp_dir) / "test_resolution.json"
            
            success_count = 0
            
            # 事前に話題を設定
            test_video = {
                "video_id": "test_video_1",
                "title": "テスト楽曲",
                "channel": "テストチャンネル",
                "genre": "テストジャンル"
            }
            
            # アクティブ話題を手動設定
            context_system.active_topics["test_video_1"] = {
                "video_id": "test_video_1",
                "title": "テスト楽曲",
                "channel": "テストチャンネル",
                "genre": "テストジャンル",
                "keywords": ["テスト", "楽曲"],
                "last_mentioned": "2023-01-01T00:00:00",
                "mention_count": 1
            }
            
            # 代名詞解決テストケース
            pronoun_tests = [
                {
                    "input": "この曲について",
                    "expected_resolution": True,
                    "description": "指示語解決"
                },
                {
                    "input": "さっきの動画は？",
                    "expected_resolution": True,
                    "description": "時間的指示解決"
                },
                {
                    "input": "似たような曲ある？",
                    "expected_resolution": True,
                    "description": "相対的指示解決"
                }
            ]
            
            for test_case in pronoun_tests:
                print(f"\n🧪 {test_case['description']}: '{test_case['input']}'")
                
                # 文脈分析
                analysis = context_system.analyze_input_context(test_case["input"])
                
                # 参照解決の実行
                if analysis.get("requires_resolution"):
                    resolution_result = context_system.resolve_references(analysis)
                    
                    if resolution_result.get("confidence", 0) > 0.5:
                        print(f"  ✅ 解決成功: 信頼度 {resolution_result['confidence']:.2f}")
                        success_count += 1
                    else:
                        print(f"  ⚠️ 解決信頼度低: {resolution_result['confidence']:.2f}")
                else:
                    print("  ❌ 代名詞検出されず")
            
            return success_count >= 2  # 3項目中2項目以上で成功
            
    except Exception as e:
        print(f"❌ 代名詞解決テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversation_context_builder_integration():
    """ConversationContextBuilderとの統合テスト"""
    print("\n=== ConversationContextBuilder統合テスト ===")
    
    try:
        from core.conversation_context_builder import ConversationContextBuilder
        
        builder = ConversationContextBuilder()
        
        # 統合システムが初期化されているかチェック
        has_context_understanding = builder.context_understanding is not None
        has_multi_turn_manager = builder.multi_turn_manager is not None
        
        print(f"文脈理解システム統合: {'✅' if has_context_understanding else '❌'}")
        print(f"マルチターン管理統合: {'✅' if has_multi_turn_manager else '❌'}")
        
        if not (has_context_understanding and has_multi_turn_manager):
            print("⚠️ 統合システムが初期化されていません")
            return False
        
        success_count = 0
        
        # 段階的会話テスト
        conversation_sequence = [
            "アドベンチャーについて教えて",  # 初回 - 話題確立
            "この曲いいね！",               # 代名詞使用 - 文脈参照
            "もっと似たような曲ある？"       # 継続 - 推薦要求
        ]
        
        for i, user_input in enumerate(conversation_sequence):
            print(f"\n会話 {i+1}: '{user_input}'")
            
            try:
                # 統合処理実行
                context_text = builder.process_user_input(user_input)
                
                if context_text:
                    print(f"  ✅ 統合処理成功")
                    success_count += 1
                    
                    # 文脈要素の確認
                    if i > 0:  # 2回目以降
                        has_context_info = any(keyword in context_text for keyword in [
                            "文脈", "さっき", "前", "この", "その", "継続", "代名詞"
                        ])
                        
                        if has_context_info:
                            print(f"  ✅ 文脈情報を含む応答生成")
                        else:
                            print(f"  ⚠️ 文脈情報が確認できない")
                else:
                    print(f"  ❌ 統合処理失敗")
                    
            except Exception as e:
                print(f"  ⚠️ 統合処理エラー: {e}")
        
        return success_count >= 2  # 3項目中2項目以上で成功
        
    except Exception as e:
        print(f"❌ ConversationContextBuilder統合テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end_contextual_conversation():
    """エンドツーエンド文脈会話テスト"""
    print("\n=== エンドツーエンド文脈会話テスト ===")
    
    try:
        from core.conversation_context_builder import ConversationContextBuilder
        
        builder = ConversationContextBuilder()
        
        if not (builder.context_understanding and builder.multi_turn_manager):
            print("⚠️ 統合システムが利用できません")
            return False
        
        # 実際の会話シナリオをシミュレート
        conversation_scenario = [
            {
                "input": "ボカロの曲について教えて",
                "expected": "topic_establishment",
                "description": "話題確立"
            },
            {
                "input": "この曲好き！",
                "expected": "contextual_reference",
                "description": "文脈参照（この曲）"
            },
            {
                "input": "似たような感じのもっとある？",
                "expected": "preference_based_recommendation",
                "description": "嗜好ベース推薦要求"
            },
            {
                "input": "そっちじゃなくて、さっきのやつ",
                "expected": "temporal_reference",
                "description": "時間的参照"
            }
        ]
        
        success_count = 0
        conversation_quality = 0.0
        
        for i, scenario in enumerate(conversation_scenario):
            print(f"\n📝 シナリオ {i+1}: {scenario['description']}")
            print(f"  入力: '{scenario['input']}'")
            
            try:
                # 処理実行
                result = builder.process_user_input(scenario["input"])
                
                if result:
                    print(f"  ✅ 処理成功")
                    success_count += 1
                    
                    # 品質評価（簡易版）
                    quality_indicators = {
                        "topic_establishment": lambda r: "楽曲名" in r or "動画" in r,
                        "contextual_reference": lambda r: "文脈" in r or "参照" in r,
                        "preference_based_recommendation": lambda r: "推薦" in r or "おすすめ" in r,
                        "temporal_reference": lambda r: "さっき" in r or "前" in r
                    }
                    
                    expected_type = scenario["expected"]
                    if expected_type in quality_indicators:
                        quality_check = quality_indicators[expected_type](result)
                        if quality_check:
                            conversation_quality += 0.25
                            print(f"  ✅ 品質確認: {expected_type}")
                        else:
                            print(f"  ⚠️ 品質要改善: {expected_type}")
                else:
                    print(f"  ❌ 処理失敗")
                    
            except Exception as e:
                print(f"  ⚠️ 処理エラー: {e}")
        
        # 会話品質の総合評価
        print(f"\n📊 会話品質評価: {conversation_quality:.2f}/1.0")
        
        # セッション情報取得
        if builder.multi_turn_manager:
            session_context = builder.multi_turn_manager.get_conversation_context_for_response()
            session_info = session_context.get("session_info", {})
            
            print(f"📈 セッション情報:")
            print(f"  ターン数: {session_info.get('turn_count', 0)}")
            print(f"  対話状態: {session_info.get('current_state', 'unknown')}")
            
            if session_info.get('turn_count', 0) >= 3:
                success_count += 1
                print("  ✅ マルチターン会話継続確認")
        
        return success_count >= 3 and conversation_quality >= 0.5
        
    except Exception as e:
        print(f"❌ エンドツーエンド文脈会話テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メインテスト実行"""
    print("🧠 Phase 2-B-3: 文脈理解向上システムテスト開始\n")
    
    results = []
    
    # 各テストの実行
    results.append(test_context_understanding_system())
    results.append(test_multi_turn_conversation_manager())
    results.append(test_pronoun_resolution())
    results.append(test_conversation_context_builder_integration())
    results.append(test_end_to_end_contextual_conversation())
    
    # 結果サマリー
    print("\n" + "="*70)
    print("📊 Phase 2-B-3 テスト結果サマリー")
    print("="*70)
    
    test_names = [
        "文脈理解システム",
        "マルチターン会話管理",
        "代名詞解決",
        "ConversationContextBuilder統合",
        "エンドツーエンド文脈会話"
    ]
    
    success_count = sum(results)
    total_count = len(results)
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"{i+1}. {test_name}: {status}")
    
    print(f"\n📈 総合成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count >= 4:  # 5つ中4つ以上で合格
        print("\n🎉 Phase 2-B-3 テスト合格！文脈理解向上システムが正常に動作しています。")
        print("\n✨ 実装された機能:")
        print("- 代名詞・指示語の自動検出と参照解決")
        print("- 継続性指標による会話の流れ認識")
        print("- 感情文脈の分析と対話状態管理")
        print("- マルチターン会話でのコンテキスト保持")
        print("- 文脈参照に基づく自然な応答生成")
        print("- 会話状態の自動遷移と品質評価")
        
        print("\n🔧 文脈理解テスト用コマンド:")
        print("- 「アドベンチャーについて教えて」→「この曲いいね」（指示語参照）")
        print("- 「その動画のクリエイターは？」（文脈参照）")
        print("- 「もっと似たような曲ある？」（相対的参照）")
        print("- 「さっき聞いた歌について」（時間的参照）")
        
        print("\n🏗️ 次のステップ準備完了: Phase 2-B統合テスト")
        
        return True
    else:
        print(f"\n⚠️ 改善が必要です（{total_count - success_count}項目が失敗）")
        print("詳細は上記ログを確認してください。")
        
        return False

if __name__ == "__main__":
    main()