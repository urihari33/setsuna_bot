#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主体性強化システム統合テスト
全体システムの動作確認とパフォーマンステスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

import json
from datetime import datetime
from core.setsuna_chat import SetsunaChat

class ProactivityIntegrationTester:
    def __init__(self):
        """統合テスターの初期化"""
        self.test_results = []
        self.chat_system = None
        
        print("=" * 60)
        print("🚀 主体性強化システム統合テスト")
        print("=" * 60)
    
    def setup_test_environment(self):
        """テスト環境のセットアップ"""
        try:
            print("\n[テスト] 🔧 テスト環境セットアップ中...")
            
            # SetsunaChat システムの初期化
            self.chat_system = SetsunaChat(memory_mode="test")
            
            # 新システムの初期化確認
            systems_status = {
                "preference_analyzer": self.chat_system.preference_analyzer is not None,
                "preference_mapper": self.chat_system.preference_mapper is not None,
                "opinion_generator": self.chat_system.opinion_generator is not None,
                "proactive_engine": self.chat_system.proactive_engine is not None,
                "new_consistency_checker": self.chat_system.new_consistency_checker is not None
            }
            
            print("[テスト] 📊 システム初期化状況:")
            for system, status in systems_status.items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {system}: {'初期化成功' if status else '初期化失敗'}")
            
            all_systems_ready = all(systems_status.values())
            
            if all_systems_ready:
                print("[テスト] ✅ 全システム初期化完了")
                return True
            else:
                print("[テスト] ⚠️ 一部システムの初期化に失敗")
                return False
                
        except Exception as e:
            print(f"[テスト] ❌ セットアップエラー: {e}")
            return False
    
    def test_basic_response(self):
        """基本応答テスト"""
        print("\n[テスト] 💬 基本応答テスト実行中...")
        
        test_cases = [
            {
                "input": "こんにちは",
                "expected_features": ["greeting_response"],
                "description": "基本的な挨拶"
            },
            {
                "input": "最近どう？",
                "expected_features": ["casual_conversation"],
                "description": "カジュアルな会話"
            }
        ]
        
        results = []
        
        for case in test_cases:
            try:
                print(f"\n  👤 入力: {case['input']}")
                
                start_time = datetime.now()
                response = self.chat_system.get_response(case['input'], mode="full_search")
                response_time = (datetime.now() - start_time).total_seconds()
                
                print(f"  🤖 応答: {response}")
                print(f"  ⏱️ 応答時間: {response_time:.2f}秒")
                
                # レスポンスの品質チェック
                quality_check = self._assess_response_quality(response, case)
                
                results.append({
                    "input": case["input"],
                    "response": response,
                    "response_time": response_time,
                    "quality_score": quality_check["score"],
                    "issues": quality_check["issues"]
                })
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                results.append({
                    "input": case["input"],
                    "error": str(e),
                    "quality_score": 0.0
                })
        
        return results
    
    def test_proactive_features(self):
        """プロアクティブ機能テスト"""
        print("\n[テスト] 💡 プロアクティブ機能テスト実行中...")
        
        test_cases = [
            {
                "input": "楽曲分析について話そう",
                "expected_features": ["music_analysis", "proactive_suggestion"],
                "description": "楽曲関連の主体的提案"
            },
            {
                "input": "映像制作のアイデアを考えてる",
                "expected_features": ["creative_context", "opinion_generation"],
                "description": "創作関連の意見生成"
            },
            {
                "input": "この楽曲で何か作れないかな？",
                "expected_features": ["collaborative_suggestion", "proactive_response"],
                "description": "協働提案の生成"
            }
        ]
        
        results = []
        
        for case in test_cases:
            try:
                print(f"\n  👤 入力: {case['input']}")
                
                # プロアクティブ判定のテスト
                proactive_check = self.chat_system._check_proactive_opportunity(
                    case['input'], "full_search"
                )
                
                if proactive_check:
                    print(f"  💡 プロアクティブ要素検出: {proactive_check.get('type', 'unknown')}")
                else:
                    print("  🔍 プロアクティブ要素なし")
                
                # 実際の応答生成
                response = self.chat_system.get_response(case['input'], mode="full_search")
                
                print(f"  🤖 応答: {response}")
                
                # プロアクティブ性の評価
                proactivity_score = self._assess_proactivity(response, case)
                
                results.append({
                    "input": case["input"],
                    "response": response,
                    "proactive_detected": proactive_check is not None,
                    "proactivity_score": proactivity_score,
                    "expected_features": case["expected_features"]
                })
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                results.append({
                    "input": case["input"],
                    "error": str(e),
                    "proactivity_score": 0.0
                })
        
        return results
    
    def test_consistency_checking(self):
        """一貫性チェック機能テスト"""
        print("\n[テスト] 🔍 一貫性チェック機能テスト実行中...")
        
        # 意図的に問題のある応答をテスト
        problematic_responses = [
            {
                "user_input": "この楽曲について教えて",
                "response": "素晴らしい楽曲ですね。いかがお感じになりますか？",
                "expected_issues": ["inappropriate_tone", "question_only_response"]
            },
            {
                "user_input": "映像制作をしよう",
                "response": "お手伝いさせていただきます。ご指示をお待ちしています。",
                "expected_issues": ["hierarchical_tone", "passive_stance"]
            }
        ]
        
        results = []
        
        for case in problematic_responses:
            try:
                print(f"\n  👤 入力: {case['user_input']}")
                print(f"  🤖 テスト応答: {case['response']}")
                
                # 一貫性チェック実行
                consistency_result = self.chat_system.new_consistency_checker.check_response_consistency(
                    case['user_input'], case['response']
                )
                
                print(f"  📊 一貫性スコア: {consistency_result['overall_score']:.2f}")
                print(f"  🔧 修正必要: {consistency_result['needs_correction']}")
                
                if consistency_result["issues"]:
                    print("  ⚠️ 検出された問題:")
                    for issue in consistency_result["issues"]:
                        print(f"    - {issue['type']}: {issue['description']}")
                
                # 修正テスト
                if consistency_result['needs_correction']:
                    corrected_response = self.chat_system.new_consistency_checker.correct_response_if_needed(
                        case['response'], consistency_result
                    )
                    print(f"  ✅ 修正後: {corrected_response}")
                    
                    results.append({
                        "original_response": case['response'],
                        "corrected_response": corrected_response,
                        "consistency_score": consistency_result['overall_score'],
                        "issues_detected": len(consistency_result["issues"]),
                        "correction_applied": corrected_response != case['response']
                    })
                else:
                    results.append({
                        "original_response": case['response'],
                        "consistency_score": consistency_result['overall_score'],
                        "issues_detected": len(consistency_result["issues"]),
                        "correction_applied": False
                    })
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                results.append({"error": str(e)})
        
        return results
    
    def test_database_integration(self):
        """データベース統合テスト"""
        print("\n[テスト] 🗄️ データベース統合テスト実行中...")
        
        results = {}
        
        try:
            # 好み推測システムのテスト
            if self.chat_system.preference_analyzer:
                print("  📊 好み推測システムテスト...")
                preferences = self.chat_system.preference_analyzer.generate_preference_profile()
                
                if preferences:
                    music_prefs = preferences.get("music_preferences", {})
                    total_videos = music_prefs.get("total_videos_analyzed", 0)
                    print(f"  ✅ 分析動画数: {total_videos}件")
                    
                    results["preference_analysis"] = {
                        "success": True,
                        "videos_analyzed": total_videos,
                        "has_preferences": len(music_prefs) > 0
                    }
                else:
                    print("  ⚠️ 好み推測データが取得できませんでした")
                    results["preference_analysis"] = {"success": False}
            
            # 価値観マッピングのテスト
            if self.chat_system.preference_mapper:
                print("  🎯 価値観マッピングテスト...")
                mapping_result = self.chat_system.preference_mapper.map_database_to_preferences()
                
                if mapping_result:
                    specific_prefs = mapping_result.get("specific_preferences", {})
                    strongly_liked = specific_prefs.get("strongly_liked", [])
                    print(f"  ✅ 強い好み: {len(strongly_liked)}件")
                    
                    results["preference_mapping"] = {
                        "success": True,
                        "preferences_mapped": len(strongly_liked),
                        "has_creative_patterns": "creative_patterns" in mapping_result
                    }
                else:
                    results["preference_mapping"] = {"success": False}
            
        except Exception as e:
            print(f"  ❌ データベース統合エラー: {e}")
            results["error"] = str(e)
        
        return results
    
    def test_performance(self):
        """パフォーマンステスト"""
        print("\n[テスト] ⚡ パフォーマンステスト実行中...")
        
        test_inputs = [
            "こんにちは",
            "この楽曲について教えて",
            "映像制作のアイデアを考えてる",
            "技術的な話をしよう",
            "一緒に何か作らない？"
        ]
        
        performance_results = []
        
        for i, input_text in enumerate(test_inputs, 1):
            print(f"  テスト {i}/5: {input_text}")
            
            try:
                # 通常モードでのテスト
                start_time = datetime.now()
                response_normal = self.chat_system.get_response(input_text, mode="full_search")
                normal_time = (datetime.now() - start_time).total_seconds()
                
                # 高速モードでのテスト
                start_time = datetime.now()
                response_fast = self.chat_system.get_response(input_text, mode="fast_response")
                fast_time = (datetime.now() - start_time).total_seconds()
                
                performance_results.append({
                    "input": input_text,
                    "normal_mode_time": normal_time,
                    "fast_mode_time": fast_time,
                    "speed_improvement": (normal_time - fast_time) / normal_time * 100
                })
                
                print(f"    通常モード: {normal_time:.2f}秒")
                print(f"    高速モード: {fast_time:.2f}秒")
                
            except Exception as e:
                print(f"    ❌ エラー: {e}")
                performance_results.append({
                    "input": input_text,
                    "error": str(e)
                })
        
        # 統計計算
        successful_tests = [r for r in performance_results if "error" not in r]
        if successful_tests:
            avg_normal_time = sum(r["normal_mode_time"] for r in successful_tests) / len(successful_tests)
            avg_fast_time = sum(r["fast_mode_time"] for r in successful_tests) / len(successful_tests)
            
            print(f"\n  📊 パフォーマンス統計:")
            print(f"    平均応答時間（通常）: {avg_normal_time:.2f}秒")
            print(f"    平均応答時間（高速）: {avg_fast_time:.2f}秒")
            print(f"    高速化効果: {((avg_normal_time - avg_fast_time) / avg_normal_time * 100):.1f}%")
        
        return performance_results
    
    def run_comprehensive_test(self):
        """総合テストの実行"""
        try:
            # セットアップ
            if not self.setup_test_environment():
                print("\n❌ セットアップに失敗しました")
                return False
            
            # 各テストの実行
            basic_results = self.test_basic_response()
            proactive_results = self.test_proactive_features()
            consistency_results = self.test_consistency_checking()
            database_results = self.test_database_integration()
            performance_results = self.test_performance()
            
            # 主体性システム統計の取得
            proactivity_stats = self.chat_system.get_proactivity_stats()
            
            # 総合結果のまとめ
            comprehensive_results = {
                "basic_response": basic_results,
                "proactive_features": proactive_results,
                "consistency_checking": consistency_results,
                "database_integration": database_results,
                "performance": performance_results,
                "proactivity_stats": proactivity_stats,
                "test_timestamp": datetime.now().isoformat()
            }
            
            # 結果の保存
            self._save_test_results(comprehensive_results)
            
            # 総合評価
            self._print_summary(comprehensive_results)
            
            return True
            
        except Exception as e:
            print(f"\n❌ 総合テストエラー: {e}")
            return False
    
    def _assess_response_quality(self, response: str, case: dict) -> dict:
        """応答品質を評価"""
        quality = {"score": 0.5, "issues": []}
        
        if not response or len(response.strip()) < 3:
            quality["issues"].append("応答が短すぎる")
            return quality
        
        # 基本的な品質チェック
        if len(response) > 10:
            quality["score"] += 0.2
        
        # 適切な日本語応答
        if any(char in response for char in "。、！？"):
            quality["score"] += 0.1
        
        # 自然な応答
        if not any(pattern in response for pattern in ["エラー", "申し訳", "できません"]):
            quality["score"] += 0.2
        
        quality["score"] = min(quality["score"], 1.0)
        return quality
    
    def _assess_proactivity(self, response: str, case: dict) -> float:
        """プロアクティブ性を評価"""
        proactivity_score = 0.0
        
        # 主体的な表現の検出
        proactive_patterns = [
            "〜したいなって", "〜してみない？", "私は〜", "個人的に",
            "〜と思うんだけど", "提案", "アイデア", "一緒に"
        ]
        
        for pattern in proactive_patterns:
            if pattern in response:
                proactivity_score += 0.2
        
        # 質問のみの応答は減点
        if response.count("？") > 0 and len(response.replace("？", "").strip()) < 10:
            proactivity_score -= 0.3
        
        return max(0.0, min(proactivity_score, 1.0))
    
    def _save_test_results(self, results: dict):
        """テスト結果を保存"""
        try:
            results_file = Path("D:/setsuna_bot/test/proactivity_test_results.json")
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n[テスト] 💾 結果を保存: {results_file}")
        except Exception as e:
            print(f"\n[テスト] ⚠️ 結果保存エラー: {e}")
    
    def _print_summary(self, results: dict):
        """総合評価サマリーを表示"""
        print("\n" + "=" * 60)
        print("📊 総合テスト結果サマリー")
        print("=" * 60)
        
        # 基本応答テスト結果
        basic_results = results["basic_response"]
        basic_success_rate = len([r for r in basic_results if "error" not in r]) / len(basic_results) * 100
        print(f"基本応答テスト: {basic_success_rate:.1f}% 成功")
        
        # プロアクティブ機能テスト結果
        proactive_results = results["proactive_features"]
        proactive_detected = len([r for r in proactive_results if r.get("proactive_detected", False)])
        print(f"プロアクティブ機能: {proactive_detected}/{len(proactive_results)} 件で検出")
        
        # 一貫性チェック結果
        consistency_results = results["consistency_checking"]
        corrections_applied = len([r for r in consistency_results if r.get("correction_applied", False)])
        print(f"一貫性チェック: {corrections_applied} 件の修正を適用")
        
        # データベース統合結果
        db_results = results["database_integration"]
        db_success = db_results.get("preference_analysis", {}).get("success", False)
        print(f"データベース統合: {'✅ 成功' if db_success else '❌ 失敗'}")
        
        # パフォーマンス結果
        performance_results = results["performance"]
        successful_perf = [r for r in performance_results if "error" not in r]
        if successful_perf:
            avg_time = sum(r["normal_mode_time"] for r in successful_perf) / len(successful_perf)
            print(f"平均応答時間: {avg_time:.2f}秒")
        
        # 主体性統計
        proactivity_stats = results["proactivity_stats"]
        print(f"主体性スコア: {proactivity_stats.get('average_proactivity_score', 0):.2f}")
        
        print("\n🎉 統合テスト完了！")

def main():
    """メイン実行関数"""
    tester = ProactivityIntegrationTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ 全てのテストが完了しました")
    else:
        print("\n❌ テストの実行に問題がありました")

if __name__ == "__main__":
    main()