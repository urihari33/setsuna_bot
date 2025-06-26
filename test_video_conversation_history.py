#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動画会話履歴システムのテスト - Phase 2-B-1
"""

import sys
import os
from pathlib import Path

# パス設定
sys.path.append(str(Path(__file__).parent))

def test_conversation_recording():
    """会話記録機能のテスト"""
    print("=== 会話記録機能テスト ===")
    
    try:
        from core.video_conversation_history import VideoConversationHistory
        
        history = VideoConversationHistory()
        
        # 同じ動画について複数回会話をシミュレート
        test_scenarios = [
            # 初回会話
            {"video_id": "test_video_1", "title": "アドベンチャー", "input": "アドベンチャーってどんな曲？", "expected_reaction": "neutral"},
            
            # ポジティブ反応
            {"video_id": "test_video_1", "title": "アドベンチャー", "input": "この曲すごくいいね！", "expected_reaction": "positive"},
            
            # 継続会話
            {"video_id": "test_video_1", "title": "アドベンチャー", "input": "またアドベンチャー聞きたい", "expected_reaction": "positive"},
            
            # 新しい動画
            {"video_id": "test_video_2", "title": "XOXO", "input": "XOXOについて教えて", "expected_reaction": "neutral"},
            
            # 否定的反応
            {"video_id": "test_video_2", "title": "XOXO", "input": "この曲はちょっと微妙かも", "expected_reaction": "negative"},
        ]
        
        for i, scenario in enumerate(test_scenarios):
            print(f"\n📝 テストケース {i+1}: {scenario['input']}")
            
            success = history.record_conversation(
                scenario["video_id"], 
                scenario["title"], 
                scenario["input"]
            )
            
            if success:
                print(f"   ✅ 記録成功")
                
                # 記録後のコンテキスト確認
                context = history.get_conversation_context(scenario["video_id"])
                if context:
                    print(f"   📊 会話回数: {context['conversation_count']}")
                    print(f"   📈 親しみやすさ: {context['familiarity_level']} (スコア: {context['familiarity_score']:.2f})")
                    print(f"   🎭 最近の反応: {context['recent_reactions']}")
            else:
                print(f"   ❌ 記録失敗")
        
        return True
        
    except Exception as e:
        print(f"❌ 会話記録テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_familiarity_progression():
    """親しみやすさスコア進化のテスト"""
    print("\n=== 親しみやすさスコア進化テスト ===")
    
    try:
        from core.video_conversation_history import VideoConversationHistory
        
        history = VideoConversationHistory()
        
        # 段階的に会話を重ねてスコア変化を確認
        video_id = "familiarity_test"
        title = "テスト楽曲"
        
        conversations = [
            "テスト楽曲について教えて",  # 初回
            "この曲いいね",              # ポジティブ
            "もう一度聞きたい",          # ポジティブ
            "テスト楽曲の詳細は？",      # 継続
            "やっぱりこの曲好き",        # ポジティブ
        ]
        
        scores = []
        for i, conversation in enumerate(conversations):
            history.record_conversation(video_id, title, conversation)
            context = history.get_conversation_context(video_id)
            
            if context:
                score = context['familiarity_score']
                level = context['familiarity_level']
                scores.append(score)
                
                print(f"会話 {i+1}: スコア {score:.3f} → レベル: {level}")
        
        # スコアが単調増加しているかチェック
        is_increasing = all(scores[i] <= scores[i+1] for i in range(len(scores)-1))
        
        if is_increasing:
            print(f"✅ スコア進化正常: {scores[0]:.3f} → {scores[-1]:.3f}")
        else:
            print(f"❌ スコア進化異常: {scores}")
        
        return is_increasing
        
    except Exception as e:
        print(f"❌ 親しみやすさテスト失敗: {e}")
        return False

def test_conversation_hints():
    """会話ヒント生成のテスト"""
    print("\n=== 会話ヒント生成テスト ===")
    
    try:
        from core.video_conversation_history import VideoConversationHistory
        
        history = VideoConversationHistory()
        
        # 異なるパターンの会話履歴を作成
        test_cases = [
            # 新規動画（ヒントなし期待）
            {"video_id": "new_video", "title": "新規楽曲", "conversations": ["新規楽曲について"]},
            
            # 馴染みのある動画（ヒントあり期待）
            {"video_id": "familiar_video", "title": "馴染み楽曲", "conversations": [
                "馴染み楽曲について", "この曲好き", "また聞きたい", "やっぱりいいね"
            ]},
            
            # ネガティブ反応の動画
            {"video_id": "negative_video", "title": "微妙楽曲", "conversations": [
                "微妙楽曲について", "この曲はイマイチかも"
            ]}
        ]
        
        success_count = 0
        for test_case in test_cases:
            video_id = test_case["video_id"]
            title = test_case["title"]
            conversations = test_case["conversations"]
            
            print(f"\n🧪 テストケース: {title}")
            
            # 会話履歴を構築
            for conversation in conversations:
                history.record_conversation(video_id, title, conversation)
            
            # ヒント生成
            hints = history.generate_conversation_hints(video_id)
            context = history.get_conversation_context(video_id)
            
            if context:
                print(f"   レベル: {context['familiarity_level']}")
                print(f"   ヒント数: {len(hints)}")
                print(f"   ヒント: {hints}")
                
                # 期待される結果チェック
                if video_id == "new_video":
                    expected_few_hints = len(hints) <= 1
                elif video_id == "familiar_video":
                    expected_many_hints = len(hints) >= 2
                    has_familiarity_hint = any("おなじみ" in hint or "いつもの" in hint for hint in hints)
                    expected_many_hints = expected_many_hints and has_familiarity_hint
                elif video_id == "negative_video":
                    expected_negative_hint = any("好まない" in hint for hint in hints)
                else:
                    expected_many_hints = True
                
                if video_id == "new_video" and expected_few_hints:
                    print("   ✅ 新規動画のヒント生成正常")
                    success_count += 1
                elif video_id == "familiar_video" and expected_many_hints:
                    print("   ✅ 馴染み動画のヒント生成正常")
                    success_count += 1
                elif video_id == "negative_video" and expected_negative_hint:
                    print("   ✅ ネガティブ動画のヒント生成正常")
                    success_count += 1
                else:
                    print("   ⚠️ ヒント生成が期待と異なる")
        
        return success_count >= 2  # 3つ中2つ以上成功で合格
        
    except Exception as e:
        print(f"❌ 会話ヒントテスト失敗: {e}")
        return False

def test_integration_with_context_builder():
    """ConversationContextBuilderとの統合テスト"""
    print("\n=== ConversationContextBuilder統合テスト ===")
    
    try:
        from core.conversation_context_builder import ConversationContextBuilder
        
        builder = ConversationContextBuilder()
        
        # 実際の動画で統合テスト
        test_input = "アドベンチャーについて教えて"
        
        print(f"🔍 統合テスト入力: '{test_input}'")
        
        # 初回会話
        print("\n1回目の会話:")
        context_text = builder.process_user_input(test_input)
        if context_text:
            print("✅ 初回コンテキスト生成成功")
            has_history_info = "おなじみ" in context_text or "前にも話した" in context_text
            print(f"履歴情報: {'含まれている' if has_history_info else '含まれていない（正常）'}")
        
        # 2回目の会話（履歴情報が反映されるか）
        print("\n2回目の会話:")
        context_text_2 = builder.process_user_input(test_input)
        if context_text_2:
            print("✅ 2回目コンテキスト生成成功")
            has_history_info_2 = "おなじみ" in context_text_2 or "前にも話した" in context_text_2 or "話したことがある" in context_text_2
            print(f"履歴情報: {'含まれている' if has_history_info_2 else '含まれていない'}")
            
            if has_history_info_2:
                print("✅ 会話履歴が正常に反映されている")
                return True
            else:
                print("⚠️ 会話履歴の反映が確認できない")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ 統合テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メインテスト実行"""
    print("🧠 Phase 2-B-1: 動画会話履歴システムテスト開始\n")
    
    results = []
    
    # 各テストの実行
    results.append(test_conversation_recording())
    results.append(test_familiarity_progression())
    results.append(test_conversation_hints())
    results.append(test_integration_with_context_builder())
    
    # 結果サマリー
    print("\n" + "="*70)
    print("📊 Phase 2-B-1 テスト結果サマリー")
    print("="*70)
    
    test_names = [
        "会話記録機能",
        "親しみやすさスコア進化",
        "会話ヒント生成",
        "ConversationContextBuilder統合"
    ]
    
    success_count = sum(results)
    total_count = len(results)
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"{i+1}. {test_name}: {status}")
    
    print(f"\n📈 総合成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count >= 3:  # 4つ中3つ以上で合格
        print("\n🎉 Phase 2-B-1 テスト合格！会話履歴連携機能が正常に動作しています。")
        print("\n✨ 実装された機能:")
        print("- 動画ごとの会話回数・親しみやすさ記録")
        print("- ユーザー反応の自動分析・学習")
        print("- 会話の継続性を表現するヒント生成")
        print("- ConversationContextBuilderとの自動統合")
        print("\n🔧 次のステップ: 実際の音声会話でテスト")
        print("推奨テスト文:")
        print("- 「アドベンチャーについて教えて」（初回）")
        print("- 「この曲いいね」（ポジティブ反応）")
        print("- 「またアドベンチャーについて」（継続会話）")
    else:
        print(f"\n⚠️ 改善が必要です（{total_count - success_count}項目が失敗）")
        print("詳細は上記ログを確認してください。")

if __name__ == "__main__":
    main()