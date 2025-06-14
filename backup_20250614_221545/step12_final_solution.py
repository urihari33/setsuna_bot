#!/usr/bin/env python3
"""ステップ12: VOICEVOX WSL接続問題の最終解決"""

import requests
import time

def final_solution_guide():
    """最終解決手順の案内"""
    print("🎯 VOICEVOX WSL接続問題 最終解決手順")
    print("="*50)
    
    print("📋 判明した事実:")
    print("✅ run.exe の場所: C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX\\vv-engine\\run.exe")
    print("❌ 問題: VOICEVOXが既に起動中のため、外部アクセス設定で再起動できない")
    print()
    
    print("🔧 解決手順:")
    print("=" * 30)
    
    print("【手順1: 既存VOICEVOX完全終了】")
    print("1. VOICEVOXアプリを完全終了")
    print("2. タスクマネージャーでVOICEVOXプロセスを確認・終了")
    print("3. 以下のコマンドで強制終了:")
    print("   taskkill /f /im VOICEVOX.exe")
    print("   taskkill /f /im run.exe")
    print()
    
    print("【手順2: エンジンを外部アクセス可能で起動】")
    print("管理者コマンドプロンプトで以下を実行:")
    print('cd "C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX\\vv-engine"')
    print('run.exe --host 0.0.0.0 --port 50021')
    print()
    
    print("【手順3: 接続確認】")
    print("エンジン起動後、この診断スクリプトを実行して確認")
    print()
    
    print("🚨 重要ポイント:")
    print("- 必ず管理者権限のコマンドプロンプトを使用")
    print("- 既存のVOICEVOXを完全終了してから実行")
    print("- --host 0.0.0.0 オプションが重要")

def wait_for_user_action():
    """ユーザーの作業完了を待機"""
    print("\n⏳ 上記手順を実行後、Enterを押して接続テストを開始してください...")
    input("準備完了後、Enterキーを押してください: ")

def test_wsl_connection():
    """WSL接続テスト"""
    print("\n🧪 WSL接続テスト開始")
    print("="*30)
    
    test_hosts = [
        ("172.20.144.1", "WSL Bridge"),
        ("192.168.0.55", "Wi-Fi IP"),
        ("127.0.0.1", "localhost")
    ]
    
    success_host = None
    
    for host, description in test_hosts:
        print(f"\n🔍 {description} ({host}) テスト中...")
        
        for attempt in range(5):
            try:
                response = requests.get(f"http://{host}:50021/version", timeout=3)
                if response.status_code == 200:
                    version_info = response.json()
                    print(f"  🎉 接続成功! Version: {version_info}")
                    success_host = host
                    break
            except Exception as e:
                if attempt == 4:
                    print(f"  ❌ 接続失敗: {str(e)[:50]}...")
            time.sleep(1)
        
        if success_host:
            break
    
    return success_host

def test_voice_synthesis(host):
    """音声合成テスト"""
    print(f"\n🎵 音声合成テスト ({host})")
    print("="*30)
    
    try:
        import json
        
        text = "WSL接続が成功しました！"
        speaker = 1
        
        # audio_query
        print("  Step 1: audio_query...")
        query_response = requests.post(
            f"http://{host}:50021/audio_query",
            params={"text": text, "speaker": speaker},
            timeout=10
        )
        
        if query_response.status_code != 200:
            print(f"  ❌ audio_query失敗: {query_response.status_code}")
            return False
        
        print("  ✅ audio_query成功")
        
        # synthesis
        print("  Step 2: synthesis...")
        synthesis_response = requests.post(
            f"http://{host}:50021/synthesis",
            params={"speaker": speaker},
            data=json.dumps(query_response.json()),
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if synthesis_response.status_code == 200:
            with open("wsl_success_test.wav", "wb") as f:
                f.write(synthesis_response.content)
            
            print("  🎉 音声合成成功!")
            print(f"  📁 wsl_success_test.wav を作成しました")
            return True
        else:
            print(f"  ❌ synthesis失敗: {synthesis_response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ エラー: {e}")
        return False

def provide_final_code(working_host):
    """最終的な使用コード提供"""
    print(f"\n🎉 WSL接続完全成功!")
    print("="*30)
    
    print(f"✅ 使用するIPアドレス: {working_host}")
    print(f"✅ ポート: 50021")
    
    print(f"\n📝 今後のPythonコードテンプレート:")
    print("="*40)
    
    final_code = f'''
import requests
import json

def voicevox_wsl_speak(text, speaker_id=1, output_file="voice_output.wav"):
    """WSL環境でのVOICEVOX音声合成関数"""
    try:
        # Step 1: audio_query
        query_response = requests.post(
            "http://{working_host}:50021/audio_query",
            params={{"text": text, "speaker": speaker_id}},
            timeout=10
        )
        
        if query_response.status_code != 200:
            print(f"audio_query エラー: {{query_response.status_code}}")
            return False
        
        # Step 2: synthesis
        synthesis_response = requests.post(
            "http://{working_host}:50021/synthesis",
            params={{"speaker": speaker_id}},
            data=json.dumps(query_response.json()),
            headers={{"Content-Type": "application/json"}},
            timeout=30
        )
        
        if synthesis_response.status_code == 200:
            with open(output_file, "wb") as f:
                f.write(synthesis_response.content)
            print(f"✅ 音声ファイル作成: {{output_file}}")
            return True
        else:
            print(f"synthesis エラー: {{synthesis_response.status_code}}")
            return False
            
    except Exception as e:
        print(f"エラー: {{e}}")
        return False

# 使用例
if __name__ == "__main__":
    voicevox_wsl_speak("WSLからVOICEVOXが使えるようになりました")
    '''
    
    print(final_code)
    
    print(f"\n🔄 元のtest_voice_after_fix.pyの修正:")
    print("="*45)
    print("元のファイルの以下の行を変更:")
    print(f'  requests.get("http://127.0.0.1:50021/version")')
    print(f'  ↓')
    print(f'  requests.get("http://{working_host}:50021/version")')
    print()
    print("speak_with_voicevox関数を上記のvoicevox_wsl_speak関数に置き換える")

def main():
    """メイン実行"""
    # 1. 解決手順案内
    final_solution_guide()
    
    # 2. ユーザー作業待機
    wait_for_user_action()
    
    # 3. 接続テスト
    working_host = test_wsl_connection()
    
    if working_host:
        # 4. 音声合成テスト
        synthesis_success = test_voice_synthesis(working_host)
        
        if synthesis_success:
            # 5. 最終コード提供
            provide_final_code(working_host)
            
            print(f"\n🎊 完全解決!")
            print(f"これでWSL環境からVOICEVOXを使用できます!")
        else:
            print(f"\n⚠️ 接続はできましたが、音声合成でエラーが発生しました")
            print(f"エンジンの初期化を待って再試行してください")
    else:
        print(f"\n❌ 接続テスト失敗")
        print(f"手順を再確認してください:")
        print(f"1. 既存VOICEVOXの完全終了")
        print(f"2. 管理者権限でのrun.exe起動")
        print(f"3. --host 0.0.0.0 オプションの確認")

if __name__ == "__main__":
    main()