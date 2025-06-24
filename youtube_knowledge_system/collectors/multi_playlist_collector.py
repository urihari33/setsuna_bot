"""
マルチプレイリストコレクター

複数プレイリストの効率的な並列処理・データ収集
"""

import sys
import asyncio
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

import googleapiclient.discovery
from google.oauth2.credentials import Credentials

# パス設定
sys.path.append(str(Path(__file__).parent.parent))

from managers.playlist_config_manager import PlaylistConfigManager
from storage.unified_storage import UnifiedStorage
from core.data_models import (
    Video, Playlist, VideoMetadata, PlaylistMetadata,
    ContentSource, AnalysisStatus, PlaylistConfig
)
from config.settings import DATA_DIR


class MultiPlaylistCollector:
    """マルチプレイリストコレクター"""
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        # 認証設定（Windows パス）
        self.credentials_path = credentials_path or r"D:\setsuna_bot\config\youtube_credentials.json"
        self.token_path = token_path or r"D:\setsuna_bot\config\youtube_token.json"
        
        # 管理システム初期化
        self.config_manager = PlaylistConfigManager()
        self.storage = UnifiedStorage()
        
        # API設定
        self.service = None
        self.api_service_name = 'youtube'
        self.api_version = 'v3'
        
        # 処理統計
        self.stats = {
            'total_playlists': 0,
            'processed_playlists': 0,
            'successful_playlists': 0,
            'failed_playlists': 0,
            'total_videos_found': 0,
            'new_videos_added': 0,
            'start_time': None,
            'errors': []
        }
    
    def _load_credentials(self) -> Optional[Credentials]:
        """認証情報を読み込み"""
        try:
            # まずJSONファイルとして読み込みを試行
            try:
                import json
                with open(self.token_path, 'r', encoding='utf-8') as token:
                    token_data = json.load(token)
                print("   JSONトークンファイルを検出")
                creds = Credentials.from_authorized_user_info(token_data)
                return creds
            except (json.JSONDecodeError, KeyError):
                # pickleファイルとして読み込み
                print("   pickleトークンファイルとして読み込み試行")
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
                return creds
        except Exception as e:
            print(f"❌ 認証読み込みエラー: {e}")
            print("   新規認証を試行します...")
            return self._recreate_credentials()
    
    def _recreate_credentials(self) -> Optional[Credentials]:
        """認証情報を再生成"""
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            import json
            
            SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
            
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
            
            # トークンを保存
            with open(self.token_path, 'w', encoding='utf-8') as token:
                token.write(creds.to_json())
            
            print("✅ 新規認証完了")
            return creds
            
        except Exception as e:
            print(f"❌ 新規認証失敗: {e}")
            return None
    
    def _initialize_service(self) -> bool:
        """YouTube APIサービスを初期化"""
        try:
            creds = self._load_credentials()
            if not creds:
                return False
            
            self.service = googleapiclient.discovery.build(
                self.api_service_name, 
                self.api_version, 
                credentials=creds
            )
            return True
            
        except Exception as e:
            print(f"❌ API初期化エラー: {e}")
            return False
    
    def verify_playlist_access(self, playlist_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """プレイリストアクセス可能性を検証
        
        Returns:
            (アクセス可能, メッセージ, プレイリスト情報)
        """
        try:
            if not self.service:
                return False, "APIサービスが初期化されていません", None
            
            # プレイリスト基本情報取得
            playlist_request = self.service.playlists().list(
                part='snippet,contentDetails',
                id=playlist_id
            )
            playlist_response = playlist_request.execute()
            
            if not playlist_response.get('items'):
                return False, "プレイリストが見つかりません", None
            
            playlist_info = playlist_response['items'][0]
            
            # 動画アクセステスト（最初の1件）
            items_request = self.service.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=1
            )
            items_response = items_request.execute()
            
            video_count = playlist_info['contentDetails']['itemCount']
            accessible_videos = len(items_response.get('items', []))
            
            if video_count > 0 and accessible_videos == 0:
                return False, "プレイリスト内の動画にアクセスできません（プライベート）", playlist_info
            
            playlist_data = {
                'id': playlist_id,
                'title': playlist_info['snippet']['title'],
                'description': playlist_info['snippet']['description'],
                'channel_title': playlist_info['snippet']['channelTitle'],
                'channel_id': playlist_info['snippet']['channelId'],
                'published_at': playlist_info['snippet']['publishedAt'],
                'item_count': video_count
            }
            
            return True, f"アクセス可能（動画数: {video_count}）", playlist_data
            
        except Exception as e:
            return False, f"検証エラー: {e}", None
    
    def collect_playlist_videos(self, playlist_id: str, max_videos: Optional[int] = None) -> Tuple[bool, List[str], str]:
        """プレイリストから動画IDを収集
        
        Returns:
            (成功フラグ, 動画IDリスト, メッセージ)
        """
        try:
            print(f"  📥 動画ID収集開始: {playlist_id}")
            
            all_video_ids = []
            next_page_token = None
            page = 1
            collected_videos = 0
            
            while True:
                print(f"    ページ {page} 処理中...")
                
                request = self.service.playlistItems().list(
                    part='snippet',
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                )
                
                response = request.execute()
                page_video_ids = []
                
                for item in response.get('items', []):
                    resource_id = item.get('snippet', {}).get('resourceId', {})
                    if resource_id.get('kind') == 'youtube#video':
                        video_id = resource_id.get('videoId')
                        if video_id:
                            all_video_ids.append(video_id)
                            page_video_ids.append(video_id)
                            collected_videos += 1
                            
                            # 最大数制限チェック
                            if max_videos and collected_videos >= max_videos:
                                print(f"    最大数到達: {max_videos}")
                                return True, all_video_ids[:max_videos], f"収集完了（制限: {max_videos}）"
                
                print(f"    {len(page_video_ids)}件取得")
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                page += 1
                
                # 安全制限
                if page > 20:  # 最大1000動画
                    print(f"    ページ制限到達")
                    break
            
            print(f"  ✅ 収集完了: {len(all_video_ids)}件")
            return True, all_video_ids, f"収集完了: {len(all_video_ids)}件"
            
        except Exception as e:
            error_msg = f"動画収集エラー: {e}"
            print(f"  ❌ {error_msg}")
            return False, [], error_msg
    
    def collect_video_details(self, video_ids: List[str]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """動画詳細情報を一括取得
        
        Returns:
            (動画詳細リスト, 失敗したIDリスト)
        """
        video_details = []
        failed_ids = []
        
        # 50件ずつバッチ処理
        batch_size = 50
        
        print(f"  📋 動画詳細取得: {len(video_ids)}件")
        
        for i in range(0, len(video_ids), batch_size):
            batch_ids = video_ids[i:i + batch_size]
            print(f"    バッチ {i//batch_size + 1}: {len(batch_ids)}件")
            
            try:
                request = self.service.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(batch_ids)
                )
                response = request.execute()
                
                batch_details = []
                found_ids = set()
                
                for item in response.get('items', []):
                    video_data = {
                        'id': item['id'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt'],
                        'channel_title': item['snippet']['channelTitle'],
                        'channel_id': item['snippet']['channelId'],
                        'duration': item['contentDetails']['duration'],
                        'view_count': int(item['statistics'].get('viewCount', 0)),
                        'like_count': int(item['statistics'].get('likeCount', 0)),
                        'comment_count': int(item['statistics'].get('commentCount', 0)),
                        'tags': item['snippet'].get('tags', []),
                        'category_id': item['snippet'].get('categoryId', ''),
                        'collected_at': datetime.now().isoformat()
                    }
                    
                    video_details.append(video_data)
                    batch_details.append(video_data)
                    found_ids.add(item['id'])
                
                # 見つからなかった動画
                missing_ids = set(batch_ids) - found_ids
                failed_ids.extend(missing_ids)
                
                print(f"      成功: {len(batch_details)}件, 失敗: {len(missing_ids)}件")
                
                # API制限を考慮した待機
                time.sleep(0.1)
                
            except Exception as e:
                print(f"      ❌ バッチエラー: {e}")
                failed_ids.extend(batch_ids)
        
        print(f"  ✅ 詳細取得完了: 成功 {len(video_details)}件, 失敗 {len(failed_ids)}件")
        return video_details, failed_ids
    
    def process_playlist_by_id(self, playlist_id: str, display_name: str = "") -> Tuple[bool, str, Dict[str, Any]]:
        """プレイリストIDを直接指定して処理（設定管理なし）
        
        Args:
            playlist_id: プレイリストID
            display_name: 表示名（オプション）
        
        Returns:
            (成功フラグ, メッセージ, 処理結果)
        """
        if not display_name:
            display_name = f"プレイリスト_{playlist_id[:8]}"
        
        result = {
            'playlist_id': playlist_id,
            'display_name': display_name,
            'videos_found': 0,
            'new_videos': 0,
            'updated_videos': 0,
            'errors': []
        }
        
        try:
            print(f"\n🔄 プレイリスト処理開始: {display_name}")
            print(f"   ID: {playlist_id}")
            
            # プレイリストアクセス検証
            accessible, verify_msg, playlist_info = self.verify_playlist_access(playlist_id)
            if not accessible:
                error_msg = f"アクセス検証失敗: {verify_msg}"
                result['errors'].append(error_msg)
                return False, error_msg, result
            
            print(f"   ✅ {verify_msg}")
            
            # 動画ID収集
            success, video_ids, collect_msg = self.collect_playlist_videos(playlist_id)
            
            if not success:
                result['errors'].append(collect_msg)
                return False, collect_msg, result
            
            result['videos_found'] = len(video_ids)
            self.stats['total_videos_found'] += len(video_ids)
            
            # 新規動画の特定
            db = self.storage.load_database()
            existing_playlist = db.playlists.get(playlist_id)
            
            if existing_playlist:
                existing_video_ids = set(existing_playlist.video_ids)
                new_video_ids = [vid for vid in video_ids if vid not in existing_video_ids]
            else:
                new_video_ids = video_ids
                existing_video_ids = set()
            
            result['new_videos'] = len(new_video_ids)
            
            print(f"   📊 既存: {len(existing_video_ids)}件, 新規: {len(new_video_ids)}件")
            
            if new_video_ids:
                # 新規動画の詳細取得
                video_details, failed_ids = self.collect_video_details(new_video_ids)
                
                if failed_ids:
                    result['errors'].append(f"動画詳細取得失敗: {len(failed_ids)}件")
                
                # データベースに追加（設定なし版）
                added_count = self._add_videos_to_database_simple(
                    video_details, 
                    playlist_id
                )
                
                result['updated_videos'] = added_count
                self.stats['new_videos_added'] += added_count
                
                print(f"   ✅ 新規動画追加: {added_count}件")
            
            # プレイリスト情報更新（設定なし版）
            self._update_playlist_metadata_simple(playlist_id, playlist_info, video_ids, display_name)
            
            # データベース保存
            self.storage.save_database()
            
            return True, f"処理完了: 新規 {result['new_videos']}件", result
            
        except Exception as e:
            error_msg = f"プレイリスト処理エラー: {e}"
            result['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
            return False, error_msg, result
    
    def process_single_video_by_id(self, video_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """動画IDを直接指定して単体処理（手動追加用）
        
        Args:
            video_id: YouTube動画ID
        
        Returns:
            (成功フラグ, メッセージ, 処理結果)
        """
        MANUAL_PLAYLIST_ID = "MANUAL_ADDED"
        
        result = {
            'video_id': video_id,
            'is_new_video': False,
            'is_existing_video': False,
            'video_title': '',
            'errors': []
        }
        
        try:
            print(f"\n🎬 動画単体処理開始: {video_id}")
            
            # API初期化確認
            if not self.service:
                if not self._initialize_service():
                    error_msg = "YouTube API初期化失敗"
                    result['errors'].append(error_msg)
                    return False, error_msg, result
            
            # 動画詳細取得
            video_details, failed_ids = self.collect_video_details([video_id])
            
            if failed_ids or not video_details:
                error_msg = f"動画が見つかりません: {video_id}"
                result['errors'].append(error_msg)
                return False, error_msg, result
            
            video_data = video_details[0]
            result['video_title'] = video_data['title']
            
            print(f"   📺 動画取得成功: {video_data['title']}")
            print(f"   📺 チャンネル: {video_data['channel_title']}")
            
            # 既存動画の確認
            db = self.storage.load_database()
            existing_video = db.videos.get(video_id)
            
            if existing_video:
                # 既存動画に手動追加プレイリストを関連付け
                if MANUAL_PLAYLIST_ID not in existing_video.playlists:
                    existing_video.playlists.append(MANUAL_PLAYLIST_ID)
                    existing_video.playlist_positions[MANUAL_PLAYLIST_ID] = len(existing_video.playlists) - 1
                    existing_video.updated_at = datetime.now()
                    self.storage.add_video(existing_video)
                    
                    result['is_existing_video'] = True
                    print(f"   ✅ 既存動画を手動追加カテゴリに関連付け")
                else:
                    print(f"   ℹ️ 既に手動追加カテゴリに存在")
                    result['is_existing_video'] = True
            else:
                # 新規動画作成
                metadata = VideoMetadata(
                    id=video_data['id'],
                    title=video_data['title'],
                    description=video_data['description'],
                    published_at=datetime.fromisoformat(video_data['published_at'].replace('Z', '+00:00')),
                    channel_title=video_data['channel_title'],
                    channel_id=video_data['channel_id'],
                    duration=video_data['duration'],
                    view_count=video_data['view_count'],
                    like_count=video_data['like_count'],
                    comment_count=video_data['comment_count'],
                    tags=video_data['tags'],
                    category_id=video_data['category_id'],
                    collected_at=datetime.fromisoformat(video_data['collected_at'])
                )
                
                video = Video(
                    source=ContentSource.YOUTUBE,
                    metadata=metadata,
                    playlists=[MANUAL_PLAYLIST_ID],
                    playlist_positions={MANUAL_PLAYLIST_ID: 0},
                    analysis_status=AnalysisStatus.PENDING,
                    creative_insight=None,
                    analysis_error=None,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                self.storage.add_video(video)
                result['is_new_video'] = True
                print(f"   ✅ 新規動画追加完了")
            
            # 手動追加プレイリストの更新
            self._update_manual_playlist_metadata(video_id, video_data)
            
            # データベース保存
            self.storage.save_database()
            
            message = f"動画追加完了: {video_data['title']}"
            if result['is_new_video']:
                message += " (新規)"
            else:
                message += " (既存・関連付け)"
            
            return True, message, result
            
        except Exception as e:
            error_msg = f"動画処理エラー: {e}"
            result['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
            return False, error_msg, result
    
    def _update_manual_playlist_metadata(self, video_id: str, video_data: Dict[str, Any]):
        """手動追加プレイリストのメタデータを更新"""
        MANUAL_PLAYLIST_ID = "MANUAL_ADDED"
        
        try:
            db = self.storage.load_database()
            existing_playlist = db.playlists.get(MANUAL_PLAYLIST_ID)
            
            if existing_playlist:
                # 既存の手動追加プレイリストに動画ID追加
                if video_id not in existing_playlist.video_ids:
                    existing_playlist.video_ids.append(video_id)
                    existing_playlist.total_videos = len(existing_playlist.video_ids)
                    existing_playlist.updated_at = datetime.now()
            else:
                # 手動追加プレイリストを新規作成
                metadata = PlaylistMetadata(
                    id=MANUAL_PLAYLIST_ID,
                    title="手動追加動画",
                    description="個別に追加されたYouTube動画のコレクション",
                    channel_title="YouTube知識システム",
                    channel_id="system",
                    item_count=1,
                    published_at=datetime.now(),
                    collected_at=datetime.now()
                )
                
                playlist = Playlist(
                    source=ContentSource.YOUTUBE,
                    metadata=metadata,
                    video_ids=[video_id],
                    last_full_sync=datetime.now(),
                    last_incremental_sync=datetime.now(),
                    sync_settings={
                        'auto_analyze': True,
                        'update_frequency': 'manual',
                        'priority': 1
                    },
                    total_videos=1,
                    analyzed_videos=0,
                    analysis_success_rate=0.0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            
            self.storage.add_playlist(playlist)
            print(f"   📋 手動追加プレイリスト更新")
            
        except Exception as e:
            print(f"   ❌ 手動追加プレイリスト更新エラー: {e}")
    
    def process_single_playlist(self, config: PlaylistConfig) -> Tuple[bool, str, Dict[str, Any]]:
        """単一プレイリストの処理
        
        Returns:
            (成功フラグ, メッセージ, 処理結果)
        """
        playlist_id = config.playlist_id
        result = {
            'playlist_id': playlist_id,
            'display_name': config.display_name,
            'videos_found': 0,
            'new_videos': 0,
            'updated_videos': 0,
            'errors': []
        }
        
        try:
            print(f"\n🔄 プレイリスト処理開始: {config.display_name}")
            print(f"   ID: {playlist_id}")
            print(f"   カテゴリ: {config.category.value}")
            
            # プレイリストアクセス検証
            accessible, verify_msg, playlist_info = self.verify_playlist_access(playlist_id)
            if not accessible:
                error_msg = f"アクセス検証失敗: {verify_msg}"
                result['errors'].append(error_msg)
                return False, error_msg, result
            
            print(f"   ✅ {verify_msg}")
            
            # 動画ID収集
            success, video_ids, collect_msg = self.collect_playlist_videos(
                playlist_id, 
                config.max_videos
            )
            
            if not success:
                result['errors'].append(collect_msg)
                return False, collect_msg, result
            
            result['videos_found'] = len(video_ids)
            self.stats['total_videos_found'] += len(video_ids)
            
            # 新規動画の特定
            db = self.storage.load_database()
            existing_playlist = db.playlists.get(playlist_id)
            
            if existing_playlist:
                existing_video_ids = set(existing_playlist.video_ids)
                new_video_ids = [vid for vid in video_ids if vid not in existing_video_ids]
            else:
                new_video_ids = video_ids
                existing_video_ids = set()
            
            result['new_videos'] = len(new_video_ids)
            
            print(f"   📊 既存: {len(existing_video_ids)}件, 新規: {len(new_video_ids)}件")
            
            if new_video_ids:
                # 新規動画の詳細取得
                video_details, failed_ids = self.collect_video_details(new_video_ids)
                
                if failed_ids:
                    result['errors'].append(f"動画詳細取得失敗: {len(failed_ids)}件")
                
                # データベースに追加
                added_count = self._add_videos_to_database(
                    video_details, 
                    playlist_id, 
                    config
                )
                
                result['updated_videos'] = added_count
                self.stats['new_videos_added'] += added_count
                
                print(f"   ✅ 新規動画追加: {added_count}件")
            
            # プレイリスト情報更新
            self._update_playlist_metadata(playlist_id, playlist_info, video_ids, config)
            
            # プレイリスト専用JSONファイルを生成
            self._generate_playlist_json(playlist_id, playlist_info, video_ids, config)
            
            return True, f"処理完了: 新規 {result['new_videos']}件", result
            
        except Exception as e:
            error_msg = f"プレイリスト処理エラー: {e}"
            result['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
            return False, error_msg, result
    
    def _add_videos_to_database(
        self, 
        video_details: List[Dict[str, Any]], 
        playlist_id: str, 
        config: PlaylistConfig
    ) -> int:
        """動画をデータベースに追加"""
        added_count = 0
        
        for video_data in video_details:
            try:
                # VideoMetadata作成
                metadata = VideoMetadata(
                    id=video_data['id'],
                    title=video_data['title'],
                    description=video_data['description'],
                    published_at=datetime.fromisoformat(video_data['published_at'].replace('Z', '+00:00')),
                    channel_title=video_data['channel_title'],
                    channel_id=video_data['channel_id'],
                    duration=video_data['duration'],
                    view_count=video_data['view_count'],
                    like_count=video_data['like_count'],
                    comment_count=video_data['comment_count'],
                    tags=video_data['tags'],
                    category_id=video_data['category_id'],
                    collected_at=datetime.fromisoformat(video_data['collected_at'])
                )
                
                # 既存動画の確認・更新
                db = self.storage.load_database()
                existing_video = db.videos.get(video_data['id'])
                
                if existing_video:
                    # 既存動画のプレイリスト追加
                    if playlist_id not in existing_video.playlists:
                        existing_video.playlists.append(playlist_id)
                        existing_video.playlist_positions[playlist_id] = len(existing_video.playlists) - 1
                        existing_video.updated_at = datetime.now()
                        self.storage.add_video(existing_video)
                        added_count += 1
                else:
                    # 新規動画作成
                    video = Video(
                        source=ContentSource.YOUTUBE,
                        metadata=metadata,
                        playlists=[playlist_id],
                        playlist_positions={playlist_id: 0},
                        analysis_status=AnalysisStatus.PENDING if config.auto_analyze else AnalysisStatus.SKIPPED,
                        creative_insight=None,
                        analysis_error=None,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    self.storage.add_video(video)
                    added_count += 1
                
            except Exception as e:
                print(f"      ❌ 動画追加エラー ({video_data['id']}): {e}")
        
        return added_count
    
    def _add_videos_to_database_simple(
        self, 
        video_details: List[Dict[str, Any]], 
        playlist_id: str
    ) -> int:
        """動画をデータベースに追加（設定なし版）"""
        added_count = 0
        
        for video_data in video_details:
            try:
                # VideoMetadata作成
                metadata = VideoMetadata(
                    id=video_data['id'],
                    title=video_data['title'],
                    description=video_data['description'],
                    published_at=datetime.fromisoformat(video_data['published_at'].replace('Z', '+00:00')),
                    channel_title=video_data['channel_title'],
                    channel_id=video_data['channel_id'],
                    duration=video_data['duration'],
                    view_count=video_data['view_count'],
                    like_count=video_data['like_count'],
                    comment_count=video_data['comment_count'],
                    tags=video_data['tags'],
                    category_id=video_data['category_id'],
                    collected_at=datetime.fromisoformat(video_data['collected_at'])
                )
                
                # 既存動画の確認・更新
                db = self.storage.load_database()
                existing_video = db.videos.get(video_data['id'])
                
                if existing_video:
                    # 既存動画のプレイリスト追加
                    if playlist_id not in existing_video.playlists:
                        existing_video.playlists.append(playlist_id)
                        existing_video.playlist_positions[playlist_id] = len(existing_video.playlists) - 1
                        existing_video.updated_at = datetime.now()
                        self.storage.add_video(existing_video)
                        added_count += 1
                else:
                    # 新規動画作成（分析は手動で実行）
                    video = Video(
                        source=ContentSource.YOUTUBE,
                        metadata=metadata,
                        playlists=[playlist_id],
                        playlist_positions={playlist_id: 0},
                        analysis_status=AnalysisStatus.PENDING,
                        creative_insight=None,
                        analysis_error=None,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    self.storage.add_video(video)
                    added_count += 1
                
            except Exception as e:
                print(f"      ❌ 動画追加エラー ({video_data['id']}): {e}")
        
        return added_count
    
    def _update_playlist_metadata_simple(
        self, 
        playlist_id: str, 
        playlist_info: Dict[str, Any], 
        video_ids: List[str],
        display_name: str
    ):
        """プレイリストメタデータを更新（設定なし版）"""
        try:
            # プレイリストメタデータ作成
            metadata = PlaylistMetadata(
                id=playlist_id,
                title=playlist_info.get('title', display_name),
                description=playlist_info.get('description', ''),
                channel_title=playlist_info.get('channel_title', ''),
                channel_id=playlist_info.get('channel_id', ''),
                published_at=datetime.fromisoformat(playlist_info['published_at'].replace('Z', '+00:00')),
                item_count=playlist_info['item_count'],
                collected_at=datetime.now()
            )
            
            # 既存プレイリストの確認
            db = self.storage.load_database()
            existing_playlist = db.playlists.get(playlist_id)
            
            if existing_playlist:
                # 既存プレイリスト更新
                existing_playlist.metadata = metadata
                existing_playlist.video_ids = video_ids
                existing_playlist.total_videos = len(video_ids)
                existing_playlist.last_incremental_sync = datetime.now()
                existing_playlist.updated_at = datetime.now()
                playlist = existing_playlist
            else:
                # 新規プレイリスト作成
                playlist = Playlist(
                    source=ContentSource.YOUTUBE,
                    metadata=metadata,
                    video_ids=video_ids,
                    last_full_sync=datetime.now(),
                    last_incremental_sync=datetime.now(),
                    sync_settings={
                        'auto_analyze': False,  # 手動分析
                        'update_frequency': 'manual',
                        'priority': 3
                    },
                    total_videos=len(video_ids),
                    analyzed_videos=0,
                    analysis_success_rate=0.0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            
            self.storage.add_playlist(playlist)
            
        except Exception as e:
            print(f"      ❌ プレイリストメタデータ更新エラー: {e}")
    
    def _update_playlist_metadata(
        self, 
        playlist_id: str, 
        playlist_info: Dict[str, Any], 
        video_ids: List[str],
        config: PlaylistConfig
    ):
        """プレイリストメタデータを更新"""
        try:
            # プレイリストメタデータ作成
            metadata = PlaylistMetadata(
                id=playlist_id,
                title=playlist_info['title'],
                description=playlist_info['description'],
                channel_title=playlist_info['channel_title'],
                channel_id=playlist_info['channel_id'],
                published_at=datetime.fromisoformat(playlist_info['published_at'].replace('Z', '+00:00')),
                item_count=playlist_info['item_count'],
                collected_at=datetime.now()
            )
            
            # 既存プレイリストの確認
            db = self.storage.load_database()
            existing_playlist = db.playlists.get(playlist_id)
            
            if existing_playlist:
                # 既存プレイリスト更新
                existing_playlist.metadata = metadata
                existing_playlist.video_ids = video_ids
                existing_playlist.total_videos = len(video_ids)
                existing_playlist.last_incremental_sync = datetime.now()
                existing_playlist.updated_at = datetime.now()
                playlist = existing_playlist
            else:
                # 新規プレイリスト作成
                playlist = Playlist(
                    source=ContentSource.YOUTUBE,
                    metadata=metadata,
                    video_ids=video_ids,
                    last_full_sync=datetime.now(),
                    last_incremental_sync=datetime.now(),
                    sync_settings={
                        'auto_analyze': config.auto_analyze,
                        'update_frequency': config.update_frequency.value,
                        'priority': config.priority
                    },
                    total_videos=len(video_ids),
                    analyzed_videos=0,
                    analysis_success_rate=0.0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            
            self.storage.add_playlist(playlist)
            
        except Exception as e:
            print(f"      ❌ プレイリストメタデータ更新エラー: {e}")
    
    def _generate_playlist_json(self, playlist_id: str, playlist_info: Dict[str, Any], 
                               video_ids: List[str], config: PlaylistConfig):
        """プレイリスト専用JSONファイルを生成"""
        try:
            from pathlib import Path
            import json
            
            # プレイリストディレクトリ
            playlist_dir = Path("D:/setsuna_bot/youtube_knowledge_system/data/playlists")
            playlist_dir.mkdir(parents=True, exist_ok=True)
            
            # プレイリスト専用ファイル
            playlist_file = playlist_dir / f"playlist_{playlist_id}.json"
            
            # 統合データベースから動画詳細を取得
            db = self.storage.load_database()
            video_details = []
            
            for i, video_id in enumerate(video_ids):
                if video_id in db.videos:
                    video = db.videos[video_id]
                    video_data = {
                        'position': i,
                        'id': video.metadata.id,
                        'title': video.metadata.title,
                        'description': video.metadata.description,
                        'published_at': video.metadata.published_at.isoformat(),
                        'channel_title': video.metadata.channel_title,
                        'channel_id': video.metadata.channel_id,
                        'duration': video.metadata.duration,
                        'view_count': video.metadata.view_count,
                        'like_count': video.metadata.like_count,
                        'comment_count': video.metadata.comment_count,
                        'tags': video.metadata.tags,
                        'category_id': video.metadata.category_id,
                        'collected_at': video.metadata.collected_at.isoformat(),
                        'analysis_status': video.analysis_status.value,
                        'has_analysis': video.creative_insight is not None
                    }
                    
                    # 分析結果があれば追加
                    if video.creative_insight:
                        video_data['creative_insight'] = {
                            'creators': [
                                {
                                    'name': creator.name,
                                    'role': creator.role,
                                    'confidence': creator.confidence
                                }
                                for creator in video.creative_insight.creators
                            ],
                            'music_info': {
                                'title': video.creative_insight.music_info.title,
                                'genre': video.creative_insight.music_info.genre,
                                'bpm': video.creative_insight.music_info.bpm,
                                'key': video.creative_insight.music_info.key,
                                'lyrics_content': video.creative_insight.music_info.lyrics_content
                            } if video.creative_insight.music_info else None,
                            'confidence_score': video.creative_insight.confidence_score,
                            'analysis_notes': video.creative_insight.analysis_notes,
                            'analyzed_at': video.creative_insight.analyzed_at.isoformat()
                        }
                    
                    video_details.append(video_data)
            
            # プレイリストJSONデータ
            playlist_data = {
                'playlist_info': {
                    'id': playlist_id,
                    'title': playlist_info.get('title', config.display_name),
                    'description': playlist_info.get('description', ''),
                    'channel_title': playlist_info.get('channel_title', ''),
                    'channel_id': playlist_info.get('channel_id', ''),
                    'item_count': playlist_info.get('item_count', len(video_ids)),
                    'published_at': playlist_info.get('published_at', datetime.now().isoformat())
                },
                'config': {
                    'display_name': config.display_name,
                    'category': config.category.value,
                    'update_frequency': config.update_frequency.value,
                    'priority': config.priority,
                    'auto_analyze': config.auto_analyze,
                    'enabled': config.enabled
                },
                'statistics': {
                    'total_videos': len(video_details),
                    'analyzed_videos': sum(1 for v in video_details if v.get('has_analysis', False)),
                    'pending_analysis': sum(1 for v in video_details if not v.get('has_analysis', False)),
                    'analysis_rate': sum(1 for v in video_details if v.get('has_analysis', False)) / len(video_details) if video_details else 0.0
                },
                'videos': video_details,
                'generated_at': datetime.now().isoformat(),
                'file_version': '1.0'
            }
            
            # JSONファイルに保存
            with open(playlist_file, 'w', encoding='utf-8') as f:
                json.dump(playlist_data, f, ensure_ascii=False, indent=2)
            
            print(f"   📄 プレイリストJSONファイル生成: {playlist_file}")
            print(f"      動画数: {len(video_details)}件, 分析済み: {playlist_data['statistics']['analyzed_videos']}件")
            
        except Exception as e:
            print(f"   ❌ プレイリストJSON生成エラー: {e}")
    
    def collect_multiple_playlists(
        self, 
        playlist_ids: Optional[List[str]] = None,
        enabled_only: bool = True,
        priority_order: bool = True
    ) -> Dict[str, Any]:
        """複数プレイリストの一括収集
        
        Args:
            playlist_ids: 処理対象のプレイリストID（None=設定から取得）
            enabled_only: 有効なプレイリストのみ処理
            priority_order: 優先度順で処理
        """
        print("🚀 マルチプレイリスト収集開始")
        print("=" * 60)
        
        self.stats['start_time'] = datetime.now()
        
        # API初期化
        if not self._initialize_service():
            return {'success': False, 'error': 'API初期化失敗', 'stats': self.stats}
        
        print("✅ YouTube API接続成功")
        
        # 処理対象プレイリストの決定
        if playlist_ids:
            # 指定されたIDから設定取得
            configs = []
            for pid in playlist_ids:
                config = self.config_manager.get_config(pid)
                if config:
                    configs.append(config)
                else:
                    print(f"⚠️ 設定が見つかりません: {pid}")
        else:
            # 設定から取得
            if priority_order:
                configs = self.config_manager.get_configs_by_priority(enabled_only)
            else:
                configs = self.config_manager.list_configs(enabled_only)
        
        if not configs:
            return {'success': False, 'error': '処理対象プレイリストなし', 'stats': self.stats}
        
        self.stats['total_playlists'] = len(configs)
        
        print(f"処理対象: {len(configs)}プレイリスト")
        for i, config in enumerate(configs, 1):
            print(f"  {i}. {config.display_name} (優先度: {config.priority})")
        
        # 順次処理
        results = []
        for config in configs:
            success, message, result = self.process_single_playlist(config)
            
            self.stats['processed_playlists'] += 1
            
            if success:
                self.stats['successful_playlists'] += 1
            else:
                self.stats['failed_playlists'] += 1
                self.stats['errors'].append(f"{config.display_name}: {message}")
            
            results.append({
                'config': config,
                'success': success,
                'message': message,
                'result': result
            })
            
            # 進捗表示
            progress = (self.stats['processed_playlists'] / self.stats['total_playlists']) * 100
            print(f"\n📊 進捗: {progress:.1f}% ({self.stats['processed_playlists']}/{self.stats['total_playlists']})")
        
        # 最終保存
        print(f"\n💾 データベース保存中...")
        self.storage.save_database()
        print(f"   ✅ 保存完了")
        
        # 結果サマリー
        duration = (datetime.now() - self.stats['start_time']).total_seconds()
        
        print(f"\n🎉 マルチプレイリスト収集完了")
        print("=" * 60)
        print(f"処理時間: {duration/60:.1f}分")
        print(f"処理プレイリスト: {self.stats['processed_playlists']}")
        print(f"成功: {self.stats['successful_playlists']}")
        print(f"失敗: {self.stats['failed_playlists']}")
        print(f"発見動画: {self.stats['total_videos_found']}")
        print(f"新規追加: {self.stats['new_videos_added']}")
        
        if self.stats['errors']:
            print(f"\nエラー:")
            for error in self.stats['errors']:
                print(f"  - {error}")
        
        return {
            'success': True,
            'results': results,
            'stats': self.stats
        }


# テスト用関数
def test_multi_playlist_collector():
    """マルチプレイリストコレクターのテスト"""
    print("=== マルチプレイリストコレクターテスト ===")
    
    collector = MultiPlaylistCollector()
    
    # 設定確認
    configs = collector.config_manager.list_configs(enabled_only=True)
    print(f"有効なプレイリスト: {len(configs)}件")
    
    if not configs:
        print("テスト対象のプレイリストがありません")
        return
    
    # 単一プレイリストテスト
    test_config = configs[0]
    print(f"\n単一プレイリストテスト: {test_config.display_name}")
    
    # API初期化
    if not collector._initialize_service():
        print("❌ API初期化失敗")
        return
    
    # プレイリストアクセステスト
    accessible, msg, info = collector.verify_playlist_access(test_config.playlist_id)
    print(f"アクセステスト: {msg}")
    
    if accessible:
        print(f"動画数: {info['item_count']}")
    
    print("\n=== テスト完了 ===")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_multi_playlist_collector()
        elif sys.argv[1] == "collect":
            collector = MultiPlaylistCollector()
            result = collector.collect_multiple_playlists()
            if not result['success']:
                print(f"❌ 収集失敗: {result.get('error')}")
        else:
            print("使用方法:")
            print("  python multi_playlist_collector.py test     # テスト実行")
            print("  python multi_playlist_collector.py collect  # 一括収集")
    else:
        test_multi_playlist_collector()