"""
JSON形式でのデータ保存管理
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from ..config.settings import DATA_DIR, HISTORY_DATA_FILE, PLAYLIST_DATA_FILE


class YouTubeDataStorage:
    """YouTube データの保存・読み込みを管理するクラス"""
    
    def __init__(self):
        # データディレクトリを作成
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def save_watch_history(self, videos: List[Dict[str, Any]]) -> None:
        """視聴履歴データを保存"""
        data = {
            "last_updated": datetime.now().isoformat(),
            "total_videos": len(videos),
            "videos": videos
        }
        
        self._save_json(HISTORY_DATA_FILE, data)
        print(f"視聴履歴 {len(videos)} 件をに保存しました: {HISTORY_DATA_FILE}")
    
    def load_watch_history(self) -> Dict[str, Any]:
        """視聴履歴データを読み込み"""
        return self._load_json(HISTORY_DATA_FILE)
    
    def save_playlists(self, playlists: List[Dict[str, Any]]) -> None:
        """プレイリストデータを保存"""
        data = {
            "last_updated": datetime.now().isoformat(),
            "total_playlists": len(playlists),
            "playlists": playlists
        }
        
        self._save_json(PLAYLIST_DATA_FILE, data)
        print(f"プレイリスト {len(playlists)} 件を保存しました: {PLAYLIST_DATA_FILE}")
    
    def load_playlists(self) -> Dict[str, Any]:
        """プレイリストデータを読み込み"""
        return self._load_json(PLAYLIST_DATA_FILE)
    
    def _save_json(self, file_path: Path, data: Dict[str, Any]) -> None:
        """JSONファイルに保存"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"JSONファイル保存エラー {file_path}: {e}")
            raise
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """JSONファイルから読み込み"""
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"JSONファイル読み込みエラー {file_path}: {e}")
            return {}
    
    def get_existing_video_ids(self) -> set:
        """既存の動画IDセットを取得（差分更新用）"""
        history_data = self.load_watch_history()
        videos = history_data.get('videos', [])
        return {video.get('id') for video in videos if video.get('id')}
    
    def merge_video_data(self, new_videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """新しい動画データを既存データとマージ"""
        existing_data = self.load_watch_history()
        existing_videos = existing_data.get('videos', [])
        
        # 既存の動画IDセット
        existing_ids = {video.get('id') for video in existing_videos}
        
        # 新しい動画のみを追加
        merged_videos = existing_videos.copy()
        new_count = 0
        
        for video in new_videos:
            if video.get('id') not in existing_ids:
                merged_videos.append(video)
                new_count += 1
        
        print(f"新しい動画 {new_count} 件を追加しました")
        return merged_videos
    
    def get_statistics(self) -> Dict[str, Any]:
        """保存されているデータの統計情報を取得"""
        history_data = self.load_watch_history()
        playlist_data = self.load_playlists()
        
        return {
            "watch_history": {
                "total_videos": len(history_data.get('videos', [])),
                "last_updated": history_data.get('last_updated', 'N/A')
            },
            "playlists": {
                "total_playlists": len(playlist_data.get('playlists', [])),
                "last_updated": playlist_data.get('last_updated', 'N/A')
            }
        }


if __name__ == "__main__":
    # テスト実行
    storage = YouTubeDataStorage()
    stats = storage.get_statistics()
    print("データ統計:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))