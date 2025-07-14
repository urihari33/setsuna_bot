#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パス修正テスト
Windows/WSL2パス問題の解決確認
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.activity_learning_engine import ActivityLearningEngine

def test_path_consistency():
    """パス一貫性テスト"""
    print("=== パス一貫性テスト ===")
    
    try:
        # エンジン初期化
        engine = ActivityLearningEngine()
        print("✅ ActivityLearningEngine初期化成功")
        
        # パス設定確認
        sessions_dir = engine.sessions_dir
        print(f"📁 セッションディレクトリ: {sessions_dir}")
        print(f"🔍 ディレクトリ存在: {sessions_dir.exists()}")
        
        # セッション作成
        session_id = engine.create_session(
            theme="パス修正テスト",
            learning_type="概要",
            depth_level=1,
            time_limit=30,  # 30秒
            budget_limit=0.1,
            tags=["パス修正"]
        )
        
        print(f"📝 セッション作成: {session_id}")
        
        # ファイルパス構築
        session_file = sessions_dir / f"{session_id}.json"
        windows_path = Path(f"D:/setsuna_bot/data/activity_knowledge/sessions/{session_id}.json")
        wsl_path = Path(f"/mnt/d/setsuna_bot/data/activity_knowledge/sessions/{session_id}.json")
        
        print(f"🎯 予想ファイルパス: {session_file}")
        print(f"🪟 Windowsパス: {windows_path}")
        print(f"🐧 WSLパス: {wsl_path}")
        
        # 初期ファイル確認
        print(f"\n📊 初期状態:")
        print(f"  セッションファイル存在: {session_file.exists()}")
        print(f"  Windowsパス存在: {windows_path.exists()}")
        print(f"  WSLパス存在: {wsl_path.exists()}")
        
        if session_file.exists():
            initial_size = session_file.stat().st_size
            print(f"  初期ファイルサイズ: {initial_size}bytes")
        
        # セッション開始
        print(f"\n🚀 セッション開始...")
        success = engine.start_session(session_id)
        
        if not success:
            print("❌ セッション開始失敗")
            return False
        
        print("✅ セッション開始成功")
        
        # データ収集待機
        print("⏳ データ収集待機中...")
        max_wait = 45  # 45秒待機
        wait_time = 0
        
        while wait_time < max_wait:
            time.sleep(5)
            wait_time += 5
            
            # 3つのパスをすべて確認
            session_exists = session_file.exists()
            windows_exists = windows_path.exists()
            wsl_exists = wsl_path.exists()
            
            print(f"⏰ {wait_time}秒: セッション={session_exists}, Windows={windows_exists}, WSL={wsl_exists}")
            
            # データ確認
            if session_exists:
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    metadata = session_data.get("session_metadata", {})
                    status = metadata.get("status", "unknown")
                    phase = metadata.get("current_phase", "unknown")
                    collected_items = metadata.get("collected_items", 0)
                    
                    print(f"    状態: {status}/{phase}, 収集: {collected_items}件")
                    
                    # 完了チェック
                    if status in ["completed", "error", "cancelled"]:
                        print(f"🎯 セッション終了: {status}")
                        break
                        
                except json.JSONDecodeError:
                    print(f"    ⚠️ JSON解析エラー")
                except Exception as e:
                    print(f"    ⚠️ 読み取りエラー: {e}")
        
        # 最終確認
        print(f"\n🏁 最終確認:")
        
        final_session_exists = session_file.exists()
        final_windows_exists = windows_path.exists()
        final_wsl_exists = wsl_path.exists()
        
        print(f"  セッションファイル存在: {final_session_exists}")
        print(f"  Windowsパス存在: {final_windows_exists}")
        print(f"  WSLパス存在: {final_wsl_exists}")
        
        # パス一貫性チェック
        if final_session_exists == final_windows_exists:
            print("✅ パス一貫性確認: セッション=Windows")
        else:
            print("❌ パス不一致: セッション≠Windows")
        
        if final_wsl_exists and not final_windows_exists:
            print("⚠️ WSLパスのみ存在（修正前の状態）")
        
        # 実際のデータ確認
        if final_session_exists:
            file_size = session_file.stat().st_size
            print(f"  ファイルサイズ: {file_size}bytes")
            
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    final_data = json.load(f)
                
                print(f"  データキー: {list(final_data.keys())}")
                
                # 収集結果確認
                collection_results = final_data.get("collection_results")
                if collection_results:
                    sources = collection_results.get("information_sources", [])
                    print(f"  収集ソース数: {len(sources)}")
                    return len(sources) > 0
                else:
                    print("  収集結果なし")
                    return False
            except Exception as e:
                print(f"  ❌ データ読み取りエラー: {e}")
                return False
        else:
            print("  ❌ ファイル不存在")
            return False
            
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    print("🔧 パス修正テスト")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    result = test_path_consistency()
    
    print("=" * 60)
    if result:
        print("🎉 パス修正成功！正しい場所にファイルが保存されました")
        print("✅ Windows/WSL2パス問題が解決されました")
    else:
        print("❌ パス修正の効果を確認できませんでした")

if __name__ == "__main__":
    main()