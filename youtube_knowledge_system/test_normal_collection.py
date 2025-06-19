#!/usr/bin/env python3
"""
通常の収集プロセステストスクリプト

対象プレイリストを通常の方法で収集し、57動画すべてが正しく処理されることを確認
"""

import sys
from pathlib import Path

# パス設定
sys.path.append('.')

from collectors.multi_playlist_collector import MultiPlaylistCollector
from managers.playlist_config_manager import PlaylistConfigManager
from storage.unified_storage import UnifiedStorage

def test_normal_collection():
    """通常の収集プロセステスト"""
    print("=== 通常収集プロセステスト ===")
    
    # テスト対象プレイリスト
    playlist_id = "PLKosfnGdlrBXVS-zL2aeOjkrXjKCL6drp"
    
    print(f"テスト対象: {playlist_id}")
    print()
    
    # 初期化
    collector = MultiPlaylistCollector()
    config_manager = PlaylistConfigManager()
    storage = UnifiedStorage()
    
    # API初期化
    if not collector._initialize_service():
        print("❌ API初期化失敗")
        return
    
    print("✅ YouTube API接続成功")
    
    # プレイリスト設定取得
    config = config_manager.get_config(playlist_id)
    if not config:
        print("❌ プレイリスト設定が見つかりません")
        return
    
    print(f"設定確認: {config.display_name}")
    print()
    
    # 収集前の状態確認
    db_before = storage.load_database()
    videos_before = len(db_before.videos)
    
    if playlist_id in db_before.playlists:
        playlist_before = db_before.playlists[playlist_id]
        playlist_videos_before = len(playlist_before.video_ids)
        print(f"📊 収集前の状態:")
        print(f"   総動画数: {videos_before}")
        print(f"   プレイリスト動画数: {playlist_videos_before}")
    else:
        playlist_videos_before = 0
        print(f"📊 収集前の状態:")
        print(f"   総動画数: {videos_before}")
        print(f"   プレイリスト: 未登録")
    
    print()
    
    # 通常の収集プロセス実行
    print("🔄 通常収集プロセス開始...")
    print("=" * 50)
    
    success, message, result = collector.process_single_playlist(config)
    
    print("=" * 50)
    
    if success:
        print(f"✅ 収集成功: {message}")
        print(f"📊 処理結果:")
        print(f"   発見動画数: {result.get('videos_found', 0)}")
        print(f"   新規動画数: {result.get('new_videos', 0)}")
        print(f"   更新動画数: {result.get('updated_videos', 0)}")
        
        if result.get('errors'):
            print(f"⚠️ エラー:")
            for error in result['errors']:
                print(f"     {error}")
        
        # 収集後の状態確認
        db_after = storage.load_database()
        videos_after = len(db_after.videos)
        
        if playlist_id in db_after.playlists:
            playlist_after = db_after.playlists[playlist_id]
            playlist_videos_after = len(playlist_after.video_ids)
            
            print(f"\n📊 収集後の状態:")
            print(f"   総動画数: {videos_after} (増加: {videos_after - videos_before})")
            print(f"   プレイリスト動画数: {playlist_videos_after} (増加: {playlist_videos_after - playlist_videos_before})")
            print(f"   メタデータ上動画数: {playlist_after.metadata.item_count}")
            
            # 完全性チェック
            if playlist_videos_after == 57:
                print(f"   ✅ 完全収集成功: 57/57動画")
            else:
                print(f"   ⚠️ 不完全収集: {playlist_videos_after}/57動画")
                missing = 57 - playlist_videos_after
                print(f"      不足動画数: {missing}")
        
        # JSONファイル確認
        playlist_json_file = Path("D:/setsuna_bot/youtube_knowledge_system/data/playlists") / f"playlist_{playlist_id}.json"
        if playlist_json_file.exists():
            import json
            with open(playlist_json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            json_videos = len(json_data.get('videos', []))
            print(f"\n📄 JSONファイル状態:")
            print(f"   ファイル: {playlist_json_file}")
            print(f"   JSON内動画数: {json_videos}")
            print(f"   統計: {json_data.get('statistics', {})}")
            
            if json_videos == 57:
                print(f"   ✅ JSON完全生成成功")
            else:
                print(f"   ⚠️ JSON不完全: {json_videos}/57動画")
        else:
            print(f"\n❌ JSONファイル未生成: {playlist_json_file}")
        
        print(f"\n🎉 テスト完了")
        
    else:
        print(f"❌ 収集失敗: {message}")
        if result.get('errors'):
            print("エラー詳細:")
            for error in result['errors']:
                print(f"  - {error}")

if __name__ == "__main__":
    test_normal_collection()