#!/usr/bin/env python3
"""ステップ6: VOICEVOXが実際にどこをリッスンしているか確認"""

import subprocess

def check_listening_ports():
    """リスニングポートの確認"""
    print("🔍 ポート50021のリスニング状況確認")
    print("="*40)
    
    # Windows側でnetstatを実行してVOICEVOXのリスニング状況を確認
    commands = [
        # Windows側からnetstatで確認
        ['powershell.exe', '-Command', 'netstat -an | findstr :50021'],
        
        # Windows側からGet-NetTCPConnectionで詳細確認
        ['powershell.exe', '-Command', 
         'Get-NetTCPConnection -LocalPort 50021 -ErrorAction SilentlyContinue | Format-Table LocalAddress,LocalPort,State'],
        
        # プロセス情報も含めて確認
        ['powershell.exe', '-Command', 'netstat -ano | findstr :50021'],
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n📋 テスト {i}: {cmd[-1]}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                print(f"✅ 結果:")
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        print(f"  {line}")
            else:
                print(f"❌ 結果なし")
                if result.stderr:
                    print(f"  エラー: {result.stderr.strip()}")
        except Exception as e:
            print(f"❌ 実行エラー: {e}")

def check_wsl_to_windows_connectivity():
    """WSLからWindowsへの基本接続確認"""
    print(f"\n🔗 WSL→Windows 基本接続確認")
    print("="*40)
    
    # WSLからWindows側への基本的な接続確認
    test_commands = [
        # Windows側へのping
        ['ping', '-c', '2', '172.20.144.1'],
        ['ping', '-c', '2', '192.168.0.55'],
        
        # telnetで50021ポートへの接続テスト
        ['timeout', '5', 'telnet', '172.20.144.1', '50021'],
        ['timeout', '5', 'telnet', '192.168.0.55', '50021'],
    ]
    
    for cmd in test_commands:
        print(f"\n📋 {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ 成功")
                if result.stdout:
                    print(f"  出力: {result.stdout.strip()[:200]}...")
            else:
                print(f"❌ 失敗 (終了コード: {result.returncode})")
                if result.stderr:
                    print(f"  エラー: {result.stderr.strip()[:200]}...")
        except subprocess.TimeoutExpired:
            print(f"⏱️ タイムアウト")
        except Exception as e:
            print(f"❌ 実行エラー: {e}")

def main():
    """メイン実行"""
    print("🔧 VOICEVOX リスニング状況とWSL接続性の確認")
    print("="*60)
    
    check_listening_ports()
    check_wsl_to_windows_connectivity()
    
    print(f"\n💡 判定方法:")
    print(f"1. netstatの結果で '0.0.0.0:50021' → 全インターフェースでリスニング（良い）")
    print(f"2. netstatの結果で '127.0.0.1:50021' → localhostのみ（問題）")
    print(f"3. telnet接続成功 → ネットワーク経路OK")
    print(f"4. telnet接続失敗 → ファイアウォールまたはVOICEVOX設定問題")

if __name__ == "__main__":
    main()