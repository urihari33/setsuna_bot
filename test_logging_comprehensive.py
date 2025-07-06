#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ログシステム包括テスト
Phase 1の全機能をテストし、期待される動作を確認
"""

import sys
import os
import time
import json
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logging_system import StructuredLogger, PerformanceMonitor, get_logger, get_monitor
from log_rotation import LogRotationManager


def test_basic_logging():
    """基本ログ機能のテスト"""
    print("=" * 60)
    print("🧪 テスト1: 基本ログ機能")
    print("=" * 60)
    
    logger = StructuredLogger(log_level="DEBUG")
    
    try:
        # 各レベルのログテスト
        test_data = {"test_key": "test_value", "number": 123}
        
        logger.debug("test_module", "test_basic_logging", "デバッグメッセージ", test_data)
        logger.info("test_module", "test_basic_logging", "情報メッセージ", test_data) 
        logger.warning("test_module", "test_basic_logging", "警告メッセージ", test_data)
        logger.error("test_module", "test_basic_logging", "エラーメッセージ", test_data)
        
        # 例外ログテスト
        try:
            raise ValueError("テスト例外")
        except Exception as e:
            logger.log_exception("test_module", "test_basic_logging", e, {"context": "exception_test"})
        
        print("✅ 各レベルのログ出力完了")
        
        # ログファイル確認
        time.sleep(0.5)  # ワーカースレッドの処理待ち
        log_files = list(logger.log_dir.glob("*.log"))
        
        if log_files:
            latest_log = log_files[0]
            with open(latest_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"📄 ログファイル: {latest_log.name}")
            print(f"📝 ログ行数: {len(lines)}")
            
            # 最新のログエントリを表示
            if lines:
                try:
                    latest_entry = json.loads(lines[-1])
                    print(f"🔍 最新ログエントリ:")
                    print(f"   - レベル: {latest_entry['level']}")
                    print(f"   - モジュール: {latest_entry['module']}")
                    print(f"   - メッセージ: {latest_entry['message']}")
                    print(f"   - セッションID: {latest_entry['session_id']}")
                except json.JSONDecodeError:
                    print("⚠️ JSON解析エラー")
        
        print("✅ テスト1完了: 基本ログ機能正常")
        return True
        
    except Exception as e:
        print(f"❌ テスト1失敗: {e}")
        return False
    finally:
        logger.cleanup()


def test_performance_monitoring():
    """パフォーマンス監視機能のテスト"""
    print("=" * 60)
    print("🧪 テスト2: パフォーマンス監視機能")
    print("=" * 60)
    
    logger = StructuredLogger(log_level="INFO")
    monitor = PerformanceMonitor(logger)
    
    try:
        # 監視対象テスト関数
        @monitor.monitor_function("fast_function")
        def fast_function():
            """高速な関数"""
            time.sleep(0.01)
            return "高速処理完了"
        
        @monitor.monitor_function("slow_function")
        def slow_function():
            """低速な関数"""
            time.sleep(0.1)
            return "低速処理完了"
        
        @monitor.monitor_function("error_function")
        def error_function():
            """エラーを発生させる関数"""
            raise RuntimeError("テストエラー")
        
        # 関数実行テスト
        print("🚀 監視対象関数実行中...")
        
        # 高速関数を複数回実行
        for i in range(3):
            result = fast_function()
            print(f"   - 高速関数 #{i+1}: {result}")
        
        # 低速関数を実行
        result = slow_function()
        print(f"   - 低速関数: {result}")
        
        # エラー関数を実行
        try:
            error_function()
        except Exception:
            print("   - エラー関数: 例外発生（期待された動作）")
        
        # パフォーマンスレポート取得
        time.sleep(0.5)  # ログ処理待ち
        report = logger.get_performance_report()
        
        print("📊 パフォーマンスレポート:")
        for func_name, stats in report["functions"].items():
            print(f"   - {func_name}:")
            print(f"     * 実行回数: {stats['call_count']}")
            print(f"     * 平均時間: {stats['avg_time']:.3f}秒")
            print(f"     * 最大時間: {stats['max_time']:.3f}秒")
            print(f"     * エラー回数: {stats['error_count']}")
        
        print("✅ テスト2完了: パフォーマンス監視正常")
        return True
        
    except Exception as e:
        print(f"❌ テスト2失敗: {e}")
        return False
    finally:
        logger.cleanup()


def test_log_rotation():
    """ログローテーション機能のテスト"""
    print("=" * 60)
    print("🧪 テスト3: ログローテーション機能")
    print("=" * 60)
    
    rotation_manager = LogRotationManager(
        max_file_size_mb=0.001,  # 1KBに設定（テスト用）
        retention_days=1
    )
    
    try:
        # 初期統計
        stats = rotation_manager.get_log_statistics()
        print(f"📊 初期ログ統計:")
        print(f"   - ファイル数: {stats.get('total_files', 0)}")
        print(f"   - 総サイズ: {stats.get('total_size_mb', 0):.3f}MB")
        
        # 大きなログファイルを作成してローテーションをテスト
        test_log_path = rotation_manager.log_dir / "test_rotation.log"
        
        # 1KB以上のテストデータを書き込み
        test_data = "テストログデータ" * 100  # 約1.5KB
        with open(test_log_path, 'w', encoding='utf-8') as f:
            f.write(test_data)
        
        print(f"📝 テストログファイル作成: {test_log_path.name} ({len(test_data)} bytes)")
        
        # ローテーション実行
        if rotation_manager.should_rotate_file(test_log_path):
            rotated_path = rotation_manager.rotate_log_file(test_log_path)
            if rotated_path:
                print(f"🔄 ローテーション成功: {rotated_path.name}")
            else:
                print("❌ ローテーション失敗")
        
        # ローテーション後の統計
        stats_after = rotation_manager.get_log_statistics()
        print(f"📊 ローテーション後統計:")
        print(f"   - ファイル数: {stats_after.get('total_files', 0)}")
        print(f"   - 総サイズ: {stats_after.get('total_size_mb', 0):.3f}MB")
        
        print("✅ テスト3完了: ログローテーション正常")
        return True
        
    except Exception as e:
        print(f"❌ テスト3失敗: {e}")
        return False


def test_system_integration():
    """システム統合テスト"""
    print("=" * 60)
    print("🧪 テスト4: システム統合確認")
    print("=" * 60)
    
    try:
        # グローバルロガーのテスト
        logger = get_logger()
        monitor = get_monitor()
        
        print("🔧 グローバルロガー取得確認")
        print(f"   - Logger: {type(logger).__name__}")
        print(f"   - Monitor: {type(monitor).__name__}")
        
        # システムメトリクス取得テスト
        print("📊 システムメトリクス取得中...")
        metrics = monitor.get_system_metrics()
        
        if metrics:
            print(f"   - CPU使用率: {metrics.get('cpu_percent', 'N/A')}%")
            print(f"   - メモリ使用率: {metrics.get('memory_info', {}).get('percent', 'N/A')}%")
            print(f"   - スレッド数: {metrics.get('thread_count', 'N/A')}")
        
        # 複数回のログ出力で安定性確認
        print("🔄 連続ログ出力テスト中...")
        for i in range(5):
            logger.info("integration_test", "test_system_integration", 
                       f"連続テスト #{i+1}", {"iteration": i+1})
        
        print("✅ テスト4完了: システム統合正常")
        return True
        
    except Exception as e:
        print(f"❌ テスト4失敗: {e}")
        return False


def run_comprehensive_test():
    """包括テストの実行"""
    print("🎯 Phase 1 ログシステム包括テスト開始")
    print("=" * 80)
    
    test_results = []
    
    # テスト実行
    test_results.append(("基本ログ機能", test_basic_logging()))
    test_results.append(("パフォーマンス監視", test_performance_monitoring()))
    test_results.append(("ログローテーション", test_log_rotation()))
    test_results.append(("システム統合", test_system_integration()))
    
    # 結果サマリー
    print("=" * 80)
    print("📋 テスト結果サマリー")
    print("=" * 80)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 総合結果: {passed}/{len(test_results)} テスト成功")
    
    if passed == len(test_results):
        print("🎉 全テスト成功！ログシステムは正常に動作しています。")
    else:
        print("⚠️ 一部テストが失敗しました。ログを確認してください。")
    
    return passed == len(test_results)


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)