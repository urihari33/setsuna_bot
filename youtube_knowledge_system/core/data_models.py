"""
統一データモデル - 拡張性を重視したYouTube知識システムのデータ構造

将来のプラットフォーム拡張・機能拡張に対応できるよう設計
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import re
from urllib.parse import urlparse, parse_qs


class ContentSource(Enum):
    """コンテンツソース種別"""
    YOUTUBE = "youtube"
    TWITTER = "twitter"  # 将来拡張
    TIKTOK = "tiktok"    # 将来拡張
    SPOTIFY = "spotify"  # 将来拡張


class AnalysisStatus(Enum):
    """分析状況"""
    PENDING = "pending"       # 分析待ち
    IN_PROGRESS = "in_progress"  # 分析中
    COMPLETED = "completed"   # 分析完了
    FAILED = "failed"         # 分析失敗
    SKIPPED = "skipped"       # スキップ


class UpdateFrequency(Enum):
    """更新頻度"""
    MANUAL = "manual"       # 手動
    DAILY = "daily"         # 毎日
    WEEKLY = "weekly"       # 毎週
    MONTHLY = "monthly"     # 毎月


class PlaylistCategory(Enum):
    """プレイリストカテゴリ"""
    MUSIC = "music"           # 音楽
    EDUCATION = "education"   # 教育
    ENTERTAINMENT = "entertainment"  # エンターテイメント
    GAMING = "gaming"         # ゲーム
    NEWS = "news"            # ニュース
    TECH = "tech"            # 技術
    OTHER = "other"          # その他


@dataclass
class VideoMetadata:
    """動画の基本メタデータ"""
    id: str
    title: str
    description: str
    published_at: datetime
    channel_title: str
    channel_id: str
    duration: str
    view_count: int
    like_count: int
    comment_count: int
    tags: List[str]
    category_id: str
    collected_at: datetime
    
    @classmethod
    def from_youtube_api(cls, data: Dict[str, Any]) -> 'VideoMetadata':
        """YouTube API レスポンスから VideoMetadata を生成"""
        return cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            published_at=cls._parse_datetime(data['published_at']),
            channel_title=data['channel_title'],
            channel_id=data['channel_id'],
            duration=data['duration'],
            view_count=int(data.get('view_count', 0)),
            like_count=int(data.get('like_count', 0)),
            comment_count=int(data.get('comment_count', 0)),
            tags=data.get('tags', []),
            category_id=data.get('category_id', ''),
            collected_at=cls._parse_datetime(data['collected_at'])
        )
    
    @staticmethod
    def _parse_datetime(datetime_str: str) -> datetime:
        """様々な日時フォーマットをパース"""
        if not datetime_str:
            return datetime.now()
        
        # Z形式を+00:00に変換
        if datetime_str.endswith('Z'):
            datetime_str = datetime_str.replace('Z', '+00:00')
        
        # マイクロ秒の桁数を調整（6桁に統一）
        if '+' in datetime_str and '.' in datetime_str:
            parts = datetime_str.split('+')
            date_part = parts[0]
            tz_part = '+' + parts[1]
            
            if '.' in date_part:
                main_part, microsec_part = date_part.rsplit('.', 1)
                # マイクロ秒を6桁に調整
                microsec_part = microsec_part.ljust(6, '0')[:6]
                datetime_str = f"{main_part}.{microsec_part}{tz_part}"
        
        try:
            return datetime.fromisoformat(datetime_str)
        except ValueError as e:
            print(f"日時パースエラー: {datetime_str} -> {e}")
            return datetime.now()


@dataclass
class CreatorInfo:
    """クリエイター情報"""
    name: str
    role: str  # vocal, composer, illustrator, movie, etc.
    confidence: float  # 信頼度スコア (0.0-1.0)
    

@dataclass
class MusicInfo:
    """音楽関連情報"""
    lyrics: str
    genre: Optional[str] = None
    bpm: Optional[int] = None  # 将来拡張
    key: Optional[str] = None  # 将来拡張
    mood: Optional[str] = None  # 将来拡張


@dataclass
class CreativeInsight:
    """創作関連の洞察・分析結果"""
    creators: List[CreatorInfo]
    music_info: Optional[MusicInfo]
    tools_used: List[str]
    themes: List[str]
    visual_elements: List[str]  # 将来拡張
    analysis_confidence: float
    analysis_timestamp: datetime
    analysis_model: str  # GPT-4, etc.
    insights: str = ""  # 分析結果テキスト


@dataclass
class Video:
    """統一動画データモデル"""
    # 基本情報
    source: ContentSource
    metadata: VideoMetadata
    
    # プレイリスト関連
    playlists: List[str]  # 所属プレイリストIDリスト
    playlist_positions: Dict[str, int]  # プレイリストでの位置
    
    # 分析関連
    analysis_status: AnalysisStatus
    creative_insight: Optional[CreativeInsight]
    analysis_error: Optional[str]
    
    # 更新情報
    created_at: datetime
    updated_at: datetime
    
    # 再試行関連（デフォルト値あり）
    retry_count: int = 0  # 再試行回数
    last_analysis_error: Optional[str] = None  # 最後のエラー内容
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換（JSON保存用）"""
        data = asdict(self)
        # datetime を ISO文字列に変換
        data['metadata']['published_at'] = self.metadata.published_at.isoformat()
        data['metadata']['collected_at'] = self.metadata.collected_at.isoformat()
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        
        if self.creative_insight:
            data['creative_insight']['analysis_timestamp'] = self.creative_insight.analysis_timestamp.isoformat()
        
        # Enum を文字列に変換
        data['source'] = self.source.value
        data['analysis_status'] = self.analysis_status.value
        
        # 再試行情報を確実に含める
        data['retry_count'] = self.retry_count
        data['last_analysis_error'] = self.last_analysis_error
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Video':
        """辞書から Video オブジェクトを復元"""
        # datetime 復元
        metadata_data = data['metadata'].copy()
        metadata_data['published_at'] = datetime.fromisoformat(metadata_data['published_at'])
        metadata_data['collected_at'] = datetime.fromisoformat(metadata_data['collected_at'])
        
        # CreativeInsight 復元
        creative_insight = None
        if data.get('creative_insight'):
            insight_data = data['creative_insight']
            creators = [CreatorInfo(**creator) for creator in insight_data['creators']]
            
            music_info = None
            if insight_data.get('music_info'):
                music_info = MusicInfo(**insight_data['music_info'])
            
            creative_insight = CreativeInsight(
                creators=creators,
                music_info=music_info,
                tools_used=insight_data['tools_used'],
                themes=insight_data['themes'],
                visual_elements=insight_data.get('visual_elements', []),
                analysis_confidence=insight_data['analysis_confidence'],
                analysis_timestamp=datetime.fromisoformat(insight_data['analysis_timestamp']),
                analysis_model=insight_data['analysis_model']
            )
        
        return cls(
            source=ContentSource(data['source']),
            metadata=VideoMetadata(**metadata_data),
            playlists=data['playlists'],
            playlist_positions=data['playlist_positions'],
            analysis_status=AnalysisStatus(data['analysis_status']),
            creative_insight=creative_insight,
            analysis_error=data.get('analysis_error'),
            retry_count=data.get('retry_count', 0),  # 新フィールド（後方互換性）
            last_analysis_error=data.get('last_analysis_error'),  # 新フィールド（後方互換性）
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )


