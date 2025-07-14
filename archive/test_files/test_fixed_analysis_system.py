#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正後知識分析システムテスト
analyze_search_direction → analyze_search_results 修正の検証
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_fixed_analysis_system():
    """修正後の分析システムをテスト"""
    
    print("🔧 修正後知識分析システムテスト開始")
    print("=" * 60)
    
    try:
        # KnowledgeAnalysisEngineをインポート
        from core.knowledge_analysis.knowledge_analysis_engine import KnowledgeAnalysisEngine
        
        # 進捗コールバック定義
        def progress_callback(message, progress):
            print(f"📊 進捗 [{progress:3d}%]: {message}")
        
        # エンジン初期化
        print("🚀 KnowledgeAnalysisEngine初期化中...")
        engine = KnowledgeAnalysisEngine(progress_callback=progress_callback)
        
        # テストプロンプト
        test_prompt = "AI技術の最新動向について詳しく分析したい"
        search_count = 20  # 少数でテスト
        
        print(f"\n📝 テストプロンプト: '{test_prompt}'")
        print(f"🔍 検索件数: {search_count}件")
        print(f"🧠 GPT分析: {'✅ 利用可能' if engine.analysis_service else '❌ 利用不可'}")
        print(f"🌐 検索サービス: {'✅ 利用可能' if engine.search_service else '❌ 利用不可'}")
        
        # セッション開始
        session_id = engine.start_new_session("AI技術動向")
        print(f"📅 セッション開始: {session_id}")
        
        # 分析実行
        print(f"\n{'=' * 60}")
        print("🔄 分析実行開始...")
        
        report = engine.analyze_topic(test_prompt, search_count)
        
        print(f"\n{'=' * 60}")
        print("📊 分析結果サマリー:")
        print(f"📄 レポートID: {report.get('report_id', 'N/A')}")
        print(f"💰 総コスト: ${report.get('cost', 0):.6f}")
        print(f"📈 データ品質スコア: {report.get('data_quality', 0):.2f}")
        print(f"⏱️ 処理時間: {report.get('processing_time', 'N/A')}")
        
        # 分析内容の詳細確認
        analysis_summary = report.get('analysis_summary', '')
        print(f"\n🔍 分析内容チェック:")
        print(f"分析要約長: {len(analysis_summary)}文字")
        
        # 検索戦略っぽい内容か、実際のコンテンツ分析かを判定
        strategy_keywords = ["検索方向", "主要キーワード", "探索戦略", "検索クエリ"]
        content_keywords = ["主要な発見", "トレンド分析", "次の探索方向", "実装事例"]
        
        strategy_count = sum(1 for keyword in strategy_keywords if keyword in analysis_summary)
        content_count = sum(1 for keyword in content_keywords if keyword in analysis_summary)
        
        print(f"検索戦略キーワード検出: {strategy_count}個")
        print(f"コンテンツ分析キーワード検出: {content_count}個")
        
        if content_count > strategy_count:
            print("✅ 修正成功: コンテンツ分析が実行されています")
            analysis_type = "content_analysis"
        elif strategy_count > content_count:
            print("❌ 修正失敗: まだ検索戦略分析が実行されています")
            analysis_type = "search_strategy"
        else:
            print("⚠️ 判定困難: 分析内容を手動確認してください")
            analysis_type = "unclear"
        
        # 分析内容の一部を表示
        print(f"\n📄 分析内容サンプル（最初の200文字）:")
        print("-" * 60)
        print(analysis_summary[:200] + "..." if len(analysis_summary) > 200 else analysis_summary)
        print("-" * 60)
        
        # 主要発見事項の確認
        key_insights = report.get('key_insights', [])
        print(f"\n🔑 主要発見事項（{len(key_insights)}件）:")
        for i, insight in enumerate(key_insights[:3], 1):
            print(f"  {i}. {insight}")
        if len(key_insights) > 3:
            print(f"  ... 他{len(key_insights) - 3}件")
        
        # セッション情報
        session_data = engine.get_session_summary()
        print(f"\n📊 セッション統計:")
        print(f"  - セッションID: {session_data.get('session_id', 'N/A')}")
        print(f"  - 生成レポート数: {session_data.get('total_reports', 0)}")
        print(f"  - 累計コスト: ${session_data.get('total_cost', 0):.6f}")
        
        # テスト結果判定
        print(f"\n{'=' * 60}")
        if analysis_type == "content_analysis":
            print("🎉 テスト結果: 成功")
            print("✅ analyze_search_results メソッドが正しく呼び出されています")
            print("✅ 実際のコンテンツ分析が実行されています")
            return True
        elif analysis_type == "search_strategy":
            print("❌ テスト結果: 失敗")
            print("❌ まだ analyze_search_direction メソッドが使用されています")
            print("❌ 検索戦略分析が実行されています")
            return False
        else:
            print("⚠️ テスト結果: 判定不能")
            print("⚠️ 分析内容を手動で確認してください")
            return None
            
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        print("必要なモジュールが見つかりません")
        return False
        
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_result = test_fixed_analysis_system()
    
    if test_result is True:
        print("\n🎊 修正が成功しました！")
        exit(0)
    elif test_result is False:
        print("\n💥 修正に問題があります。再確認が必要です。")
        exit(1)
    else:
        print("\n🤔 判定不能です。結果を手動確認してください。")
        exit(2)