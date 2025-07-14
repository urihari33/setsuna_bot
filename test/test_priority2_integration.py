#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Priority 2統合テスト - 全システムの動作検証
Phase 2D-2F: 会話知識強化システム総合テスト
"""

import sys
import os
from pathlib import Path
import json
import time
from datetime import datetime

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# テスト対象システム
try:
    from core.conversation_history_analyzer import ConversationHistoryAnalyzer
    from core.user_interest_tracker import UserInterestTracker
    from core.preference_evolution_engine import PreferenceEvolutionEngine
    from core.real_time_knowledge_updater import RealTimeKnowledgeUpdater, NewInformation, KnowledgeUpdate
    from core.incremental_learning_engine import IncrementalLearningEngine
    from core.knowledge_validation_system import KnowledgeValidationSystem
    from core.knowledge_quality_manager import KnowledgeQualityManager
    from core.data_consistency_checker import DataConsistencyChecker
    from core.performance_monitor import PerformanceMonitor
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"⚠️ インポートエラー: {e}")
    IMPORTS_SUCCESSFUL = False

class Priority2IntegrationTest:
    """Priority 2統合テストクラス"""
    
    def __init__(self):
        """初期化"""
        self.test_results = {
            "test_start_time": datetime.now().isoformat(),
            "phase_2d_results": {},
            "phase_2e_results": {},
            "phase_2f_results": {},
            "integration_results": {},
            "performance_results": {},
            "test_summary": {}
        }
        
        self.systems = {}
        self.test_data = self._prepare_test_data()
        
    def _prepare_test_data(self):
        """テストデータ準備"""
        return {
            "test_user_input": "アオペラの新しい動画について教えて",
            "test_video_id": "test_video_123",
            "test_new_information": {
                "info_id": "test_info_001",
                "content": "アオペラの新メンバーに関する情報",
                "info_type": "artist",
                "confidence": 0.8,
                "source_context": "テスト環境",
                "extraction_method": "manual_extraction",
                "related_entities": ["アオペラ", "新メンバー"],
                "validation_status": "pending",
                "detected_at": datetime.now().isoformat()
            },
            "test_knowledge_update": {
                "update_id": "test_update_001",
                "target_entity": "アオペラ",
                "update_type": "enhance",
                "old_value": "既存情報",
                "new_value": "更新された情報",
                "confidence": 0.9,
                "supporting_evidence": ["証拠1", "証拠2"],
                "impact_score": 0.7,
                "applied_at": None
            }
        }
    
    def run_comprehensive_test(self):
        """包括的テスト実行"""
        print("🚀 Priority 2統合テスト開始")
        print("=" * 60)
        
        try:
            # 前提条件チェック
            if not self._check_prerequisites():
                return self.test_results
            
            # Phase 2D テスト
            print("\n📊 Phase 2D: 会話履歴分析システムテスト")
            self.test_results["phase_2d_results"] = self._test_phase_2d()
            
            # Phase 2E テスト
            print("\n🔄 Phase 2E: リアルタイム知識更新システムテスト")
            self.test_results["phase_2e_results"] = self._test_phase_2e()
            
            # Phase 2F テスト
            print("\n🔍 Phase 2F: 知識品質管理システムテスト")
            self.test_results["phase_2f_results"] = self._test_phase_2f()
            
            # システム間統合テスト
            print("\n🔗 システム間統合テスト")
            self.test_results["integration_results"] = self._test_system_integration()
            
            # パフォーマンステスト
            print("\n⚡ パフォーマンステスト")
            self.test_results["performance_results"] = self._test_performance()
            
            # テストサマリー生成
            self.test_results["test_summary"] = self._generate_test_summary()
            
        except Exception as e:
            print(f"❌ テスト実行中にエラーが発生: {e}")
            self.test_results["critical_error"] = str(e)
        
        finally:
            self.test_results["test_end_time"] = datetime.now().isoformat()
            self._save_test_results()
        
        return self.test_results
    
    def _check_prerequisites(self):
        """前提条件チェック"""
        print("🔍 前提条件チェック中...")
        
        if not IMPORTS_SUCCESSFUL:
            print("❌ 必要なモジュールのインポートに失敗しました")
            return False
        
        # 必要なディレクトリの存在確認
        required_dirs = [
            Path("D:/setsuna_bot/data") if os.name == 'nt' else Path("/mnt/d/setsuna_bot/data"),
            Path("D:/setsuna_bot/youtube_knowledge_system/data") if os.name == 'nt' else Path("/mnt/d/setsuna_bot/youtube_knowledge_system/data")
        ]
        
        for directory in required_dirs:
            if not directory.exists():
                print(f"⚠️ 必要なディレクトリが見つかりません: {directory}")
                # ディレクトリを作成
                directory.mkdir(parents=True, exist_ok=True)
                print(f"✅ ディレクトリを作成しました: {directory}")
        
        print("✅ 前提条件チェック完了")
        return True
    
    def _test_phase_2d(self):
        """Phase 2D テスト"""
        results = {
            "conversation_history_analyzer": {},
            "user_interest_tracker": {},
            "preference_evolution_engine": {}
        }
        
        try:
            # 会話履歴分析システムテスト
            print("  📈 会話履歴分析システム...")
            analyzer = ConversationHistoryAnalyzer()
            self.systems["analyzer"] = analyzer
            
            # データ読み込みテスト
            analyzer._load_conversation_data()
            results["conversation_history_analyzer"] = {
                "initialization": "success",
                "data_loaded": True,
                "multi_turn_data_size": len(analyzer.multi_turn_data),
                "video_conversation_data_size": len(analyzer.video_conversation_data)
            }
            
            print("    ✅ 会話履歴分析システム初期化成功")
            
        except Exception as e:
            print(f"    ❌ 会話履歴分析システムエラー: {e}")
            results["conversation_history_analyzer"]["error"] = str(e)
        
        try:
            # ユーザー興味追跡システムテスト
            print("  🎯 ユーザー興味追跡システム...")
            interest_tracker = UserInterestTracker()
            self.systems["interest_tracker"] = interest_tracker
            
            # テスト用インタラクション
            detected_topics = interest_tracker.track_user_interaction(
                self.test_data["test_user_input"]
            )
            
            results["user_interest_tracker"] = {
                "initialization": "success",
                "interaction_tracking": "success",
                "detected_topics": detected_topics,
                "interest_metrics_count": len(interest_tracker.interest_metrics)
            }
            
            print("    ✅ ユーザー興味追跡システム動作確認完了")
            
        except Exception as e:
            print(f"    ❌ ユーザー興味追跡システムエラー: {e}")
            results["user_interest_tracker"]["error"] = str(e)
        
        try:
            # 好み進化エンジンテスト
            print("  🔮 好み進化エンジン...")
            evolution_engine = PreferenceEvolutionEngine()
            self.systems["evolution_engine"] = evolution_engine
            
            # 好み進化分析テスト
            evolutions = evolution_engine.analyze_preference_evolution()
            
            results["preference_evolution_engine"] = {
                "initialization": "success",
                "evolution_analysis": "success",
                "detected_evolutions": len(evolutions),
                "emerging_interests_count": len(evolution_engine.emerging_interests)
            }
            
            print("    ✅ 好み進化エンジン動作確認完了")
            
        except Exception as e:
            print(f"    ❌ 好み進化エンジンエラー: {e}")
            results["preference_evolution_engine"]["error"] = str(e)
        
        return results
    
    def _test_phase_2e(self):
        """Phase 2E テスト"""
        results = {
            "real_time_knowledge_updater": {},
            "incremental_learning_engine": {},
            "knowledge_validation_system": {}
        }
        
        try:
            # リアルタイム知識更新システムテスト
            print("  🔄 リアルタイム知識更新システム...")
            knowledge_updater = RealTimeKnowledgeUpdater()
            self.systems["knowledge_updater"] = knowledge_updater
            
            # 新情報処理テスト
            new_info = NewInformation(**self.test_data["test_new_information"])
            detected_info = knowledge_updater.process_user_input(
                self.test_data["test_user_input"]
            )
            
            results["real_time_knowledge_updater"] = {
                "initialization": "success",
                "information_processing": "success",
                "detected_info_count": len(detected_info),
                "new_information_count": len(knowledge_updater.new_information)
            }
            
            print("    ✅ リアルタイム知識更新システム動作確認完了")
            
        except Exception as e:
            print(f"    ❌ リアルタイム知識更新システムエラー: {e}")
            results["real_time_knowledge_updater"]["error"] = str(e)
        
        try:
            # 増分学習エンジンテスト
            print("  📚 増分学習エンジン...")
            learning_engine = IncrementalLearningEngine()
            self.systems["learning_engine"] = learning_engine
            
            # 学習セッション開始
            session_id = learning_engine.start_learning_session("test")
            
            # テスト用知識更新
            test_update = KnowledgeUpdate(**self.test_data["test_knowledge_update"])
            processing_results = learning_engine.process_knowledge_updates([test_update])
            
            # セッション終了
            session_stats = learning_engine.end_learning_session()
            
            results["incremental_learning_engine"] = {
                "initialization": "success",
                "session_management": "success",
                "updates_processed": processing_results["processed_updates"],
                "successful_integrations": processing_results["successful_integrations"],
                "session_id": session_id
            }
            
            print("    ✅ 増分学習エンジン動作確認完了")
            
        except Exception as e:
            print(f"    ❌ 増分学習エンジンエラー: {e}")
            results["incremental_learning_engine"]["error"] = str(e)
        
        try:
            # 知識検証システムテスト
            print("  ✅ 知識検証システム...")
            validation_system = KnowledgeValidationSystem()
            self.systems["validation_system"] = validation_system
            
            # 新情報検証テスト
            new_info = NewInformation(**self.test_data["test_new_information"])
            validation_result = validation_system.validate_new_information(new_info)
            
            results["knowledge_validation_system"] = {
                "initialization": "success",
                "validation_execution": "success",
                "validation_score": validation_result.validation_score,
                "validation_passed": validation_result.passed,
                "confidence_level": validation_result.confidence_level
            }
            
            print("    ✅ 知識検証システム動作確認完了")
            
        except Exception as e:
            print(f"    ❌ 知識検証システムエラー: {e}")
            results["knowledge_validation_system"]["error"] = str(e)
        
        return results
    
    def _test_phase_2f(self):
        """Phase 2F テスト"""
        results = {
            "knowledge_quality_manager": {},
            "data_consistency_checker": {},
            "performance_monitor": {}
        }
        
        try:
            # 知識品質管理システムテスト
            print("  🎯 知識品質管理システム...")
            quality_manager = KnowledgeQualityManager()
            self.systems["quality_manager"] = quality_manager
            
            # 品質監視テスト
            monitoring_results = quality_manager.monitor_quality_continuously()
            quality_report = quality_manager.generate_quality_report()
            
            results["knowledge_quality_manager"] = {
                "initialization": "success",
                "quality_monitoring": "success",
                "monitored_entities": monitoring_results["monitored_entities"],
                "quality_alerts": monitoring_results["quality_alerts_generated"],
                "overall_quality_score": quality_report.overall_score
            }
            
            print("    ✅ 知識品質管理システム動作確認完了")
            
        except Exception as e:
            print(f"    ❌ 知識品質管理システムエラー: {e}")
            results["knowledge_quality_manager"]["error"] = str(e)
        
        try:
            # データ整合性チェックシステムテスト
            print("  🔍 データ整合性チェックシステム...")
            consistency_checker = DataConsistencyChecker()
            self.systems["consistency_checker"] = consistency_checker
            
            # 包括的整合性チェック
            integrity_report = consistency_checker.run_comprehensive_check()
            
            results["data_consistency_checker"] = {
                "initialization": "success",
                "integrity_check": "success",
                "files_checked": integrity_report.total_files_checked,
                "entities_checked": integrity_report.total_entities_checked,
                "issues_found": integrity_report.issues_found,
                "integrity_score": integrity_report.integrity_score
            }
            
            print("    ✅ データ整合性チェックシステム動作確認完了")
            
        except Exception as e:
            print(f"    ❌ データ整合性チェックシステムエラー: {e}")
            results["data_consistency_checker"]["error"] = str(e)
        
        try:
            # パフォーマンス監視システムテスト
            print("  ⚡ パフォーマンス監視システム...")
            performance_monitor = PerformanceMonitor()
            self.systems["performance_monitor"] = performance_monitor
            
            # システムスナップショット取得
            snapshot = performance_monitor._capture_system_snapshot()
            dashboard_data = performance_monitor.get_performance_dashboard()
            
            results["performance_monitor"] = {
                "initialization": "success",
                "snapshot_capture": "success",
                "cpu_usage": snapshot.cpu_usage,
                "memory_usage": snapshot.memory_usage,
                "dashboard_generation": "success"
            }
            
            print("    ✅ パフォーマンス監視システム動作確認完了")
            
        except Exception as e:
            print(f"    ❌ パフォーマンス監視システムエラー: {e}")
            results["performance_monitor"]["error"] = str(e)
        
        return results
    
    def _test_system_integration(self):
        """システム間統合テスト"""
        results = {
            "data_flow_test": {},
            "cross_system_communication": {},
            "end_to_end_workflow": {}
        }
        
        try:
            print("  🔗 データフローテスト...")
            
            # エンドツーエンドワークフローシミュレーション
            workflow_results = self._simulate_end_to_end_workflow()
            results["end_to_end_workflow"] = workflow_results
            
            print("    ✅ エンドツーエンドワークフロー完了")
            
        except Exception as e:
            print(f"    ❌ システム間統合テストエラー: {e}")
            results["integration_error"] = str(e)
        
        return results
    
    def _simulate_end_to_end_workflow(self):
        """エンドツーエンドワークフローシミュレーション"""
        workflow_results = {
            "steps_completed": 0,
            "total_steps": 7,
            "step_results": []
        }
        
        try:
            # Step 1: ユーザー入力処理
            if "interest_tracker" in self.systems:
                detected_topics = self.systems["interest_tracker"].track_user_interaction(
                    self.test_data["test_user_input"]
                )
                workflow_results["steps_completed"] += 1
                workflow_results["step_results"].append("ユーザー興味追跡完了")
            
            # Step 2: 新情報検出
            if "knowledge_updater" in self.systems:
                detected_info = self.systems["knowledge_updater"].process_user_input(
                    self.test_data["test_user_input"]
                )
                workflow_results["steps_completed"] += 1
                workflow_results["step_results"].append("新情報検出完了")
            
            # Step 3: 情報検証
            if "validation_system" in self.systems and detected_info:
                for info in detected_info:
                    validation_result = self.systems["validation_system"].validate_new_information(info)
                workflow_results["steps_completed"] += 1
                workflow_results["step_results"].append("情報検証完了")
            
            # Step 4: 学習統合
            if "learning_engine" in self.systems:
                session_id = self.systems["learning_engine"].start_learning_session("integration_test")
                workflow_results["steps_completed"] += 1
                workflow_results["step_results"].append("学習セッション開始完了")
            
            # Step 5: 好み進化分析
            if "evolution_engine" in self.systems:
                evolutions = self.systems["evolution_engine"].analyze_preference_evolution()
                workflow_results["steps_completed"] += 1
                workflow_results["step_results"].append("好み進化分析完了")
            
            # Step 6: 品質管理
            if "quality_manager" in self.systems:
                monitoring_results = self.systems["quality_manager"].monitor_quality_continuously()
                workflow_results["steps_completed"] += 1
                workflow_results["step_results"].append("品質監視完了")
            
            # Step 7: 整合性チェック
            if "consistency_checker" in self.systems:
                summary = self.systems["consistency_checker"].get_consistency_summary()
                workflow_results["steps_completed"] += 1
                workflow_results["step_results"].append("整合性チェック完了")
        
        except Exception as e:
            workflow_results["workflow_error"] = str(e)
        
        return workflow_results
    
    def _test_performance(self):
        """パフォーマンステスト"""
        results = {
            "system_response_times": {},
            "memory_usage": {},
            "error_rates": {}
        }
        
        try:
            # 各システムの応答時間測定
            for system_name, system in self.systems.items():
                start_time = time.time()
                
                # システム固有の軽量操作実行
                if hasattr(system, 'get_analytics') or hasattr(system, 'get_summary'):
                    try:
                        if hasattr(system, 'get_analytics'):
                            _ = system.get_analytics()
                        elif hasattr(system, 'get_summary'):
                            _ = system.get_summary()
                    except:
                        pass  # エラーは無視して時間のみ測定
                
                end_time = time.time()
                response_time = end_time - start_time
                
                results["system_response_times"][system_name] = response_time
            
            # 全体的なパフォーマンス評価
            if results["system_response_times"]:
                avg_response_time = sum(results["system_response_times"].values()) / len(results["system_response_times"])
                results["average_response_time"] = avg_response_time
                results["performance_grade"] = "good" if avg_response_time < 1.0 else "acceptable" if avg_response_time < 3.0 else "needs_improvement"
        
        except Exception as e:
            results["performance_test_error"] = str(e)
        
        return results
    
    def _generate_test_summary(self):
        """テストサマリー生成"""
        summary = {
            "overall_status": "unknown",
            "phase_results": {},
            "system_counts": {},
            "critical_issues": [],
            "recommendations": []
        }
        
        try:
            # フェーズ別結果集計
            phases = ["phase_2d_results", "phase_2e_results", "phase_2f_results"]
            total_systems = 0
            successful_systems = 0
            
            for phase in phases:
                if phase in self.test_results:
                    phase_data = self.test_results[phase]
                    phase_system_count = len(phase_data)
                    phase_success_count = len([s for s in phase_data.values() if isinstance(s, dict) and "error" not in s])
                    
                    total_systems += phase_system_count
                    successful_systems += phase_success_count
                    
                    summary["phase_results"][phase] = {
                        "total_systems": phase_system_count,
                        "successful_systems": phase_success_count,
                        "success_rate": phase_success_count / phase_system_count if phase_system_count > 0 else 0
                    }
            
            # 全体成功率
            overall_success_rate = successful_systems / total_systems if total_systems > 0 else 0
            
            if overall_success_rate >= 0.9:
                summary["overall_status"] = "excellent"
            elif overall_success_rate >= 0.7:
                summary["overall_status"] = "good"
            elif overall_success_rate >= 0.5:
                summary["overall_status"] = "acceptable"
            else:
                summary["overall_status"] = "needs_attention"
            
            summary["system_counts"] = {
                "total_systems": total_systems,
                "successful_systems": successful_systems,
                "success_rate": overall_success_rate
            }
            
            # 推奨事項生成
            if overall_success_rate < 1.0:
                summary["recommendations"].append("一部のシステムでエラーが発生しました。ログを確認して修正してください。")
            
            if summary["overall_status"] == "excellent":
                summary["recommendations"].append("すべてのシステムが正常に動作しています。定期的な監視を継続してください。")
            
        except Exception as e:
            summary["summary_generation_error"] = str(e)
        
        return summary
    
    def _save_test_results(self):
        """テスト結果保存"""
        try:
            test_results_path = Path("D:/setsuna_bot/test") if os.name == 'nt' else Path("/mnt/d/setsuna_bot/test")
            test_results_path.mkdir(parents=True, exist_ok=True)
            
            results_file = test_results_path / f"priority2_integration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            
            print(f"\n📄 テスト結果を保存しました: {results_file}")
            
        except Exception as e:
            print(f"⚠️ テスト結果の保存に失敗: {e}")
    
    def print_test_summary(self):
        """テスト結果サマリー表示"""
        print("\n" + "=" * 60)
        print("🎯 Priority 2統合テスト結果サマリー")
        print("=" * 60)
        
        if "test_summary" in self.test_results:
            summary = self.test_results["test_summary"]
            
            print(f"📊 全体ステータス: {summary.get('overall_status', 'unknown').upper()}")
            
            if "system_counts" in summary:
                counts = summary["system_counts"]
                print(f"✅ 成功システム: {counts.get('successful_systems', 0)}/{counts.get('total_systems', 0)} ({counts.get('success_rate', 0):.1%})")
            
            # フェーズ別結果
            if "phase_results" in summary:
                print("\n📈 フェーズ別結果:")
                for phase, result in summary["phase_results"].items():
                    phase_name = {
                        "phase_2d_results": "Phase 2D (会話履歴分析)",
                        "phase_2e_results": "Phase 2E (リアルタイム知識更新)",
                        "phase_2f_results": "Phase 2F (品質管理)"
                    }.get(phase, phase)
                    
                    print(f"  {phase_name}: {result.get('successful_systems', 0)}/{result.get('total_systems', 0)} ({result.get('success_rate', 0):.1%})")
            
            # 推奨事項
            if "recommendations" in summary and summary["recommendations"]:
                print("\n💡 推奨事項:")
                for recommendation in summary["recommendations"]:
                    print(f"  • {recommendation}")
        
        # パフォーマンス結果
        if "performance_results" in self.test_results:
            perf = self.test_results["performance_results"]
            if "average_response_time" in perf:
                print(f"\n⚡ 平均応答時間: {perf['average_response_time']:.3f}秒")
                print(f"   パフォーマンス評価: {perf.get('performance_grade', 'unknown').upper()}")
        
        print("\n🎉 Priority 2統合テスト完了!")
        print("=" * 60)

def main():
    """メイン実行"""
    print("🚀 Priority 2 会話知識強化システム 統合テスト")
    print(f"📅 実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # テスト実行
    test_runner = Priority2IntegrationTest()
    results = test_runner.run_comprehensive_test()
    
    # 結果表示
    test_runner.print_test_summary()
    
    return results

if __name__ == "__main__":
    main()