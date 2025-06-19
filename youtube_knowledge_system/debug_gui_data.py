#!/usr/bin/env python3
"""
GUI表示データデバッグスクリプト

GUIで表示される統計データの詳細を確認
"""

import sys
from pathlib import Path

# パス設定
sys.path.append('.')

from managers.playlist_manager import PlaylistManager

def debug_gui_data():
    """GUI表示データをデバッグ"""
    print("=== GUI表示データのデバッグ ===")
    
    manager = PlaylistManager()
    
    # プレイリスト状況取得
    print("プレイリスト状況を取得中...")
    status = manager.get_playlist_status()
    
    if 'error' in status:
        print(f"❌ エラー: {status['error']}")
        return
    
    print(f"設定統計: {status['config_stats']}")
    print(f"データベース統計: {status['database_stats']}")
    print()
    
    print("プレイリスト詳細:")
    for detail in status.get('playlist_details', []):
        print(f"  ID: {detail['id']}")
        print(f"  表示名: {detail['display_name']}")
        print(f"  DB内: {detail['in_database']}")
        print(f"  動画数: {detail['total_videos']}")
        print(f"  分析済み: {detail['analyzed_videos']}")
        print(f"  分析率: {detail['analysis_rate']:.1%}")
        print(f"  最終同期: {detail['last_sync']}")
        print()
    
    # 設定マネージャーの詳細確認
    print("設定マネージャーの詳細:")
    configs = manager.config_manager.list_configs()
    print(f"設定数: {len(configs)}")
    
    for config in configs:
        print(f"  プレイリストID: {config.playlist_id}")
        print(f"  表示名: {config.display_name}")
        print(f"  有効: {config.enabled}")
        print()
    
    # ストレージの詳細確認
    print("ストレージの詳細:")
    db = manager.storage.load_database()
    print(f"総動画数: {len(db.videos)}")
    print(f"総プレイリスト数: {len(db.playlists)}")
    print(f"プレイリストリスト: {list(db.playlists.keys())}")
    
    # 新しいプレイリストIDを検索
    new_playlist_id = "PLKosfnGdlrBXVS-zL2aeOjkrXjKCL6drp"
    if new_playlist_id in db.playlists:
        playlist = db.playlists[new_playlist_id]
        print(f"新しいプレイリスト発見:")
        print(f"  タイトル: {playlist.metadata.title}")
        print(f"  動画数: {len(playlist.video_ids)}")
    else:
        print(f"❌ 新しいプレイリスト {new_playlist_id} が見つかりません")
    
    # 動画内の新しいプレイリスト参照を確認
    videos_with_new_playlist = []
    for video_id, video in db.videos.items():
        if new_playlist_id in video.playlists:
            videos_with_new_playlist.append(video_id)
    
    print(f"新しいプレイリストを参照する動画数: {len(videos_with_new_playlist)}")
    if videos_with_new_playlist:
        print(f"  最初の5件: {videos_with_new_playlist[:5]}")

if __name__ == "__main__":
    debug_gui_data()