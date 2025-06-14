#!/usr/bin/env python3
"""ステップ5: WSL-Windows間の詳細なネットワーク調査"""

import subprocess
import socket
import requests
import json

def run_command(command, description):
    """コマンドを実行して結果を表示"""
    print(f"\n📋 {description}")
    print(f"コマンド: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ 成功:")
            print(f"  {result.stdout.strip()}")
        else:
            print(f"❌ エラー:")
            print(f"  {result.stderr.strip()}")
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ 実行エラー: {e}")
        return None

def check_wsl_network_config():
    """WSLのネットワーク設定を詳細確認"""
    print("🔍 WSLネットワーク設定の詳細調査")
    print("="*50)
    
    # WSLのバージョン確認
    run_command(['wsl', '--version'], "WSLバージョン確認")
    
    # ネットワーク設定確認
    run_command(['ip', 'addr', 'show'], "ネットワークインターフェース一覧")
    run_command(['ip', 'route', 'show'], "ルーティングテーブル")
    run_command(['cat', '/etc/resolv.conf'], "DNS設定確認")
    
    # Windowsホストへの接続性確認
    print(f"\n🔗 Windowsホストへの接続性テスト")
    
    # 既知のWindowsIPへのping
    windows_ips = ["172.20.144.1", "192.168.0.55"]
    for ip in windows_ips:
        run_command(['ping', '-c', '3', ip], f"{ip} への ping")
    
    # ポートスキャン
    print(f"\n🔌 ポートスキャンテスト")
    for ip in windows_ips:
        test_port_connectivity(ip, 50021)

def test_port_connectivity(host, port):
    """特定のポートへの接続テスト"""
    print(f"  🔍 {host}:{port} への接続テスト...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"    ✅ ポート接続成功")
            return True
        else:
            print(f"    ❌ ポート接続失敗 (エラーコード: {result})")
            return False
    except Exception as e:
        print(f"    ❌ 接続エラー: {e}")
        return False

def check_voicevox_process_windows():
    """Windows側でVOICEVOXプロセス確認"""
    print(f"\n🔍 Windows側VOICEVOXプロセス確認")
    
    # PowerShellコマンドでVOICEVOXプロセスをチェック
    powershell_commands = [
        ['powershell.exe', '-Command', 'Get-Process | Where-Object {$_.ProcessName -like "*voicevox*"} | Format-Table'],
        ['powershell.exe', '-Command', 'netstat -an | findstr :50021'],
    ]
    
    for cmd in powershell_commands:
        run_command(cmd, f"Windows側プロセス確認: {cmd[-1]}")

def test_different_connection_methods():
    """異なる接続方法をテスト"""
    print(f"\n🧪 様々な接続方法のテスト")
    
    # テスト対象
    test_cases = [
        ("127.0.0.1", "localhost"),
        ("172.20.144.1", "WSL bridge"),
        ("192.168.0.55", "Wi-Fi IP"),
        ("host.docker.internal", "Docker host"),
        ("localhost.localdomain", "localhost domain"),
    ]
    
    for host, description in test_cases:
        print(f"\n  🔍 {description} ({host}) テスト:")
        
        # Socket接続テスト
        if test_port_connectivity(host, 50021):
            # HTTP接続テスト
            try:
                response = requests.get(f"http://{host}:50021/version", timeout=3)
                if response.status_code == 200:
                    print(f"    ✅ HTTP接続成功: {response.json()}")
                else:
                    print(f"    ❌ HTTP失敗: {response.status_code}")
            except Exception as e:
                print(f"    ❌ HTTP接続エラー: {e}")

def check_firewall_and_network():
    """ファイアウォールとネットワーク設定確認"""
    print(f"\n🛡️ ファイアウォール・ネットワーク確認")
    
    # Windows側でファイアウォール確認
    firewall_commands = [
        ['powershell.exe', '-Command', 'Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*VOICEVOX*"} | Format-Table'],
        ['powershell.exe', '-Command', 'Get-NetFirewallPortFilter | Where-Object {$_.LocalPort -eq 50021} | Format-Table'],
    ]
    
    for cmd in firewall_commands:
        run_command(cmd, f"ファイアウォール確認")

def main():
    """メイン調査実行"""
    print("🕵️ WSL-VOICEVOX接続問題の詳細調査")
    print("="*60)
    
    # 1. WSLネットワーク設定確認
    check_wsl_network_config()
    
    # 2. Windows側プロセス確認
    check_voicevox_process_windows()
    
    # 3. 様々な接続方法テスト
    test_different_connection_methods()
    
    # 4. ファイアウォール確認
    check_firewall_and_network()
    
    print(f"\n📊 調査完了")
    print(f"="*60)
    print(f"💡 次のステップ:")
    print(f"1. 上記の結果から問題箇所を特定")
    print(f"2. 特定された問題に対する具体的な対処")
    print(f"3. VOICEVOX設定の調整（必要に応じて）")

if __name__ == "__main__":
    main()