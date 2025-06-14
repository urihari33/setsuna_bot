#!/usr/bin/env python3
"""ステップ3: 複数の方法でWindowsのIPアドレスを確認"""

import requests
import subprocess
import socket

def test_voicevox_connection(host, description=""):
    """指定されたホストでVOICEVOX接続をテスト"""
    try:
        url = f"http://{host}:50021/version"
        print(f"  🔍 テスト中: {url} {description}")
        
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            version_info = response.json()
            print(f"  ✅ 成功! バージョン: {version_info}")
            return host
        else:
            print(f"  ❌ HTTP {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"  ❌ 接続拒否")
        return None
    except requests.exceptions.Timeout:
        print(f"  ❌ タイムアウト")
        return None
    except Exception as e:
        print(f"  ❌ エラー: {e}")
        return None

def get_wsl_host_ip():
    """WSLからWindowsホストのIPアドレスを取得"""
    methods = []
    
    # 方法1: hostname -I でWSLのIPを取得し、ゲートウェイを推測
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        if result.returncode == 0:
            wsl_ip = result.stdout.strip().split()[0]
            print(f"💡 WSL IP: {wsl_ip}")
            
            # 通常WSLのIPが172.x.x.xの場合、Windowsは172.x.x.1
            if wsl_ip.startswith('172.'):
                parts = wsl_ip.split('.')
                windows_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
                methods.append((windows_ip, "WSL推測IP"))
    except:
        pass
    
    # 方法2: ip route でデフォルトゲートウェイを取得
    try:
        result = subprocess.run(['ip', 'route', 'show', 'default'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip()
            if 'via' in lines:
                gateway_ip = lines.split('via')[1].split()[0]
                methods.append((gateway_ip, "デフォルトゲートウェイ"))
    except:
        pass
    
    # 方法3: よくあるWSLのWindows IP
    common_ips = [
        ("172.17.0.1", "Docker bridge"),
        ("172.18.0.1", "WSL bridge"),
        ("172.19.0.1", "WSL bridge 2"),
        ("172.20.0.1", "WSL bridge 3"),
        ("192.168.1.1", "ローカルルーター"),
    ]
    methods.extend(common_ips)
    
    return methods

def main():
    """メイン処理"""
    print("🔧 WSL → Windows VOICEVOX 接続確認")
    print("="*45)
    
    # まず基本的な方法を試す
    basic_hosts = [
        ("127.0.0.1", "localhost"),
        ("localhost", "localhost名前解決"),
    ]
    
    print("📡 基本接続テスト:")
    working_host = None
    for host, desc in basic_hosts:
        result = test_voicevox_connection(host, f"({desc})")
        if result:
            working_host = result
            break
    
    if working_host:
        print(f"\n🎉 成功! {working_host} で接続できました")
        return working_host
    
    # WSL特有の方法を試す
    print(f"\n📡 WSL環境での詳細検索:")
    
    ip_methods = get_wsl_host_ip()
    
    for host, desc in ip_methods:
        result = test_voicevox_connection(host, f"({desc})")
        if result:
            working_host = result
            break
    
    if working_host:
        print(f"\n🎉 成功! {working_host} で接続できました")
        print(f"\n📝 今後はこのIPアドレスを使用してください:")
        print(f"IP: {working_host}")
        return working_host
    else:
        print(f"\n❌ 全ての方法で接続に失敗しました")
        print(f"\n💡 手動確認が必要です:")
        print(f"1. Windowsのコマンドプロンプトで以下を実行:")
        print(f"   ipconfig")
        print(f"2. 'IPv4 アドレス' をメモ")
        print(f"3. そのIPアドレスで再テスト")
        print(f"\n🔧 ファイアウォール確認:")
        print(f"1. Windowsの設定 → プライバシーとセキュリティ → Windows セキュリティ")
        print(f"2. ファイアウォールとネットワーク保護")
        print(f"3. プライベートネットワークでVOICEVOXを許可")
        return None

if __name__ == "__main__":
    result = main()
    
    if result:
        print(f"\n✅ 次のステップに進む準備ができました")
        print(f"使用するIP: {result}")