@dataclass
class PlaylistMetadata:
    """プレイリストのメタデータ"""
    id: str
    title: str
    description: str
    channel_title: str
    channel_id: str
    published_at: datetime
    item_count: int
    collected_at: datetime


@dataclass
class Playlist:
    """統一プレイリストデータモデル"""
    source: ContentSource
    metadata: PlaylistMetadata
    video_ids: List[str]  # 動画IDリスト（順序保持）
    
    # 更新管理
    last_full_sync: datetime
    last_incremental_sync: Optional[datetime]
    sync_settings: Dict[str, Any]  # 更新頻度、フィルタ設定等
    
    # 統計情報
    total_videos: int
    analyzed_videos: int
    analysis_success_rate: float
    
    # タイムスタンプ
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        data = asdict(self)
        # datetime 変換
        data['metadata']['published_at'] = self.metadata.published_at.isoformat()
        data['metadata']['collected_at'] = self.metadata.collected_at.isoformat()
        data['last_full_sync'] = self.last_full_sync.isoformat()
        if self.last_incremental_sync:
            data['last_incremental_sync'] = self.last_incremental_sync.isoformat()
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['source'] = self.source.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Playlist':
        """辞書から復元"""
        metadata_data = data['metadata'].copy()
        metadata_data['published_at'] = datetime.fromisoformat(metadata_data['published_at'])
        metadata_data['collected_at'] = datetime.fromisoformat(metadata_data['collected_at'])
        
        return cls(
            source=ContentSource(data['source']),
            metadata=PlaylistMetadata(**metadata_data),
            video_ids=data['video_ids'],
            last_full_sync=datetime.fromisoformat(data['last_full_sync']),
            last_incremental_sync=datetime.fromisoformat(data['last_incremental_sync']) if data.get('last_incremental_sync') else None,
            sync_settings=data['sync_settings'],
            total_videos=data['total_videos'],
            analyzed_videos=data['analyzed_videos'],
            analysis_success_rate=data['analysis_success_rate'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )


@dataclass
class PlaylistConfig:
    """プレイリスト設定データモデル"""
    playlist_id: str
    display_name: str
    url: str
    update_frequency: UpdateFrequency
    priority: int  # 1-5 (1が最高優先度)
    enabled: bool
    category: PlaylistCategory
    auto_analyze: bool  # 新規動画の自動分析
    
    # 追加オプション
    max_videos: Optional[int] = None  # 取得する最大動画数
    description: str = ""
    tags: List[str] = None
    
    # タイムスタンプ
    created_at: datetime = None
    last_updated: datetime = None
    
    def __post_init__(self):
        """初期化後処理"""
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    @staticmethod
    def extract_playlist_id(url_or_id: str) -> Optional[str]:
        """URLまたはIDからプレイリストIDを抽出"""
        # 既にIDの場合
        if url_or_id.startswith('PL') and len(url_or_id) == 34:
            return url_or_id
        
        # URLから抽出
        try:
            parsed = urlparse(url_or_id)
            if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
                # playlist パラメータから抽出
                query_params = parse_qs(parsed.query)
                if 'list' in query_params:
                    playlist_id = query_params['list'][0]
                    if playlist_id.startswith('PL'):
                        return playlist_id
                
                # パスから抽出 (/playlist?list=...)
                if '/playlist' in parsed.path:
                    if 'list' in query_params:
                        return query_params['list'][0]
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def validate_playlist_id(playlist_id: str) -> bool:
        """プレイリストIDの妥当性チェック"""
        if not playlist_id:
            return False
        # YouTube プレイリストIDは通常 PL で始まり34文字
        return bool(re.match(r'^PL[a-zA-Z0-9_-]{32}$', playlist_id))
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        data = asdict(self)
        data['update_frequency'] = self.update_frequency.value
        data['category'] = self.category.value
        data['created_at'] = self.created_at.isoformat()
        data['last_updated'] = self.last_updated.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlaylistConfig':
        """辞書から復元"""
        data = data.copy()
        data['update_frequency'] = UpdateFrequency(data['update_frequency'])
        data['category'] = PlaylistCategory(data['category'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)


@dataclass
class PlaylistConfigDatabase:
    """プレイリスト設定データベース"""
    configs: Dict[str, PlaylistConfig]  # playlist_id -> PlaylistConfig
    
    # メタデータ
    last_updated: datetime
    total_playlists: int
    database_version: str = "1.0"
    
    def __post_init__(self):
        """初期化後処理"""
        self.total_playlists = len(self.configs)
    
    def add_config(self, config: PlaylistConfig):
        """設定を追加"""
        self.configs[config.playlist_id] = config
        self.total_playlists = len(self.configs)
        self.last_updated = datetime.now()
    
    def remove_config(self, playlist_id: str) -> bool:
        """設定を削除"""
        if playlist_id in self.configs:
            del self.configs[playlist_id]
            self.total_playlists = len(self.configs)
            self.last_updated = datetime.now()
            return True
        return False
    
    def get_enabled_configs(self) -> List[PlaylistConfig]:
        """有効な設定のみを取得"""
        return [config for config in self.configs.values() if config.enabled]
    
    def get_configs_by_priority(self) -> List[PlaylistConfig]:
        """優先度順で設定を取得"""
        return sorted(self.configs.values(), key=lambda x: x.priority)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'configs': {pid: config.to_dict() for pid, config in self.configs.items()},
            'last_updated': self.last_updated.isoformat(),
            'total_playlists': self.total_playlists,
            'database_version': self.database_version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlaylistConfigDatabase':
        """辞書から復元"""
        configs = {}
        for pid, config_data in data['configs'].items():
            configs[pid] = PlaylistConfig.from_dict(config_data)
        
        return cls(
            configs=configs,
            last_updated=datetime.fromisoformat(data['last_updated']),
            total_playlists=data['total_playlists'],
            database_version=data.get('database_version', '1.0')
        )


def create_empty_playlist_config_database() -> PlaylistConfigDatabase:
    """空のプレイリスト設定データベースを作成"""
    return PlaylistConfigDatabase(
        configs={},
        last_updated=datetime.now(),
        total_playlists=0
    )


@dataclass
class KnowledgeDatabase:
    """統合知識データベース"""
    videos: Dict[str, Video]  # video_id -> Video
    playlists: Dict[str, Playlist]  # playlist_id -> Playlist
    
    # 横断インデックス
    creator_index: Dict[str, List[str]]  # creator_name -> video_ids
    tag_index: Dict[str, List[str]]  # tag -> video_ids
    theme_index: Dict[str, List[str]]  # theme -> video_ids
    
    # メタデータ
    last_updated: datetime
    total_videos: int
    total_playlists: int
    database_version: str
    
    def __post_init__(self):
        """インデックスを更新"""
        self.rebuild_indexes()
    
    def rebuild_indexes(self):
        """インデックスを再構築"""
        self.creator_index = {}
        self.tag_index = {}
        self.theme_index = {}
        
        for video_id, video in self.videos.items():
            # クリエイターインデックス
            if video.creative_insight:
                for creator in video.creative_insight.creators:
                    if creator.name not in self.creator_index:
                        self.creator_index[creator.name] = []
                    self.creator_index[creator.name].append(video_id)
            
            # タグインデックス
            for tag in video.metadata.tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = []
                self.tag_index[tag].append(video_id)
            
            # テーマインデックス
            if video.creative_insight:
                for theme in video.creative_insight.themes:
                    if theme not in self.theme_index:
                        self.theme_index[theme] = []
                    self.theme_index[theme].append(video_id)
        
        # 統計更新
        self.total_videos = len(self.videos)
        self.total_playlists = len(self.playlists)
        self.last_updated = datetime.now()
    
    def add_video(self, video: Video):
        """動画を追加"""
        self.videos[video.metadata.id] = video
        self.rebuild_indexes()
    
    def add_playlist(self, playlist: Playlist):
        """プレイリストを追加"""
        self.playlists[playlist.metadata.id] = playlist
        self.rebuild_indexes()
    
    def get_videos_by_creator(self, creator_name: str) -> List[Video]:
        """クリエイター名で動画検索"""
        video_ids = self.creator_index.get(creator_name, [])
        return [self.videos[vid] for vid in video_ids if vid in self.videos]
    
    def get_videos_by_tag(self, tag: str) -> List[Video]:
        """タグで動画検索"""
        video_ids = self.tag_index.get(tag, [])
        return [self.videos[vid] for vid in video_ids if vid in self.videos]
    
    def get_videos_by_theme(self, theme: str) -> List[Video]:
        """テーマで動画検索"""
        video_ids = self.theme_index.get(theme, [])
        return [self.videos[vid] for vid in video_ids if vid in self.videos]
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'videos': {vid: video.to_dict() for vid, video in self.videos.items()},
            'playlists': {pid: playlist.to_dict() for pid, playlist in self.playlists.items()},
            'creator_index': self.creator_index,
            'tag_index': self.tag_index,
            'theme_index': self.theme_index,
            'last_updated': self.last_updated.isoformat(),
            'total_videos': self.total_videos,
            'total_playlists': self.total_playlists,
            'database_version': self.database_version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeDatabase':
        """辞書から復元"""
        videos = {vid: Video.from_dict(vdata) for vid, vdata in data['videos'].items()}
        playlists = {pid: Playlist.from_dict(pdata) for pid, pdata in data['playlists'].items()}
        
        db = cls(
            videos=videos,
            playlists=playlists,
            creator_index=data['creator_index'],
            tag_index=data['tag_index'],
            theme_index=data['theme_index'],
            last_updated=datetime.fromisoformat(data['last_updated']),
            total_videos=data['total_videos'],
            total_playlists=data['total_playlists'],
            database_version=data['database_version']
        )
        return db


# ユーティリティ関数
def create_empty_database() -> KnowledgeDatabase:
    """空のデータベースを作成"""
    return KnowledgeDatabase(
        videos={},
        playlists={},
        creator_index={},
        tag_index={},
        theme_index={},
        last_updated=datetime.now(),
        total_videos=0,
        total_playlists=0,
        database_version="1.0"
    )


def migrate_legacy_data(playlist_file: str, analysis_file: str) -> KnowledgeDatabase:
    """既存データを新しいデータモデルに移行"""
    from pathlib import Path
    import json
    
    db = create_empty_database()
    
    # 既存のプレイリストデータを読み込み
    if Path(playlist_file).exists():
        with open(playlist_file, 'r', encoding='utf-8') as f:
            playlist_data = json.load(f)
        
        # Playlist オブジェクト作成
        playlist_info = playlist_data['playlist_info']
        playlist = Playlist(
            source=ContentSource.YOUTUBE,
            metadata=PlaylistMetadata(
                id=playlist_info['id'],
                title=playlist_info['title'],
                description=playlist_info['description'],
                channel_title=playlist_info['channel_title'],
                channel_id=playlist_info['channel_id'],
                published_at=datetime.fromisoformat(playlist_info['published_at']),
                item_count=playlist_info['item_count'],
                collected_at=datetime.fromisoformat(playlist_data['last_updated'])
            ),
            video_ids=[video['id'] for video in playlist_data['videos']],
            last_full_sync=datetime.fromisoformat(playlist_data['last_updated']),
            last_incremental_sync=None,
            sync_settings={},
            total_videos=playlist_data['total_videos'],
            analyzed_videos=0,
            analysis_success_rate=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Video オブジェクト作成
        for video_data in playlist_data['videos']:
            video = Video(
                source=ContentSource.YOUTUBE,
                metadata=VideoMetadata.from_youtube_api(video_data),
                playlists=[playlist.metadata.id],
                playlist_positions={playlist.metadata.id: video_data.get('position', 0)},
                analysis_status=AnalysisStatus.PENDING,
                creative_insight=None,
                analysis_error=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add_video(video)
        
        db.add_playlist(playlist)
    
    # 分析データを統合
    if Path(analysis_file).exists():
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # TODO: 分析データの統合処理を実装
        # 現在は基本構造のみ作成
    
    return db