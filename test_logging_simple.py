#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ログシステム簡単テスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logging_system import StructuredLogger

def test_basic_logging():
    """基本的なログ機能のテスト"""
    print("🧪 基本ログテスト開始")
    
    # ロガー初期化
    logger = StructuredLogger(log_level="INFO")
    
    try:
        # 基本ログテスト
        logger.info("test", "test_basic_logging", "テストメッセージ1")
        logger.warning("test", "test_basic_logging", "警告テスト")
        logger.error("test", "test_basic_logging", "エラーテスト")
        
        print("✅ ログ出力完了")
        
        # ログファイル確認
        log_dir = logger.log_dir
        log_files = list(log_dir.glob("*.log"))
        print(f"📁 ログファイル数: {len(log_files)}")
        
        if log_files:
            latest_log = log_files[0]
            print(f"📄 最新ログファイル: {latest_log}")
            
            # ファイル内容確認
            if latest_log.exists():
                with open(latest_log, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                print(f"📝 ログ行数: {len(lines)}")
        
        print("✅ 基本テスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # クリーンアップ
        logger.cleanup()

if __name__ == "__main__":
    test_basic_logging()