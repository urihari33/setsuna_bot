#!/usr/bin/env python3
"""ステップ10: VOICEVOXファイルパス確認と修正"""

import subprocess

def check_voicevox_directory():
    """VOICEVOXディレクトリの詳細確認"""
    print("🔍 VOICEVOXディレクトリ詳細確認")
    print("="*40)
    
    # VOICEVOXフォルダが存在するか確認
    paths_to_check = [
        "C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX",
        "C:\\Program Files\\VOICEVOX", 
        "C:\\Program Files (x86)\\VOICEVOX",
        "C:\\Users\\coszi\\Desktop\\VOICEVOX",
        "C:\\VOICEVOX"
    ]
    
    for path in paths_to_check:
        print(f"\n📁 チェック中: {path}")
        cmd = ['powershell.exe', '-Command', f'Test-Path "{path}"']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                exists = result.stdout.strip().lower() == 'true'
                if exists:
                    print(f"  ✅ フォルダ存在")
                    
                    # フォルダ内容確認
                    list_cmd = ['powershell.exe', '-Command', 
                              f'Get-ChildItem -Path "{path}" | Format-Table Name,Length']
                    
                    try:
                        list_result = subprocess.run(list_cmd, capture_output=True, text=True, timeout=10)
                        if list_result.returncode == 0:
                            print(f"  📋 フォルダ内容:")
                            print(f"    {list_result.stdout}")
                    except:
                        pass
                else:
                    print(f"  ❌ フォルダ不存在")
        except Exception as e:
            print(f"  ❌ 確認エラー: {e}")

def find_run_exe():
    """run.exe の正確な場所を検索"""
    print(f"\n🔍 run.exe ファイル検索")
    print("="*30)
    
    # Cドライブ全体でrun.exeを検索
    search_cmd = ['powershell.exe', '-Command', 
                  'Get-ChildItem -Path "C:\\" -Name "run.exe" -Recurse -ErrorAction SilentlyContinue | Where-Object {$_ -like "*voicevox*"}']
    
    try:
        result = subprocess.run(search_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            print(f"✅ run.exe ファイルが見つかりました:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"  {line}")
        else:
            print(f"❌ run.exe が見つかりません")
            
            # 代替検索: VOICEVOX関連の実行ファイル全体を検索
            alt_cmd = ['powershell.exe', '-Command', 
                      'Get-ChildItem -Path "C:\\" -Name "*.exe" -Recurse -ErrorAction SilentlyContinue | Where-Object {$_ -like "*voicevox*"}']
            
            print(f"\n🔍 代替検索: VOICEVOX関連実行ファイル")
            try:
                alt_result = subprocess.run(alt_cmd, capture_output=True, text=True, timeout=30)
                if alt_result.returncode == 0 and alt_result.stdout.strip():
                    print(f"✅ VOICEVOX関連ファイル:")
                    for line in alt_result.stdout.strip().split('\n'):
                        if line.strip():
                            print(f"  {line}")
            except Exception as e:
                print(f"❌ 代替検索エラー: {e}")
                
    except Exception as e:
        print(f"❌ 検索エラー: {e}")

def provide_manual_commands():
    """手動実行用のコマンド提供"""
    print(f"\n💡 手動実行用コマンド集")
    print("="*35)
    
    print(f"【パターン1: 絶対パスで実行】")
    print(f'管理者コマンドプロンプトで以下を実行:')
    print(f'"C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX\\run.exe" --host 0.0.0.0')
    print(f"")
    
    print(f"【パターン2: cdコマンドで移動後実行】")
    print(f'1. cd "C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX"')
    print(f'2. dir (ファイル一覧確認)')
    print(f'3. .\\run.exe --host 0.0.0.0')
    print(f"")
    
    print(f"【パターン3: PowerShell版】")
    print(f'管理者PowerShellで以下を実行:')
    print(f'& "C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX\\run.exe" --host 0.0.0.0')
    print(f"")
    
    print(f"【パターン4: エクスプローラー経由】")
    print(f'1. エクスプローラーで以下を開く:')
    print(f'   C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX')
    print(f'2. run.exe があることを確認')
    print(f'3. アドレスバーに "cmd" と入力してEnter')
    print(f'4. .\\run.exe --host 0.0.0.0')
    print(f"")
    
    print(f"【デバッグ用: 現在地確認】")
    print(f'コマンドプロンプトで以下を実行して現在地確認:')
    print(f'cd')
    print(f'dir')

def check_current_status():
    """現在のVOICEVOX状況確認"""
    print(f"\n📊 現在のVOICEVOX状況")
    print("="*30)
    
    # プロセス確認
    try:
        proc_cmd = ['powershell.exe', '-Command', 
                   'Get-Process | Where-Object {$_.ProcessName -like "*voicevox*"} | Format-Table ProcessName,Id,Path']
        result = subprocess.run(proc_cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print(f"✅ 実行中のVOICEVOXプロセス:")
                print(f"  {result.stdout}")
            else:
                print(f"❌ VOICEVOXプロセスは実行されていません")
    except Exception as e:
        print(f"❌ プロセス確認エラー: {e}")
    
    # ポート確認
    try:
        port_cmd = ['powershell.exe', '-Command', 'netstat -an | findstr :50021']
        result = subprocess.run(port_cmd, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and result.stdout.strip():
            print(f"\n✅ ポート50021の状況:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"  {line}")
        else:
            print(f"\n❌ ポート50021は使用されていません")
    except Exception as e:
        print(f"❌ ポート確認エラー: {e}")

def main():
    """メイン実行"""
    print("🔧 VOICEVOXパス問題の詳細調査と解決")
    print("="*50)
    
    # 1. ディレクトリ確認
    check_voicevox_directory()
    
    # 2. run.exe検索
    find_run_exe()
    
    # 3. 現在状況確認
    check_current_status()
    
    # 4. 手動実行コマンド提供
    provide_manual_commands()
    
    print(f"\n🎯 次のアクション:")
    print(f"1. 上記の検索結果から正しいパスを確認")
    print(f"2. 提供されたコマンドパターンのいずれかを実行")
    print(f"3. run.exe が見つからない場合はVOICEVOXの再インストール検討")

if __name__ == "__main__":
    main()