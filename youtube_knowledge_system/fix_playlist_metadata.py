#!/usr/bin/env python3
"""
プレイリストメタデータ修正スクリプト

新しく追加されたプレイリストのメタデータを統合データベースに追加
"""

import sys
from pathlib import Path

# パス設定
sys.path.append('.')

from storage.unified_storage import UnifiedStorage
from core.data_models import Playlist, PlaylistMetadata, ContentSource
from datetime import datetime

def fix_playlist_metadata():
    """プレイリストメタデータを修正"""
    storage = UnifiedStorage()
    db = storage.load_database()
    
    # 新しいプレイリストID
    new_playlist_id = "PLKosfnGdlrBXVS-zL2aeOjkrXjKCL6drp"
    
    print(f"現在のプレイリスト数: {len(db.playlists)}")
    print(f"プレイリストリスト: {list(db.playlists.keys())}")
    
    # 既に存在するかチェック
    if new_playlist_id in db.playlists:
        print(f"✅ プレイリスト {new_playlist_id} は既に存在します")
        playlist = db.playlists[new_playlist_id]
        print(f"   タイトル: {playlist.metadata.title}")
        print(f"   動画数: {len(playlist.video_ids)}")
        return
    
    # 新しいプレイリストの動画IDを収集
    video_ids_in_playlist = []
    print(f"総動画数: {len(db.videos)}")
    
    for video_id, video in db.videos.items():
        if new_playlist_id in video.playlists:
            position = video.playlist_positions.get(new_playlist_id, 0)
            video_ids_in_playlist.append((position, video_id))
            print(f"  動画発見: {video_id} (位置: {position})")
    
    print(f"プレイリスト内の動画: {len(video_ids_in_playlist)}件")
    
    # 位置順にソート
    video_ids_in_playlist.sort()
    video_ids = [vid for pos, vid in video_ids_in_playlist]
    
    print(f"新しいプレイリスト用の動画を発見: {len(video_ids)}件")
    
    if not video_ids:
        print("❌ 新しいプレイリストの動画が見つかりません")
        return
    
    # プレイリストメタデータを作成
    playlist_metadata = PlaylistMetadata(
        id=new_playlist_id,
        title="お手伝いした動画リスト",
        description="",
        channel_title="urihari 33",  # 推定
        channel_id="UCovPDxnAVTyWP7kg98B5Bxg",  # 推定
        published_at=datetime.now(),
        item_count=len(video_ids),
        collected_at=datetime.now()
    )
    
    # プレイリストオブジェクトを作成
    playlist = Playlist(
        source=ContentSource.YOUTUBE,
        metadata=playlist_metadata,
        video_ids=video_ids,
        last_full_sync=datetime.now(),
        last_incremental_sync=datetime.now(),
        sync_settings={},
        total_videos=len(video_ids),
        analyzed_videos=0,  # 後で更新
        analysis_success_rate=0.0,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # 分析済み動画数を計算
    analyzed_count = sum(1 for vid in video_ids if vid in db.videos and db.videos[vid].creative_insight is not None)
    playlist.analyzed_videos = analyzed_count
    playlist.analysis_success_rate = analyzed_count / len(video_ids) if video_ids else 0.0
    
    # データベースに追加
    db.playlists[new_playlist_id] = playlist
    
    # 統計を更新
    db.total_playlists = len(db.playlists)
    db.last_updated = datetime.now()
    
    # 保存
    storage._database = db
    try:
        storage.save_database()
        print(f"✅ プレイリストメタデータを追加しました:")
        print(f"   プレイリストID: {new_playlist_id}")
        print(f"   タイトル: {playlist.metadata.title}")
        print(f"   動画数: {len(video_ids)}")
        print(f"   分析済み: {analyzed_count}件")
        print(f"   分析率: {playlist.analysis_success_rate:.1%}")
    except Exception as e:
        print(f"❌ データベース保存に失敗しました: {e}")

if __name__ == "__main__":
    fix_playlist_metadata()