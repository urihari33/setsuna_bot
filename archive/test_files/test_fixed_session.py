#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正済み学習セッションテスト
モック検索サービス統合後の動作確認
"""

import sys
import os
import time
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_fixed_session():
    """修正済みセッションテスト"""
    print("=== 修正済み学習セッションテスト ===")
    
    try:
        from core.activity_learning_engine import ActivityLearningEngine
        
        # エンジン初期化
        engine = ActivityLearningEngine()
        
        # テストセッション作成
        session_id = engine.create_session(
            theme="活動方針用資料",
            learning_type="概要", 
            depth_level=3,
            time_limit=60,  # 1分間
            budget_limit=1.0,
            tags=["修正テスト", "モック検索"]
        )
        
        print(f"✅ テストセッション作成: {session_id}")
        
        # セッション開始
        success = engine.start_session(session_id)
        
        if success:
            print("✅ セッション開始成功")
            
            # 60秒間待機して完了を確認
            print("📊 セッション実行中...")
            
            for i in range(12):  # 5秒間隔で12回チェック（60秒）
                time.sleep(5)
                
                status = engine.get_session_status(session_id)
                if status:
                    print(f"  [{i+1}/12] {status['status']} - {status['current_phase']}")
                    print(f"    収集: {status['progress']['collected_items']}件")
                    print(f"    処理: {status['progress']['processed_items']}件")
                    print(f"    コスト: ${status['progress']['current_cost']:.2f}")
                    print(f"    経過時間: {status['progress']['time_elapsed']:.0f}秒")
                    
                    if status['status'] == 'completed':
                        print("🎉 セッション完了!")
                        break
                    elif status['status'] == 'error':
                        print("❌ セッションエラー")
                        break
                else:
                    print(f"  [{i+1}/12] セッション状態取得失敗")
            
            # 最終状態確認
            final_status = engine.get_session_status(session_id)
            if final_status:
                print(f"\n📊 最終結果:")
                print(f"  ステータス: {final_status['status']}")
                print(f"  収集アイテム: {final_status['progress']['collected_items']}件")
                print(f"  処理アイテム: {final_status['progress']['processed_items']}件")
                print(f"  総コスト: ${final_status['progress']['current_cost']:.2f}")
                print(f"  経過時間: {final_status['progress']['time_elapsed']:.0f}秒")
                
                return final_status['progress']['collected_items'] > 0
        
        return False
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        return False

def run_analysis():
    """分析実行"""
    print("\n=== セッション結果分析 ===")
    
    try:
        from debug_session_analyzer import DebugSessionAnalyzer
        
        # 分析ツール初期化
        analyzer = DebugSessionAnalyzer()
        
        # 最新セッション分析
        result = analyzer.analyze_latest_session()
        
        if result:
            print(f"📊 分析結果:")
            print(f"  セッションID: {result.session_id}")
            print(f"  ステータス: {result.status}")
            print(f"  検出問題: {len(result.issues)}件")
            print(f"  推奨事項: {len(result.recommendations)}件")
            
            # パフォーマンス指標
            metrics = result.performance_metrics
            print(f"  収集アイテム: {metrics.get('collected_items', 0)}件")
            print(f"  フィルタリング効率: {metrics.get('filtering_efficiency', 0):.1%}")
            print(f"  実行時間: {metrics.get('total_duration', 0):.1f}秒")
            
            # 問題があれば表示
            if result.issues:
                print(f"\n🚨 検出された問題:")
                for i, issue in enumerate(result.issues[:3], 1):
                    print(f"  {i}. {issue}")
            
            return result.performance_metrics.get('collected_items', 0) > 0
        
        return False
        
    except Exception as e:
        print(f"❌ 分析エラー: {e}")
        return False

def main():
    """メイン関数"""
    print("🚀 修正済み学習セッション統合テスト開始")
    print("=" * 60)
    
    # セッション実行テスト
    session_success = test_fixed_session()
    
    # 分析実行
    analysis_success = run_analysis()
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 統合テスト結果")
    print("=" * 60)
    
    print(f"セッション実行: {'✅ 成功' if session_success else '❌ 失敗'}")
    print(f"結果分析: {'✅ 成功' if analysis_success else '❌ 失敗'}")
    
    if session_success and analysis_success:
        print("\n🎉 修正が完全に成功しました！")
        print("学習セッションが正常にデータを収集し、処理できています。")
        print("\n💡 修正のポイント:")
        print("  ✅ DuckDuckGo API問題を特定")
        print("  ✅ モック検索サービスを実装")
        print("  ✅ フォールバック機能を追加")
        print("  ✅ 詳細デバッグログを実装")
        print("  ✅ 問題分析ツールを作成")
        
        print("\n🚀 次のステップ:")
        print("  - 実際のGUIから学習セッションを実行")
        print("  - より長時間のセッションでの動作確認")
        print("  - 他の代替検索エンジンの実装検討")
        
    else:
        print("\n⚠️ 一部の機能で問題があります")
        print("詳細な分析を実行してください")
    
    print("=" * 60)

if __name__ == "__main__":
    main()