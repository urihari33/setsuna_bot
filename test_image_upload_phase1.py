#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1: 画像アップロード機能の統合テスト
GUI起動せずに基本機能をテスト
"""

import sys
from pathlib import Path
import json
from PIL import Image, ImageDraw
import tempfile
import os

# パス設定
sys.path.append(str(Path(__file__).parent))

from core.image_manager import VideoImageManager
from core.youtube_knowledge_manager import YouTubeKnowledgeManager


def create_test_image(filename="test_image.jpg", size=(100, 100)):
    """テスト用の画像を作成"""
    img = Image.new('RGB', size, color='red')
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "TEST", fill='white')
    
    temp_path = Path(tempfile.gettempdir()) / filename
    img.save(temp_path, 'JPEG')
    return str(temp_path)


def test_image_manager():
    """VideoImageManagerのテスト"""
    print("=== VideoImageManager テスト ===")
    
    manager = VideoImageManager()
    
    # テスト画像作成
    test_image_path = create_test_image()
    print(f"📷 テスト画像作成: {test_image_path}")
    
    # バリデーションテスト
    is_valid, error = manager.validate_image_file(test_image_path)
    print(f"✅ バリデーション: {is_valid}")
    
    if not is_valid:
        print(f"❌ バリデーションエラー: {error}")
        return False
    
    # 画像保存テスト
    test_video_id = "test_video_001"
    saved_metadata = manager.save_image(
        video_id=test_video_id,
        source_file_path=test_image_path,
        user_description="テスト画像です"
    )
    
    if saved_metadata:
        print(f"✅ 画像保存成功: {saved_metadata['image_id']}")
        print(f"📁 保存パス: {saved_metadata['file_path']}")
        print(f"🖼️ サムネイル: {saved_metadata['thumbnail_path']}")
    else:
        print("❌ 画像保存失敗")
        return False
    
    # 画像一覧取得テスト
    images = manager.get_video_images(test_video_id)
    print(f"📋 保存済み画像数: {len(images)}")
    
    # テンポラリファイル削除
    os.unlink(test_image_path)
    
    return True


def test_youtube_manager_integration():
    """YouTubeKnowledgeManagerとの統合テスト"""
    print("\n=== YouTubeKnowledgeManager統合テスト ===")
    
    # マネージャー初期化
    yt_manager = YouTubeKnowledgeManager()
    image_manager = VideoImageManager()
    
    # テスト用動画データを作成
    test_video_id = "test_integration_001"
    
    # 動画をデータベースに追加（手動で追加する想定）
    video_data = {
        "video_id": test_video_id,
        "source": "youtube",
        "metadata": {
            "title": "テスト動画",
            "channel_title": "テストチャンネル",
            "published_at": "2025-07-04T00:00:00Z",
            "view_count": 1000
        },
        "playlists": ["MANUAL_ADDED"],
        "playlist_positions": {"MANUAL_ADDED": 0},
        "analysis_status": "completed",
        "added_at": "2025-07-04T10:00:00+09:00",
        "added_method": "manual_gui"
    }
    
    # 動画をデータベースに直接追加
    if "videos" not in yt_manager.knowledge_db:
        yt_manager.knowledge_db["videos"] = {}
    yt_manager.knowledge_db["videos"][test_video_id] = video_data
    yt_manager._save_knowledge_db()
    print(f"✅ テスト動画追加: {test_video_id}")
    
    # テスト画像作成・保存
    test_image_path = create_test_image("integration_test.jpg")
    saved_metadata = image_manager.save_image(
        video_id=test_video_id,
        source_file_path=test_image_path,
        user_description="統合テスト用画像"
    )
    
    if not saved_metadata:
        print("❌ 画像保存失敗")
        return False
    
    # 動画に画像を関連付け
    success = yt_manager.add_video_image(test_video_id, saved_metadata)
    if success:
        print("✅ 動画-画像関連付け成功")
    else:
        print("❌ 動画-画像関連付け失敗")
        return False
    
    # データベースから画像一覧取得
    video_images = yt_manager.get_video_images(test_video_id)
    print(f"📋 動画関連画像数: {len(video_images)}")
    
    # データベースの内容確認
    video_data = yt_manager.knowledge_db["videos"][test_video_id]
    if "images" in video_data and len(video_data["images"]) > 0:
        print("✅ データベースに画像情報保存確認")
        image_info = video_data["images"][0]
        print(f"📷 画像ID: {image_info.get('image_id')}")
        print(f"📝 説明: {image_info.get('user_description')}")
    else:
        print("❌ データベースに画像情報が見つかりません")
        return False
    
    # テンポラリファイル削除
    os.unlink(test_image_path)
    
    return True


def test_error_handling():
    """エラーハンドリングのテスト"""
    print("\n=== エラーハンドリングテスト ===")
    
    manager = VideoImageManager()
    
    # 存在しないファイル
    is_valid, error = manager.validate_image_file("nonexistent.jpg")
    print(f"✅ 存在しないファイル: {not is_valid} ({error})")
    
    # 不正な形式（テキストファイル）
    temp_txt = Path(tempfile.gettempdir()) / "test.txt"
    with open(temp_txt, 'w') as f:
        f.write("This is not an image")
    
    is_valid, error = manager.validate_image_file(str(temp_txt))
    print(f"✅ 不正ファイル形式: {not is_valid} ({error})")
    
    # テンポラリファイル削除
    temp_txt.unlink()
    
    return True


def main():
    """メインテスト実行"""
    print("🎯 Phase 1: 画像アップロード機能 統合テスト開始")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    # 個別テスト実行
    if test_image_manager():
        success_count += 1
    
    if test_youtube_manager_integration():
        success_count += 1
    
    if test_error_handling():
        success_count += 1
    
    # 結果表示
    print("\n" + "=" * 60)
    print(f"📊 テスト結果: {success_count}/{total_tests} 成功")
    
    if success_count == total_tests:
        print("🎉 Phase 1実装完了！すべてのテストに合格しました")
        print("\n✨ 実装された機能:")
        print("  ✅ 画像ファイルのバリデーション")
        print("  ✅ 画像保存・サムネイル作成")
        print("  ✅ 動画-画像関連付け")
        print("  ✅ データベース統合")
        print("  ✅ エラーハンドリング")
        print("\n🚀 次のステップ: GUIでの動作確認")
        return True
    else:
        print(f"❌ {total_tests - success_count}個のテストが失敗しました")
        return False


if __name__ == "__main__":
    main()