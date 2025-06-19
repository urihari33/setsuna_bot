"""
既存プレイリストの設定システム移行

統一データベース内の既存プレイリストを新しい設定管理システムに移行
"""

import sys
from pathlib import Path
from datetime import datetime

# パス設定
sys.path.append(str(Path(__file__).parent.parent))

from storage.unified_storage import UnifiedStorage
from managers.playlist_config_manager import PlaylistConfigManager, create_default_config_for_existing_playlist
from core.data_models import PlaylistCategory, UpdateFrequency


def migrate_existing_playlists():
    """既存プレイリストを設定システムに移行"""
    print("🔄 既存プレイリストの設定システム移行を開始")
    print("=" * 60)
    
    # データベース読み込み
    storage = UnifiedStorage()
    db = storage.load_database()
    
    print(f"既存プレイリスト数: {len(db.playlists)}")
    
    if not db.playlists:
        print("移行するプレイリストがありません")
        return True
    
    # 設定管理システム初期化
    config_manager = PlaylistConfigManager()
    existing_configs = config_manager.load_configs()
    
    print(f"既存設定数: {len(existing_configs.configs)}")
    
    # 移行処理
    migrated_count = 0
    skipped_count = 0
    
    for playlist_id, playlist in db.playlists.items():
        print(f"\n処理中: {playlist_id}")
        print(f"  タイトル: {playlist.metadata.title}")
        print(f"  動画数: {playlist.total_videos}")
        
        # 既に設定済みかチェック
        if playlist_id in existing_configs.configs:
            print(f"  ⏭️ スキップ: 既に設定済み")
            skipped_count += 1
            continue
        
        try:
            # デフォルト設定を作成
            config = create_default_config_for_existing_playlist(
                playlist_id=playlist_id,
                display_name=playlist.metadata.title
            )
            
            # カテゴリ推定（簡易版）
            title_lower = playlist.metadata.title.lower()
            if any(keyword in title_lower for keyword in ['music', '音楽', 'song', 'cover']):
                config.category = PlaylistCategory.MUSIC
            elif any(keyword in title_lower for keyword in ['tutorial', 'lesson', '講座', '学習']):
                config.category = PlaylistCategory.EDUCATION
            elif any(keyword in title_lower for keyword in ['game', 'gaming', 'ゲーム']):
                config.category = PlaylistCategory.GAMING
            elif any(keyword in title_lower for keyword in ['tech', '技術', 'programming']):
                config.category = PlaylistCategory.TECH
            else:
                config.category = PlaylistCategory.OTHER
            
            # 更新頻度の推定（最終更新から判断）
            if playlist.last_incremental_sync:
                days_since_update = (datetime.now() - playlist.last_incremental_sync).days
                if days_since_update <= 7:
                    config.update_frequency = UpdateFrequency.WEEKLY
                elif days_since_update <= 30:
                    config.update_frequency = UpdateFrequency.MONTHLY
                else:
                    config.update_frequency = UpdateFrequency.MANUAL
            else:
                config.update_frequency = UpdateFrequency.MANUAL
            
            # 設定データベースに追加
            existing_configs.add_config(config)
            
            print(f"  ✅ 移行完了")
            print(f"    カテゴリ: {config.category.value}")
            print(f"    更新頻度: {config.update_frequency.value}")
            
            migrated_count += 1
            
        except Exception as e:
            print(f"  ❌ 移行エラー: {e}")
    
    # 設定保存
    if migrated_count > 0:
        config_manager._config_db = existing_configs
        if config_manager.save_configs():
            print(f"\n✅ 移行完了: {migrated_count}件移行, {skipped_count}件スキップ")
        else:
            print(f"\n❌ 設定保存エラー")
            return False
    else:
        print(f"\n移行対象がありませんでした: {skipped_count}件既存")
    
    # 移行結果確認
    print(f"\n=== 移行結果確認 ===")
    final_configs = config_manager.load_configs()
    print(f"設定総数: {len(final_configs.configs)}")
    
    # カテゴリ別集計
    category_stats = {}
    for config in final_configs.configs.values():
        category = config.category.value
        category_stats[category] = category_stats.get(category, 0) + 1
    
    print("カテゴリ別:")
    for category, count in category_stats.items():
        print(f"  {category}: {count}件")
    
    print(f"\n🎉 移行処理完了")
    return True


def verify_migration():
    """移行結果の検証"""
    print("\n🔍 移行結果の検証")
    print("=" * 40)
    
    # データベースと設定の照合
    storage = UnifiedStorage()
    db = storage.load_database()
    
    config_manager = PlaylistConfigManager()
    configs = config_manager.load_configs()
    
    print(f"データベース内プレイリスト: {len(db.playlists)}")
    print(f"設定内プレイリスト: {len(configs.configs)}")
    
    # 差分チェック
    db_playlist_ids = set(db.playlists.keys())
    config_playlist_ids = set(configs.configs.keys())
    
    missing_in_config = db_playlist_ids - config_playlist_ids
    extra_in_config = config_playlist_ids - db_playlist_ids
    
    if missing_in_config:
        print(f"\n⚠️ 設定に未登録: {len(missing_in_config)}件")
        for pid in missing_in_config:
            print(f"  {pid}: {db.playlists[pid].metadata.title}")
    
    if extra_in_config:
        print(f"\n⚠️ データベースに未存在: {len(extra_in_config)}件")
        for pid in extra_in_config:
            print(f"  {pid}: {configs.configs[pid].display_name}")
    
    if not missing_in_config and not extra_in_config:
        print("\n✅ データベースと設定が完全に一致しています")
    
    return len(missing_in_config) == 0


def test_config_system():
    """設定システムのテスト"""
    print("\n🧪 設定システムのテスト")
    print("=" * 40)
    
    config_manager = PlaylistConfigManager()
    
    # 統計表示
    stats = config_manager.get_statistics()
    print("統計情報:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 設定一覧（優先度順）
    print(f"\n設定一覧（優先度順）:")
    configs = config_manager.get_configs_by_priority()
    
    for i, config in enumerate(configs[:5], 1):  # 最初の5件のみ表示
        print(f"  {i}. {config.display_name}")
        print(f"     ID: {config.playlist_id}")
        print(f"     カテゴリ: {config.category.value}")
        print(f"     更新頻度: {config.update_frequency.value}")
        print(f"     優先度: {config.priority}")
        print(f"     有効: {'✅' if config.enabled else '❌'}")
    
    if len(configs) > 5:
        print(f"  ... 他 {len(configs) - 5} 件")
    
    # 妥当性チェック
    print(f"\n妥当性チェック:")
    issues = config_manager.validate_all_configs()
    if issues:
        print(f"⚠️ {len(issues)}件の問題を発見:")
        for playlist_id, issue in issues:
            print(f"  {playlist_id}: {issue}")
    else:
        print("✅ 全設定が妥当です")
    
    print(f"\n🎉 テスト完了")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "migrate":
            migrate_existing_playlists()
        elif sys.argv[1] == "verify":
            verify_migration()
        elif sys.argv[1] == "test":
            test_config_system()
        else:
            print("使用方法:")
            print("  python migrate_to_config_system.py migrate  # 移行実行")
            print("  python migrate_to_config_system.py verify   # 移行確認")
            print("  python migrate_to_config_system.py test     # テスト実行")
    else:
        # デフォルトは移行実行
        if migrate_existing_playlists():
            verify_migration()
            test_config_system()