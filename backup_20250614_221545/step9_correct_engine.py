#!/usr/bin/env python3
"""ステップ9: 正しいVOICEVOXエンジン起動"""

import subprocess
import requests
import time

def find_voicevox_files():
    """VOICEVOXファイルの詳細確認"""
    print("🔍 VOICEVOXファイル構成確認")
    print("="*40)
    
    # VOICEVOXフォルダの中身を確認
    cmd = ['powershell.exe', '-Command', 
           'Get-ChildItem -Path "C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX" | Format-Table Name,Length,LastWriteTime']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=10)
        if result.returncode == 0:
            print("✅ VOICEVOXフォルダ内容:")
            print(result.stdout)
        else:
            print("❌ フォルダ確認失敗")
    except Exception as e:
        print(f"❌ エラー: {e}")

def stop_all_voicevox():
    """すべてのVOICEVOX関連プロセス停止"""
    print("\n🛑 全VOICEVOXプロセス停止")
    print("="*30)
    
    try:
        result = subprocess.run([
            'powershell.exe', '-Command',
            'Get-Process | Where-Object {$_.ProcessName -like "*voicevox*"} | Stop-Process -Force'
        ], capture_output=True, text=True, timeout=10)
        print("✅ プロセス停止実行")
        time.sleep(3)
    except Exception as e:
        print(f"❌ プロセス停止エラー: {e}")

def start_engine_directly():
    """エンジンを直接起動"""
    print("\n🚀 VOICEVOXエンジン直接起動")
    print("="*35)
    
    engine_path = "C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX\\run.exe"
    
    print(f"📍 エンジンパス: {engine_path}")
    print(f"🎯 起動オプション: --host 0.0.0.0")
    
    print(f"\n💡 以下を**管理者権限**で実行してください:")
    print(f"="*50)
    print(f"【重要: 管理者権限のコマンドプロンプト】")
    print(f"1. Windowsキー+R で「ファイル名を指定して実行」")
    print(f"2. 「cmd」と入力してCtrl+Shift+Enterで管理者権限起動")
    print(f"3. 以下をコピー貼り付けして実行:")
    print(f"")
    print(f'cd "C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX"')
    print(f'run.exe --host 0.0.0.0 --port 50021')
    print(f"")
    print(f"【または PowerShell管理者権限】")
    print(f"1. Windowsキー+X で管理者PowerShell起動")
    print(f"2. 以下を実行:")
    print(f'& "C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX\\run.exe" --host 0.0.0.0 --port 50021')
    print(f"="*50)
    
    input("\n⏳ 管理者権限で上記コマンドを実行してください。起動後Enterを押してください...")

def test_connection_detailed():
    """詳細な接続テスト"""
    print(f"\n🧪 詳細接続テスト")
    print("="*25)
    
    test_hosts = [
        ("172.20.144.1", "WSL Bridge IP"),
        ("192.168.0.55", "Wi-Fi IP"),  
        ("127.0.0.1", "localhost"),
        ("0.0.0.0", "全インターフェース")
    ]
    
    success_hosts = []
    
    for host, description in test_hosts:
        print(f"\n🔍 {description} ({host}) テスト:")
        
        for attempt in range(5):  # 5回試行
            try:
                response = requests.get(f"http://{host}:50021/version", timeout=3)
                if response.status_code == 200:
                    version_info = response.json()
                    print(f"  ✅ 成功! バージョン: {version_info}")
                    success_hosts.append((host, description))
                    break
            except Exception as e:
                if attempt == 4:  # 最後の試行
                    print(f"  ❌ 失敗: {str(e)[:50]}...")
            
            time.sleep(1)
    
    return success_hosts

def check_final_listening():
    """最終リスニング状況確認"""
    print(f"\n📊 最終リスニング状況確認")
    print("="*35)
    
    try:
        result = subprocess.run([
            'powershell.exe', '-Command', 'netstat -an | findstr :50021'
        ], capture_output=True, text=True, encoding='utf-8', timeout=5)
        
        if result.returncode == 0 and result.stdout.strip():
            print("現在のリスニング状況:")
            listening_external = False
            
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"  {line}")
                    if "0.0.0.0:50021" in line and "LISTENING" in line:
                        print(f"  🎉 外部アクセス可能状態を確認!")
                        listening_external = True
                    elif "127.0.0.1:50021" in line and "LISTENING" in line:
                        print(f"  ⚠️ まだlocalhostのみ")
            
            return listening_external
        else:
            print("❌ リスニング情報を取得できません")
            return False
            
    except Exception as e:
        print(f"❌ 確認エラー: {e}")
        return False

def main():
    """メイン処理"""
    print("🔧 VOICEVOX エンジン直接起動による解決")
    print("="*45)
    
    # 1. ファイル構成確認
    find_voicevox_files()
    
    # 2. 既存プロセス停止
    stop_all_voicevox()
    
    # 3. エンジン直接起動（手動）
    start_engine_directly()
    
    # 4. 接続テスト
    success_hosts = test_connection_detailed()
    
    # 5. 最終確認
    external_listening = check_final_listening()
    
    # 結果判定
    if success_hosts:
        print(f"\n🎉 接続成功!")
        print(f"✅ 接続可能なホスト:")
        for host, desc in success_hosts:
            print(f"  - {host} ({desc})")
        
        if external_listening:
            print(f"✅ 外部アクセス設定も確認済み")
        
        # 推奨IPを決定
        recommended_ip = None
        for host, desc in success_hosts:
            if host == "172.20.144.1":
                recommended_ip = host
                break
        
        if not recommended_ip:
            recommended_ip = success_hosts[0][0]
        
        print(f"\n📝 推奨設定:")
        print(f"今後のコードでは: {recommended_ip}:50021 を使用")
        
        # テストコード生成
        print(f"\n🧪 最終確認用テストコード:")
        print("="*30)
        print(f'''
import requests
import json

def final_test():
    try:
        response = requests.get("http://{recommended_ip}:50021/version", timeout=5)
        print(f"✅ 接続成功: {{response.json()}}")
        
        # 簡単な音声合成テスト
        text = "WSL接続が成功しました"
        query_response = requests.post(
            "http://{recommended_ip}:50021/audio_query",
            params={{"text": text, "speaker": 1}}
        )
        
        synthesis_response = requests.post(
            "http://{recommended_ip}:50021/synthesis",
            params={{"speaker": 1}},
            data=json.dumps(query_response.json()),
            headers={{"Content-Type": "application/json"}}
        )
        
        if synthesis_response.status_code == 200:
            with open("final_test.wav", "wb") as f:
                f.write(synthesis_response.content)
            print("✅ 音声合成成功: final_test.wav")
        
    except Exception as e:
        print(f"❌ エラー: {{e}}")

if __name__ == "__main__":
    final_test()
        ''')
        
    else:
        print(f"\n❌ 接続に失敗しました")
        print(f"\n🔍 トラブルシューティング:")
        print(f"1. 管理者権限で実行しましたか？")
        print(f"2. run.exe が正しく起動していますか？")
        print(f"3. --host 0.0.0.0 オプションが含まれていますか？")
        print(f"4. ファイアウォールでブロックされていませんか？")

if __name__ == "__main__":
    main()