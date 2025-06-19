"""
プレイリスト設定管理システム

複数プレイリストの設定・管理を統合的に行う
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.data_models import (
    PlaylistConfig, PlaylistConfigDatabase, 
    create_empty_playlist_config_database,
    UpdateFrequency, PlaylistCategory
)
from config.settings import DATA_DIR


class PlaylistConfigManager:
    """プレイリスト設定管理クラス"""
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or DATA_DIR
        self.config_file = self.config_dir / "playlist_configs.json"
        self.backup_dir = self.config_dir / "config_backups"
        
        # ディレクトリ作成
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self._config_db: Optional[PlaylistConfigDatabase] = None
    
    def load_configs(self) -> PlaylistConfigDatabase:
        """設定データベースを読み込み"""
        if self._config_db is None:
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self._config_db = PlaylistConfigDatabase.from_dict(data)
                    print(f"プレイリスト設定を読み込みました: {self._config_db.total_playlists}件")
                except Exception as e:
                    print(f"設定読み込みエラー: {e}")
                    print("新しい設定データベースを作成します")
                    self._config_db = create_empty_playlist_config_database()
            else:
                print("設定ファイルが見つかりません。新規作成します")
                self._config_db = create_empty_playlist_config_database()
        
        return self._config_db
    
    def save_configs(self) -> bool:
        """設定データベースを保存"""
        try:
            # バックアップ作成
            if self.config_file.exists():
                backup_name = f"playlist_configs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = self.backup_dir / backup_name
                import shutil
                shutil.copy2(self.config_file, backup_path)
                print(f"設定バックアップを作成: {backup_path}")
            
            # 設定保存
            config_db = self.load_configs()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_db.to_dict(), f, ensure_ascii=False, indent=2)
            
            print(f"プレイリスト設定を保存: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"設定保存エラー: {e}")
            return False
    
    def add_playlist(
        self, 
        url_or_id: str,
        display_name: str = "",
        category: PlaylistCategory = PlaylistCategory.OTHER,
        update_frequency: UpdateFrequency = UpdateFrequency.MANUAL,
        priority: int = 3,
        auto_analyze: bool = True,
        **kwargs
    ) -> Tuple[bool, str]:
        """プレイリストを追加
        
        Returns:
            (成功フラグ, メッセージ)
        """
        try:
            # プレイリストID抽出
            playlist_id = PlaylistConfig.extract_playlist_id(url_or_id)
            if not playlist_id:
                return False, f"無効なプレイリストURL/ID: {url_or_id}"
            
            # ID妥当性チェック
            if not PlaylistConfig.validate_playlist_id(playlist_id):
                return False, f"無効なプレイリストID形式: {playlist_id}"
            
            # 重複チェック
            config_db = self.load_configs()
            if playlist_id in config_db.configs:
                return False, f"プレイリストは既に登録済み: {playlist_id}"
            
            # 表示名の設定
            if not display_name:
                display_name = f"プレイリスト_{playlist_id[:8]}"
            
            # URLの正規化
            if url_or_id.startswith('PL'):
                url = f"https://www.youtube.com/playlist?list={playlist_id}"
            else:
                url = url_or_id
            
            # 設定作成
            config = PlaylistConfig(
                playlist_id=playlist_id,
                display_name=display_name,
                url=url,
                update_frequency=update_frequency,
                priority=priority,
                enabled=True,
                category=category,
                auto_analyze=auto_analyze,
                description=kwargs.get('description', ''),
                tags=kwargs.get('tags', []),
                max_videos=kwargs.get('max_videos')
            )
            
            # データベースに追加
            config_db.add_config(config)
            self._config_db = config_db
            
            # 保存
            if self.save_configs():
                return True, f"プレイリストを追加しました: {display_name} ({playlist_id})"
            else:
                return False, "設定の保存に失敗しました"
                
        except Exception as e:
            return False, f"プレイリスト追加エラー: {e}"
    
    def remove_playlist(self, playlist_id: str) -> Tuple[bool, str]:
        """プレイリストを削除"""
        try:
            config_db = self.load_configs()
            
            if playlist_id not in config_db.configs:
                return False, f"プレイリストが見つかりません: {playlist_id}"
            
            config = config_db.configs[playlist_id]
            display_name = config.display_name
            
            # 削除実行
            if config_db.remove_config(playlist_id):
                self._config_db = config_db
                
                if self.save_configs():
                    return True, f"プレイリストを削除しました: {display_name} ({playlist_id})"
                else:
                    return False, "設定の保存に失敗しました"
            else:
                return False, f"削除に失敗しました: {playlist_id}"
                
        except Exception as e:
            return False, f"プレイリスト削除エラー: {e}"
    
    def update_config(self, playlist_id: str, **updates) -> Tuple[bool, str]:
        """プレイリスト設定を更新"""
        try:
            config_db = self.load_configs()
            
            if playlist_id not in config_db.configs:
                return False, f"プレイリストが見つかりません: {playlist_id}"
            
            config = config_db.configs[playlist_id]
            
            # 更新可能なフィールド
            allowed_updates = {
                'display_name', 'update_frequency', 'priority', 'enabled',
                'category', 'auto_analyze', 'description', 'tags', 'max_videos'
            }
            
            updated_fields = []
            for field, value in updates.items():
                if field in allowed_updates:
                    # Enum型の変換
                    if field == 'update_frequency' and isinstance(value, str):
                        value = UpdateFrequency(value)
                    elif field == 'category' and isinstance(value, str):
                        value = PlaylistCategory(value)
                    
                    setattr(config, field, value)
                    updated_fields.append(field)
            
            if updated_fields:
                config.last_updated = datetime.now()
                config_db.last_updated = datetime.now()
                self._config_db = config_db
                
                if self.save_configs():
                    return True, f"設定を更新しました: {', '.join(updated_fields)}"
                else:
                    return False, "設定の保存に失敗しました"
            else:
                return False, "更新する項目がありません"
                
        except Exception as e:
            return False, f"設定更新エラー: {e}"
    
    def get_config(self, playlist_id: str) -> Optional[PlaylistConfig]:
        """特定のプレイリスト設定を取得"""
        config_db = self.load_configs()
        return config_db.configs.get(playlist_id)
    
    def list_configs(self, enabled_only: bool = False) -> List[PlaylistConfig]:
        """プレイリスト設定一覧を取得"""
        config_db = self.load_configs()
        if enabled_only:
            return config_db.get_enabled_configs()
        else:
            return list(config_db.configs.values())
    
    def get_configs_by_priority(self, enabled_only: bool = True) -> List[PlaylistConfig]:
        """優先度順でプレイリスト設定を取得"""
        configs = self.list_configs(enabled_only)
        return sorted(configs, key=lambda x: x.priority)
    
    def get_configs_by_category(self, category: PlaylistCategory) -> List[PlaylistConfig]:
        """カテゴリ別でプレイリスト設定を取得"""
        config_db = self.load_configs()
        return [config for config in config_db.configs.values() if config.category == category]
    
    def enable_playlist(self, playlist_id: str) -> Tuple[bool, str]:
        """プレイリストを有効化"""
        return self.update_config(playlist_id, enabled=True)
    
    def disable_playlist(self, playlist_id: str) -> Tuple[bool, str]:
        """プレイリストを無効化"""
        return self.update_config(playlist_id, enabled=False)
    
    def get_statistics(self) -> Dict[str, any]:
        """統計情報を取得"""
        config_db = self.load_configs()
        
        total = len(config_db.configs)
        enabled = len([c for c in config_db.configs.values() if c.enabled])
        
        # カテゴリ別集計
        category_stats = {}
        for category in PlaylistCategory:
            count = len([c for c in config_db.configs.values() if c.category == category])
            if count > 0:
                category_stats[category.value] = count
        
        # 更新頻度別集計
        frequency_stats = {}
        for freq in UpdateFrequency:
            count = len([c for c in config_db.configs.values() if c.update_frequency == freq])
            if count > 0:
                frequency_stats[freq.value] = count
        
        return {
            'total_playlists': total,
            'enabled_playlists': enabled,
            'disabled_playlists': total - enabled,
            'category_stats': category_stats,
            'frequency_stats': frequency_stats,
            'last_updated': config_db.last_updated.isoformat() if config_db.last_updated else None
        }
    
    def validate_all_configs(self) -> List[Tuple[str, str]]:
        """全設定の妥当性をチェック"""
        config_db = self.load_configs()
        issues = []
        
        for playlist_id, config in config_db.configs.items():
            # プレイリストID形式チェック
            if not PlaylistConfig.validate_playlist_id(playlist_id):
                issues.append((playlist_id, f"無効なプレイリストID形式: {playlist_id}"))
            
            # 優先度範囲チェック
            if not (1 <= config.priority <= 5):
                issues.append((playlist_id, f"優先度が範囲外: {config.priority} (1-5)"))
            
            # 表示名チェック
            if not config.display_name or len(config.display_name.strip()) == 0:
                issues.append((playlist_id, "表示名が設定されていません"))
        
        return issues


def create_default_config_for_existing_playlist(playlist_id: str, display_name: str = "") -> PlaylistConfig:
    """既存プレイリスト用のデフォルト設定を作成"""
    if not display_name:
        display_name = f"プレイリスト_{playlist_id[:8]}"
    
    return PlaylistConfig(
        playlist_id=playlist_id,
        display_name=display_name,
        url=f"https://www.youtube.com/playlist?list={playlist_id}",
        update_frequency=UpdateFrequency.MANUAL,
        priority=3,
        enabled=True,
        category=PlaylistCategory.OTHER,
        auto_analyze=True
    )


# テスト用関数
def test_playlist_config_manager():
    """プレイリスト設定管理のテスト"""
    print("=== プレイリスト設定管理テスト ===")
    
    manager = PlaylistConfigManager()
    
    # 統計表示
    stats = manager.get_statistics()
    print(f"現在の統計: {stats}")
    
    # 設定一覧表示
    configs = manager.list_configs()
    print(f"\n登録済みプレイリスト: {len(configs)}件")
    
    for config in configs:
        print(f"  {config.playlist_id}: {config.display_name}")
        print(f"    カテゴリ: {config.category.value}")
        print(f"    更新頻度: {config.update_frequency.value}")
        print(f"    有効: {config.enabled}")
        print(f"    優先度: {config.priority}")
    
    print("\n=== テスト完了 ===")


if __name__ == "__main__":
    test_playlist_config_manager()