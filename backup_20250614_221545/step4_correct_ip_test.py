#!/usr/bin/env python3
"""ステップ4: 正しいIPアドレスでVOICEVOX接続テスト"""

import requests

def test_voicevox_with_ip(ip_address):
    """指定されたIPアドレスでVOICEVOXをテスト"""
    print(f"📡 {ip_address}:50021 でテスト中...")
    
    try:
        url = f"http://{ip_address}:50021/version"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            version_info = response.json()
            print(f"✅ 接続成功!")
            print(f"📋 バージョン: {version_info}")
            return True
        else:
            print(f"❌ HTTP エラー: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 接続拒否 (ファイアウォールが原因の可能性)")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ タイムアウト")
        return False
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def main():
    """メイン処理"""
    print("🔧 正しいIPアドレスでのVOICEVOX接続テスト")
    print("="*50)
    
    # ipconfigで確認されたIPアドレス
    test_ips = [
        "192.168.0.55",    # Wi-Fi の IPv4アドレス
        "172.20.144.1",    # WSL用のIPアドレス
    ]
    
    working_ip = None
    
    for ip in test_ips:
        print(f"\n{'='*30}")
        success = test_voicevox_with_ip(ip)
        
        if success:
            working_ip = ip
            break
    
    if working_ip:
        print(f"\n🎉 成功しました!")
        print(f"✅ 使用するIPアドレス: {working_ip}")
        print(f"\n📝 今後のコードでは以下を使用:")
        print(f'requests.get("http://{working_ip}:50021/version")')
        
    else:
        print(f"\n❌ 両方のIPアドレスで接続に失敗しました")
        print(f"\n🛡️ ファイアウォール設定が必要です:")
        print(f"1. Windows設定を開く")
        print(f"2. プライバシーとセキュリティ → Windows セキュリティ")
        print(f"3. ファイアウォールとネットワーク保護")
        print(f"4. 詳細設定 → 受信の規則")
        print(f"5. 新しい規則 → ポート → TCP → 50021 → 許可")

if __name__ == "__main__":
    main()