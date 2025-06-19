"""
YouTube Data API を使用したデータ収集
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from .auth_manager import YouTubeAuthManager
from ..storage.json_storage import YouTubeDataStorage
from ..config.settings import MAX_RESULTS_PER_REQUEST, MAX_TOTAL_VIDEOS


class YouTubeDataCollector:
    """YouTube データ収集メインクラス"""
    
    def __init__(self):
        self.auth_manager = YouTubeAuthManager()
        self.storage = YouTubeDataStorage()
        self.service = None
    
    def initialize(self):
        """初期化処理"""
        print("YouTube Data Collector を初期化中...")
        self.service = self.auth_manager.get_youtube_service()
        print("初期化完了")
    
    def collect_watch_history(self, max_results: int = MAX_TOTAL_VIDEOS) -> List[Dict[str, Any]]:
        """
        視聴履歴を収集
        注意: YouTube Data API v3では直接的な視聴履歴取得はできないため、
        代替として「後で見る」「高く評価した動画」「アップロード動画」を取得
        """
        if not self.service:
            self.initialize()
        
        all_videos = []
        
        # 複数のプレイリストから動画を収集
        playlist_ids = self._get_special_playlists()
        
        for playlist_name, playlist_id in playlist_ids.items():
            if playlist_id:
                print(f"{playlist_name} から動画を収集中...")
                videos = self._get_playlist_videos(playlist_id, max_results // len(playlist_ids))
                all_videos.extend(videos)
                
                # API制限を考慮して少し待機
                time.sleep(0.5)
        
        # 動画の詳細情報を取得
        if all_videos:
            detailed_videos = self._enrich_video_data(all_videos)
            
            # 差分更新
            merged_videos = self.storage.merge_video_data(detailed_videos)
            self.storage.save_watch_history(merged_videos)
            
            return detailed_videos
        
        return []
    
    def _get_special_playlists(self) -> Dict[str, Optional[str]]:
        """特殊なプレイリストIDを取得"""
        try:
            # チャンネル情報を取得
            channels_response = self.service.channels().list(
                part="contentDetails",
                mine=True
            ).execute()
            
            if not channels_response.get('items'):
                print("チャンネル情報が取得できませんでした")
                return {}
            
            channel = channels_response['items'][0]
            content_details = channel.get('contentDetails', {})
            related_playlists = content_details.get('relatedPlaylists', {})
            
            playlist_ids = {
                "高く評価した動画": related_playlists.get('likes'),
                "後で見る": related_playlists.get('watchLater'),
                "アップロード動画": related_playlists.get('uploads')
            }
            
            print("取得可能なプレイリスト:")
            for name, playlist_id in playlist_ids.items():
                status = "✓" if playlist_id else "✗"
                print(f"  {status} {name}: {playlist_id or 'N/A'}")
            
            return playlist_ids
            
        except Exception as e:
            print(f"プレイリスト情報取得エラー: {e}")
            return {}
    
    def _get_playlist_videos(self, playlist_id: str, max_results: int) -> List[Dict[str, Any]]:
        """指定されたプレイリストから動画を取得"""
        videos = []
        next_page_token = None
        
        try:
            while len(videos) < max_results:
                request = self.service.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=playlist_id,
                    maxResults=min(MAX_RESULTS_PER_REQUEST, max_results - len(videos)),
                    pageToken=next_page_token
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    video_data = {
                        'id': item['contentDetails']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt'],
                        'channel_title': item['snippet']['channelTitle'],
                        'channel_id': item['snippet']['channelId'],
                        'playlist_id': playlist_id
                    }
                    videos.append(video_data)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                # API制限を考慮して待機
                time.sleep(0.1)
        
        except Exception as e:
            print(f"プレイリスト動画取得エラー: {e}")
        
        print(f"  {len(videos)} 件の動画を取得しました")
        return videos
    
    def _enrich_video_data(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """動画データに詳細情報を追加"""
        if not videos:
            return videos
        
        print("動画の詳細情報を取得中...")
        
        # 動画IDのリストを作成
        video_ids = [video['id'] for video in videos]
        
        # YouTube APIから詳細情報を取得（50件ずつ）
        enriched_videos = []
        
        for i in range(0, len(video_ids), MAX_RESULTS_PER_REQUEST):
            batch_ids = video_ids[i:i + MAX_RESULTS_PER_REQUEST]
            
            try:
                request = self.service.videos().list(
                    part="snippet,statistics,contentDetails",
                    id=','.join(batch_ids)
                )
                
                response = request.execute()
                
                # 詳細情報を動画データに追加
                for item in response.get('items', []):
                    video_id = item['id']
                    
                    # 元の動画データを検索
                    original_video = next((v for v in videos if v['id'] == video_id), None)
                    if original_video:
                        enriched_video = original_video.copy()
                        enriched_video.update({
                            'view_count': item['statistics'].get('viewCount', '0'),
                            'like_count': item['statistics'].get('likeCount', '0'),
                            'duration': item['contentDetails'].get('duration', ''),
                            'tags': item['snippet'].get('tags', []),
                            'category_id': item['snippet'].get('categoryId', ''),
                            'collected_at': datetime.now().isoformat()
                        })
                        enriched_videos.append(enriched_video)
                
                # API制限を考慮して待機
                time.sleep(0.1)
                
            except Exception as e:
                print(f"動画詳細情報取得エラー: {e}")
                # エラーの場合は元のデータをそのまま使用
                for video_id in batch_ids:
                    original_video = next((v for v in videos if v['id'] == video_id), None)
                    if original_video:
                        enriched_videos.append(original_video)
        
        print(f"詳細情報を {len(enriched_videos)} 件の動画に追加しました")
        return enriched_videos
    
    def collect_user_playlists(self) -> List[Dict[str, Any]]:
        """ユーザーのプレイリスト一覧を取得"""
        if not self.service:
            self.initialize()
        
        playlists = []
        next_page_token = None
        
        try:
            while True:
                request = self.service.playlists().list(
                    part="snippet,contentDetails",
                    mine=True,
                    maxResults=MAX_RESULTS_PER_REQUEST,
                    pageToken=next_page_token
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    playlist_data = {
                        'id': item['id'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt'],
                        'item_count': item['contentDetails']['itemCount'],
                        'collected_at': datetime.now().isoformat()
                    }
                    playlists.append(playlist_data)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                time.sleep(0.1)
        
        except Exception as e:
            print(f"プレイリスト取得エラー: {e}")
        
        if playlists:
            self.storage.save_playlists(playlists)
        
        print(f"プレイリスト {len(playlists)} 件を取得しました")
        return playlists


if __name__ == "__main__":
    # テスト実行
    collector = YouTubeDataCollector()
    
    print("=== YouTube Data Collector テスト ===")
    
    # 認証テスト
    print("\n1. 認証テスト")
    if collector.auth_manager.test_connection():
        print("認証テスト成功！")
    else:
        print("認証テスト失敗")
        exit(1)
    
    # データ収集テスト
    print("\n2. データ収集テスト")
    videos = collector.collect_watch_history(max_results=10)  # テスト用に少数
    print(f"収集した動画数: {len(videos)}")
    
    # プレイリスト収集テスト
    print("\n3. プレイリスト収集テスト")
    playlists = collector.collect_user_playlists()
    print(f"収集したプレイリスト数: {len(playlists)}")
    
    # 統計情報表示
    print("\n4. 統計情報")
    stats = collector.storage.get_statistics()
    print("保存済みデータ統計:")
    for category, info in stats.items():
        print(f"  {category}: {info}")
    
    print("\n=== テスト完了 ===")