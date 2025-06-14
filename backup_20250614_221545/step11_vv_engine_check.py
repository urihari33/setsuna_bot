#!/usr/bin/env python3
"""ステップ11: vv-engineフォルダの詳細確認"""

import subprocess

def check_vv_engine_folder():
    """vv-engineフォルダの中身を確認"""
    print("🔍 vv-engine フォルダ内容確認")
    print("="*40)
    
    vv_engine_path = "C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX\\vv-engine"
    
    # vv-engineフォルダの存在確認
    print(f"📁 パス: {vv_engine_path}")
    
    cmd = ['powershell.exe', '-Command', f'Test-Path "{vv_engine_path}"']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip().lower() == 'true':
            print("✅ vv-engineフォルダ存在")
            
            # フォルダ内容の詳細確認
            list_cmd = ['powershell.exe', '-Command', 
                       f'Get-ChildItem -Path "{vv_engine_path}" -Recurse | Format-Table Name,Length,FullName']
            
            try:
                list_result = subprocess.run(list_cmd, capture_output=True, text=True, timeout=15)
                if list_result.returncode == 0:
                    print("📋 vv-engine内容:")
                    print(list_result.stdout)
                else:
                    print("❌ 内容確認失敗")
            except Exception as e:
                print(f"❌ 内容確認エラー: {e}")
                
        else:
            print("❌ vv-engineフォルダ不存在")
            return False
            
    except Exception as e:
        print(f"❌ 確認エラー: {e}")
        return False
    
    return True

def find_engine_executables():
    """エンジン実行ファイルを検索"""
    print(f"\n🔍 エンジン実行ファイル検索")
    print("="*35)
    
    search_paths = [
        "C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX\\vv-engine",
        "C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX"
    ]
    
    for path in search_paths:
        print(f"\n📂 検索パス: {path}")
        
        # .exeファイルを検索
        cmd = ['powershell.exe', '-Command', 
               f'Get-ChildItem -Path "{path}" -Name "*.exe" -Recurse -ErrorAction SilentlyContinue']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                print("✅ 発見された実行ファイル:")
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        print(f"  {line.strip()}")
            else:
                print("❌ 実行ファイルなし")
        except Exception as e:
            print(f"❌ 検索エラー: {e}")

def check_voicevox_exe_options():
    """VOICEVOX.exeのオプション確認"""
    print(f"\n🔍 VOICEVOX.exe オプション確認")
    print("="*40)
    
    voicevox_exe = "C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX\\VOICEVOX.exe"
    
    # --helpオプションで確認
    help_cmd = ['powershell.exe', '-Command', f'& "{voicevox_exe}" --help']
    
    print(f"📋 VOICEVOX.exe --help の結果:")
    try:
        result = subprocess.run(help_cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ ヘルプ出力:")
            print(result.stdout)
        else:
            print("❌ ヘルプ取得失敗")
            if result.stderr:
                print(f"エラー: {result.stderr}")
    except Exception as e:
        print(f"❌ ヘルプ確認エラー: {e}")

def provide_new_solutions():
    """新しい解決策を提供"""
    print(f"\n💡 新しいアプローチ")
    print("="*25)
    
    print(f"【方法1: VOICEVOX.exe でエンジンも起動】")
    print(f"最新のVOICEVOXは統合されている可能性があります")
    print(f"管理者コマンドプロンプトで:")
    print(f'"C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX\\VOICEVOX.exe" --host=0.0.0.0')
    print(f"")
    
    print(f"【方法2: vv-engine内のファイル実行】")
    print(f"vv-engineフォルダに実行ファイルがある場合:")
    print(f"（上記の検索結果に基づいて決定）")
    print(f"")
    
    print(f"【方法3: 環境変数設定】")
    print(f"VOICEVOX起動前に環境変数を設定:")
    print(f"set VOICEVOX_ENGINE_HOST=0.0.0.0")
    print(f'"C:\\Users\\coszi\\AppData\\Local\\Programs\\VOICEVOX\\VOICEVOX.exe"')
    print(f"")
    
    print(f"【方法4: 設定ファイル確認】")
    print(f"VOICEVOXの設定ファイルでホスト設定を変更できる可能性")

def main():
    """メイン実行"""
    print("🔧 VOICEVOX v0.23.1 新構成の調査")
    print("="*40)
    
    print("💡 run.exeが見つからないため、新しい構成を調査します")
    
    # 1. vv-engineフォルダ確認
    vv_engine_exists = check_vv_engine_folder()
    
    # 2. 実行ファイル検索
    find_engine_executables()
    
    # 3. VOICEVOX.exeのオプション確認
    check_voicevox_exe_options()
    
    # 4. 新しい解決策提供
    provide_new_solutions()
    
    print(f"\n🎯 次のステップ:")
    print(f"1. 上記の検索結果を確認")
    print(f"2. vv-engine内にエンジンファイルがあるか確認")
    print(f"3. VOICEVOX.exeで--hostオプションが使えるかテスト")

if __name__ == "__main__":
    main()