"""
マルチプレイリスト差分更新マネージャー

複数プレイリストの効率的な差分更新・重複動画統合処理
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from collections import defaultdict

# パス設定
sys.path.append(str(Path(__file__).parent.parent))

from managers.playlist_config_manager import PlaylistConfigManager
from collectors.multi_playlist_collector import MultiPlaylistCollector
from storage.unified_storage import UnifiedStorage
from core.data_models import (
    Video, Playlist, VideoMetadata, PlaylistMetadata,
    ContentSource, AnalysisStatus, UpdateFrequency
)


class MultiIncrementalManager:
    """マルチプレイリスト差分更新マネージャー"""
    
    def __init__(self):
        self.config_manager = PlaylistConfigManager()
        self.collector = MultiPlaylistCollector()
        self.storage = UnifiedStorage()
        
        # 更新統計
        self.stats = {
            'total_playlists': 0,
            'updated_playlists': 0,
            'skipped_playlists': 0,
            'failed_playlists': 0,
            'total_new_videos': 0,
            'duplicate_videos_found': 0,
            'videos_unified': 0,
            'start_time': None,
            'playlist_results': [],
            'errors': []
        }
    
    def should_update_playlist(self, playlist_id: str, config, force_update: bool = False) -> Tuple[bool, str]:
        """プレイリストの更新が必要かチェック
        
        Returns:
            (更新必要, 理由)
        """
        if force_update:
            return True, "強制更新"
        
        if not config.enabled:
            return False, "無効化されている"
        
        # データベースから最終更新時刻を取得
        db = self.storage.load_database()
        playlist = db.playlists.get(playlist_id)
        
        if not playlist:
            return True, "プレイリストがデータベースに未存在"
        
        if not playlist.last_incremental_sync:
            return True, "初回同期"
        
        # 更新頻度に基づく判定
        now = datetime.now()
        last_sync = playlist.last_incremental_sync
        time_diff = now - last_sync
        
        update_intervals = {
            UpdateFrequency.DAILY: timedelta(days=1),
            UpdateFrequency.WEEKLY: timedelta(weeks=1),
            UpdateFrequency.MONTHLY: timedelta(days=30),
            UpdateFrequency.MANUAL: timedelta(days=365)  # 手動は1年
        }
        
        required_interval = update_intervals.get(config.update_frequency, timedelta(days=7))
        
        if time_diff >= required_interval:
            return True, f"更新間隔到達 ({time_diff.days}日経過)"
        else:
            return False, f"更新間隔未到達 ({time_diff.days}/{required_interval.days}日)"
    
    def detect_playlist_changes(self, playlist_id: str) -> Tuple[bool, List[str], List[str], str]:
        """プレイリストの変更を検出
        
        Returns:
            (成功フラグ, 新規動画IDリスト, 削除動画IDリスト, メッセージ)
        """
        try:
            print(f"  🔍 変更検出: {playlist_id}")
            
            # API初期化
            if not self.collector.service:
                if not self.collector._initialize_service():
                    return False, [], [], "API初期化失敗"
            
            # 現在のAPI動画一覧取得
            success, current_video_ids, msg = self.collector.collect_playlist_videos(playlist_id)
            if not success:
                return False, [], [], f"API取得失敗: {msg}"
            
            # データベースの既存動画一覧
            db = self.storage.load_database()
            playlist = db.playlists.get(playlist_id)
            
            if playlist:
                existing_video_ids = set(playlist.video_ids)
            else:
                existing_video_ids = set()
            
            current_video_ids_set = set(current_video_ids)
            
            # 差分計算
            new_videos = [vid for vid in current_video_ids if vid not in existing_video_ids]
            deleted_videos = [vid for vid in existing_video_ids if vid not in current_video_ids_set]
            
            print(f"    API: {len(current_video_ids)}件, DB: {len(existing_video_ids)}件")
            print(f"    新規: {len(new_videos)}件, 削除: {len(deleted_videos)}件")
            
            return True, new_videos, deleted_videos, f"変更検出完了"
            
        except Exception as e:
            error_msg = f"変更検出エラー: {e}"
            print(f"    ❌ {error_msg}")
            return False, [], [], error_msg
    
    def handle_duplicate_videos(self, new_video_ids: List[str], target_playlist_id: str) -> Dict[str, Any]:
        """重複動画の処理
        
        Returns:
            重複処理結果の詳細
        """
        result = {
            'total_new': len(new_video_ids),
            'truly_new': 0,
            'duplicates_found': 0,
            'unified_videos': 0,
            'duplicate_details': []
        }
        
        if not new_video_ids:
            return result
        
        print(f"  🔄 重複チェック: {len(new_video_ids)}件")
        
        db = self.storage.load_database()
        truly_new_videos = []
        
        for video_id in new_video_ids:
            existing_video = db.videos.get(video_id)
            
            if existing_video:
                # 重複動画 - プレイリスト参照を追加
                result['duplicates_found'] += 1
                
                if target_playlist_id not in existing_video.playlists:
                    existing_video.playlists.append(target_playlist_id)
                    
                    # プレイリスト内位置を計算
                    target_playlist = db.playlists.get(target_playlist_id)
                    if target_playlist:
                        position = len(target_playlist.video_ids)
                    else:
                        position = 0
                    
                    existing_video.playlist_positions[target_playlist_id] = position
                    existing_video.updated_at = datetime.now()
                    
                    self.storage.add_video(existing_video)
                    result['unified_videos'] += 1
                    
                    result['duplicate_details'].append({
                        'video_id': video_id,
                        'title': existing_video.metadata.title,
                        'existing_playlists': len(existing_video.playlists) - 1,
                        'action': 'playlist_reference_added'
                    })
                    
                    print(f"    🔗 統合: {video_id} -> {len(existing_video.playlists)}プレイリスト")
                else:
                    result['duplicate_details'].append({
                        'video_id': video_id,
                        'title': existing_video.metadata.title,
                        'existing_playlists': len(existing_video.playlists),
                        'action': 'already_in_playlist'
                    })
                    print(f"    ⏭️ 既存: {video_id}")
            else:
                # 真の新規動画
                truly_new_videos.append(video_id)
                result['truly_new'] += 1
        
        print(f"    ✅ 重複処理完了: 新規 {result['truly_new']}件, 重複 {result['duplicates_found']}件, 統合 {result['unified_videos']}件")
        
        # 統計更新
        self.stats['duplicate_videos_found'] += result['duplicates_found']
        self.stats['videos_unified'] += result['unified_videos']
        
        # 真の新規動画のIDリストを結果に追加
        result['truly_new_video_ids'] = truly_new_videos
        
        return result
    
    def update_single_playlist(self, playlist_id: str, force_update: bool = False) -> Tuple[bool, str, Dict[str, Any]]:
        """単一プレイリストの差分更新
        
        Returns:
            (成功フラグ, メッセージ, 詳細結果)
        """
        result = {
            'playlist_id': playlist_id,
            'display_name': '',
            'update_needed': False,
            'changes_detected': False,
            'new_videos': 0,
            'deleted_videos': 0,
            'duplicate_handling': None,
            'errors': []
        }
        
        try:
            # 設定取得
            config = self.config_manager.get_config(playlist_id)
            if not config:
                error_msg = f"プレイリスト設定が見つかりません: {playlist_id}"
                result['errors'].append(error_msg)
                return False, error_msg, result
            
            result['display_name'] = config.display_name
            print(f"\n🔄 差分更新: {config.display_name}")
            print(f"   ID: {playlist_id}")
            
            # 更新必要性チェック
            should_update, reason = self.should_update_playlist(playlist_id, config, force_update)
            result['update_needed'] = should_update
            
            if not should_update:
                print(f"   ⏭️ スキップ: {reason}")
                return True, f"スキップ: {reason}", result
            
            print(f"   ✅ 更新実行: {reason}")
            
            # 変更検出
            success, new_videos, deleted_videos, detect_msg = self.detect_playlist_changes(playlist_id)
            if not success:
                result['errors'].append(detect_msg)
                return False, detect_msg, result
            
            result['new_videos'] = len(new_videos)
            result['deleted_videos'] = len(deleted_videos)
            result['changes_detected'] = len(new_videos) > 0 or len(deleted_videos) > 0
            
            if not result['changes_detected']:
                print(f"   ✅ 変更なし")
                # 最終同期時刻のみ更新
                self._update_sync_timestamp(playlist_id)
                return True, "変更なし（同期時刻更新）", result
            
            # 新規動画の重複処理
            if new_videos:
                duplicate_result = self.handle_duplicate_videos(new_videos, playlist_id)
                result['duplicate_handling'] = duplicate_result
                
                # 真の新規動画のみ詳細取得・追加
                truly_new_videos = duplicate_result['truly_new_video_ids']
                if truly_new_videos:
                    print(f"  📥 新規動画詳細取得: {len(truly_new_videos)}件")
                    
                    video_details, failed_ids = self.collector.collect_video_details(truly_new_videos)
                    
                    if failed_ids:
                        result['errors'].append(f"動画詳細取得失敗: {len(failed_ids)}件")
                    
                    # データベースに追加
                    added_count = self.collector._add_videos_to_database(
                        video_details, 
                        playlist_id, 
                        config
                    )
                    
                    print(f"  ✅ 新規動画追加: {added_count}件")
            
            # 削除動画の処理
            if deleted_videos:
                print(f"  🗑️ 削除動画処理: {len(deleted_videos)}件")
                self._handle_deleted_videos(playlist_id, deleted_videos)
            
            # プレイリスト情報の更新
            self._update_playlist_after_sync(playlist_id, new_videos, deleted_videos)
            
            self.stats['total_new_videos'] += len(new_videos)
            
            success_msg = f"更新完了: 新規 {len(new_videos)}件"
            if deleted_videos:
                success_msg += f", 削除 {len(deleted_videos)}件"
            
            return True, success_msg, result
            
        except Exception as e:
            error_msg = f"差分更新エラー: {e}"
            result['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
            return False, error_msg, result
    
    def _handle_deleted_videos(self, playlist_id: str, deleted_video_ids: List[str]):
        """削除された動画の処理"""
        db = self.storage.load_database()
        
        for video_id in deleted_video_ids:
            video = db.videos.get(video_id)
            if video and playlist_id in video.playlists:
                video.playlists.remove(playlist_id)
                if playlist_id in video.playlist_positions:
                    del video.playlist_positions[playlist_id]
                video.updated_at = datetime.now()
                
                # 他のプレイリストからも参照されていない場合は動画を削除
                if not video.playlists:
                    del db.videos[video_id]
                    print(f"    🗑️ 動画削除: {video_id}")
                else:
                    self.storage.add_video(video)
                    print(f"    📝 参照削除: {video_id}")
    
    def _update_sync_timestamp(self, playlist_id: str):
        """同期時刻のみ更新"""
        db = self.storage.load_database()
        playlist = db.playlists.get(playlist_id)
        
        if playlist:
            playlist.last_incremental_sync = datetime.now()
            playlist.updated_at = datetime.now()
            self.storage.add_playlist(playlist)
    
    def _update_playlist_after_sync(self, playlist_id: str, new_videos: List[str], deleted_videos: List[str]):
        """同期後のプレイリスト情報更新"""
        db = self.storage.load_database()
        playlist = db.playlists.get(playlist_id)
        
        if playlist:
            # 動画IDリストを再構築
            current_video_ids = [vid for vid in playlist.video_ids if vid not in deleted_videos]
            current_video_ids.extend(new_videos)
            
            playlist.video_ids = current_video_ids
            playlist.total_videos = len(current_video_ids)
            playlist.last_incremental_sync = datetime.now()
            playlist.updated_at = datetime.now()
            
            # 分析済み動画数の再計算
            analyzed_count = 0
            for video_id in current_video_ids:
                video = db.videos.get(video_id)
                if video and video.analysis_status == AnalysisStatus.COMPLETED:
                    analyzed_count += 1
            
            playlist.analyzed_videos = analyzed_count
            playlist.analysis_success_rate = analyzed_count / len(current_video_ids) if current_video_ids else 0
            
            self.storage.add_playlist(playlist)
    
    def update_multiple_playlists(
        self,
        playlist_ids: Optional[List[str]] = None,
        force_update: bool = False,
        priority_order: bool = True,
        enabled_only: bool = True
    ) -> Dict[str, Any]:
        """複数プレイリストの一括差分更新
        
        Args:
            playlist_ids: 更新対象ID（None=設定から取得）
            force_update: 強制更新フラグ
            priority_order: 優先度順で更新
            enabled_only: 有効なプレイリストのみ
        """
        print("🚀 マルチプレイリスト差分更新開始")
        print("=" * 60)
        
        self.stats['start_time'] = datetime.now()
        
        # API初期化
        if not self.collector._initialize_service():
            return {'success': False, 'error': 'API初期化失敗', 'stats': self.stats}
        
        print("✅ YouTube API接続成功")
        
        # 更新対象プレイリストの決定
        if playlist_ids:
            configs = []
            for pid in playlist_ids:
                config = self.config_manager.get_config(pid)
                if config:
                    configs.append(config)
                else:
                    print(f"⚠️ 設定が見つかりません: {pid}")
        else:
            if priority_order:
                configs = self.config_manager.get_configs_by_priority(enabled_only)
            else:
                configs = self.config_manager.list_configs(enabled_only)
        
        if not configs:
            return {'success': False, 'error': '更新対象プレイリストなし', 'stats': self.stats}
        
        self.stats['total_playlists'] = len(configs)
        
        print(f"更新対象: {len(configs)}プレイリスト")
        if force_update:
            print("🔥 強制更新モード")
        
        # 順次更新
        for config in configs:
            success, message, result = self.update_single_playlist(config.playlist_id, force_update)
            
            self.stats['playlist_results'].append({
                'config': config,
                'success': success,
                'message': message,
                'result': result
            })
            
            if success:
                if result['update_needed']:
                    self.stats['updated_playlists'] += 1
                else:
                    self.stats['skipped_playlists'] += 1
            else:
                self.stats['failed_playlists'] += 1
                self.stats['errors'].append(f"{config.display_name}: {message}")
            
            # 進捗表示
            processed = self.stats['updated_playlists'] + self.stats['skipped_playlists'] + self.stats['failed_playlists']
            progress = (processed / self.stats['total_playlists']) * 100
            print(f"\n📊 進捗: {progress:.1f}% ({processed}/{self.stats['total_playlists']})")
        
        # 最終保存
        print(f"\n💾 データベース保存中...")
        self.storage.save_database()
        print(f"   ✅ 保存完了")
        
        # 結果サマリー
        duration = (datetime.now() - self.stats['start_time']).total_seconds()
        
        print(f"\n🎉 マルチプレイリスト差分更新完了")
        print("=" * 60)
        print(f"処理時間: {duration/60:.1f}分")
        print(f"対象プレイリスト: {self.stats['total_playlists']}")
        print(f"更新済み: {self.stats['updated_playlists']}")
        print(f"スキップ: {self.stats['skipped_playlists']}")
        print(f"失敗: {self.stats['failed_playlists']}")
        print(f"新規動画: {self.stats['total_new_videos']}")
        print(f"重複発見: {self.stats['duplicate_videos_found']}")
        print(f"動画統合: {self.stats['videos_unified']}")
        
        if self.stats['errors']:
            print(f"\nエラー:")
            for error in self.stats['errors']:
                print(f"  - {error}")
        
        return {
            'success': True,
            'stats': self.stats
        }
    
    def get_update_schedule(self) -> List[Dict[str, Any]]:
        """更新スケジュールを取得"""
        configs = self.config_manager.list_configs(enabled_only=True)
        db = self.storage.load_database()
        
        schedule = []
        now = datetime.now()
        
        for config in configs:
            playlist = db.playlists.get(config.playlist_id)
            
            item = {
                'playlist_id': config.playlist_id,
                'display_name': config.display_name,
                'update_frequency': config.update_frequency.value,
                'priority': config.priority,
                'last_sync': None,
                'next_scheduled': None,
                'overdue': False,
                'should_update': False
            }
            
            if playlist and playlist.last_incremental_sync:
                item['last_sync'] = playlist.last_incremental_sync.isoformat()
                
                # 次回更新予定を計算
                intervals = {
                    UpdateFrequency.DAILY: timedelta(days=1),
                    UpdateFrequency.WEEKLY: timedelta(weeks=1),
                    UpdateFrequency.MONTHLY: timedelta(days=30),
                    UpdateFrequency.MANUAL: None
                }
                
                interval = intervals.get(config.update_frequency)
                if interval:
                    next_update = playlist.last_incremental_sync + interval
                    item['next_scheduled'] = next_update.isoformat()
                    item['overdue'] = now > next_update
                    item['should_update'] = item['overdue']
            else:
                item['should_update'] = True  # 未同期
            
            schedule.append(item)
        
        # 優先度・期限切れ順でソート
        schedule.sort(key=lambda x: (not x['should_update'], x['priority'], x['overdue']))
        
        return schedule


# テスト用関数
def test_multi_incremental_manager():
    """マルチ差分更新マネージャーのテスト"""
    print("=== マルチ差分更新マネージャーテスト ===")
    
    manager = MultiIncrementalManager()
    
    # 更新スケジュール確認
    schedule = manager.get_update_schedule()
    print(f"更新スケジュール: {len(schedule)}件")
    
    for item in schedule:
        status = "🔴" if item['should_update'] else "🟢"
        overdue = "⏰" if item['overdue'] else ""
        
        print(f"  {status}{overdue} {item['display_name']}")
        print(f"     更新頻度: {item['update_frequency']}")
        print(f"     最終同期: {item['last_sync']}")
        print(f"     次回予定: {item['next_scheduled']}")
    
    print("\n=== テスト完了 ===")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_multi_incremental_manager()
        elif sys.argv[1] == "update":
            force = "--force" in sys.argv
            manager = MultiIncrementalManager()
            result = manager.update_multiple_playlists(force_update=force)
            if not result['success']:
                print(f"❌ 更新失敗: {result.get('error')}")
        else:
            print("使用方法:")
            print("  python multi_incremental_manager.py test         # テスト実行")
            print("  python multi_incremental_manager.py update       # 差分更新")
            print("  python multi_incremental_manager.py update --force  # 強制更新")
    else:
        test_multi_incremental_manager()