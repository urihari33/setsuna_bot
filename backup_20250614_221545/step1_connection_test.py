#!/usr/bin/env python3
"""ステップ1: シンプルな接続テスト"""

import requests

def test_connection():
    """VOICEVOXへの接続をテスト"""
    print("📡 VOICEVOX接続テスト")
    print("="*30)
    
    try:
        response = requests.get("http://127.0.0.1:50021/version", timeout=5)
        
        if response.status_code == 200:
            version_info = response.json()
            print(f"✅ 接続成功!")
            print(f"バージョン: {version_info}")
            return True
        else:
            print(f"❌ 接続失敗: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 接続エラー: VOICEVOXに接続できません")
        return False
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    
    if success:
        print("\n✅ 接続OK - 次のステップに進めます")
    else:
        print("\n❌ 接続NG - 設定確認が必要です")