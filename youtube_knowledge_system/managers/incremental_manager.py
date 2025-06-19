"""
差分更新マネージャー

効率的なプレイリスト差分更新機能を提供
"""

import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from collectors.auth_manager import YouTubeAuthManager
from storage.unified_storage import UnifiedStorage
from core.data_models import (
    Video, Playlist, VideoMetadata, PlaylistMetadata,
    ContentSource, AnalysisStatus
)
from config.settings import MAX_RESULTS_PER_REQUEST


class IncrementalUpdateManager:
    """差分更新管理クラス"""
    
    def __init__(self, storage: UnifiedStorage = None, auth_manager: YouTubeAuthManager = None):
        self.storage = storage or UnifiedStorage()
        self.auth_manager = auth_manager or YouTubeAuthManager()
        self.service = None
        self._last_update_times = {}  # プレイリスト別最終更新時刻
    
    def initialize(self):
        """YouTube API サービス初期化"""
        if not self.service:
            print("差分更新マネージャーを初期化中...")
            self.service = self.auth_manager.get_youtube_service()
            print("初期化完了")
    
    def detect_new_videos(self, playlist_id: str, limit_check: int = None) -> List[str]:
        """
        新規動画IDを検出
        
        Args:
            playlist_id: プレイリストID
            limit_check: チェックする動画数の上限（テスト用）
            
        Returns:
            新規動画IDのリスト
        """
        if not self.service:
            self.initialize()
        
        print(f"プレイリスト {playlist_id} の新規動画を検出中...")
        
        # 現在のデータベース状況を取得
        current_playlist = self.storage.get_playlist(playlist_id)
        if current_playlist:
            existing_video_ids = set(current_playlist.video_ids)
            last_sync = current_playlist.last_full_sync
            print(f"既存動画数: {len(existing_video_ids)}")
            print(f"最終同期: {last_sync}")
        else:
            existing_video_ids = set()
            print("新規プレイリストです")
        
        # YouTube API でプレイリストの最新動画IDリストを取得
        try:
            latest_video_ids = self._fetch_playlist_video_ids(playlist_id, limit_check)
            print(f"プレイリスト最新動画数: {len(latest_video_ids)}")
        except Exception as e:
            print(f"プレイリスト取得エラー: {e}")
            return []
        
        # 差分計算
        new_video_ids = [vid for vid in latest_video_ids if vid not in existing_video_ids]
        
        print(f"新規動画検出: {len(new_video_ids)}件")
        if new_video_ids:
            print(f"新規動画ID: {new_video_ids[:5]}{'...' if len(new_video_ids) > 5 else ''}")
        
        return new_video_ids
    
    def _fetch_playlist_video_ids(self, playlist_id: str, limit: int = None) -> List[str]:
        """
        プレイリストから動画IDのみを効率的に取得
        
        Args:
            playlist_id: プレイリストID
            limit: 取得上限数
            
        Returns:
            動画IDのリスト（プレイリスト順序維持）
        """
        video_ids = []
        next_page_token = None
        total_fetched = 0
        max_per_request = MAX_RESULTS_PER_REQUEST
        
        while True:
            try:
                # 最小限のフィールドのみリクエスト（API配額節約）
                request = self.service.playlistItems().list(
                    part='snippet',
                    playlistId=playlist_id,
                    maxResults=min(max_per_request, (limit - total_fetched) if limit else max_per_request),
                    pageToken=next_page_token,
                    fields='items/snippet/resourceId/videoId,nextPageToken'
                )
                
                response = request.execute()
                
                # 動画IDを抽出
                for item in response.get('items', []):
                    resource_id = item.get('snippet', {}).get('resourceId', {})
                    if resource_id.get('kind') == 'youtube#video':
                        video_ids.append(resource_id['videoId'])
                        total_fetched += 1
                        
                        if limit and total_fetched >= limit:
                            break
                
                # 次のページがあるかチェック
                next_page_token = response.get('nextPageToken')
                if not next_page_token or (limit and total_fetched >= limit):
                    break
                
                # API制限を考慮して少し待機
                time.sleep(0.1)
                
            except Exception as e:
                print(f"プレイリスト動画ID取得エラー: {e}")
                break
        
        return video_ids
    
    def update_playlist_incrementally(self, playlist_id: str, force_update: bool = False) -> Dict[str, Any]:
        """
        プレイリストの差分更新を実行
        
        Args:
            playlist_id: プレイリストID
            force_update: 強制更新フラグ
            
        Returns:
            更新結果の詳細情報
        """
        start_time = datetime.now()
        
        print(f"\\n=== プレイリスト差分更新開始: {playlist_id} ===")
        
        # 新規動画IDを検出
        new_video_ids = self.detect_new_videos(playlist_id)
        
        if not new_video_ids and not force_update:
            print("新規動画がありません。更新をスキップします。")
            return {
                'playlist_id': playlist_id,
                'status': 'no_updates',
                'new_videos_count': 0,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
        
        # 新規動画の詳細情報を取得
        print(f"\\n新規動画の詳細情報を取得中... ({len(new_video_ids)}件)")
        try:
            new_videos_data = self._fetch_video_details(new_video_ids)
            print(f"詳細情報取得完了: {len(new_videos_data)}件")
        except Exception as e:
            print(f"動画詳細取得エラー: {e}")
            return {
                'playlist_id': playlist_id,
                'status': 'error',
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
        
        # プレイリスト情報も更新が必要かチェック
        playlist_updated = self._update_playlist_metadata(playlist_id)
        
        # 統一データモデルに変換してデータベースに追加
        print("\\nデータベースに追加中...")
        added_videos = 0
        for video_data in new_videos_data:
            try:
                video = self._convert_to_unified_model(video_data, playlist_id)
                self.storage.add_video(video)
                added_videos += 1
            except Exception as e:
                print(f"動画変換エラー {video_data.get('id', 'unknown')}: {e}")
        
        # プレイリストの動画リストを更新
        self._update_playlist_video_list(playlist_id, new_video_ids)
        
        # データベース保存
        self.storage.save_database()
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        result = {
            'playlist_id': playlist_id,
            'status': 'success',
            'new_videos_count': len(new_video_ids),
            'added_videos_count': added_videos,
            'new_video_ids': new_video_ids,
            'playlist_updated': playlist_updated,
            'processing_time': processing_time,
            'updated_at': end_time.isoformat()
        }
        
        print(f"\\n=== 差分更新完了 ===")
        print(f"新規動画: {added_videos}件追加")
        print(f"処理時間: {processing_time:.2f}秒")
        
        return result
    
    def _fetch_video_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """
        動画IDリストから詳細情報を取得
        
        Args:
            video_ids: 動画IDリスト
            
        Returns:
            動画詳細情報のリスト
        """
        if not video_ids:
            return []
        
        videos_data = []
        
        # YouTube API は一度に50件まで取得可能
        batch_size = 50
        for i in range(0, len(video_ids), batch_size):
            batch_ids = video_ids[i:i + batch_size]
            
            try:
                request = self.service.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(batch_ids)
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    video_data = {
                        'id': item['id'],
                        'title': item['snippet'].get('title', ''),
                        'description': item['snippet'].get('description', ''),
                        'published_at': item['snippet'].get('publishedAt', ''),
                        'channel_title': item['snippet'].get('channelTitle', ''),
                        'channel_id': item['snippet'].get('channelId', ''),
                        'duration': item['contentDetails'].get('duration', ''),
                        'view_count': item['statistics'].get('viewCount', '0'),
                        'like_count': item['statistics'].get('likeCount', '0'),
                        'comment_count': item['statistics'].get('commentCount', '0'),
                        'tags': item['snippet'].get('tags', []),
                        'category_id': item['snippet'].get('categoryId', ''),
                        'collected_at': datetime.now().isoformat()
                    }
                    videos_data.append(video_data)
                
                # API制限を考慮して少し待機
                time.sleep(0.2)
                
            except Exception as e:
                print(f"動画詳細取得エラー (batch {i//batch_size + 1}): {e}")
                continue
        
        return videos_data
    
    def _update_playlist_metadata(self, playlist_id: str) -> bool:
        """
        プレイリストメタデータを更新
        
        Args:
            playlist_id: プレイリストID
            
        Returns:
            更新があったかどうか
        """
        try:
            # プレイリスト情報を取得
            request = self.service.playlists().list(
                part='snippet,contentDetails',
                id=playlist_id
            )
            response = request.execute()
            
            if not response.get('items'):
                print(f"プレイリスト {playlist_id} が見つかりません")
                return False
            
            playlist_info = response['items'][0]
            
            # 既存のプレイリストを取得
            existing_playlist = self.storage.get_playlist(playlist_id)
            
            # 新規プレイリストまたは情報更新が必要な場合
            if not existing_playlist:
                # 新規プレイリスト作成
                metadata = PlaylistMetadata(
                    id=playlist_id,
                    title=playlist_info['snippet'].get('title', ''),
                    description=playlist_info['snippet'].get('description', ''),
                    channel_title=playlist_info['snippet'].get('channelTitle', ''),
                    channel_id=playlist_info['snippet'].get('channelId', ''),
                    published_at=datetime.fromisoformat(
                        playlist_info['snippet']['publishedAt'].replace('Z', '+00:00')
                    ),
                    item_count=playlist_info['contentDetails'].get('itemCount', 0),
                    collected_at=datetime.now()
                )
                
                playlist = Playlist(
                    source=ContentSource.YOUTUBE,
                    metadata=metadata,
                    video_ids=[],
                    last_full_sync=datetime.now(),
                    last_incremental_sync=datetime.now(),
                    sync_settings={},
                    total_videos=0,
                    analyzed_videos=0,
                    analysis_success_rate=0.0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                self.storage.add_playlist(playlist)
                print(f"新規プレイリストを作成: {metadata.title}")
                return True
            else:
                # 既存プレイリストの更新
                existing_playlist.metadata.item_count = playlist_info['contentDetails'].get('itemCount', 0)
                existing_playlist.last_incremental_sync = datetime.now()
                existing_playlist.updated_at = datetime.now()
                
                self.storage.add_playlist(existing_playlist)
                return True
                
        except Exception as e:
            print(f"プレイリストメタデータ更新エラー: {e}")
            return False
    
    def _update_playlist_video_list(self, playlist_id: str, new_video_ids: List[str]):
        """
        プレイリストの動画リストを更新
        
        Args:
            playlist_id: プレイリストID
            new_video_ids: 新規動画IDリスト
        """
        playlist = self.storage.get_playlist(playlist_id)
        if playlist:
            # 新規動画IDを既存リストに追加
            updated_video_ids = playlist.video_ids + new_video_ids
            playlist.video_ids = updated_video_ids
            playlist.total_videos = len(updated_video_ids)
            playlist.updated_at = datetime.now()
            
            self.storage.add_playlist(playlist)
    
    def _convert_to_unified_model(self, video_data: Dict[str, Any], playlist_id: str) -> Video:
        """
        YouTube API データを統一データモデルに変換
        
        Args:
            video_data: YouTube API から取得した動画データ
            playlist_id: 所属プレイリストID
            
        Returns:
            統一データモデルの Video オブジェクト
        """
        # VideoMetadata作成
        metadata = VideoMetadata(
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
        
        # プレイリスト内での位置を取得
        playlist = self.storage.get_playlist(playlist_id)
        position = len(playlist.video_ids) if playlist else 0
        
        # Video作成
        video = Video(
            source=ContentSource.YOUTUBE,
            metadata=metadata,
            playlists=[playlist_id],
            playlist_positions={playlist_id: position},
            analysis_status=AnalysisStatus.PENDING,
            creative_insight=None,
            analysis_error=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return video
    
    def sync_all_playlists(self, playlist_ids: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        複数プレイリストの一括差分更新
        
        Args:
            playlist_ids: 更新対象プレイリストIDリスト（Noneの場合は全て）
            
        Returns:
            プレイリストごとの更新結果
        """
        print("\\n=== 複数プレイリスト一括差分更新開始 ===")
        
        # 対象プレイリストを決定
        if playlist_ids is None:
            db = self.storage.load_database()
            playlist_ids = list(db.playlists.keys())
        
        print(f"更新対象プレイリスト: {len(playlist_ids)}件")
        
        results = {}
        
        for i, playlist_id in enumerate(playlist_ids, 1):
            print(f"\\n[{i}/{len(playlist_ids)}] {playlist_id}")
            try:
                result = self.update_playlist_incrementally(playlist_id)
                results[playlist_id] = result
            except Exception as e:
                print(f"プレイリスト更新エラー {playlist_id}: {e}")
                results[playlist_id] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            # プレイリスト間で少し待機
            if i < len(playlist_ids):
                time.sleep(1.0)
        
        # 全体サマリー
        total_new_videos = sum(r.get('new_videos_count', 0) for r in results.values())
        successful_updates = sum(1 for r in results.values() if r.get('status') == 'success')
        
        print(f"\\n=== 一括更新完了 ===")
        print(f"成功: {successful_updates}/{len(playlist_ids)}プレイリスト")
        print(f"新規動画総数: {total_new_videos}件")
        
        return results


# ユーティリティ関数
def get_incremental_manager() -> IncrementalUpdateManager:
    """IncrementalUpdateManager のシングルトンインスタンスを取得"""
    return IncrementalUpdateManager()