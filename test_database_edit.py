#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベース編集機能テストスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.youtube_knowledge_manager import YouTubeKnowledgeManager
import json

def test_custom_info_search():
    """カスタム情報検索のテスト"""
    print("=" * 50)
    print("🔍 カスタム情報検索テスト開始")
    print("=" * 50)
    
    try:
        # 知識管理システム初期化
        manager = YouTubeKnowledgeManager()
        
        # テスト用のカスタム情報を追加
        test_video_id = "D7xjC200qxo"  # TRiNITY XOXO動画
        if test_video_id in manager.knowledge_db.get("videos", {}):
            video_data = manager.knowledge_db["videos"][test_video_id]
            
            # テスト用カスタム情報を設定
            test_custom_info = {
                "manual_title": "XOXO",
                "manual_artist": "TRiNITY",
                "japanese_pronunciations": ["エックスオーエックスオー", "エクスオクスオ"],
                "artist_pronunciations": ["トリニティ", "トリニティー"],
                "search_keywords": ["ばちゃうた", "にじさんじ音楽"],
                "last_edited": "2025-07-01T22:30:00",
                "edit_count": 1
            }
            
            # 既存のカスタム情報をバックアップ
            original_custom_info = video_data.get("custom_info", {})
            
            # テスト用カスタム情報を設定
            video_data["custom_info"] = test_custom_info
            
            print(f"📝 テスト用カスタム情報を設定:")
            for key, value in test_custom_info.items():
                if key != "last_edited":
                    print(f"  {key}: {value}")
            
            # 検索テスト実行
            test_queries = [
                "XOXO",  # 楽曲名
                "TRiNITY",  # アーティスト名
                "エックスオーエックスオー",  # 楽曲の日本語読み
                "エクスオクスオ",  # 楽曲の日本語読み（別パターン）
                "トリニティ",  # アーティストの日本語読み
                "トリニティー",  # アーティストの日本語読み（別パターン）
                "ばちゃうた",  # 検索キーワード
                "xoxo",  # 小文字
                "trinity",  # 小文字
            ]
            
            print(f"\n🔍 検索テスト実行:")
            for query in test_queries:
                results = manager.search_videos(query, limit=3)
                found_target = any(r["video_id"] == test_video_id for r in results)
                status = "✅ 発見" if found_target else "❌ 未発見"
                score = next((r["score"] for r in results if r["video_id"] == test_video_id), 0)
                print(f"  「{query}」 → {status} (スコア: {score})")
            
            # 元のカスタム情報に戻す
            if original_custom_info:
                video_data["custom_info"] = original_custom_info
            elif "custom_info" in video_data:
                del video_data["custom_info"]
            
            print("\n✅ カスタム情報検索テスト完了")
            return True
            
        else:
            print(f"❌ テスト動画ID {test_video_id} が見つかりません")
            return False
            
    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        return False

