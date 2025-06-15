#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音声出力確認テスト
フォールバック音声がMockBotに正しく送信されているか確認
"""

import asyncio
import time
from simple_hotkey_voice_fixed import SimpleHotkeyVoice

print("🔊 音声出力確認テスト")
print("=" * 40)

class TestBot:
    """音声入力テスト用Bot"""
    
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.received_messages = []
        print("✅ TestBot初期化完了")
    
    async def handle_simple_voice_input(self, text):
        """音声入力ハンドラー"""
        print(f"🎤 TestBot音声受信: '{text}'")
        self.received_messages.append({
            'text': text,
            'timestamp': time.time()
        })
        print(f"📝 受信メッセージ数: {len(self.received_messages)}件")

def test_voice_callback(recognized_text):
    """コールバックテスト"""
    print(f"📞 コールバック受信: '{recognized_text}'")

def test_fallback_voice_generation():
    """フォールバック音声生成テスト"""
    print("\n📋 フォールバック音声生成テスト開始")
    
    # TestBot作成
    test_bot = TestBot()
    
    # SimpleHotkeyVoice作成
    hotkey_voice = SimpleHotkeyVoice(test_bot, test_voice_callback)
    
    print("🔄 手動でフォールバック音声を生成...")
    
    # 手動でフォールバック実行
    hotkey_voice._fallback_test_recording()
    
    # 3秒待機（非同期処理のため）
    print("⏳ 3秒待機中...")
    time.sleep(3)
    
    # 結果確認
    print(f"\n📊 テスト結果:")
    print(f"   受信メッセージ数: {len(test_bot.received_messages)}件")
    
    if test_bot.received_messages:
        print("   受信したメッセージ:")
        for i, msg in enumerate(test_bot.received_messages, 1):
            print(f"     {i}. '{msg['text']}'")
        print("✅ フォールバック音声生成・送信成功")
    else:
        print("❌ メッセージが受信されませんでした")
    
    return len(test_bot.received_messages) > 0

def test_direct_text_processing():
    """直接テキスト処理テスト"""
    print("\n📋 直接テキスト処理テスト開始")
    
    test_bot = TestBot()
    hotkey_voice = SimpleHotkeyVoice(test_bot, test_voice_callback)
    
    test_texts = [
        "テスト音声1",
        "せつな、こんにちは",
        "直接処理テスト"
    ]
    
    print("📝 テストテキストを直接処理...")
    
    for text in test_texts:
        print(f"   処理中: '{text}'")
        hotkey_voice._process_recognized_text(text)
        time.sleep(1)  # 処理時間確保
    
    # 結果確認
    print(f"\n📊 直接処理テスト結果:")
    print(f"   送信テキスト数: {len(test_texts)}件")
    print(f"   受信メッセージ数: {len(test_bot.received_messages)}件")
    
    if len(test_bot.received_messages) == len(test_texts):
        print("✅ 直接テキスト処理成功")
        return True
    else:
        print("❌ 一部メッセージが処理されませんでした")
        return False

# テスト実行
def main():
    print("フォールバック音声システムの動作確認を行います\n")
    
    # テスト1: フォールバック音声生成
    test1_success = test_fallback_voice_generation()
    
    # テスト2: 直接テキスト処理
    test2_success = test_direct_text_processing()
    
    # 総合結果
    print("\n" + "=" * 40)
    print("📊 総合テスト結果:")
    print(f"   フォールバック音声生成: {'✅ 成功' if test1_success else '❌ 失敗'}")
    print(f"   直接テキスト処理: {'✅ 成功' if test2_success else '❌ 失敗'}")
    
    if test1_success and test2_success:
        print("\n🎉 全テスト成功！")
        print("フォールバック音声システムが正常に動作しています")
        print("\n📋 次のステップ:")
        print("   1. 元のsimple_hotkey_voice.pyを修正版に置き換え")
        print("   2. Discord bot統合テスト")
        print("   3. 完全な音声対話テスト")
    else:
        print("\n🔧 修正が必要な項目があります")
        print("失敗したテストの詳細を確認してください")

if __name__ == "__main__":
    main()