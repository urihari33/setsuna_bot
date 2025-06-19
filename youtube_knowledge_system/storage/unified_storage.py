"""
統一データストレージシステム

拡張性とパフォーマンスを両立した統合データ管理
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from core.data_models import (
    KnowledgeDatabase, Video, Playlist, 
    create_empty_database, migrate_legacy_data
)
from config.settings import DATA_DIR


class UnifiedStorage:
    """統一データストレージ管理クラス"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or DATA_DIR
        self.db_file = self.data_dir / "unified_knowledge_db.json"
        self.backup_dir = self.data_dir / "backups"
        self.legacy_dir = self.data_dir / "legacy"
        
        # ディレクトリ作成
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.legacy_dir.mkdir(parents=True, exist_ok=True)
        
        self._database: Optional[KnowledgeDatabase] = None
    
    def load_database(self) -> KnowledgeDatabase:
        """データベースを読み込み"""
        if self._database is None:
            if self.db_file.exists():
                try:
                    with open(self.db_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self._database = KnowledgeDatabase.from_dict(data)
                    print(f"統合データベースを読み込みました: {self._database.total_videos}動画, {self._database.total_playlists}プレイリスト")
                except Exception as e:
                    print(f"データベース読み込みエラー: {e}")
                    print("新しいデータベースを作成します")
                    self._database = create_empty_database()
            else:
                # 既存データがあるか確認
                legacy_files = self._find_legacy_files()
                if legacy_files:
                    print("既存データを新しい形式に移行します...")
                    self._database = self._migrate_legacy_data(legacy_files)
                    self.save_database()
                else:
                    self._database = create_empty_database()
        
        return self._database
    
    def save_database(self, create_backup: bool = True) -> None:
        """データベースを保存"""
        if self._database is None:
            return
        
        # バックアップ作成
        if create_backup and self.db_file.exists():
            backup_file = self.backup_dir / f"unified_knowledge_db_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy2(self.db_file, backup_file)
            print(f"バックアップを作成しました: {backup_file}")
        
        # データベース保存
        try:
            self._database.last_updated = datetime.now()
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self._database.to_dict(), f, ensure_ascii=False, indent=2)
            print(f"統合データベースを保存しました: {self.db_file}")
        except Exception as e:
            print(f"データベース保存エラー: {e}")
            raise
    
    def add_video(self, video: Video) -> None:
        """動画を追加"""
        db = self.load_database()
        db.add_video(video)
        self._database = db
    
    def add_playlist(self, playlist: Playlist) -> None:
        """プレイリストを追加"""
        db = self.load_database()
        db.add_playlist(playlist)
        self._database = db
    
    def get_video(self, video_id: str) -> Optional[Video]:
        """動画を取得"""
        db = self.load_database()
        return db.videos.get(video_id)
    
    def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        """プレイリストを取得"""
        db = self.load_database()
        return db.playlists.get(playlist_id)
    
    def get_videos_by_playlist(self, playlist_id: str) -> List[Video]:
        """プレイリストの動画を順序付きで取得"""
        db = self.load_database()
        playlist = db.playlists.get(playlist_id)
        if not playlist:
            return []
        
        videos = []
        for video_id in playlist.video_ids:
            if video_id in db.videos:
                videos.append(db.videos[video_id])
        
        return videos
    
    def search_videos_by_creator(self, creator_name: str) -> List[Video]:
        """クリエイター名で動画検索"""
        db = self.load_database()
        return db.get_videos_by_creator(creator_name)
    
    def search_videos_by_tag(self, tag: str) -> List[Video]:
        """タグで動画検索"""
        db = self.load_database()
        return db.get_videos_by_tag(tag)
    
    def search_videos_by_theme(self, theme: str) -> List[Video]:
        """テーマで動画検索"""
        db = self.load_database()
        return db.get_videos_by_theme(theme)
    
    def get_all_creators(self) -> List[str]:
        """全クリエイター名を取得"""
        db = self.load_database()
        return list(db.creator_index.keys())
    
    def get_all_tags(self) -> List[str]:
        """全タグを取得"""
        db = self.load_database()
        return list(db.tag_index.keys())
    
    def get_all_themes(self) -> List[str]:
        """全テーマを取得"""
        db = self.load_database()
        return list(db.theme_index.keys())
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        db = self.load_database()
        
        analyzed_videos = sum(1 for v in db.videos.values() if v.creative_insight is not None)
        analysis_success_rate = analyzed_videos / len(db.videos) if db.videos else 0
        
        playlist_stats = {}
        for pid, playlist in db.playlists.items():
            playlist_videos = [db.videos[vid] for vid in playlist.video_ids if vid in db.videos]
            analyzed_in_playlist = sum(1 for v in playlist_videos if v.creative_insight is not None)
            
            playlist_stats[pid] = {
                'title': playlist.metadata.title,
                'total_videos': len(playlist_videos),
                'analyzed_videos': analyzed_in_playlist,
                'analysis_rate': analyzed_in_playlist / len(playlist_videos) if playlist_videos else 0,
                'last_sync': playlist.last_full_sync.isoformat()
            }
        
        return {
            'total_videos': db.total_videos,
            'total_playlists': db.total_playlists,
            'analyzed_videos': analyzed_videos,
            'analysis_success_rate': analysis_success_rate,
            'total_creators': len(db.creator_index),
            'total_tags': len(db.tag_index),
            'total_themes': len(db.theme_index),
            'last_updated': db.last_updated.isoformat(),
            'playlists': playlist_stats,
            'database_version': db.database_version
        }
    
    def cleanup_old_backups(self, keep_days: int = 30) -> None:
        """古いバックアップファイルを削除"""
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        
        for backup_file in self.backup_dir.glob("unified_knowledge_db_*.json"):
            if backup_file.stat().st_mtime < cutoff_time:
                backup_file.unlink()
                print(f"古いバックアップを削除しました: {backup_file}")
    
    def export_for_setsuna(self, output_file: Path = None) -> Path:
        """せつなさん用のデータエクスポート"""
        if output_file is None:
            output_file = self.data_dir / "setsuna_export.json"
        
        db = self.load_database()
        
        # せつなさん向けに最適化したデータ構造
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_videos': db.total_videos,
            'creators': {
                name: {
                    'video_count': len(video_ids),
                    'roles': self._get_creator_roles(name, db),
                    'recent_videos': [
                        {
                            'title': db.videos[vid].metadata.title,
                            'published_at': db.videos[vid].metadata.published_at.isoformat()
                        }
                        for vid in video_ids[:5] if vid in db.videos
                    ]
                }
                for name, video_ids in db.creator_index.items()
            },
            'popular_themes': {
                theme: len(video_ids)
                for theme, video_ids in sorted(db.theme_index.items(), key=lambda x: len(x[1]), reverse=True)[:20]
            },
            'music_insights': self._extract_music_insights(db)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"せつなさん用データをエクスポートしました: {output_file}")
        return output_file
    
    def _find_legacy_files(self) -> Dict[str, Path]:
        """既存データファイルを探索"""
        legacy_files = {}
        
        # プレイリストファイル
        playlist_files = list(self.data_dir.glob("playlists/playlist_*.json"))
        if playlist_files:
            legacy_files['playlists'] = playlist_files
        
        # 分析結果ファイル
        analysis_files = list(self.data_dir.glob("analyzed_*.json"))
        if analysis_files:
            legacy_files['analysis'] = analysis_files
        
        return legacy_files
    
    def _migrate_legacy_data(self, legacy_files: Dict[str, Any]) -> KnowledgeDatabase:
        """既存データを移行"""
        db = create_empty_database()
        
        # プレイリストファイルを処理
        if 'playlists' in legacy_files:
            for playlist_file in legacy_files['playlists']:
                try:
                    print(f"プレイリストファイルを移行中: {playlist_file}")
                    playlist_db = migrate_legacy_data(str(playlist_file), "")
                    
                    # データを統合
                    for video_id, video in playlist_db.videos.items():
                        db.add_video(video)
                    
                    for playlist_id, playlist in playlist_db.playlists.items():
                        db.add_playlist(playlist)
                    
                    # レガシーファイルを移動
                    legacy_target = self.legacy_dir / playlist_file.name
                    shutil.move(str(playlist_file), str(legacy_target))
                    print(f"レガシーファイルを移動しました: {legacy_target}")
                    
                except Exception as e:
                    print(f"プレイリストファイル移行エラー {playlist_file}: {e}")
        
        # 分析結果を統合（後で実装）
        if 'analysis' in legacy_files:
            for analysis_file in legacy_files['analysis']:
                # TODO: 分析結果の統合処理
                pass
        
        return db
    
    def _get_creator_roles(self, creator_name: str, db: KnowledgeDatabase) -> List[str]:
        """クリエイターの役割一覧を取得"""
        roles = set()
        
        for video_id in db.creator_index.get(creator_name, []):
            video = db.videos.get(video_id)
            if video and video.creative_insight:
                for creator in video.creative_insight.creators:
                    if creator.name == creator_name:
                        roles.add(creator.role)
        
        return list(roles)
    
    def _extract_music_insights(self, db: KnowledgeDatabase) -> Dict[str, Any]:
        """音楽関連の洞察を抽出"""
        total_with_lyrics = 0
        popular_genres = {}
        
        for video in db.videos.values():
            if video.creative_insight and video.creative_insight.music_info:
                music_info = video.creative_insight.music_info
                if music_info.lyrics:
                    total_with_lyrics += 1
                if music_info.genre:
                    popular_genres[music_info.genre] = popular_genres.get(music_info.genre, 0) + 1
        
        return {
            'videos_with_lyrics': total_with_lyrics,
            'popular_genres': dict(sorted(popular_genres.items(), key=lambda x: x[1], reverse=True)[:10])
        }


# シングルトンインスタンス
_storage_instance = None

def get_storage() -> UnifiedStorage:
    """ストレージインスタンスを取得"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = UnifiedStorage()
    return _storage_instance