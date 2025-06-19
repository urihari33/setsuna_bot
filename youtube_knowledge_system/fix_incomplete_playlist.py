#!/usr/bin/env python3
"""
不完全なプレイリストデータ修復スクリプト

データベースに不足している動画を追加し、プレイリストを完全な状態に修復
"""

import sys
from pathlib import Path

# パス設定
sys.path.append('.')

from collectors.multi_playlist_collector import MultiPlaylistCollector
from managers.playlist_config_manager import PlaylistConfigManager
from storage.unified_storage import UnifiedStorage

def fix_incomplete_playlist():
    """不完全なプレイリストデータを修復"""
    print("=== 不完全プレイリストデータ修復 ===")
    
    # 修復対象プレイリスト
    playlist_id = "PLKosfnGdlrBXVS-zL2aeOjkrXjKCL6drp"
    
    print(f"修復対象: {playlist_id}")
    print()
    
    # 初期化
    collector = MultiPlaylistCollector()
    config_manager = PlaylistConfigManager()
    storage = UnifiedStorage()
    
    # API初期化
    if not collector._initialize_service():
        print("❌ API初期化失敗")
        return
    
    print("✅ YouTube API接続成功")
    
    # プレイリスト設定取得
    config = config_manager.get_config(playlist_id)
    if not config:
        print("❌ プレイリスト設定が見つかりません")
        return
    
    print(f"設定確認: {config.display_name}")
    print()
    
    # 現在のデータベース状態確認
    db = storage.load_database()
    if playlist_id in db.playlists:
        current_playlist = db.playlists[playlist_id]
        print(f"📊 現在のデータベース状態:")
        print(f"   データベース内動画数: {len(current_playlist.video_ids)}")
        print(f"   メタデータ上動画数: {current_playlist.metadata.item_count}")
        print(f"   不足動画数: {current_playlist.metadata.item_count - len(current_playlist.video_ids)}")
    else:
        print("❌ データベースにプレイリストが見つかりません")
        return
    
    print()
    
    # プレイリスト再収集実行
    print("🔄 プレイリスト再収集開始...")
    success, message, result = collector.process_single_playlist(config)
    
    if success:
        print(f"✅ 修復完了: {message}")
        print(f"   処理結果: {result}")
        
        # 修復後の状態確認
        db_updated = storage.load_database()
        if playlist_id in db_updated.playlists:
            updated_playlist = db_updated.playlists[playlist_id]
            print(f"📊 修復後のデータベース状態:")
            print(f"   データベース内動画数: {len(updated_playlist.video_ids)}")
            print(f"   メタデータ上動画数: {updated_playlist.metadata.item_count}")
            print(f"   新規追加動画数: {result.get('new_videos', 0)}")
            print(f"   更新動画数: {result.get('updated_videos', 0)}")
            
            # JSONファイル確認
            playlist_json_file = Path("D:/setsuna_bot/youtube_knowledge_system/data/playlists") / f"playlist_{playlist_id}.json"
            if playlist_json_file.exists():
                print(f"   ✅ JSONファイル生成済み: {playlist_json_file}")
            else:
                print(f"   ⚠️ JSONファイル未生成")
        
        print(f"\n🎉 プレイリスト修復完了")
        
    else:
        print(f"❌ 修復失敗: {message}")
        if result.get('errors'):
            print("エラー詳細:")
            for error in result['errors']:
                print(f"  - {error}")

if __name__ == "__main__":
    fix_incomplete_playlist()