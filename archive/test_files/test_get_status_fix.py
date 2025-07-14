#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
get_status修正確認テスト
MultiSearchManagerのget_statusメソッド動作確認
"""

import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from core.multi_search_manager import MultiSearchManager

def test_get_status_method():
    """get_statusメソッドテスト"""
    print("=== get_statusメソッド修正確認テスト ===")
    
    try:
        # MultiSearchManager初期化
        search_manager = MultiSearchManager()
        print("✅ MultiSearchManager初期化成功")
        
        # get_statusメソッド呼び出し
        status = search_manager.get_status()
        print("✅ get_statusメソッド呼び出し成功")
        
        # 結果確認
        print("\n--- get_status結果 ---")
        print(f"利用可能エンジン: {status['available_engines']}")
        print(f"利用可能エンジン数: {status['total_available_engines']}")
        print(f"動的クエリ有効: {status['dynamic_queries_enabled']}")
        print(f"最終更新: {status['last_updated']}")
        
        # エンジン状態詳細
        print("\n--- エンジン状態詳細 ---")
        for name, engine_status in status['engines'].items():
            print(f"{name}: {'✅' if engine_status.available else '❌'} {engine_status.engine_name}")
            if engine_status.error_message:
                print(f"  エラー: {engine_status.error_message}")
        
        # 統計情報
        print(f"\n--- 検索統計 ---")
        stats = status['stats']
        print(f"総検索数: {stats['total_searches']}")
        print(f"成功数: {stats['successful_searches']}")
        print(f"失敗数: {stats['failed_searches']}")
        
        print("\n✅ get_statusメソッド修正確認テスト成功")
        return True
        
    except AttributeError as e:
        if "get_status" in str(e):
            print(f"❌ get_statusメソッドが見つかりません: {e}")
        else:
            print(f"❌ 属性エラー: {e}")
        return False
        
    except Exception as e:
        print(f"❌ get_statusメソッド修正確認テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メインテスト実行"""
    print("🚀 get_status修正確認テスト開始")
    
    result = test_get_status_method()
    
    if result:
        print("🎉 get_statusメソッド修正完了")
        print("✅ ActivityLearningEngineでの呼び出しエラー解決準備完了")
    else:
        print("⚠️ 追加修正が必要です")
    
    return result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)