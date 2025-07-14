#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
検索サービス統合モジュール
Google Custom Search API専用実装
MockSearchServiceは削除されました
"""

# GoogleSearchManagerをSearchEngineManagerとしてエクスポート
from .google_search_manager import GoogleSearchManager

# 後方互換性のためのエイリアス
SearchEngineManager = GoogleSearchManager

# 削除されたクラスの説明
class MockSearchService:
    """
    MockSearchServiceは削除されました
    現在はGoogle Custom Search APIのみを使用します
    """
    def __init__(self):
        raise NotImplementedError(
            "MockSearchServiceは削除されました。"
            "Google Custom Search APIを設定してください。"
            "詳細はGOOGLE_SEARCH_SETUP.mdを参照。"
        )

# テスト用コード（実行しない）
if __name__ == "__main__":
    print("=== 検索サービス統合モジュール ===")
    print("MockSearchServiceは削除されました")
    print("現在はGoogle Custom Search API専用です")
    
    # GoogleSearchManagerの動作確認
    try:
        search_manager = SearchEngineManager()  # GoogleSearchManagerのエイリアス
        status = search_manager.get_status()
        
        print(f"\n📊 検索サービス状態:")
        print(f"  Google検索準備完了: {status['ready']}")
        print(f"  利用可能検索数: {status['quota_remaining']}")
        
        if not status['ready']:
            print(f"  理由: {status['not_ready_reason']}")
        
    except Exception as e:
        print(f"検索サービス初期化エラー: {e}")
    
    print("\n✅ Google専用検索システム準備完了")