#!/usr/bin/env python3
"""VOICEVOXログ確認ツール"""

import os
import platform
from pathlib import Path
import datetime

def find_voicevox_logs():
    """VOICEVOXのログファイルを検索"""
    system = platform.system()
    possible_paths = []
    
    if system == "Windows":
        username = os.getenv('USERNAME')
        possible_paths = [
            f"C:/Users/{username}/AppData/Roaming/voicevox/logs",
            f"C:/Users/{username}/AppData/Roaming/voicevox-cpu/logs",
            f"C:/Users/{username}/AppData/Local/Programs/VOICEVOX/logs",
        ]
    elif system == "Darwin":  # macOS
        username = os.getenv('USER')
        possible_paths = [
            f"/Users/{username}/Library/Logs/voicevox",
            f"/Users/{username}/Library/Application Support/voicevox/logs",
        ]
    elif system == "Linux":
        username = os.getenv('USER')
        possible_paths = [
            f"/home/{username}/.config/voicevox/logs",
            f"/home/{username}/.local/share/voicevox/logs",
        ]
    
    print(f"🔍 {system} でログファイルを検索中...")
    
    existing_paths = []
    for path_str in possible_paths:
        path = Path(path_str)
        if path.exists():
            existing_paths.append(path)
            print(f"✅ 発見: {path}")
        else:
            print(f"❌ なし: {path}")
    
    return existing_paths

def read_recent_logs(log_dir, lines=50):
    """最新のログを読み取り"""
    log_files = []
    
    # ログファイルを検索
    for ext in ['*.log', '*.txt']:
        log_files.extend(list(log_dir.glob(ext)))
    
    if not log_files:
        print(f"  ❌ {log_dir} にログファイルが見つかりません")
        return
    
    # 最新のファイルを取得
    latest_file = max(log_files, key=os.path.getmtime)
    file_time = datetime.datetime.fromtimestamp(os.path.getmtime(latest_file))
    
    print(f"  📄 最新ログ: {latest_file.name}")
    print(f"  🕒 更新時刻: {file_time}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines_list = f.readlines()
            
        print(f"  📊 総行数: {len(lines_list)}")
        
        # 最後のN行を表示
        recent_lines = lines_list[-lines:]
        
        print(f"\n  📋 最新 {len(recent_lines)} 行:")
        print("  " + "="*60)
        
        for i, line in enumerate(recent_lines, 1):
            print(f"  {len(recent_lines)-len(recent_lines)+i:3d}: {line.rstrip()}")
            
        print("  " + "="*60)
        
        # エラーキーワードを検索
        error_keywords = ['error', 'ERROR', 'failed', 'FAILED', 'exception', 'Exception']
        error_lines = []
        
        for i, line in enumerate(lines_list):
            for keyword in error_keywords:
                if keyword in line:
                    error_lines.append((i+1, line.strip()))
                    break
        
        if error_lines:
            print(f"\n  ⚠️ エラー関連のログ ({len(error_lines)}件):")
            for line_no, content in error_lines[-10:]:  # 最新10件
                print(f"    行{line_no}: {content}")
        else:
            print(f"\n  ✅ エラー関連のログは見つかりませんでした")
            
    except Exception as e:
        print(f"  ❌ ログ読み取りエラー: {e}")

def check_voicevox_processes():
    """VOICEVOXプロセスの詳細確認"""
    print(f"\n🔍 プロセス詳細確認...")
    
    try:
        import psutil
        
        voicevox_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'memory_info']):
            try:
                name = proc.info['name'].lower()
                cmdline = ' '.join(proc.info['cmdline'] or []).lower()
                
                if 'voicevox' in name or 'voicevox' in cmdline:
                    memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                    voicevox_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'status': proc.info['status'],
                        'memory_mb': memory_mb,
                        'cmdline': proc.info['cmdline']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if voicevox_processes:
            print(f"  ✅ VOICEVOX関連プロセス ({len(voicevox_processes)}個):")
            for proc in voicevox_processes:
                print(f"    PID {proc['pid']}: {proc['name']}")
                print(f"      状態: {proc['status']}")
                print(f"      メモリ: {proc['memory_mb']:.1f} MB")
                if proc['cmdline']:
                    print(f"      コマンド: {' '.join(proc['cmdline'])}")
                print()
        else:
            print(f"  ❌ VOICEVOX関連プロセスが見つかりません")
            
    except ImportError:
        print(f"  ⚠️ psutil がインストールされていません")
        print(f"    pip install psutil で詳細確認が可能になります")

def main():
    """メイン実行"""
    print("🔧 VOICEVOX ログ＆プロセス確認ツール")
    print("="*60)
    
    # 1. ログファイル検索
    log_dirs = find_voicevox_logs()
    
    if log_dirs:
        print(f"\n📋 ログ内容確認:")
        for log_dir in log_dirs:
            print(f"\n📁 {log_dir}:")
            read_recent_logs(log_dir)
    else:
        print(f"\n❌ ログファイルが見つかりませんでした")
        print(f"💡 VOICEVOXが一度も起動していない可能性があります")
    
    # 2. プロセス確認
    check_voicevox_processes()
    
    # 3. 手動確認項目
    print(f"\n💡 手動で確認してください:")
    print(f"1. VOICEVOXアプリが起動していますか？")
    print(f"2. エンジン設定画面の表示内容")
    print(f"3. メインウィンドウのエラーメッセージ")
    print(f"4. タスクマネージャーでCPU/メモリ使用率")

if __name__ == "__main__":
    main()