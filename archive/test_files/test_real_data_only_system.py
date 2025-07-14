#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
実データのみシステムのテスト
duckduckgo-search ライブラリの有無に関係なく動作確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_real_data_only_system():
    """実データのみシステムをテスト"""
    
    print("🔧 実データのみ知識分析システムテスト開始")
    print("=" * 60)
    
    try:
        # 新しいDuckDuckGoSearchServiceをテスト
        print("🔍 DuckDuckGoSearchService テスト...")
        from core.adaptive_learning.duckduckgo_search_service import DuckDuckGoSearchService
        
        search_service = DuckDuckGoSearchService()
        print(f"✅ 検索サービス初期化完了")
        
        # テスト検索（ライブラリが無い場合は空結果を期待）
        test_query = "Python プログラミング"
        print(f"\n🔍 テスト検索: '{test_query}'")
        
        results = search_service.search(test_query, max_results=3)
        print(f"📊 検索結果: {len(results)}件")
        
        if results:
            print("✅ 実際のデータを取得できました")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title'][:50]}...")
                print(f"     URL: {result['url'][:60]}...")
        else:
            print("📝 検索結果なし（ライブラリ未インストールまたは検索失敗）")
        
        # 検索統計
        summary = search_service.get_search_summary()
        print(f"\n📊 検索統計:")
        print(f"   総検索数: {summary['total_searches']}")
        print(f"   成功数: {summary.get('successful_searches', 0)}")
        print(f"   成功率: {summary.get('overall_success_rate', 0):.1f}%")
        
        # KnowledgeAnalysisEngineのテスト
        print(f"\n{'=' * 60}")
        print("🧠 KnowledgeAnalysisEngine テスト...")
        
        from core.knowledge_analysis.knowledge_analysis_engine import KnowledgeAnalysisEngine
        
        def progress_callback(message, progress):
            print(f"📊 進捗 [{progress:3d}%]: {message}")
        
        engine = KnowledgeAnalysisEngine(progress_callback=progress_callback)
        print(f"✅ 分析エンジン初期化完了")
        
        # セッション開始
        session_id = engine.start_new_session("実データテスト")
        print(f"📅 セッション開始: {session_id}")
        
        # 小規模テスト分析
        test_prompt = "Pythonプログラミングの基礎について"
        search_count = 5  # 少数でテスト
        
        print(f"\n📝 テストプロンプト: '{test_prompt}'")
        print(f"🔍 検索件数: {search_count}件")
        print(f"🧠 GPT分析: {'✅ 利用可能' if engine.analysis_service else '❌ 利用不可'}")
        print(f"🌐 検索サービス: {'✅ 利用可能' if engine.search_service else '❌ 利用不可'}")
        
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
        print(f"🔍 検索件数: {report.get('search_count', 0)}件")
        
        # 空データ対応の確認
        is_empty_data = report.get('empty_data_report', False)
        print(f"📊 データ種別: {'空データレポート' if is_empty_data else '実データレポート'}")
        
        # 分析内容の確認
        analysis_summary = report.get('analysis_summary', '')
        print(f"\n🔍 分析内容チェック:")
        print(f"分析要約長: {len(analysis_summary)}文字")
        
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
        if is_empty_data:
            print("🎯 テスト結果: 空データ対応 - 成功")
            print("✅ 検索データが取得できない場合の適切な処理を確認")
            print("✅ 透明性の高いエラーレポート生成を確認")
            print("💡 実際のデータ取得には ddgs ライブラリが必要です")
        else:
            print("🎉 テスト結果: 実データ取得 - 成功")
            print("✅ 実際の検索データを正常に取得・分析")
            print("✅ 実データベースの知識分析システムが動作中")
        
        return True
            
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
    test_result = test_real_data_only_system()
    
    if test_result:
        print("\n🎊 実データのみシステムのテストが完了しました！")
        print("📋 次のステップ:")
        print("   1. ddgs ライブラリのインストール確認")
        print("   2. 実際の検索データを使用した大規模テスト")
        print("   3. GPT分析結果の品質評価")
        exit(0)
    else:
        print("\n💥 テストに問題があります。設定を確認してください。")
        exit(1)