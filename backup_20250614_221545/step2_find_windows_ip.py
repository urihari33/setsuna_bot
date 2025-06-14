#!/usr/bin/env python3
"""ステップ2: WindowsのIPアドレスを見つけてVOICEVOXに接続"""

import requests
import subprocess
import re

def find_windows_ip():
    """WindowsのIPアドレスを取得"""
    print("🔍 WindowsのIPアドレスを検索中...")
    
    try:
        # WSLからWindowsのIPを取得する方法
        result = subprocess.run(['cat', '/etc/resolv.conf'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            # nameserver行からIPアドレスを抽出
            lines = result.stdout.split('\n')
            for line in lines:
                if line.startswith('nameserver'):
                    ip = line.split()[1]
                    print(f"💡 検出されたWindowsIP: {ip}")
                    return ip
        
        print("❌ resolv.confからIPが見つかりませんでした")
        return None
        
    except Exception as e:
        print(f"❌ IP検索エラー: {e}")
        return None

def test_voicevox_with_ip(ip_address):
    """指定されたIPでVOICEVOXに接続テスト"""
    print(f"📡 {ip_address}:50021 で接続テスト中...")
    
    try:
        url = f"http://{ip_address}:50021/version"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            version_info = response.json()
            print(f"✅ 接続成功!")
            print(f"URL: {url}")
            print(f"バージョン: {version_info}")
            return ip_address
        else:
            print(f"❌ HTTP {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {ip_address} に接続できません")
        return None
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None

def main():
    """メイン処理"""
    print("🔧 WSL環境でのVOICEVOX接続確認")
    print("="*40)
    
    # WindowsのIPアドレスを検索
    windows_ip = find_windows_ip()
    
    if not windows_ip:
        print("\n💡 手動でWindowsのIPアドレスを確認してください:")
        print("1. Windowsのコマンドプロンプトで 'ipconfig' を実行")
        print("2. 'IPv4 アドレス' を確認")
        print("3. そのIPアドレスを使用")
        return
    
    # 検出されたIPでテスト
    working_ip = test_voicevox_with_ip(windows_ip)
    
    if working_ip:
        print(f"\n🎉 成功! 以降は以下のIPアドレスを使用してください:")
        print(f"IP: {working_ip}")
        print(f"URL: http://{working_ip}:50021")
        
        # 次のステップ用のコード例を表示
        print(f"\n📝 修正例:")
        print(f'requests.get("http://{working_ip}:50021/version")')
        
    else:
        print(f"\n❌ 接続に失敗しました")
        print(f"\n🔧 対処法:")
        print(f"1. Windowsでファイアウォール設定を確認")
        print(f"2. VOICEVOXが正常に起動しているか確認")
        print(f"3. WindowsのIPアドレスを手動で確認")

if __name__ == "__main__":
    main()