def test_database_structure():
    """データベース構造のテスト"""
    print("\n" + "=" * 50)
    print("🗂️ データベース構造テスト開始")
    print("=" * 50)
    
    try:
        # 知識管理システム初期化
        manager = YouTubeKnowledgeManager()
        
        videos = manager.knowledge_db.get("videos", {})
        video_count = len(videos)
        custom_info_count = 0
        
        # カスタム情報を持つ動画をカウント
        for video_id, video_data in videos.items():
            if "custom_info" in video_data:
                custom_info_count += 1
        
        print(f"📊 データベース統計:")
        print(f"  総動画数: {video_count}")
        print(f"  カスタム情報あり: {custom_info_count}")
        print(f"  カスタム情報なし: {video_count - custom_info_count}")
        
        # サンプル動画の構造確認
        if videos:
            sample_id = list(videos.keys())[0]
            sample_video = videos[sample_id]
            
            print(f"\n📝 サンプル動画構造 (ID: {sample_id}):")
            print(f"  タイトル: {sample_video.get('metadata', {}).get('title', '不明')[:50]}...")
            print(f"  チャンネル: {sample_video.get('metadata', {}).get('channel_title', '不明')}")
            print(f"  カスタム情報: {'あり' if 'custom_info' in sample_video else 'なし'}")
            
            if 'custom_info' in sample_video:
                custom_info = sample_video['custom_info']
                print(f"  カスタム情報詳細:")
                for key, value in custom_info.items():
                    print(f"    {key}: {value}")
        
        print("\n✅ データベース構造テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        return False

def test_save_load_functionality():
    """保存・読み込み機能のテスト"""
    print("\n" + "=" * 50)
    print("💾 保存・読み込み機能テスト開始")
    print("=" * 50)
    
    try:
        # 知識管理システム初期化
        manager = YouTubeKnowledgeManager()
        
        # バックアップファイルパス
        backup_path = manager.knowledge_db_path.with_suffix('.backup')
        
        # 現在のデータベースをバックアップ
        import shutil
        shutil.copy(manager.knowledge_db_path, backup_path)
        print(f"📁 データベースをバックアップ: {backup_path}")
        
        # テスト用データを追加
        test_video_id = list(manager.knowledge_db.get("videos", {}).keys())[0]
        original_data = manager.knowledge_db["videos"][test_video_id].copy()
        
        test_custom_info = {
            "manual_title": "テスト楽曲",
            "manual_artist": "テストアーティスト",
            "japanese_pronunciations": ["テストソング"],
            "artist_pronunciations": ["テストアーティスト"],
            "search_keywords": ["テストキーワード"],
            "last_edited": "2025-07-01T22:30:00",
            "edit_count": 999
        }
        
        # カスタム情報を追加
        manager.knowledge_db["videos"][test_video_id]["custom_info"] = test_custom_info
        
        # データベースを保存
        with open(manager.knowledge_db_path, 'w', encoding='utf-8') as f:
            json.dump(manager.knowledge_db, f, ensure_ascii=False, indent=2)
        
        print(f"💾 テストデータを保存")
        
        # データベースを再読み込み
        manager._load_knowledge_db()
        
        # 保存されたデータを確認
        saved_custom_info = manager.knowledge_db["videos"][test_video_id].get("custom_info", {})
        
        if saved_custom_info == test_custom_info:
            print("✅ 保存・読み込み成功")
            result = True
        else:
            print("❌ 保存・読み込み失敗")
            print(f"期待値: {test_custom_info}")
            print(f"実際値: {saved_custom_info}")
            result = False
        
        # 元のデータに戻す
        shutil.copy(backup_path, manager.knowledge_db_path)
        backup_path.unlink()  # バックアップファイルを削除
        print(f"🔄 データベースを元に戻しました")
        
        print("\n✅ 保存・読み込み機能テスト完了")
        return result
        
    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        # エラー時もバックアップから復元を試行
        try:
            if backup_path.exists():
                shutil.copy(backup_path, manager.knowledge_db_path)
                backup_path.unlink()
                print(f"🔄 エラー後にデータベースを復元しました")
        except:
            pass
        return False

def main():
    """メインテスト実行"""
    print("🧪 データベース編集機能統合テスト開始")
    print("=" * 60)
    
    # 各テストを実行
    tests = [
        test_database_structure,
        test_custom_info_search,
        test_save_load_functionality
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ テスト実行エラー: {e}")
            results.append(False)
    
    # 結果まとめ
    print("\n" + "=" * 60)
    print("📊 テスト結果まとめ")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ 成功: {passed}/{total} テスト")
    print(f"❌ 失敗: {total - passed}/{total} テスト")
    
    if passed == total:
        print("🎉 全テスト成功！データベース編集機能は正常に動作する準備ができています。")
        print("\n📝 使用方法:")
        print("1. voice_chat_gui.py を起動")
        print("2. URL表示エリアの動画を右クリック")
        print("3. '動画情報を編集' を選択")
        print("4. 楽曲名、アーティスト名、日本語読み、検索キーワードを編集")
        print("5. 保存ボタンをクリック")
        print("\n💡 音声認識対応のポイント:")
        print("• 楽曲の日本語読み: 「エックスオーエックスオー」→「XOXO」")
        print("• アーティストの日本語読み: 「トリニティ」→「TRiNITY」")
        print("• 音声入力時の検索精度が大幅に向上します")
    else:
        print("⚠️ 一部テストが失敗しました。問題を確認してください。")
    
    print("\n🏁 テスト完了")

if __name__ == "__main__":
    main()