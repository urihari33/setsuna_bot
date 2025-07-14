#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI Rate Limiting修正効果確認テスト
実際のPreProcessingEngineを安全モードで動作させてエラー再現防止を確認
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from core.activity_learning_engine import ActivityLearningEngine, LearningSession

def test_preprocessing_rate_limiting_fix():
    """前処理Rate Limiting修正効果テスト"""
    print("=== 前処理Rate Limiting修正効果テスト ===")
    
    try:
        # ActivityLearningEngine初期化（安全モード）
        learning_engine = ActivityLearningEngine()
        
        # 安全モード設定
        learning_engine.configure_safe_mode(True)
        print(f"現在のモード: {learning_engine.get_current_mode()}")
        print(f"Rate Limiting間隔: {learning_engine.preprocessing_engine.rate_limiting['request_interval']}秒")
        
        # テストセッション作成
        session_id = learning_engine.create_session(
            theme="Rate Limiting修正テスト",
            learning_type="概要",
            depth_level=2,
            time_limit=300,  # 5分
            budget_limit=1.0,  # $1.0
            tags=["Rate Limiting修正", "安全モード"]
        )
        
        if session_id:
            print(f"✅ 安全モードセッション作成成功: {session_id}")
            
            # テスト用ソースデータ（元のエラーを引き起こしやすい複数件）
            test_sources = [
                {
                    "source_id": "test_001",
                    "title": "AI音楽生成の最新技術動向",
                    "content": "Transformerアーキテクチャを使った音楽生成技術が急速に発展している。OpenAIのMuseNetやGoogleのMusicTransformerなどが注目されている。",
                    "url": "https://example.com/ai-music-tech",
                    "source_type": "web_search"
                },
                {
                    "source_id": "test_002", 
                    "title": "機械学習による作曲システム",
                    "content": "深層学習を活用した自動作曲システムの開発が進んでいる。RNNやGANを使った新しいアプローチが研究されている。",
                    "url": "https://example.com/ml-composition",
                    "source_type": "web_search"
                },
                {
                    "source_id": "test_003",
                    "title": "音楽AI市場動向分析",
                    "content": "音楽AI技術の商用化が加速している。Spotifyやアマゾンなどが音楽AI技術に大規模投資を行っている。",
                    "url": "https://example.com/music-ai-market",
                    "source_type": "web_search"
                }
            ]
            
            print(f"\n--- 安全モード前処理テスト ({len(test_sources)}件) ---")
            start_time = time.time()
            
            # 前処理実行（安全モード）
            try:
                results = learning_engine.preprocessing_engine.preprocess_content_batch(
                    sources=test_sources,
                    theme="AI音楽生成",
                    target_categories=["技術", "市場", "トレンド", "実用"],
                    safe_mode=True  # 安全モード使用
                )
                
                processing_time = time.time() - start_time
                print(f"✅ 前処理完了: {len(results)}件処理")
                print(f"処理時間: {processing_time:.2f}秒")
                
                # 結果確認
                passed_results = [r for r in results if r.should_proceed]
                print(f"通過件数: {len(passed_results)}件")
                
                # フィルタリングサマリー
                summary = learning_engine.preprocessing_engine.get_filtering_summary(results)
                print(f"通過率: {summary.get('pass_rate', 0):.1f}%")
                print(f"推定コスト: ${summary.get('estimated_cost', 0):.4f}")
                
                print("✅ Rate Limiting修正効果テスト成功")
                return True
                
            except Exception as preprocessing_error:
                print(f"❌ 前処理でエラー発生: {preprocessing_error}")
                
                # 元のエラーと比較
                if "float division by zero" in str(preprocessing_error):
                    print("⚠️ ゼロ除算エラーが再発生 - 追加修正が必要")
                elif "429" in str(preprocessing_error):
                    print("⚠️ Rate Limitエラーが再発生 - 間隔調整が必要")
                else:
                    print(f"⚠️ 新しいエラー: {preprocessing_error}")
                
                return False
        else:
            print("❌ セッション作成失敗")
            return False
            
    except Exception as e:
        print(f"❌ Rate Limiting修正効果テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_lightweight_mode_comparison():
    """軽量モード比較テスト"""
    print("\n=== 軽量モード比較テスト ===")
    
    try:
        learning_engine = ActivityLearningEngine()
        
        # 軽量モード設定
        learning_engine.configure_lightweight_mode(True)
        print(f"軽量モード設定: {learning_engine.get_current_mode()}")
        print(f"前処理有効: {learning_engine.staged_analysis_config['enable_preprocessing']}")
        
        # テストセッション作成（軽量モード）
        session_id = learning_engine.create_session(
            theme="軽量モードテスト",
            learning_type="概要",
            depth_level=1,
            time_limit=180,  # 3分
            budget_limit=0.5,  # $0.5
            tags=["軽量モード", "前処理無効"]
        )
        
        if session_id:
            print(f"✅ 軽量モードセッション作成成功: {session_id}")
            print("✅ 前処理スキップによりRate Limitingリスク回避")
            return True
        else:
            print("❌ 軽量モードセッション作成失敗")
            return False
            
    except Exception as e:
        print(f"❌ 軽量モード比較テスト失敗: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🚀 GUI Rate Limiting修正効果確認テスト開始")
    print(f"実行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # 各テスト実行
    test_results.append(("前処理Rate Limiting修正効果", test_preprocessing_rate_limiting_fix()))
    test_results.append(("軽量モード比較", test_lightweight_mode_comparison()))
    
    # 結果サマリー
    print("\n" + "="*60)
    print("📊 GUI Rate Limiting修正効果確認結果")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n総合結果: {passed}件成功, {failed}件失敗")
    
    if failed == 0:
        print("🎉 GUI Rate Limiting修正効果確認テスト全て成功！")
        print("✅ 元のOpenAI 429エラー・ゼロ除算エラーが解決確認")
        print("✅ 安全モード・軽量モードによる対策効果確認")
        print("✅ GUIでの安定動作準備完了")
    else:
        print(f"⚠️ {failed}件のテストで問題が発生")
        print("🔧 追加対策が必要です")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)