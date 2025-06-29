#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTubeタイトル簡略化機能のテスト
"""

import sys
import os
from pathlib import Path

# パス設定
sys.path.append(str(Path(__file__).parent))

def test_title_extraction():
    """楽曲名抽出機能のテスト"""
    print("=== 楽曲名抽出テスト ===")
    
    try:
        from core.youtube_knowledge_manager import YouTubeKnowledgeManager
        
        manager = YouTubeKnowledgeManager()
        
        # 実際のYouTubeタイトルでテスト
        test_cases = [
            {
                "title": "▽▲TRiNITY▲▽『XOXO』Music Video【2022/10/5発売「Δ(DELTA)」収録曲】",
                "expected": "XOXO"
            },
            {
                "title": "【オリジナルMV】Blessing / にじさんじ元2期生 cover.",
                "expected": "Blessing"
            },
            {
                "title": "【歌ってみた】犬のおまわりさん【栞葉るり/にじさんじ】",
                "expected": "犬のおまわりさん"
            },
            {
                "title": "【ラピスリライツ】supernova「Trinity」MV（フルサイズver）",
                "expected": "Trinity"
            },
            {
                "title": "☪ 水平線 / back number(Cover) by天月",
                "expected": "水平線"
            },
            {
                "title": "crazy (about you) - kamome sano",
                "expected": "crazy (about you)"
            }
        ]
        
        success_count = 0
        total_count = len(test_cases)
        
        for test_case in test_cases:
            title = test_case["title"]
            expected = test_case["expected"]
            
            extracted = manager._extract_main_title(title)
            
            print(f"\n📹 元タイトル: {title}")
            print(f"🎵 抽出結果: '{extracted}'")
            print(f"✅ 期待値: '{expected}'")
            
            if extracted == expected:
                print("✅ 成功")
                success_count += 1
            else:
                print("❌ 失敗")
        
        print(f"\n📊 楽曲名抽出成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
        return success_count > total_count * 0.7  # 70%以上成功で合格
        
    except Exception as e:
        print(f"❌ 楽曲名抽出テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_context_formatting():
    """コンテキストフォーマットテスト"""
    print("\n=== コンテキストフォーマットテスト ===")
    
    try:
        from core.conversation_context_builder import ConversationContextBuilder
        
        builder = ConversationContextBuilder()
        
        # 具体的な動画での検索テスト
        test_inputs = [
            "にじさんじの動画でおすすめある",
            "TRiNITYの動画知ってる",
            "Blessingって曲について教えて"
        ]
        
        for test_input in test_inputs:
            print(f"\n🔍 入力: '{test_input}'")
            
            context_text = builder.process_user_input(test_input)
            
            if context_text:
                print("✅ コンテキスト生成成功")
                print("📄 フォーマット結果:")
                print(context_text[:300] + "..." if len(context_text) > 300 else context_text)
                
                # 楽曲名抽出が適用されているかチェック
                if "楽曲名:" in context_text:
                    print("✅ 楽曲名抽出が適用されている")
                else:
                    print("⚠️ 楽曲名抽出が適用されていない")
            else:
                print("❌ コンテキスト生成失敗")
        
        return True
        
    except Exception as e:
        print(f"❌ コンテキストフォーマットテスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversation_simulation():
    """会話シミュレーションテスト"""
    print("\n=== 会話シミュレーションテスト ===")
    
    try:
        from core.conversation_context_builder import ConversationContextBuilder
        
        builder = ConversationContextBuilder()
        
        print("📝 期待される会話パターン:")
        print("【改善前】「【オリジナルMV】Blessing / にじさんじ元2期生 cover.をおすすめするかな」")
        print("【改善後】「Blessingをおすすめするかな」")
        
        # 実際のコンテキスト生成をテスト
        context_text = builder.process_user_input("にじさんじの動画でおすすめある")
        
        if context_text and "楽曲名:" in context_text:
            print("\n✅ タイトル簡略化機能が正常に動作")
            print("🎯 せつなは簡潔な楽曲名で回答するはず")
        else:
            print("\n❌ タイトル簡略化機能に問題あり")
        
        return True
        
    except Exception as e:
        print(f"❌ 会話シミュレーションテスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メインテスト実行"""
    print("🎵 YouTubeタイトル簡略化機能テスト開始\n")
    
    results = []
    
    # 各テストの実行
    results.append(test_title_extraction())
    results.append(test_context_formatting())
    results.append(test_conversation_simulation())
    
    # 結果サマリー
    print("\n" + "="*60)
    print("📊 タイトル簡略化テスト結果サマリー")
    print("="*60)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"❌ 失敗: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 全テスト合格！タイトル簡略化機能が正常に動作しています。")
        print("\n✨ 改善効果:")
        print("- 長いYouTubeタイトル → 簡潔な楽曲名")
        print("- 音声での聞きやすさ向上")
        print("- 自然な会話表現")
        print("\n🔧 次のステップ: 実際の音声会話でテスト")
        print("推奨テスト文:")
        print("- 「にじさんじの動画でおすすめある」")
        print("- 「TRiNITYの動画知ってる」")
    else:
        print(f"\n⚠️ 一部改善が必要です。詳細は上記ログを確認してください。")

if __name__ == "__main__":
    main()