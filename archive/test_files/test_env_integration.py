#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
環境変数統合テスト
ConfigManager統合後の動作確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class EnvIntegrationTest:
    """環境変数統合テストクラス"""
    
    def __init__(self):
        """初期化"""
        print("=== 環境変数統合テスト ===")
        self.test_results = {
            "config_manager_test": False,
            "learning_engine_env_test": False,
            "preprocessing_engine_env_test": False,
            "proposal_engine_env_test": False,
            "integration_system_env_test": False,
            "gui_env_test": False,
            "dotenv_integration_test": False
        }
    
    def run_env_integration_tests(self):
        """環境変数統合テスト実行"""
        print("\n🔧 環境変数統合テスト開始:")
        
        try:
            # 1. ConfigManagerテスト
            self._test_config_manager()
            
            # 2. 各コンポーネントの環境変数統合テスト
            self._test_learning_engine_env()
            self._test_preprocessing_engine_env()
            self._test_proposal_engine_env()
            self._test_integration_system_env()
            
            # 3. GUI環境変数統合テスト
            self._test_gui_env()
            
            # 4. python-dotenv統合テスト
            self._test_dotenv_integration()
            
            # 結果サマリー
            self._print_test_summary()
            
        except Exception as e:
            print(f"❌ 環境変数統合テスト失敗: {e}")
            raise
    
    def _test_config_manager(self):
        """ConfigManagerテスト"""
        print("\n⚙️ 1. ConfigManagerテスト:")
        
        try:
            from core.config_manager import ConfigManager, get_config_manager
            
            # ConfigManager直接初期化
            config = ConfigManager()
            
            # 設定取得テスト
            openai_key = config.get_openai_key()
            voicevox_url = config.get_voicevox_url()
            
            print(f"✅ OpenAI API Key: {'設定済み' if openai_key else '未設定'}")
            print(f"✅ VOICEVOX URL: {voicevox_url}")
            
            # 設定検証結果
            validation_result = config.get_validation_result()
            print(f"✅ 設定検証: {'成功' if validation_result.is_valid else '失敗'}")
            
            if validation_result.missing_keys:
                print(f"  不足キー: {validation_result.missing_keys}")
            
            if validation_result.warnings:
                print(f"  警告: {validation_result.warnings}")
            
            # グローバルインスタンステスト
            global_config = get_config_manager()
            global_key = global_config.get_openai_key()
            print(f"✅ グローバル設定: {'設定済み' if global_key else '未設定'}")
            
            # 設定サマリー
            summary = config.get_config_summary()
            print(f"✅ 設定サマリー取得: {'成功' if summary else '失敗'}")
            
            self.test_results["config_manager_test"] = validation_result.is_valid and bool(summary)
            
        except Exception as e:
            print(f"❌ ConfigManagerテスト失敗: {e}")
    
    def _test_learning_engine_env(self):
        """ActivityLearningEngine環境変数テスト"""
        print("\n📚 2. ActivityLearningEngine環境変数テスト:")
        
        try:
            from core.activity_learning_engine import ActivityLearningEngine
            
            # インスタンス作成
            engine = ActivityLearningEngine()
            
            # API設定確認
            api_configured = engine.openai_client is not None
            print(f"✅ OpenAI API設定: {'成功' if api_configured else '失敗'}")
            
            # 前処理エンジン確認
            preprocessing_configured = engine.preprocessing_engine.openai_client is not None
            print(f"✅ 前処理エンジンAPI設定: {'成功' if preprocessing_configured else '失敗'}")
            
            # 段階的分析設定テスト
            config = engine.get_staged_analysis_config()
            print(f"✅ 段階的分析設定: {'取得成功' if config else '失敗'}")
            
            self.test_results["learning_engine_env_test"] = api_configured and preprocessing_configured
            
        except Exception as e:
            print(f"❌ ActivityLearningEngine環境変数テスト失敗: {e}")
    
    def _test_preprocessing_engine_env(self):
        """PreprocessingEngine環境変数テスト"""
        print("\n🔄 3. PreprocessingEngine環境変数テスト:")
        
        try:
            from core.preprocessing_engine import PreProcessingEngine
            
            # インスタンス作成
            engine = PreProcessingEngine()
            
            # API設定確認
            api_configured = engine.openai_client is not None
            print(f"✅ OpenAI API設定: {'成功' if api_configured else '失敗'}")
            
            # 統計情報取得
            stats = engine.get_statistics()
            print(f"✅ 統計情報取得: {'成功' if stats else '失敗'}")
            
            # 設定確認
            print(f"✅ GPT-3.5設定: {engine.gpt35_config['model']}")
            
            self.test_results["preprocessing_engine_env_test"] = api_configured
            
        except Exception as e:
            print(f"❌ PreprocessingEngine環境変数テスト失敗: {e}")
    
    def _test_proposal_engine_env(self):
        """ActivityProposalEngine環境変数テスト"""
        print("\n💡 4. ActivityProposalEngine環境変数テスト:")
        
        try:
            from core.activity_proposal_engine import ActivityProposalEngine
            
            # インスタンス作成
            engine = ActivityProposalEngine()
            
            # API設定確認
            api_configured = engine.openai_client is not None
            print(f"✅ OpenAI API設定: {'成功' if api_configured else '失敗'}")
            
            # 既存提案読み込み確認
            proposal_count = len(engine.generated_proposals)
            print(f"✅ 既存提案読み込み: {proposal_count}件")
            
            # 統計情報取得
            stats = engine.get_proposal_statistics()
            print(f"✅ 統計情報取得: {'成功' if stats else '失敗'}")
            
            self.test_results["proposal_engine_env_test"] = api_configured
            
        except Exception as e:
            print(f"❌ ActivityProposalEngine環境変数テスト失敗: {e}")
    
    def _test_integration_system_env(self):
        """KnowledgeIntegrationSystem環境変数テスト"""
        print("\n🧠 5. KnowledgeIntegrationSystem環境変数テスト:")
        
        try:
            from core.knowledge_integration_system import KnowledgeIntegrationSystem
            
            # インスタンス作成
            system = KnowledgeIntegrationSystem()
            
            # API設定確認
            api_configured = system.openai_client is not None
            print(f"✅ OpenAI API設定: {'成功' if api_configured else '失敗'}")
            
            # 既存統合知識確認
            integration_count = len(system.integrated_knowledge)
            print(f"✅ 統合知識読み込み: {integration_count}件")
            
            # 知識グラフ確認
            graph_nodes = system.knowledge_graph.number_of_nodes()
            print(f"✅ 知識グラフ: {graph_nodes}ノード")
            
            self.test_results["integration_system_env_test"] = api_configured
            
        except Exception as e:
            print(f"❌ KnowledgeIntegrationSystem環境変数テスト失敗: {e}")
    
    def _test_gui_env(self):
        """GUI環境変数テスト"""
        print("\n🖥️ 6. GUI環境変数テスト:")
        
        try:
            # GUI基本モジュールインポート
            from gui.learning_session_gui import LearningSessionGUI
            print("✅ GUI モジュールインポート成功")
            
            # ConfigManager統合確認
            from core.config_manager import get_config_manager
            config = get_config_manager()
            
            # 設定状況確認
            config_summary = config.get_config_summary()
            print(f"✅ 設定確認: OpenAI {'設定済み' if config_summary['openai_configured'] else '未設定'}")
            print(f"✅ VOICEVOX URL: {config_summary.get('voicevox_url', 'N/A')}")
            
            # 個別コンポーネント確認は時間がかかるため省略
            print("✅ GUI統合準備完了")
            
            self.test_results["gui_env_test"] = config_summary['openai_configured']
            
        except Exception as e:
            print(f"❌ GUI環境変数テスト失敗: {e}")
    
    def _test_dotenv_integration(self):
        """python-dotenv統合テスト"""
        print("\n📋 7. python-dotenv統合テスト:")
        
        try:
            # .envファイル存在確認
            env_path = Path(__file__).parent / ".env"
            env_exists = env_path.exists()
            print(f"✅ .envファイル: {'存在' if env_exists else '不存在'}")
            
            # python-dotenv可用性確認
            try:
                from dotenv import load_dotenv
                dotenv_available = True
                print("✅ python-dotenv: 利用可能")
            except ImportError:
                dotenv_available = False
                print("❌ python-dotenv: 未インストール")
            
            # 環境変数読み込みテスト
            if dotenv_available and env_exists:
                load_dotenv(env_path)
                openai_key = os.getenv('OPENAI_API_KEY')
                print(f"✅ 環境変数読み込み: {'成功' if openai_key else '失敗'}")
                
                # 他の設定確認
                voicevox_url = os.getenv('VOICEVOX_URL')
                print(f"✅ VOICEVOX設定: {voicevox_url if voicevox_url else 'デフォルト'}")
            
            self.test_results["dotenv_integration_test"] = dotenv_available and env_exists
            
        except Exception as e:
            print(f"❌ python-dotenv統合テスト失敗: {e}")
    
    def _print_test_summary(self):
        """テスト結果サマリー表示"""
        print("\n" + "="*70)
        print("📊 環境変数統合テスト 結果サマリー")
        print("="*70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        test_names = {
            "config_manager_test": "ConfigManagerテスト",
            "learning_engine_env_test": "ActivityLearningEngine環境変数テスト",
            "preprocessing_engine_env_test": "PreprocessingEngine環境変数テスト",
            "proposal_engine_env_test": "ActivityProposalEngine環境変数テスト",
            "integration_system_env_test": "KnowledgeIntegrationSystem環境変数テスト",
            "gui_env_test": "GUI環境変数テスト",
            "dotenv_integration_test": "python-dotenv統合テスト"
        }
        
        for test_key, result in self.test_results.items():
            test_name = test_names.get(test_key, test_key)
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:50}: {status}")
        
        print("-" * 70)
        print(f"総合結果: {passed_tests}/{total_tests} テスト通過")
        
        if passed_tests == total_tests:
            print("🎉 環境変数統合が完全成功しました！")
            print("全コンポーネントが.envファイルから設定を読み込めています。")
            
            # 成功効果の表示
            print("\n💡 実装効果:")
            print("  ✅ .envファイルからの自動設定読み込み")
            print("  ✅ 毎回のCLI環境変数設定が不要")
            print("  ✅ 設定管理の一元化")
            print("  ✅ 詳細なエラーハンドリング")
            print("  ✅ 統一的な設定検証")
            
            print("\n🚀 次のステップ:")
            print("  - GUI起動: python gui/learning_session_gui.py")
            print("  - API Key確認ボタンで設定状況確認")
            print("  - 小規模学習セッションでの動作確認")
            
        elif passed_tests >= total_tests * 0.8:
            print("⚠️ 環境変数統合が部分的に成功しました。")
            print("基本機能は動作していますが、一部に改善が必要です。")
            
        else:
            print("❌ 環境変数統合が失敗しました。")
            print("複数のコンポーネントで問題があり、修正が必要です。")
            print("\n🔧 対処方法:")
            print("  - pip install python-dotenv")
            print("  - .envファイルでOPENAI_API_KEY設定確認")
            print("  - 依存関係の確認")
        
        print("="*70)


def main():
    """メイン関数"""
    env_test = EnvIntegrationTest()
    
    try:
        env_test.run_env_integration_tests()
        
    except Exception as e:
        print(f"\n❌ テスト中断: {e}")


if __name__ == "__main__":
    main()