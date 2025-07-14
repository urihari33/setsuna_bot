#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
コンテキスト理解エンジンテスト - Phase 2C動作確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from core.context_understanding_engine import ContextUnderstandingEngine
import json

class ContextUnderstandingTester:
    """コンテキスト理解テスター"""
    
    def __init__(self):
        """初期化"""
        self.engine = ContextUnderstandingEngine()
        
    def run_comprehensive_test(self):
        """包括的テスト実行"""
        print("🧠 コンテキスト理解エンジン包括テスト")
        print("=" * 60)
        
        test_results = {}
        
        # テスト1: コンテキスト分析
        test_results["context_analysis"] = self.test_context_analysis()
        
        # テスト2: 感情状態推定
        test_results["emotion_estimation"] = self.test_emotion_estimation()
        
        # テスト3: 知識深度分析
        test_results["knowledge_depth"] = self.test_knowledge_depth_analysis()
        
        # テスト4: 文脈的推薦生成
        test_results["contextual_recommendations"] = self.test_contextual_recommendations()
        
        # テスト5: トピック遷移予測
        test_results["topic_transition"] = self.test_topic_transition_prediction()
        
        # テスト6: 会話学習機能
        test_results["conversation_learning"] = self.test_conversation_learning()
        
        # 総合結果
        self.display_comprehensive_results(test_results)
        
        return test_results
    
    def test_context_analysis(self):
        """コンテキスト分析テスト"""
        print("\n🔍 コンテキスト分析テスト")
        print("-" * 40)
        
        test_conversations = [
            {
                "input": "最近のボカロ曲で何かいいのない？",
                "expected_topics": ["ボカロ"],
                "expected_temporal": "recent"
            },
            {
                "input": "TRiNITYの曲が好きなんだけど、似たようなアーティストいる？",
                "expected_topics": ["アーティスト"],
                "expected_temporal": "general"
            },
            {
                "input": "昔聞いた懐かしい曲を探してるんだ",
                "expected_topics": ["時代"],
                "expected_temporal": "past"
            }
        ]
        
        results = {}
        
        for i, case in enumerate(test_conversations, 1):
            try:
                print(f"📝 ケース{i}: {case['input']}")
                
                # コンテキスト分析実行
                context = self.engine.analyze_conversation_context(
                    case["input"], 
                    session_id=f"test_session_{i}"
                )
                
                # トピック抽出確認
                topic_match = any(
                    expected in context.mentioned_topics 
                    for expected in case["expected_topics"]
                )
                
                # 時間的コンテキスト確認
                temporal_match = context.temporal_context == case["expected_temporal"]
                
                results[f"case_{i}"] = {
                    "success": True,
                    "topics_extracted": context.mentioned_topics,
                    "temporal_context": context.temporal_context,
                    "emotional_state": context.emotional_state,
                    "topic_match": topic_match,
                    "temporal_match": temporal_match,
                    "knowledge_depth": context.knowledge_depth
                }
                
                print(f"   抽出トピック: {context.mentioned_topics}")
                print(f"   時間的文脈: {context.temporal_context}")
                print(f"   感情状態: {context.emotional_state}")
                print(f"   トピック適合: {'○' if topic_match else '×'}")
                print(f"   時間的適合: {'○' if temporal_match else '×'}")
                
            except Exception as e:
                results[f"case_{i}"] = {"success": False, "error": str(e)}
                print(f"❌ エラー: {e}")
            
            print()
        
        success_rate = len([r for r in results.values() if r.get("success", False)]) / len(test_conversations) * 100
        print(f"📊 コンテキスト分析成功率: {success_rate:.1f}%")
        
        return {"success_rate": success_rate, "details": results}
    
    def test_emotion_estimation(self):
        """感情状態推定テスト"""
        print("\n😊 感情状態推定テスト")
        print("-" * 40)
        
        emotion_test_cases = [
            {
                "input": "この曲すごく楽しくて最高！",
                "expected_emotion": "excited"
            },
            {
                "input": "どんな曲なのか気になるなあ",
                "expected_emotion": "curious"
            },
            {
                "input": "昔よく聞いた懐かしい曲だね",
                "expected_emotion": "nostalgic"
            },
            {
                "input": "ゆっくりできる癒しの音楽がいい",
                "expected_emotion": "relaxed"
            },
            {
                "input": "もっと詳しく教えて欲しい",
                "expected_emotion": "focused"
            }
        ]
        
        results = {}
        correct_predictions = 0
        
        for i, case in enumerate(emotion_test_cases, 1):
            try:
                context = self.engine.analyze_conversation_context(case["input"])
                predicted_emotion = context.emotional_state
                is_correct = predicted_emotion == case["expected_emotion"]
                
                if is_correct:
                    correct_predictions += 1
                
                results[f"emotion_{i}"] = {
                    "input": case["input"],
                    "expected": case["expected_emotion"],
                    "predicted": predicted_emotion,
                    "correct": is_correct
                }
                
                status = "✅" if is_correct else "❌"
                print(f"{status} '{case['input'][:30]}...'")
                print(f"   期待: {case['expected_emotion']}, 予測: {predicted_emotion}")
                
            except Exception as e:
                results[f"emotion_{i}"] = {"error": str(e)}
                print(f"❌ エラー: {e}")
        
        accuracy = correct_predictions / len(emotion_test_cases) * 100
        print(f"\n📊 感情推定精度: {accuracy:.1f}%")
        
        return {"accuracy": accuracy, "details": results}
    
    def test_knowledge_depth_analysis(self):
        """知識深度分析テスト"""
        print("\n📚 知識深度分析テスト")
        print("-" * 40)
        
        depth_test_cases = [
            {
                "input": "ボカロって何？初めて聞いた",
                "topic": "ボカロ",
                "expected_depth": "beginner"  # < 0.3
            },
            {
                "input": "ボカロはだいたい知ってるけど、もっと詳しく教えて",
                "topic": "ボカロ",
                "expected_depth": "intermediate"  # 0.3-0.7
            },
            {
                "input": "ボカロマニアなんだけど、レアな楽曲ない？",
                "topic": "ボカロ",
                "expected_depth": "advanced"  # > 0.7
            }
        ]
        
        results = {}
        
        for i, case in enumerate(depth_test_cases, 1):
            try:
                context = self.engine.analyze_conversation_context(case["input"])
                
                # 知識深度スコア取得
                depth_score = context.knowledge_depth.get(case["topic"], 0.5)
                
                # 深度レベル判定
                if depth_score < 0.3:
                    predicted_level = "beginner"
                elif depth_score > 0.7:
                    predicted_level = "advanced"
                else:
                    predicted_level = "intermediate"
                
                is_correct = predicted_level == case["expected_depth"]
                
                results[f"depth_{i}"] = {
                    "input": case["input"],
                    "topic": case["topic"],
                    "expected_level": case["expected_depth"],
                    "predicted_level": predicted_level,
                    "depth_score": depth_score,
                    "correct": is_correct
                }
                
                status = "✅" if is_correct else "❌"
                print(f"{status} '{case['input'][:40]}...'")
                print(f"   トピック: {case['topic']}")
                print(f"   期待レベル: {case['expected_depth']}")
                print(f"   予測レベル: {predicted_level} (スコア: {depth_score:.2f})")
                
            except Exception as e:
                results[f"depth_{i}"] = {"error": str(e)}
                print(f"❌ エラー: {e}")
            
            print()
        
        return {"details": results}
    
    def test_contextual_recommendations(self):
        """文脈的推薦生成テスト"""
        print("\n💡 文脈的推薦生成テスト")
        print("-" * 40)
        
        try:
            # テスト用コンテキスト作成
            test_input = "ボカロの明るい曲が聞きたい気分だなあ"
            context = self.engine.analyze_conversation_context(test_input)
            
            print(f"テスト入力: {test_input}")
            print(f"抽出コンテキスト:")
            print(f"  トピック: {context.mentioned_topics}")
            print(f"  感情状態: {context.emotional_state}")
            print(f"  時間的文脈: {context.temporal_context}")
            
            # 推薦生成
            recommendations = self.engine.generate_contextual_recommendations(context, max_recommendations=5)
            
            print(f"\n📋 生成された推薦 ({len(recommendations)}件):")
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec.content_title}")
                    print(f"     タイプ: {rec.recommendation_type}")
                    print(f"     関連度: {rec.context_relevance:.3f}")
                    print(f"     信頼度: {rec.confidence:.3f}")
                    print(f"     理由: {', '.join(rec.reasoning)}")
                    print(f"     タイミング: {rec.timing}")
                    print()
            else:
                print("  推薦が生成されませんでした")
            
            # 推薦タイプ別統計
            rec_types = {}
            for rec in recommendations:
                rec_type = rec.recommendation_type
                rec_types[rec_type] = rec_types.get(rec_type, 0) + 1
            
            print(f"📊 推薦タイプ別統計: {rec_types}")
            
            return {
                "success": len(recommendations) > 0,
                "recommendation_count": len(recommendations),
                "recommendation_types": rec_types,
                "average_relevance": sum(r.context_relevance for r in recommendations) / len(recommendations) if recommendations else 0
            }
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def test_topic_transition_prediction(self):
        """トピック遷移予測テスト"""
        print("\n🔄 トピック遷移予測テスト")
        print("-" * 40)
        
        try:
            # 複数の会話ターンを実行して遷移パターンを作成
            conversation_sequence = [
                "ボカロが好きなんだ",
                "初音ミクの曲をよく聞く",
                "アニソンも聞くよ",
                "ゲーム音楽も面白いよね"
            ]
            
            print("🔄 会話シーケンスを実行:")
            for i, utterance in enumerate(conversation_sequence, 1):
                print(f"  {i}. {utterance}")
                context = self.engine.analyze_conversation_context(utterance)
            
            # 最後のコンテキストから遷移予測
            if hasattr(self.engine, 'current_context') and self.engine.current_context:
                current_topics = self.engine.current_context.mentioned_topics
                print(f"\n現在のトピック: {current_topics}")
                
                # 遷移予測実行
                transitions = self.engine.predict_topic_transition(current_topics)
                
                print(f"📈 予測される遷移 ({len(transitions)}件):")
                for transition in transitions:
                    print(f"  {transition.from_topic} → {transition.to_topic}")
                    print(f"    タイプ: {transition.transition_type}")
                    print(f"    強度: {transition.strength:.3f}")
                    print(f"    パターン: {transition.patterns}")
                    print()
                
                return {
                    "success": True,
                    "transition_count": len(transitions),
                    "current_topics": current_topics
                }
            else:
                print("⚠️ 現在のコンテキストが設定されていません")
                return {"success": False, "error": "No current context"}
                
        except Exception as e:
            print(f"❌ エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def test_conversation_learning(self):
        """会話学習機能テスト"""
        print("\n🎓 会話学習機能テスト")
        print("-" * 40)
        
        try:
            # 学習シナリオ
            learning_scenarios = [
                {
                    "user_input": "ロック音楽が好き",
                    "system_response": "ロック音楽の推薦をします",
                    "user_feedback": "いいね、気に入った"
                },
                {
                    "user_input": "クラシック音楽について",
                    "system_response": "クラシック音楽を紹介します",
                    "user_feedback": "ちょっと違うかな"
                }
            ]
            
            print("📚 学習シナリオを実行:")
            
            # 学習前の好み設定を記録
            initial_preferences = dict(self.engine.user_preferences)
            
            for i, scenario in enumerate(learning_scenarios, 1):
                print(f"\n  シナリオ{i}:")
                print(f"    ユーザー: {scenario['user_input']}")
                print(f"    システム: {scenario['system_response']}")
                print(f"    フィードバック: {scenario['user_feedback']}")
                
                # コンテキスト分析
                context = self.engine.analyze_conversation_context(scenario["user_input"])
                
                # 学習実行
                self.engine.learn_from_conversation(
                    scenario["user_input"],
                    scenario["system_response"], 
                    scenario["user_feedback"]
                )
            
            # 学習後の好み設定
            final_preferences = dict(self.engine.user_preferences)
            
            print(f"\n📊 学習結果:")
            print(f"  学習前の好み数: {len(initial_preferences)}")
            print(f"  学習後の好み数: {len(final_preferences)}")
            
            # 新しく学習された好み
            new_preferences = {k: v for k, v in final_preferences.items() if k not in initial_preferences}
            if new_preferences:
                print(f"  新規学習された好み:")
                for pref, value in new_preferences.items():
                    print(f"    {pref}: {value:.2f}")
            
            # 統計情報
            stats = self.engine.get_engine_statistics()
            print(f"\n📈 エンジン統計:")
            for key, value in stats.items():
                print(f"    {key}: {value}")
            
            return {
                "success": True,
                "initial_preferences_count": len(initial_preferences),
                "final_preferences_count": len(final_preferences),
                "new_preferences_count": len(new_preferences),
                "statistics": stats
            }
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def display_comprehensive_results(self, test_results):
        """総合結果表示"""
        print("\n" + "=" * 60)
        print("📊 総合テスト結果")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for test_name, result in test_results.items():
            total_tests += 1
            
            # 成功判定
            success = False
            if result.get("success", False):
                success = True
            elif result.get("success_rate", 0) > 60:
                success = True
            elif result.get("accuracy", 0) > 60:
                success = True
            
            if success:
                passed_tests += 1
                status = "✅ 合格"
            else:
                status = "❌ 不合格"
            
            print(f"{status} {test_name}")
            
            # 主要メトリクス表示
            if "success_rate" in result:
                print(f"    成功率: {result['success_rate']:.1f}%")
            elif "accuracy" in result:
                print(f"    精度: {result['accuracy']:.1f}%")
            elif "recommendation_count" in result:
                print(f"    推薦数: {result['recommendation_count']}")
        
        overall_success_rate = passed_tests / total_tests * 100
        print(f"\n🎯 総合成功率: {overall_success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        if overall_success_rate >= 80:
            print("🎉 コンテキスト理解エンジンが正常に動作しています！")
        elif overall_success_rate >= 60:
            print("⚠️ 一部機能に改善が必要です。")
        else:
            print("🔧 大幅な修正が必要です。")

def main():
    """メイン実行"""
    tester = ContextUnderstandingTester()
    results = tester.run_comprehensive_test()
    
    print(f"\n✨ コンテキスト理解エンジンテスト完了")
    
    return results

if __name__ == "__main__":
    main()