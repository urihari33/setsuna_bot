"""
既存データから統一システムへの移行スクリプト

現在のデータを新しい統一データモデルに移行してテスト
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# パッケージパスを追加
sys.path.append(str(Path(__file__).parent))

from core.data_models import (
    Video, Playlist, VideoMetadata, PlaylistMetadata, 
    ContentSource, AnalysisStatus, CreatorInfo, MusicInfo, CreativeInsight,
    create_empty_database
)
from storage.unified_storage import UnifiedStorage


def migrate_playlist_data(playlist_file: Path, storage: UnifiedStorage) -> str:
    """プレイリストデータを移行"""
    print(f"プレイリストファイルを移行中: {playlist_file}")
    
    with open(playlist_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # プレイリストメタデータ作成
    playlist_info = data['playlist_info']
    playlist_metadata = PlaylistMetadata(
        id=playlist_info['id'],
        title=playlist_info['title'],
        description=playlist_info['description'],
        channel_title=playlist_info['channel_title'],
        channel_id=playlist_info['channel_id'],
        published_at=datetime.fromisoformat(playlist_info['published_at'].replace('Z', '+00:00')),
        item_count=playlist_info['item_count'],
        collected_at=datetime.fromisoformat(data['last_updated'])
    )
    
    # 動画データを移行
    video_ids = []
    for video_data in data['videos']:
        # VideoMetadata作成
        video_metadata = VideoMetadata(
            id=video_data['id'],
            title=video_data['title'],
            description=video_data['description'],
            published_at=datetime.fromisoformat(video_data['published_at'].replace('Z', '+00:00')),
            channel_title=video_data['channel_title'],
            channel_id=video_data['channel_id'],
            duration=video_data['duration'],
            view_count=int(video_data.get('view_count', 0)),
            like_count=int(video_data.get('like_count', 0)),
            comment_count=int(video_data.get('comment_count', 0)),
            tags=video_data.get('tags', []),
            category_id=video_data.get('category_id', ''),
            collected_at=datetime.fromisoformat(video_data['collected_at'])
        )
        
        # Video作成
        video = Video(
            source=ContentSource.YOUTUBE,
            metadata=video_metadata,
            playlists=[playlist_info['id']],
            playlist_positions={playlist_info['id']: video_data.get('position', 0)},
            analysis_status=AnalysisStatus.PENDING,
            creative_insight=None,
            analysis_error=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        storage.add_video(video)
        video_ids.append(video_data['id'])
    
    # Playlist作成
    playlist = Playlist(
        source=ContentSource.YOUTUBE,
        metadata=playlist_metadata,
        video_ids=video_ids,
        last_full_sync=datetime.fromisoformat(data['last_updated']),
        last_incremental_sync=None,
        sync_settings={},
        total_videos=data['total_videos'],
        analyzed_videos=0,
        analysis_success_rate=0.0,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    storage.add_playlist(playlist)
    print(f"プレイリスト移行完了: {playlist_info['title']} ({len(video_ids)}動画)")
    return playlist_info['id']


def migrate_analysis_data(analysis_file: Path, storage: UnifiedStorage):
    """分析データを移行"""
    print(f"分析ファイルを移行中: {analysis_file}")
    
    with open(analysis_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # creative_insights から各動画の分析結果を抽出
    if 'videos' in data:
        for video_data in data['videos']:
            video_id = video_data['id']
            video = storage.get_video(video_id)
            
            if video and video_data.get('analysis'):
                analysis = video_data['analysis']
                
                # クリエイター情報の構築
                creators = []
                if 'creators' in analysis:
                    for role, creator_list in analysis['creators'].items():
                        if isinstance(creator_list, list):
                            for creator_name in creator_list:
                                creators.append(CreatorInfo(
                                    name=creator_name,
                                    role=role,
                                    confidence=analysis.get('confidence', 0.8)
                                ))
                        elif isinstance(creator_list, dict):
                            for creator_name, count in creator_list.items():
                                creators.append(CreatorInfo(
                                    name=creator_name,
                                    role=role,
                                    confidence=analysis.get('confidence', 0.8)
                                ))
                
                # 音楽情報の構築
                music_info = None
                if 'lyrics' in analysis and analysis['lyrics']:
                    music_info = MusicInfo(
                        lyrics=analysis['lyrics'],
                        genre=analysis.get('genre')
                    )
                
                # CreativeInsight作成
                creative_insight = CreativeInsight(
                    creators=creators,
                    music_info=music_info,
                    tools_used=analysis.get('tools', []),
                    themes=analysis.get('themes', []),
                    visual_elements=[],
                    analysis_confidence=analysis.get('confidence', 0.8),
                    analysis_timestamp=datetime.fromisoformat(analysis.get('timestamp', datetime.now().isoformat())),
                    analysis_model=analysis.get('model', 'GPT-4')
                )
                
                # 動画を更新
                video.creative_insight = creative_insight
                video.analysis_status = AnalysisStatus.COMPLETED
                video.updated_at = datetime.now()
                
                storage.add_video(video)  # 更新保存
    
    # 統計情報から全体的な分析結果を統合
    elif 'creative_insights' in data:
        insights = data['creative_insights']
        print(f"統計ベースの分析データを処理中: {len(insights.get('creators', {}).get('vocal', {}))}ボーカル, {len(insights.get('creators', {}).get('movie', {}))}映像制作者")
        
        # 統計データから個別動画への分析結果の推定は困難
        # 実際の分析済み動画数を更新するのみ
        if 'analysis_info' in data:
            analysis_info = data['analysis_info']
            analyzed_count = analysis_info.get('analyzed_videos', 0)
            success_rate = analysis_info.get('analysis_success_rate', 0.0)
            
            # プレイリストの統計を更新
            db = storage.load_database()
            for playlist in db.playlists.values():
                playlist.analyzed_videos = analyzed_count
                playlist.analysis_success_rate = success_rate
                storage.add_playlist(playlist)
            
            print(f"分析統計を更新: {analyzed_count}動画分析済み, 成功率{success_rate:.2%}")
    
    print("分析データ移行完了")


def test_unified_system(storage: UnifiedStorage):
    """統一システムのテスト"""
    print("\n=== 統一システムテスト ===")
    
    # 統計情報取得
    stats = storage.get_statistics()
    print(f"総動画数: {stats['total_videos']}")
    print(f"総プレイリスト数: {stats['total_playlists']}")
    print(f"分析済み動画数: {stats['analyzed_videos']}")
    print(f"分析成功率: {stats['analysis_success_rate']:.2%}")
    print(f"クリエイター数: {stats['total_creators']}")
    
    # 検索テスト
    print("\n--- 検索テスト ---")
    creators = storage.get_all_creators()[:5]
    for creator in creators:
        videos = storage.search_videos_by_creator(creator)
        print(f"クリエイター '{creator}': {len(videos)}動画")
    
    # タグ検索テスト
    tags = storage.get_all_tags()[:3]
    for tag in tags:
        videos = storage.search_videos_by_tag(tag)
        print(f"タグ '{tag}': {len(videos)}動画")
    
    # プレイリスト動画取得テスト
    db = storage.load_database()
    for playlist_id in list(db.playlists.keys())[:2]:
        videos = storage.get_videos_by_playlist(playlist_id)
        playlist = db.playlists[playlist_id]
        print(f"プレイリスト '{playlist.metadata.title}': {len(videos)}動画")


def main():
    """メイン実行"""
    print("=== 統一システム移行開始 ===")
    
    # ストレージ初期化
    storage = UnifiedStorage()
    
    # データディレクトリのパス
    data_dir = Path("/mnt/d/setsuna_bot/youtube_knowledge_system/data")
    
    # 既存ファイルを確認
    playlist_files = list(data_dir.glob("playlists/playlist_*.json"))
    analysis_files = list(data_dir.glob("analyzed_*.json"))
    
    print(f"発見されたプレイリストファイル: {len(playlist_files)}")
    print(f"発見された分析ファイル: {len(analysis_files)}")
    
    # プレイリストデータ移行
    migrated_playlists = []
    for playlist_file in playlist_files:
        try:
            playlist_id = migrate_playlist_data(playlist_file, storage)
            migrated_playlists.append(playlist_id)
        except Exception as e:
            print(f"プレイリスト移行エラー {playlist_file}: {e}")
    
    # 分析データ移行
    for analysis_file in analysis_files:
        try:
            migrate_analysis_data(analysis_file, storage)
        except Exception as e:
            print(f"分析データ移行エラー {analysis_file}: {e}")
    
    # データベース保存
    storage.save_database()
    
    # テスト実行
    test_unified_system(storage)
    
    # せつなさん用エクスポート
    export_file = storage.export_for_setsuna()
    print(f"\nせつなさん用データエクスポート完了: {export_file}")
    
    print("\n=== 移行完了 ===")


if __name__ == "__main__":
    main()