#!/usr/bin/env python3
"""
プレイリスト動画数デバッグスクリプト

実際の動画数と読み取り数の差異を調査
"""

import sys
from pathlib import Path

# パス設定
sys.path.append('.')

from storage.unified_storage import UnifiedStorage
from managers.playlist_config_manager import PlaylistConfigManager

def debug_playlist_videos():
    """プレイリスト動画数をデバッグ"""
    print("=== プレイリスト動画数デバッグ ===")
    
    storage = UnifiedStorage()
    config_manager = PlaylistConfigManager()
    
    # データベースと設定を読み込み
    db = storage.load_database()
    configs = config_manager.list_configs()
    
    target_playlist_id = "PLKosfnGdlrBXVS-zL2aeOjkrXjKCL6drp"
    
    print(f"調査対象: {target_playlist_id}")
    print()
    
    # 1. 設定情報確認
    config = config_manager.get_config(target_playlist_id)
    if config:
        print("📋 設定情報:")
        print(f"   表示名: {config.display_name}")
        print(f"   有効: {config.enabled}")
        print(f"   作成日: {config.created_at}")
    else:
        print("❌ 設定が見つかりません")
    print()
    
    # 2. データベース内のプレイリスト情報
    if target_playlist_id in db.playlists:
        playlist = db.playlists[target_playlist_id]
        print("🗃️ データベース内プレイリスト:")
        print(f"   タイトル: {playlist.metadata.title}")
        print(f"   説明: {playlist.metadata.description}")
        print(f"   チャンネル: {playlist.metadata.channel_title}")
        print(f"   アイテム数（メタデータ）: {playlist.metadata.item_count}")
        print(f"   video_ids数: {len(playlist.video_ids)}")
        print(f"   total_videos: {playlist.total_videos}")
        print(f"   最終同期: {playlist.last_full_sync}")
        print()
        
        # video_idsの詳細
        print("📹 video_ids詳細:")
        for i, vid in enumerate(playlist.video_ids):
            exists_in_db = vid in db.videos
            print(f"   {i+1:2d}. {vid} {'✅' if exists_in_db else '❌'}")
        print()
        
    else:
        print("❌ データベースにプレイリストが見つかりません")
    
    # 3. 動画データベース内でプレイリストを参照している動画を検索
    videos_referencing_playlist = []
    for video_id, video in db.videos.items():
        if target_playlist_id in video.playlists:
            position = video.playlist_positions.get(target_playlist_id, -1)
            videos_referencing_playlist.append((position, video_id, video.metadata.title))
    
    # 位置順にソート
    videos_referencing_playlist.sort()
    
    print(f"🔍 プレイリストを参照している動画: {len(videos_referencing_playlist)}件")
    for position, video_id, title in videos_referencing_playlist:
        print(f"   位置{position:2d}: {video_id} - {title[:50]}...")
    print()
    
    # 4. 統計サマリー
    print("📊 統計サマリー:")
    if target_playlist_id in db.playlists:
        playlist = db.playlists[target_playlist_id]
        print(f"   メタデータ上のアイテム数: {playlist.metadata.item_count}")
        print(f"   video_ids配列のサイズ: {len(playlist.video_ids)}")
    
    print(f"   プレイリストを参照する動画数: {len(videos_referencing_playlist)}")
    print(f"   データベース総動画数: {len(db.videos)}")
    print()
    
    # 5. 不一致がある場合の詳細分析
    if target_playlist_id in db.playlists:
        playlist = db.playlists[target_playlist_id]
        video_ids_set = set(playlist.video_ids)
        referencing_videos_set = set(vid for _, vid, _ in videos_referencing_playlist)
        
        # video_idsにあるが参照されていない動画
        in_list_not_referenced = video_ids_set - referencing_videos_set
        # 参照されているがvideo_idsにない動画
        referenced_not_in_list = referencing_videos_set - video_ids_set
        
        if in_list_not_referenced:
            print("⚠️ video_idsにあるが動画データで参照されていない:")
            for vid in in_list_not_referenced:
                print(f"   {vid}")
            print()
        
        if referenced_not_in_list:
            print("⚠️ 動画データで参照されているがvideo_idsにない:")
            for vid in referenced_not_in_list:
                print(f"   {vid}")
            print()
    
    # 6. JSONファイル確認
    playlist_json_file = Path("D:/setsuna_bot/youtube_knowledge_system/data/playlists") / f"playlist_{target_playlist_id}.json"
    if playlist_json_file.exists():
        import json
        with open(playlist_json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        print("📄 生成されたJSONファイル:")
        print(f"   ファイル: {playlist_json_file}")
        print(f"   動画数: {len(json_data.get('videos', []))}")
        print(f"   統計: {json_data.get('statistics', {})}")
    else:
        print("❌ JSONファイルが見つかりません")

if __name__ == "__main__":
    debug_playlist_videos()