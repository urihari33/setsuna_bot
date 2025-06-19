"""
特定プレイリストからのデータ収集
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from .auth_manager import YouTubeAuthManager
from ..storage.json_storage import YouTubeDataStorage
from ..config.settings import MAX_RESULTS_PER_REQUEST


class SpecificPlaylistCollector:
    """特定プレイリストからの動画収集クラス"""
    
    def __init__(self):
        self.auth_manager = YouTubeAuthManager()
        self.storage = YouTubeDataStorage()
        self.service = None
    
    def initialize(self):
        """初期化処理"""
        print("Specific Playlist Collector を初期化中...")
        self.service = self.auth_manager.get_youtube_service()
        print("初期化完了")
    
    def collect_playlist_videos(self, playlist_id: str, max_results: int = 1000) -> List[Dict[str, Any]]:
        """指定されたプレイリストから全動画を取得"""
        if not self.service:
            self.initialize()
        
        print(f"プレイリスト {playlist_id} から動画を収集中...")
        
        # まずプレイリスト情報を取得
        playlist_info = self._get_playlist_info(playlist_id)
        if not playlist_info:
            print("プレイリスト情報の取得に失敗しました")
            return []
        
        print(f"プレイリスト名: {playlist_info['title']}")
        print(f"説明: {playlist_info['description'][:100]}...")
        print(f"動画数: {playlist_info['item_count']} 件")
        
        # 動画リストを取得
        videos = self._get_all_playlist_videos(playlist_id, max_results)
        
        # 動画の詳細情報を取得
        if videos:
            detailed_videos = self._enrich_video_data(videos, playlist_info)
            
            # 専用ファイルに保存
            self._save_playlist_data(playlist_id, playlist_info, detailed_videos)
            
            return detailed_videos
        
        return []
    
    def _get_playlist_info(self, playlist_id: str) -> Optional[Dict[str, Any]]:
        """プレイリスト基本情報を取得"""
        try:
            request = self.service.playlists().list(
                part="snippet,contentDetails",
                id=playlist_id
            )
            response = request.execute()
            
            if response.get('items'):
                item = response['items'][0]
                return {
                    'id': playlist_id,
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel_title': item['snippet']['channelTitle'],
                    'channel_id': item['snippet']['channelId'],
                    'published_at': item['snippet']['publishedAt'],
                    'item_count': item['contentDetails']['itemCount']
                }
            else:
                print(f"プレイリスト {playlist_id} が見つかりません")
                return None
                
        except Exception as e:
            print(f"プレイリスト情報取得エラー: {e}")
            return None
    
    def _get_all_playlist_videos(self, playlist_id: str, max_results: int) -> List[Dict[str, Any]]:
        """プレイリストから全動画を取得"""
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
                    # プライベート動画や削除された動画をスキップ
                    if item['snippet']['title'] == 'Private video' or item['snippet']['title'] == 'Deleted video':
                        continue
                        
                    video_data = {
                        'id': item['contentDetails']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt'],
                        'channel_title': item['snippet']['channelTitle'],
                        'channel_id': item['snippet']['channelId'],
                        'playlist_id': playlist_id,
                        'position': item['snippet']['position']  # プレイリスト内の位置
                    }
                    videos.append(video_data)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                # API制限を考慮して待機
                time.sleep(0.1)
                
                # 進捗表示
                print(f"  取得済み: {len(videos)} 件")
        
        except Exception as e:
            print(f"プレイリスト動画取得エラー: {e}")
        
        print(f"合計 {len(videos)} 件の動画を取得しました")
        return videos
    
    def _enrich_video_data(self, videos: List[Dict[str, Any]], playlist_info: Dict[str, Any]) -> List[Dict[str, Any]]:
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
                            'comment_count': item['statistics'].get('commentCount', '0'),
                            'duration': item['contentDetails'].get('duration', ''),
                            'tags': item['snippet'].get('tags', []),
                            'category_id': item['snippet'].get('categoryId', ''),
                            'collected_at': datetime.now().isoformat(),
                            'source_playlist': playlist_info['title'],
                            'source_playlist_channel': playlist_info['channel_title']
                        })
                        enriched_videos.append(enriched_video)
                
                # API制限を考慮して待機
                time.sleep(0.1)
                
                # 進捗表示
                print(f"  詳細情報取得済み: {len(enriched_videos)} 件")
                
            except Exception as e:
                print(f"動画詳細情報取得エラー: {e}")
                # エラーの場合は元のデータをそのまま使用
                for video_id in batch_ids:
                    original_video = next((v for v in videos if v['id'] == video_id), None)
                    if original_video:
                        original_video['collected_at'] = datetime.now().isoformat()
                        original_video['source_playlist'] = playlist_info['title']
                        original_video['source_playlist_channel'] = playlist_info['channel_title']
                        enriched_videos.append(original_video)
        
        print(f"詳細情報を {len(enriched_videos)} 件の動画に追加しました")
        return enriched_videos
    
    def _save_playlist_data(self, playlist_id: str, playlist_info: Dict[str, Any], videos: List[Dict[str, Any]]):
        """プレイリストデータを専用ファイルに保存"""
        from pathlib import Path
        
        # Windows環境での正しいパス設定
        playlist_dir = Path("D:/setsuna_bot/youtube_knowledge_system/data/playlists")
        playlist_dir.mkdir(parents=True, exist_ok=True)
        
        # プレイリスト専用ファイル
        playlist_file = playlist_dir / f"playlist_{playlist_id}.json"
        
        data = {
            "playlist_info": playlist_info,
            "last_updated": datetime.now().isoformat(),
            "total_videos": len(videos),
            "videos": videos
        }
        
        import json
        with open(playlist_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"プレイリストデータを保存しました: {playlist_file}")
    
    def get_playlist_statistics(self, playlist_id: str) -> Dict[str, Any]:
        """プレイリストの統計情報を取得"""
        from pathlib import Path
        import json
        
        playlist_file = Path("D:/setsuna_bot/youtube_knowledge_system/data/playlists") / f"playlist_{playlist_id}.json"
        
        if not playlist_file.exists():
            return {"error": "プレイリストデータが見つかりません"}
        
        with open(playlist_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        videos = data.get('videos', [])
        
        # 統計計算
        total_views = sum(int(v.get('view_count', 0)) for v in videos)
        total_likes = sum(int(v.get('like_count', 0)) for v in videos)
        channels = set(v.get('channel_title', '') for v in videos)
        
        return {
            "playlist_title": data['playlist_info']['title'],
            "total_videos": len(videos),
            "total_views": total_views,
            "total_likes": total_likes,
            "unique_channels": len(channels),
            "last_updated": data.get('last_updated'),
            "channels": list(channels)
        }


if __name__ == "__main__":
    import sys
    
    # コマンドライン引数での設定
    if len(sys.argv) > 1:
        test_playlist_id = sys.argv[1]
        max_videos = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    else:
        test_playlist_id = "PL4R2l8ETuvxueMZJo63H8ykV_OY0LuzfX"
        max_videos = 50
    
    # テスト実行
    collector = SpecificPlaylistCollector()
    
    print(f"=== 特定プレイリスト収集テスト ===")
    print(f"プレイリストID: {test_playlist_id}")
    print(f"最大取得数: {max_videos} 件")
    
    # データ収集
    videos = collector.collect_playlist_videos(test_playlist_id, max_results=max_videos)
    
    if videos:
        print(f"\n=== 収集結果 ===")
        print(f"取得した動画数: {len(videos)}")
        
        # 統計情報表示
        stats = collector.get_playlist_statistics(test_playlist_id)
        print(f"\n=== 統計情報 ===")
        for key, value in stats.items():
            if key != 'channels':  # チャンネルリストは長いので除外
                print(f"{key}: {value}")
        
        # サンプル動画を表示
        print(f"\n=== サンプル動画（最初の3件）===")
        for i, video in enumerate(videos[:3]):
            print(f"{i+1}. {video['title']}")
            print(f"   チャンネル: {video['channel_title']}")
            print(f"   再生回数: {video.get('view_count', 'N/A')}")
            print(f"   時間: {video.get('duration', 'N/A')}")
            print()
    
    print("=== テスト完了 ===")