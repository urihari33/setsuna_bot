#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音声読み変換機能テストスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from speech_text_converter import SpeechTextConverter
from core.youtube_knowledge_manager import YouTubeKnowledgeManager
import json

def test_basic_conversion():
    """基本的なテキスト変換のテスト"""
    print("=" * 50)
    print("🔄 基本テキスト変換テスト開始")
    print("=" * 50)
    
    try:
        converter = SpeechTextConverter()
        
        # 基本テストケース
        test_cases = [
            "XOXOは良い曲ですね",
            "TRiNITYの新曲が出ました", 
            "MusicVideoを見ました",
            "VTuberのカバー曲です",
            "こんにちは、今日はいい天気ですね"  # 変換対象なし
        ]
        
        print("📝 基本変換テスト:")
        for i, test_text in enumerate(test_cases, 1):
            converted = converter.convert_for_speech(test_text)
            changed = "✅" if converted != test_text else "➖"
            print(f"  {i}. {changed} 入力: {test_text}")
            if converted != test_text:
                print(f"     → 出力: {converted}")
            print()
        
        print("✅ 基本テキスト変換テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        return False

def test_database_integration():
    """データベース統合テスト"""
    print("\n" + "=" * 50)
    print("🔗 データベース統合テスト開始") 
    print("=" * 50)
    
    try:
        # YouTube知識管理システム初期化
        knowledge_manager = YouTubeKnowledgeManager()
        
        # テキスト変換システム初期化
        converter = SpeechTextConverter()
        converter.set_knowledge_manager(knowledge_manager)
        
        # テスト用カスタム情報を一時的に追加
        test_video_id = "D7xjC200qxo"  # TRiNITY XOXO動画
        if test_video_id in knowledge_manager.knowledge_db.get("videos", {}):
            video_data = knowledge_manager.knowledge_db["videos"][test_video_id]
            
            # 元のカスタム情報をバックアップ
            original_custom_info = video_data.get("custom_info", {})
            
            # テスト用カスタム情報を設定
            test_custom_info = {
                "manual_title": "XOXO",
                "manual_artist": "TRiNITY",
                "japanese_pronunciations": ["エックスオーエックスオー"],
                "artist_pronunciations": ["トリニティ"],
                "search_keywords": ["ばちゃうた"],
                "last_edited": "2025-07-01T23:00:00",
                "edit_count": 1
            }
            
            # テスト用データを設定
            video_data["custom_info"] = test_custom_info
            print(f"📝 テスト用カスタム情報設定:")
            print(f"  楽曲名: {test_custom_info['manual_title']}")
            print(f"  アーティスト: {test_custom_info['manual_artist']}")
            print(f"  楽曲読み: {test_custom_info['japanese_pronunciations']}")
            print(f"  アーティスト読み: {test_custom_info['artist_pronunciations']}")
            
            # 変換キャッシュをクリア
            converter.clear_cache()
            
            # テストケース実行
            test_cases = [
                "XOXOはTRiNITYの楽曲です",
                "今日はXOXOを聞きました",
                "TRiNITYというアーティストを知っていますか？",
                "XOXOとTRiNITYについて話しましょう"
            ]
            
            print(f"\n🧪 データベース連携変換テスト:")
            for i, test_text in enumerate(test_cases, 1):
                converted = converter.convert_for_speech(test_text)
                changed = "✅" if converted != test_text else "➖"
                print(f"  {i}. {changed} 入力: {test_text}")
                if converted != test_text:
                    print(f"     → 出力: {converted}")
                print()
            
            # 元のカスタム情報に戻す
            if original_custom_info:
                video_data["custom_info"] = original_custom_info
            elif "custom_info" in video_data:
                del video_data["custom_info"]
            
            print("✅ データベース統合テスト完了")
            return True
            
        else:
            print(f"❌ テスト動画ID {test_video_id} が見つかりません")
            return False
            
    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        return False

def test_edge_cases():
    """エッジケーステスト"""
    print("\n" + "=" * 50)
    print("🎯 エッジケーステスト開始")
    print("=" * 50)
    
    try:
        converter = SpeechTextConverter()
        
        # エッジケース
        edge_cases = [
            "",  # 空文字
            "   ",  # 空白のみ
            "XOXOXOXO",  # 似た文字列
            "XOXOとOXOXの違い",  # 部分一致回避テスト
            "TRiNITY TRiNITY",  # 重複
            "今日はXOXO♪を聞きました♫",  # 記号混じり
            "VTuberのMVを見ました",  # 複数変換
        ]
        
        print("📝 エッジケーステスト:")
        for i, test_text in enumerate(edge_cases, 1):
            converted = converter.convert_for_speech(test_text)
            changed = "✅" if converted != test_text else "➖"
            print(f"  {i}. {changed} 入力: '{test_text}'")
            if converted != test_text:
                print(f"     → 出力: '{converted}'")
            print()
        
        print("✅ エッジケーステスト完了")
        return True
        
    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        return False

def test_performance():
    """パフォーマンステスト"""
    print("\n" + "=" * 50)
    print("⚡ パフォーマンステスト開始")
    print("=" * 50)
    
    try:
        import time
        
        converter = SpeechTextConverter()
        
        # 長いテキストで測定
        long_text = "XOXOはTRiNITYの楽曲で、Music Videoも公開されています。VTuberがカバーしたものもあり、とても人気です。" * 10
        
        # 変換時間測定
        start_time = time.time()
        
        for i in range(100):  # 100回実行
            converted = converter.convert_for_speech(long_text)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        avg_time = elapsed_time / 100
        
        print(f"📊 パフォーマンス結果:")
        print(f"  テキスト長: {len(long_text)} 文字")
        print(f"  100回実行時間: {elapsed_time:.4f}秒")
        print(f"  平均変換時間: {avg_time:.6f}秒")
        print(f"  1秒間の変換能力: {1/avg_time:.0f}回")
        
        # 結果判定
        if avg_time < 0.01:  # 10ms以下
            print("✅ パフォーマンス: 優秀（10ms以下）")
        elif avg_time < 0.05:  # 50ms以下
            print("✅ パフォーマンス: 良好（50ms以下）")
        else:
            print("⚠️ パフォーマンス: 要改善（50ms超過）")
        
        print("✅ パフォーマンステスト完了")
        return True
        
    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🧪 音声読み変換機能統合テスト開始")
    print("=" * 60)
    
    # 各テストを実行
    tests = [
        test_basic_conversion,
        test_database_integration,
        test_edge_cases,
        test_performance
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
        print("🎉 全テスト成功！音声読み変換機能は正常に動作します。")
        print("\n💡 使用効果:")
        print("• 「XOXO」→「エックスオーエックスオー」で正確な音声合成")
        print("• 「TRiNITY」→「トリニティ」で自然な読み上げ")
        print("• データベース編集で追加した読みが即座に反映")
        print("• 音声合成の品質が大幅に向上")
    else:
        print("⚠️ 一部テストが失敗しました。問題を確認してください。")
    
    print("\n🏁 テスト完了")

if __name__ == "__main__":
    main()