#!/usr/bin/env python3
"""ステップ8: エンコーディング問題を修正したVOICEVOX起動"""

import subprocess
import requests
import time
import os

def run_command_with_encoding(command, description, encoding='utf-8'):
    """エンコーディングを指定してコマンド実行"""
    print(f"📋 {description}")
    try:
        # まずutf-8で試す
        result = subprocess.run(command, capture_output=True, text=True, 
                              encoding='utf-8', timeout=15)
        if result.returncode == 0:
            print(f"✅ 成功 (utf-8)")
            return result.stdout.strip()
        
        # utf-8で失敗したら他のエンコーディングを試す
        for enc in ['shift-jis', 'cp932', 'utf-16']:
            try:
                result = subprocess.run(command, capture_output=True, text=True, 
                                      encoding=enc, timeout=15)
                if result.returncode == 0:
                    print(f"✅ 成功 ({enc})")
                    return result.stdout.strip()
            except:
                continue
        
        print(f"❌ 全エンコーディングで失敗")
        return None
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None

def start_voicevox_manual_method():
    """手動でVOICEVOXを起動する方法"""
    print("🎯 手動でのVOICEVOX起動")
    print("="*40)
    
    voicevox_path = "C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX\\run.exe"
    
    print(f"📍 VOICEVOX実行ファイル: {voicevox_path}")
    print(f"\n💡 以下の方法で手動起動してください:")
    print(f"="*50)
    print(f"【方法1: コマンドプロンプト】")
    print(f'1. Windowsのコマンドプロンプトを開く')
    print(f'2. 以下をコピーして実行:')
    print(f'   cd "C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX"')
    print(f'   run.exe --host 0.0.0.0')
    print(f"")
    print(f"【方法2: PowerShell】")
    print(f'1. PowerShellを開く')
    print(f'2. 以下をコピーして実行:')
    print(f'   & "C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX\\run.exe" --host 0.0.0.0')
    print(f"")
    print(f"【方法3: 直接実行】")
    print(f'1. エクスプローラーで以下のフォルダを開く:')
    print(f'   C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX')
    print(f'2. run.exe をShift+右クリック')
    print(f'3. "ここでPowerShellウィンドウを開く"')
    print(f'4. 以下を実行: .\\run.exe --host 0.0.0.0')
    print(f"="*50)
    
    input("\n⏳ 上記の方法でVOICEVOXを起動してください。起動後、Enterを押してください...")
    
    return True

def test_connection_loop():
    """接続テストループ"""
    print(f"\n🔍 接続テスト開始")
    print("="*40)
    
    test_hosts = ["172.20.144.1", "192.168.0.55", "127.0.0.1"]
    
    print(f"💡 以下のホストで接続テストを実行中...")
    for host in test_hosts:
        print(f"  - {host}:50021")
    
    max_attempts = 60  # 最大60秒
    for attempt in range(max_attempts):
        if attempt % 10 == 0:
            print(f"\n  テスト {attempt//10 + 1}/{max_attempts//10}: ", end="")
        
        for host in test_hosts:
            try:
                response = requests.get(f"http://{host}:50021/version", timeout=2)
                if response.status_code == 200:
                    version_info = response.json()
                    print(f"\n🎉 接続成功!")
                    print(f"✅ ホスト: {host}")
                    print(f"✅ バージョン: {version_info}")
                    return host
            except:
                pass
        
        print(".", end="", flush=True)
        time.sleep(1)
    
    print(f"\n❌ 接続テストタイムアウト")
    return None

def verify_final_status():
    """最終状況確認"""
    print(f"\n🔍 最終状況確認")
    print("="*40)
    
    # netstatでリスニング状況確認
    try:
        result = subprocess.run(
            ['powershell.exe', '-Command', 'netstat -an | findstr :50021'],
            capture_output=True, text=True, encoding='utf-8', timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            print(f"📊 現在のリスニング状況:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"  {line}")
                    if "0.0.0.0:50021" in line:
                        print(f"  ✅ 外部アクセス可能!")
                        return True
                    elif "127.0.0.1:50021" in line:
                        print(f"  ⚠️ まだlocalhostのみ")
        else:
            print(f"❌ リスニング状況を確認できません")
            
    except Exception as e:
        print(f"❌ 確認エラー: {e}")
    
    return False

def main():
    """メイン処理"""
    print("🔧 VOICEVOX WSL接続問題 修正版解決プロセス")
    print("="*55)
    
    print("💡 エンコーディング問題を回避して手動起動します")
    
    # 手動起動の案内
    if start_voicevox_manual_method():
        
        # 接続テスト
        working_host = test_connection_loop()
        
        # 最終確認
        external_access = verify_final_status()
        
        if working_host:
            print(f"\n🎉 解決成功!")
            print(f"✅ WSLから {working_host}:50021 でアクセス可能")
            
            if external_access:
                print(f"✅ 外部アクセス設定も正常")
            else:
                print(f"⚠️ まだlocalhostのみの可能性")
            
            print(f"\n📝 今後のPythonコードでは:")
            print(f'requests.get("http://{working_host}:50021/version")')
            
            # 最終テスト用コード生成
            print(f"\n🧪 最終テスト用コード:")
            print(f"="*30)
            test_code = f'''
import requests
import json

def test_fixed_voicevox():
    try:
        # 接続確認
        response = requests.get("http://{working_host}:50021/version", timeout=5)
        print(f"✅ 接続成功: {{response.json()}}")
        
        # 音声合成テスト
        text = "WSL接続修復テストです"
        speaker = 1
        
        # audio_query
        query_response = requests.post(
            "http://{working_host}:50021/audio_query",
            params={{"text": text, "speaker": speaker}},
            timeout=10
        )
        
        # synthesis
        synthesis_response = requests.post(
            "http://{working_host}:50021/synthesis",
            params={{"speaker": speaker}},
            data=json.dumps(query_response.json()),
            headers={{"Content-Type": "application/json"}},
            timeout=30
        )
        
        if synthesis_response.status_code == 200:
            with open("wsl_fixed_test.wav", "wb") as f:
                f.write(synthesis_response.content)
            print("✅ 音声合成成功: wsl_fixed_test.wav")
        
    except Exception as e:
        print(f"❌ エラー: {{e}}")

if __name__ == "__main__":
    test_fixed_voicevox()
'''
            print(test_code)
            
        else:
            print(f"\n❌ 接続に失敗しました")
            print(f"💡 確認事項:")
            print(f"1. VOICEVOXが正常に起動しているか")
            print(f"2. --host 0.0.0.0 オプションが適用されているか")
            print(f"3. ファイアウォールの設定")

if __name__ == "__main__":
    main()