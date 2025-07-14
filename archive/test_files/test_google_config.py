#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google API設定診断ツール
API Key と Search Engine IDの設定状況を詳しく調査
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_google_config():
    """Google設定の詳細診断"""
    print("=== Google API設定診断 ===\n")
    
    # 1. 環境変数の直接確認
    print("1. 環境変数の直接確認:")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    print(f"  GOOGLE_API_KEY: {'設定済み' if google_api_key else '未設定'}")
    if google_api_key:
        print(f"    長さ: {len(google_api_key)} 文字")
        print(f"    開始: {google_api_key[:10]}...")
        print(f"    終了: ...{google_api_key[-10:]}")
    
    print(f"  GOOGLE_SEARCH_ENGINE_ID: {'設定済み' if google_search_engine_id else '未設定'}")
    if google_search_engine_id:
        print(f"    値: {google_search_engine_id}")
        print(f"    長さ: {len(google_search_engine_id)} 文字")
    
    print()
    
    # 2. ConfigManagerの確認
    print("2. ConfigManagerの確認:")
    try:
        from core.config_manager import get_config_manager
        config = get_config_manager()
        
        print(f"  ConfigManager初期化: 成功")
        print(f"  Google API Key取得: {'成功' if config.get_google_api_key() else '失敗'}")
        print(f"  Google Search Engine ID取得: {'成功' if config.get_google_search_engine_id() else '失敗'}")
        print(f"  Google設定有効判定: {config.is_google_search_configured()}")
        
        # 設定検証結果
        validation = config.get_validation_result()
        print(f"  設定検証: {'通過' if validation.is_valid else '失敗'}")
        
        if validation.missing_keys:
            print(f"  不足キー: {validation.missing_keys}")
        if validation.errors:
            print(f"  エラー: {validation.errors}")
        if validation.warnings:
            print(f"  警告: {validation.warnings}")
            
    except Exception as e:
        print(f"  ConfigManagerエラー: {e}")
    
    print()
    
    # 3. GoogleSearchServiceの確認
    print("3. GoogleSearchServiceの確認:")
    try:
        from core.google_search_service import GoogleSearchService
        service = GoogleSearchService()
        
        print(f"  GoogleSearchService初期化: 成功")
        print(f"  設定検証: {service._validate_config()}")
        
        # サービス情報
        info = service.get_service_info()
        print(f"  サービス状態: {info['status']}")
        
    except Exception as e:
        print(f"  GoogleSearchServiceエラー: {e}")
    
    print()
    
    # 4. GoogleSearchManagerの確認
    print("4. GoogleSearchManagerの確認:")
    try:
        from core.google_search_manager import GoogleSearchManager
        manager = GoogleSearchManager()
        
        print(f"  GoogleSearchManager初期化: 成功")
        
        status = manager.get_status()
        print(f"  準備完了: {status['ready']}")
        print(f"  Google サービス利用可能: {status['google_service_available']}")
        print(f"  設定有効: {status['config_valid']}")
        print(f"  利用可能検索数: {status['quota_remaining']}")
        
        if not status['ready']:
            print(f"  準備未完了の理由: {status['not_ready_reason']}")
            
    except Exception as e:
        print(f"  GoogleSearchManagerエラー: {e}")
    
    print()
    
    # 5. .envファイルの確認
    print("5. .envファイルの確認:")
    env_path = project_root / ".env"
    
    if env_path.exists():
        print(f"  .envファイル: 存在")
        
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        google_lines = [line.strip() for line in lines if 'GOOGLE' in line]
        print(f"  Google関連行数: {len(google_lines)}")
        
        for line in google_lines:
            print(f"    {line}")
            
    else:
        print(f"  .envファイル: 存在しない")
    
    print("\n=== 診断完了 ===")

def test_api_request():
    """実際のAPI リクエスト テスト（簡単なテスト）"""
    print("\n=== API リクエスト テスト ===")
    
    try:
        import requests
        
        google_api_key = os.getenv("GOOGLE_API_KEY")
        google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        
        if not google_api_key or not google_search_engine_id:
            print("❌ Google API設定が不完全です")
            return
        
        # Google Custom Search APIエンドポイント
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': google_api_key,
            'cx': google_search_engine_id,
            'q': 'test query',
            'num': 1
        }
        
        print(f"🔍 テストリクエスト送信中...")
        print(f"  エンドポイント: {url}")
        print(f"  API Key: {google_api_key[:10]}...{google_api_key[-10:]}")
        print(f"  Search Engine ID: {google_search_engine_id}")
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"  レスポンス ステータス: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API リクエスト成功")
            data = response.json()
            items = data.get('items', [])
            print(f"  検索結果数: {len(items)}")
            
        else:
            print("❌ API リクエスト失敗")
            print(f"  エラー内容: {response.text}")
            
    except Exception as e:
        print(f"❌ API テスト中にエラー: {e}")

if __name__ == "__main__":
    test_google_config()
    test_api_request()