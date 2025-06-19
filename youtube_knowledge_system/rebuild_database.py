#!/usr/bin/env python3
"""
データベース再構築スクリプト

新しいプレイリストメタデータを含む統合データベースを再構築
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# パス設定
sys.path.append('.')

from storage.unified_storage import UnifiedStorage
from core.data_models import Playlist, PlaylistMetadata, ContentSource
from core.data_models import KnowledgeDatabase, Video, VideoMetadata, CreativeInsight, AnalysisStatus

def rebuild_database():
    """データベースを再構築"""
    storage = UnifiedStorage()
    
    # 現在のJSONファイルを直接読み込み
    json_file = Path("D:/setsuna_bot/youtube_knowledge_system/data/unified_knowledge_db.json")
    
    print("JSONファイルを直接読み込み...")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"ファイルから読み込んだ動画数: {len(data.get('videos', {}))}")
    print(f"ファイルから読み込んだプレイリスト数: {len(data.get('playlists', {}))}")
    
    # 新しいプレイリストIDが含まれる動画を検索
    new_playlist_id = "PLKosfnGdlrBXVS-zL2aeOjkrXjKCL6drp"
    videos_with_new_playlist = []
    
    for video_id, video_data in data.get('videos', {}).items():
        if new_playlist_id in video_data.get('playlists', []):
            position = video_data.get('playlist_positions', {}).get(new_playlist_id, 0)
            videos_with_new_playlist.append((position, video_id))
            print(f"  新プレイリスト動画: {video_id} (位置: {position})")
    
    print(f"新しいプレイリストの動画数: {len(videos_with_new_playlist)}")
    
    if not videos_with_new_playlist:
        print("❌ 新しいプレイリストの動画が見つかりません")
        return
    
    # 位置順にソート
    videos_with_new_playlist.sort()
    video_ids = [vid for pos, vid in videos_with_new_playlist]
    
    # 新しいプレイリストメタデータを手動で追加
    new_playlist_metadata = {
        "source": "youtube",
        "metadata": {
            "id": new_playlist_id,
            "title": "お手伝いした動画リスト",
            "description": "",
            "channel_title": "urihari 33",
            "channel_id": "UCovPDxnAVTyWP7kg98B5Bxg",
            "published_at": "2025-06-20T01:33:23+00:00",
            "item_count": len(video_ids),
            "collected_at": "2025-06-20T01:40:24+00:00"
        },
        "video_ids": video_ids,
        "last_full_sync": "2025-06-20T01:40:24+00:00",
        "last_incremental_sync": "2025-06-20T01:40:24+00:00",
        "total_videos": len(video_ids),
        "analyzed_videos": 0,
        "analysis_success_rate": 0.0
    }
    
    # 分析済み動画数を計算
    analyzed_count = 0
    for vid in video_ids:
        if vid in data.get('videos', {}):
            video_data = data['videos'][vid]
            if video_data.get('creative_insight') is not None:
                analyzed_count += 1
    
    new_playlist_metadata['analyzed_videos'] = analyzed_count
    new_playlist_metadata['analysis_success_rate'] = analyzed_count / len(video_ids) if video_ids else 0.0
    
    # プレイリストデータに追加
    data['playlists'][new_playlist_id] = new_playlist_metadata
    
    # 統計を更新
    data['total_playlists'] = len(data['playlists'])
    data['last_updated'] = datetime.now().isoformat()
    
    print(f"新しいプレイリストメタデータを追加:")
    print(f"  プレイリストID: {new_playlist_id}")
    print(f"  タイトル: {new_playlist_metadata['metadata']['title']}")
    print(f"  動画数: {len(video_ids)}")
    print(f"  分析済み: {analyzed_count}件")
    print(f"  分析率: {new_playlist_metadata['analysis_success_rate']:.1%}")
    
    # バックアップを作成
    backup_file = Path(f"D:/setsuna_bot/youtube_knowledge_system/data/backups/manual_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    backup_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"バックアップ作成: {backup_file}")
    with open(json_file, 'r', encoding='utf-8') as src:
        with open(backup_file, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
    
    # 修正されたデータを保存
    print("修正されたデータベースを保存...")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✅ データベース再構築完了！")
    print(f"   総プレイリスト数: {len(data['playlists'])}")
    print(f"   総動画数: {len(data['videos'])}")

if __name__ == "__main__":
    rebuild_database()