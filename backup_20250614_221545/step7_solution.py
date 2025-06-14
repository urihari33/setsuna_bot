#!/usr/bin/env python3
"""ステップ7: VOICEVOX接続問題の解決"""

import subprocess
import requests
import time

def cleanup_voicevox_processes():
    """VOICEVOXプロセスのクリーンアップ"""
    print("🧹 VOICEVOXプロセスのクリーンアップ")
    print("="*40)
    
    commands = [
        # 全VOICEVOXプロセスを表示
        ['powershell.exe', '-Command', 
         'Get-Process | Where-Object {$_.ProcessName -like "*voicevox*"} | Format-Table Id,ProcessName'],
        
        # 全VOICEVOXプロセスを終了
        ['powershell.exe', '-Command', 
         'Get-Process | Where-Object {$_.ProcessName -like "*voicevox*"} | Stop-Process -Force'],
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n📋 ステップ {i}: プロセス{'表示' if i == 1 else '終了'}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                print(f"✅ 成功")
                if result.stdout.strip():
                    print(f"結果: {result.stdout.strip()}")
            else:
                print(f"❌ 失敗: {result.stderr.strip()}")
        except Exception as e:
            print(f"❌ エラー: {e}")
    
    print(f"\n⏱️ プロセス終了後、5秒待機...")
    time.sleep(5)

def start_voicevox_with_external_access():
    """外部アクセス可能でVOICEVOXを起動"""
    print(f"\n🚀 外部アクセス可能でVOICEVOX起動")
    print("="*40)
    
    # VOICEVOXの実行ファイルパスを探す
    find_commands = [
        ['powershell.exe', '-Command', 
         'Get-ChildItem -Path "C:\\Users\\*\\AppData\\Local\\Programs\\VOICEVOX" -Name "run.exe" -Recurse -ErrorAction SilentlyContinue'],
        ['powershell.exe', '-Command', 
         'Get-ChildItem -Path "C:\\Program Files*\\VOICEVOX" -Name "run.exe" -Recurse -ErrorAction SilentlyContinue'],
    ]
    
    voicevox_path = None
    for cmd in find_commands:
        print(f"📍 VOICEVOX実行ファイル検索中...")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                # パスを組み立て
                if "AppData" in cmd[2]:
                    voicevox_path = f"C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX\\run.exe"
                else:
                    voicevox_path = f"C:\\Program Files\\VOICEVOX\\run.exe"
                print(f"✅ 発見: {voicevox_path}")
                break
        except Exception as e:
            print(f"❌ 検索エラー: {e}")
    
    if not voicevox_path:
        print(f"❌ run.exe が見つかりません")
        print(f"💡 手動でVOICEVOXフォルダを確認してください")
        return False
    
    # 外部アクセス可能で起動
    print(f"\n🎯 外部アクセス有効でVOICEVOX起動中...")
    print(f"パス: {voicevox_path}")
    print(f"オプション: --host 0.0.0.0")
    
    try:
        # PowerShellでバックグラウンド起動
        start_cmd = [
            'powershell.exe', '-Command', 
            f'Start-Process -FilePath "{voicevox_path}" -ArgumentList "--host", "0.0.0.0" -WindowStyle Hidden'
        ]
        
        result = subprocess.run(start_cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ 起動コマンド実行成功")
        else:
            print(f"❌ 起動失敗: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 起動エラー: {e}")
        return False
    
    return True

def wait_and_test_connection():
    """起動待機と接続テスト"""
    print(f"\n⏱️ VOICEVOX起動待機とテスト")
    print("="*40)
    
    # 起動待機（最大3分）
    max_wait = 180
    for i in range(max_wait):
        if i % 15 == 0:  # 15秒ごとに表示
            print(f"  待機中... {i//60:02d}:{i%60:02d}")
        
        # 接続テスト（WSLから）
        try:
            response = requests.get("http://172.20.144.1:50021/version", timeout=2)
            if response.status_code == 200:
                version_info = response.json()
                print(f"\n🎉 WSLから接続成功！")
                print(f"✅ バージョン: {version_info}")
                print(f"✅ 使用IP: 172.20.144.1")
                return "172.20.144.1"
        except:
            pass
        
        time.sleep(1)
    
    print(f"\n❌ 接続テストタイムアウト")
    return None

def verify_listening_status():
    """リスニング状況の確認"""
    print(f"\n🔍 最終確認: リスニング状況")
    print("="*40)
    
    cmd = ['powershell.exe', '-Command', 'netstat -an | findstr :50021']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ リスニング状況:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"  {line}")
                    if "0.0.0.0:50021" in line:
                        print(f"  ✅ 外部アクセス可能状態を確認")
                    elif "127.0.0.1:50021" in line:
                        print(f"  ⚠️ まだlocalhostのみ")
    except Exception as e:
        print(f"❌ 確認エラー: {e}")

def main():
    """メイン解決プロセス"""
    print("🔧 VOICEVOX WSL接続問題 解決プロセス")
    print("="*50)
    
    print("📋 解決手順:")
    print("1. 既存VOICEVOXプロセス全終了")
    print("2. 外部アクセス可能で再起動")
    print("3. 接続テスト")
    print("4. 最終確認")
    
    input("\n⚠️ 重要: VOICEVOX作業中のデータがあれば保存してください。Enterで続行...")
    
    # 1. プロセスクリーンアップ
    cleanup_voicevox_processes()
    
    # 2. 外部アクセス可能で起動
    if start_voicevox_with_external_access():
        
        # 3. 接続テスト
        working_ip = wait_and_test_connection()
        
        # 4. 最終確認
        verify_listening_status()
        
        if working_ip:
            print(f"\n🎉 解決成功！")
            print(f"✅ WSLから {working_ip}:50021 でVOICEVOXにアクセス可能")
            print(f"\n📝 今後のコードでは以下を使用:")
            print(f'requests.get("http://{working_ip}:50021/version")')
        else:
            print(f"\n❌ 解決失敗")
            print(f"💡 手動で確認が必要です")
    else:
        print(f"\n❌ VOICEVOXの起動に失敗しました")

if __name__ == "__main__":
    main()