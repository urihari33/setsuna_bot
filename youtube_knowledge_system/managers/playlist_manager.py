"""
プレイリスト管理システム

プレイリストの追加・削除・検証を統合的に管理
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# パス設定
sys.path.append(str(Path(__file__).parent.parent))

from managers.playlist_config_manager import PlaylistConfigManager
from collectors.multi_playlist_collector import MultiPlaylistCollector
from storage.unified_storage import UnifiedStorage
from core.data_models import (
    PlaylistConfig, PlaylistCategory, UpdateFrequency
)


class PlaylistManager:
    """プレイリスト統合管理クラス"""
    
    def __init__(self):
        self.config_manager = PlaylistConfigManager()
        self.collector = MultiPlaylistCollector()
        self.storage = UnifiedStorage()
    
    def add_playlist_from_url(
        self,
        url_or_id: str,
        display_name: str = "",
        category: PlaylistCategory = PlaylistCategory.OTHER,
        update_frequency: UpdateFrequency = UpdateFrequency.MANUAL,
        priority: int = 3,
        auto_analyze: bool = True,
        verify_access: bool = True,
        collect_immediately: bool = False,
        **kwargs
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """URLからプレイリストを追加
        
        Args:
            url_or_id: プレイリストURLまたはID
            display_name: 表示名
            category: カテゴリ
            update_frequency: 更新頻度
            priority: 優先度 (1-5)
            auto_analyze: 自動分析フラグ
            verify_access: アクセス検証を行うか
            collect_immediately: 即座にデータ収集を行うか
            
        Returns:
            (成功フラグ, メッセージ, 詳細結果)
        """
        result = {
            'playlist_id': None,
            'display_name': display_name,
            'verification': None,
            'collection': None,
            'config_added': False
        }
        
        try:
            print(f"🔄 プレイリスト追加処理開始")
            print(f"   URL/ID: {url_or_id}")
            
            # プレイリストID抽出
            playlist_id = PlaylistConfig.extract_playlist_id(url_or_id)
            if not playlist_id:
                return False, f"無効なプレイリストURL/ID: {url_or_id}", result
            
            result['playlist_id'] = playlist_id
            print(f"   抽出ID: {playlist_id}")
            
            # 重複チェック
            existing_config = self.config_manager.get_config(playlist_id)
            if existing_config:
                return False, f"プレイリストは既に登録済み: {existing_config.display_name}", result
            
            # アクセス検証
            if verify_access:
                print(f"   🔍 アクセス検証中...")
                
                # API初期化
                if not self.collector._initialize_service():
                    return False, "YouTube API初期化失敗", result
                
                accessible, verify_msg, playlist_info = self.collector.verify_playlist_access(playlist_id)
                result['verification'] = {
                    'accessible': accessible,
                    'message': verify_msg,
                    'playlist_info': playlist_info
                }
                
                if not accessible:
                    return False, f"アクセス検証失敗: {verify_msg}", result
                
                print(f"   ✅ {verify_msg}")
                
                # プレイリスト情報から自動設定
                if playlist_info and not display_name:
                    display_name = playlist_info['title']
                    result['display_name'] = display_name
                    print(f"   自動設定表示名: {display_name}")
                
                # カテゴリ自動推定
                if playlist_info and category == PlaylistCategory.OTHER:
                    estimated_category = self._estimate_category(playlist_info['title'], playlist_info['description'])
                    if estimated_category != PlaylistCategory.OTHER:
                        category = estimated_category
                        print(f"   推定カテゴリ: {category.value}")
            
            # 設定追加
            print(f"   📝 設定追加中...")
            success, config_msg = self.config_manager.add_playlist(
                url_or_id=url_or_id,
                display_name=display_name,
                category=category,
                update_frequency=update_frequency,
                priority=priority,
                auto_analyze=auto_analyze,
                **kwargs
            )
            
            if not success:
                return False, f"設定追加失敗: {config_msg}", result
            
            result['config_added'] = True
            print(f"   ✅ 設定追加完了")
            
            # 即座にデータ収集
            if collect_immediately:
                print(f"   📥 データ収集開始...")
                
                config = self.config_manager.get_config(playlist_id)
                if config:
                    collect_success, collect_msg, collect_result = self.collector.process_single_playlist(config)
                    result['collection'] = {
                        'success': collect_success,
                        'message': collect_msg,
                        'result': collect_result
                    }
                    
                    if collect_success:
                        print(f"   ✅ データ収集完了: {collect_msg}")
                    else:
                        print(f"   ⚠️ データ収集失敗: {collect_msg}")
                        # 設定は追加済みなので警告レベル
                
                # 保存
                self.storage.save_database()
                print(f"   💾 データベース保存完了")
            
            success_msg = f"プレイリスト追加完了: {display_name} ({playlist_id})"
            if collect_immediately and result.get('collection', {}).get('success'):
                success_msg += f" - データ収集も完了"
            
            return True, success_msg, result
            
        except Exception as e:
            error_msg = f"プレイリスト追加エラー: {e}"
            print(f"   ❌ {error_msg}")
            return False, error_msg, result
    
    def _estimate_category(self, title: str, description: str) -> PlaylistCategory:
        """タイトルと説明からカテゴリを推定"""
        text = (title + " " + description).lower()
        
        # キーワードベースの推定
        category_keywords = {
            PlaylistCategory.MUSIC: ['music', '音楽', 'song', 'cover', 'mv', 'album', 'artist', '歌', 'vocal'],
            PlaylistCategory.EDUCATION: ['tutorial', 'lesson', '講座', '学習', '教育', 'course', 'study', '授業'],
            PlaylistCategory.GAMING: ['game', 'gaming', 'ゲーム', 'play', 'gameplay', 'stream', '実況'],
            PlaylistCategory.TECH: ['tech', '技術', 'programming', 'code', 'software', 'development', 'IT'],
            PlaylistCategory.NEWS: ['news', 'ニュース', '報道', '速報', 'breaking', 'update'],
            PlaylistCategory.ENTERTAINMENT: ['entertainment', 'エンタメ', 'funny', '面白', 'comedy', 'variety', 'show']
        }
        
        # スコア計算
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        # 最高スコアのカテゴリを返す
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        
        return PlaylistCategory.OTHER
    
    def remove_playlist(
        self, 
        playlist_id: str, 
        remove_data: bool = False,
        backup_before_removal: bool = True
    ) -> Tuple[bool, str]:
        """プレイリストを削除
        
        Args:
            playlist_id: プレイリストID
            remove_data: データベースからもデータを削除するか
            backup_before_removal: 削除前にバックアップを作成するか
        """
        try:
            print(f"🗑️ プレイリスト削除処理開始: {playlist_id}")
            
            # 設定確認
            config = self.config_manager.get_config(playlist_id)
            if not config:
                return False, f"プレイリスト設定が見つかりません: {playlist_id}"
            
            display_name = config.display_name
            print(f"   対象: {display_name}")
            
            # バックアップ作成
            if backup_before_removal:
                print(f"   💾 バックアップ作成中...")
                backup_success = self.storage.save_database()  # 現在の状態を保存
                if backup_success:
                    print(f"   ✅ バックアップ完了")
                else:
                    print(f"   ⚠️ バックアップ失敗")
            
            # データベースからの削除
            if remove_data:
                print(f"   🗄️ データベースからデータ削除中...")
                
                db = self.storage.load_database()
                
                # プレイリストがデータベースに存在するかチェック
                if playlist_id in db.playlists:
                    playlist = db.playlists[playlist_id]
                    video_count = len(playlist.video_ids)
                    
                    # プレイリストを削除
                    del db.playlists[playlist_id]
                    
                    # 動画からプレイリスト参照を削除
                    videos_updated = 0
                    videos_removed = 0
                    
                    for video_id in list(db.videos.keys()):
                        video = db.videos[video_id]
                        if playlist_id in video.playlists:
                            video.playlists.remove(playlist_id)
                            if playlist_id in video.playlist_positions:
                                del video.playlist_positions[playlist_id]
                            
                            # プレイリストを参照する動画がなくなった場合は動画自体を削除
                            if not video.playlists:
                                del db.videos[video_id]
                                videos_removed += 1
                            else:
                                videos_updated += 1
                    
                    # データベース保存
                    self.storage._database = db
                    self.storage.save_database()
                    
                    print(f"   ✅ データ削除完了:")
                    print(f"      プレイリスト削除: 1件 ({video_count}動画)")
                    print(f"      動画更新: {videos_updated}件")
                    print(f"      動画削除: {videos_removed}件")
                else:
                    print(f"   ⚠️ データベースにプレイリストが見つかりません")
            
            # 設定削除
            print(f"   ⚙️ 設定削除中...")
            success, config_msg = self.config_manager.remove_playlist(playlist_id)
            
            if not success:
                return False, f"設定削除失敗: {config_msg}"
            
            print(f"   ✅ 設定削除完了")
            
            removal_msg = f"プレイリスト削除完了: {display_name} ({playlist_id})"
            if remove_data:
                removal_msg += " - データも削除"
            
            return True, removal_msg
            
        except Exception as e:
            error_msg = f"プレイリスト削除エラー: {e}"
            print(f"   ❌ {error_msg}")
            return False, error_msg
    
    def update_playlist_data(
        self, 
        playlist_ids: Optional[List[str]] = None,
        force_full_update: bool = False
    ) -> Dict[str, Any]:
        """プレイリストデータの更新
        
        Args:
            playlist_ids: 更新対象ID（None=全有効プレイリスト）
            force_full_update: 強制的に全更新するか
        """
        try:
            print(f"🔄 プレイリストデータ更新開始")
            
            if playlist_ids:
                print(f"   対象: 指定プレイリスト {len(playlist_ids)}件")
                result = self.collector.collect_multiple_playlists(
                    playlist_ids=playlist_ids,
                    enabled_only=False,
                    priority_order=False
                )
            else:
                print(f"   対象: 全有効プレイリスト")
                result = self.collector.collect_multiple_playlists(
                    enabled_only=True,
                    priority_order=True
                )
            
            return result
            
        except Exception as e:
            error_msg = f"データ更新エラー: {e}"
            print(f"   ❌ {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def get_playlist_status(self) -> Dict[str, Any]:
        """プレイリスト状況の取得"""
        try:
            # 設定統計
            config_stats = self.config_manager.get_statistics()
            
            # データベース統計
            db = self.storage.load_database()
            
            # プレイリスト別詳細
            playlist_details = []
            configs = self.config_manager.list_configs()
            
            for config in configs:
                playlist = db.playlists.get(config.playlist_id)
                
                detail = {
                    'id': config.playlist_id,
                    'display_name': config.display_name,
                    'category': config.category.value,
                    'enabled': config.enabled,
                    'priority': config.priority,
                    'auto_analyze': config.auto_analyze,
                    'update_frequency': config.update_frequency.value,
                    'in_database': playlist is not None
                }
                
                if playlist:
                    detail.update({
                        'total_videos': playlist.total_videos,
                        'analyzed_videos': playlist.analyzed_videos,
                        'analysis_rate': playlist.analysis_success_rate,
                        'last_sync': playlist.last_incremental_sync.isoformat() if playlist.last_incremental_sync else None
                    })
                else:
                    detail.update({
                        'total_videos': 0,
                        'analyzed_videos': 0,
                        'analysis_rate': 0.0,
                        'last_sync': None
                    })
                
                playlist_details.append(detail)
            
            # 全体統計
            total_videos = sum(p.total_videos for p in db.playlists.values())
            total_analyzed = sum(p.analyzed_videos for p in db.playlists.values())
            
            return {
                'config_stats': config_stats,
                'database_stats': {
                    'total_playlists': len(db.playlists),
                    'total_videos': total_videos,
                    'total_analyzed': total_analyzed,
                    'analysis_rate': total_analyzed / total_videos if total_videos > 0 else 0
                },
                'playlist_details': playlist_details
            }
            
        except Exception as e:
            return {'error': f"状況取得エラー: {e}"}


# コマンドライン用関数
def test_playlist_manager():
    """プレイリスト管理のテスト"""
    print("=== プレイリスト管理テスト ===")
    
    manager = PlaylistManager()
    
    # 現在の状況表示
    status = manager.get_playlist_status()
    
    if 'error' in status:
        print(f"❌ {status['error']}")
        return
    
    print("現在の状況:")
    print(f"  設定プレイリスト: {status['config_stats']['total_playlists']}")
    print(f"  DBプレイリスト: {status['database_stats']['total_playlists']}")
    print(f"  総動画数: {status['database_stats']['total_videos']}")
    print(f"  分析済み: {status['database_stats']['total_analyzed']}")
    
    print("\nプレイリスト詳細:")
    for detail in status['playlist_details']:
        status_icon = "✅" if detail['enabled'] else "❌"
        db_icon = "📁" if detail['in_database'] else "🆕"
        
        print(f"  {status_icon}{db_icon} {detail['display_name']}")
        print(f"     ID: {detail['id']}")
        print(f"     カテゴリ: {detail['category']}")
        print(f"     動画: {detail['total_videos']}件")
        print(f"     分析済み: {detail['analyzed_videos']}件")
    
    print("\n=== テスト完了 ===")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_playlist_manager()
        else:
            print("使用方法:")
            print("  python playlist_manager.py test  # テスト実行")
    else:
        test_playlist_manager()