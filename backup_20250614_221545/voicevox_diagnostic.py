#!/usr/bin/env python3
"""VOICEVOX 詳細診断ツール - ver 0.23.1対応"""

import requests
import socket
import time
import json
import subprocess
import psutil
import sys
from urllib.parse import urlparse

def check_port_usage(host='127.0.0.1', port=50021):
    """ポートが使用されているかチェック"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"  ⚠️ ポートチェックエラー: {e}")
        return False

def find_voicevox_processes():
    """VOICEVOX関連プロセスを検索"""
    processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = proc.info['name'].lower()
                cmdline = ' '.join(proc.info['cmdline'] or []).lower()
                
                if ('voicevox' in name or 'voicevox' in cmdline or 
                    'run.exe' in name or 'run.exe' in cmdline):
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': proc.info['cmdline']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        print(f"  ⚠️ プロセス検索エラー: {e}")
    
    return processes

def test_voicevox_api(host='127.0.0.1', port=50021):
    """VOICEVOX API の詳細テスト"""
    base_url = f"http://{host}:{port}"
    
    print(f"  🔍 テスト対象: {base_url}")
    
    # 基本接続テスト
    endpoints = [
        ('/version', 'バージョン情報'),
        ('/speakers', 'スピーカー一覧'),
        ('/speaker_info', 'スピーカー詳細'),
        ('/docs', 'API ドキュメント'),
        ('/setting', 'エンジン設定')
    ]
    
    results = {}
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅" if response.status_code == 200 else f"❌({response.status_code})"
            results[endpoint] = {
                'status': status,
                'description': description,
                'response_time': response.elapsed.total_seconds()
            }
            
            if endpoint == '/version' and response.status_code == 200:
                version_info = response.json()
                print(f"    📋 VOICEVOX Version: {version_info}")
                
        except requests.exceptions.ConnectionError:
            results[endpoint] = {'status': '❌接続エラー', 'description': description}
        except requests.exceptions.Timeout:
            results[endpoint] = {'status': '⏱️タイムアウト', 'description': description}
        except Exception as e:
            results[endpoint] = {'status': f'❌{str(e)[:30]}', 'description': description}
    
    return results

def scan_ports():
    """複数ポートをスキャン"""
    ports_to_check = [50021, 50022, 50023, 50031, 50041, 50051]
    active_ports = []
    
    print("  🔍 ポートスキャン実行中...")
    for port in ports_to_check:
        if check_port_usage(port=port):
            active_ports.append(port)
            print(f"    ✅ ポート {port}: 使用中")
        else:
            print(f"    ❌ ポート {port}: 未使用")
    
    return active_ports

def check_voicevox_window():
    """VOICEVOXウィンドウの存在確認"""
    try:
        if sys.platform == "win32":
            import win32gui
            
            def enum_windows_callback(hwnd, windows):
                window_text = win32gui.GetWindowText(hwnd)
                if 'voicevox' in window_text.lower():
                    windows.append((hwnd, window_text))
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            return windows
        else:
            print("    ℹ️ ウィンドウ検索はWindows環境でのみ対応")
            return []
    except ImportError:
        print("    ⚠️ pywin32が必要です: pip install pywin32")
        return []
    except Exception as e:
        print(f"    ⚠️ ウィンドウ検索エラー: {e}")
        return []

def comprehensive_diagnosis():
    """総合診断実行"""
    print("🔧 VOICEVOX 総合診断ツール (ver 0.23.1対応)")
    print("=" * 60)
    
    # 1. プロセス検索
    print("\n📋 1. プロセス検索")
    processes = find_voicevox_processes()
    if processes:
        print("  ✅ VOICEVOX関連プロセスが見つかりました:")
        for proc in processes:
            print(f"    PID: {proc['pid']}, 名前: {proc['name']}")
            if proc['cmdline']:
                print(f"      コマンド: {' '.join(proc['cmdline'])}")
    else:
        print("  ❌ VOICEVOX関連プロセスが見つかりません")
    
    # 2. ウィンドウ検索
    print("\n🪟 2. ウィンドウ検索")
    windows = check_voicevox_window()
    if windows:
        print("  ✅ VOICEVOXウィンドウが見つかりました:")
        for hwnd, title in windows:
            print(f"    {title}")
    else:
        print("  ❌ VOICEVOXウィンドウが見つかりません")
    
    # 3. ポートスキャン
    print("\n🔌 3. ポートスキャン")
    active_ports = scan_ports()
    
    # 4. API接続テスト
    print("\n🌐 4. API接続テスト")
    
    # デフォルトポート
    print("  📡 デフォルトポート (50021) テスト:")
    default_results = test_voicevox_api()
    for endpoint, result in default_results.items():
        print(f"    {result['status']} {endpoint} - {result['description']}")
        if 'response_time' in result:
            print(f"      応答時間: {result['response_time']:.3f}秒")
    
    # アクティブポートでのテスト
    for port in active_ports:
        if port != 50021:
            print(f"\n  📡 ポート {port} テスト:")
            results = test_voicevox_api(port=port)
            for endpoint, result in results.items():
                print(f"    {result['status']} {endpoint}")
    
    # 5. 音声テスト用のサンプルコード生成
    print("\n🎤 5. 修正されたテストコード")
    working_port = None
    for port in [50021] + active_ports:
        try:
            response = requests.get(f"http://127.0.0.1:{port}/version", timeout=3)
            if response.status_code == 200:
                working_port = port
                break
        except:
            continue
    
    if working_port:
        print(f"  ✅ ポート {working_port} で動作するVOICEVOXが見つかりました")
        print(f"  💡 以下のテストコードを試してください:")
        print(f"""
import requests
import json

def test_voicevox_simple():
    try:
        # バージョン確認
        response = requests.get("http://127.0.0.1:{working_port}/version", timeout=5)
        print(f"VOICEVOX Version: {{response.json()}}")
        
        # 音声合成テスト
        text = "テストです"
        speaker = 1  # 四国めたん
        
        # Step 1: audio_query
        params = {{"text": text, "speaker": speaker}}
        query_response = requests.post(
            f"http://127.0.0.1:{working_port}/audio_query", 
            params=params,
            timeout=10
        )
        
        if query_response.status_code == 200:
            print("✅ audio_query 成功")
            
            # Step 2: synthesis
            synthesis_response = requests.post(
                f"http://127.0.0.1:{working_port}/synthesis",
                params={{"speaker": speaker}},
                data=json.dumps(query_response.json()),
                headers={{"Content-Type": "application/json"}},
                timeout=30
            )
            
            if synthesis_response.status_code == 200:
                print("✅ 音声合成成功！")
                # WAVファイルとして保存
                with open("test_voice.wav", "wb") as f:
                    f.write(synthesis_response.content)
                print("test_voice.wav として保存しました")
            else:
                print(f"❌ synthesis エラー: {{synthesis_response.status_code}}")
        else:
            print(f"❌ audio_query エラー: {{query_response.status_code}}")
            
    except Exception as e:
        print(f"❌ エラー: {{e}}")

if __name__ == "__main__":
    test_voicevox_simple()
        """)
    else:
        print("  ❌ 動作するVOICEVOXエンジンが見つかりません")
        print("  💡 対処法:")
        print("    1. VOICEVOXを再起動してください")
        print("    2. 設定ファイルをリセットしてください")
        print("    3. ファイアウォールの設定を確認してください")

if __name__ == "__main__":
    comprehensive_diagnosis()