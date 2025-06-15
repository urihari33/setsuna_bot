#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
非同期処理修正テスト
asyncio処理の問題を特定・修正
"""

import asyncio
import time
import threading
from concurrent.futures import Future

print("🔧 非同期処理修正テスト")
print("=" * 40)

class AsyncTestBot:
    """非同期処理テスト用Bot"""
    
    def __init__(self):
        # 新しいイベントループを作成
        self.loop = asyncio.new_event_loop()
        self.received_messages = []
        
        # バックグラウンドでループを実行
        self.loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.loop_thread.start()
        
        print("✅ AsyncTestBot初期化完了")
        print(f"   ループスレッド: {self.loop_thread.name}")
    
    def _run_loop(self):
        """バックグラウンドでイベントループを実行"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    async def handle_simple_voice_input(self, text):
        """音声入力ハンドラー（修正版）"""
        print(f"🎤 AsyncTestBot音声受信: '{text}'")
        self.received_messages.append({
            'text': text,
            'timestamp': time.time()
        })
        print(f"📝 受信メッセージ数: {len(self.received_messages)}件")
        return f"処理完了: {text}"

def test_async_processing():
    """非同期処理テスト"""
    print("\n📋 非同期処理テスト開始")
    
    bot = AsyncTestBot()
    
    # 少し待機してループが開始されるのを待つ
    time.sleep(0.5)
    
    test_messages = [
        "非同期テスト1",
        "非同期テスト2", 
        "非同期テスト3"
    ]
    
    print("📝 非同期でメッセージを送信中...")
    
    futures = []
    for msg in test_messages:
        print(f"   送信: '{msg}'")
        
        # 非同期タスクをスケジュール
        future = asyncio.run_coroutine_threadsafe(
            bot.handle_simple_voice_input(msg),
            bot.loop
        )
        futures.append(future)
    
    # 全ての非同期処理の完了を待機
    print("⏳ 非同期処理完了を待機中...")
    
    for i, future in enumerate(futures):
        try:
            result = future.result(timeout=5)
            print(f"   タスク{i+1}完了: {result}")
        except Exception as e:
            print(f"   タスク{i+1}エラー: {e}")
    
    # 結果確認
    time.sleep(1)  # 少し追加待機
    
    print(f"\n📊 非同期処理テスト結果:")
    print(f"   送信メッセージ数: {len(test_messages)}件")
    print(f"   受信メッセージ数: {len(bot.received_messages)}件")
    
    if len(bot.received_messages) == len(test_messages):
        print("✅ 非同期処理成功")
        return True
    else:
        print("❌ 非同期処理で問題発生")
        return False

def test_modified_voice_processing():
    """修正版音声処理テスト"""
    print("\n📋 修正版音声処理テスト開始")
    
    class ModifiedSimpleHotkeyVoice:
        """修正版シンプルホットキー音声（テスト用）"""
        
        def __init__(self, bot_instance):
            self.bot = bot_instance
        
        def _process_recognized_text_fixed(self, recognized_text):
            """修正版テキスト処理"""
            try:
                print(f"📝 修正版テキスト処理: '{recognized_text}'")
                
                # Botに音声メッセージ送信（修正版）
                if self.bot and hasattr(self.bot, 'loop'):
                    future = asyncio.run_coroutine_threadsafe(
                        self.bot.handle_simple_voice_input(recognized_text),
                        self.bot.loop
                    )
                    
                    # 結果を待機（タイムアウト付き）
                    try:
                        result = future.result(timeout=3)
                        print(f"✅ Discord bot送信完了: {result}")
                    except Exception as e:
                        print(f"❌ Discord bot送信エラー: {e}")
                
            except Exception as e:
                print(f"❌ 修正版テキスト処理エラー: {e}")
    
    bot = AsyncTestBot()
    time.sleep(0.5)  # ループ開始待機
    
    voice_system = ModifiedSimpleHotkeyVoice(bot)
    
    test_texts = [
        "修正版テスト1",
        "修正版テスト2"
    ]
    
    print("📝 修正版でテキストを処理中...")
    
    for text in test_texts:
        print(f"   処理: '{text}'")
        voice_system._process_recognized_text_fixed(text)
        time.sleep(1)
    
    # 結果確認
    print(f"\n📊 修正版処理テスト結果:")
    print(f"   処理テキスト数: {len(test_texts)}件")
    print(f"   受信メッセージ数: {len(bot.received_messages)}件")
    
    if len(bot.received_messages) == len(test_texts):
        print("✅ 修正版処理成功")
        return True
    else:
        print("❌ 修正版処理で問題発生")
        return False

# テスト実行
def main():
    print("非同期処理の問題を診断・修正します\n")
    
    # テスト1: 基本的な非同期処理
    test1_success = test_async_processing()
    
    # テスト2: 修正版音声処理
    test2_success = test_modified_voice_processing()
    
    # 総合結果
    print("\n" + "=" * 40)
    print("📊 非同期処理修正テスト結果:")
    print(f"   基本非同期処理: {'✅ 成功' if test1_success else '❌ 失敗'}")
    print(f"   修正版音声処理: {'✅ 成功' if test2_success else '❌ 失敗'}")
    
    if test1_success and test2_success:
        print("\n🎉 非同期処理修正成功！")
        print("この修正をSimpleHotkeyVoiceクラスに適用できます")
        print("\n📋 修正のポイント:")
        print("   1. バックグラウンドでイベントループを実行")
        print("   2. future.result()で処理完了を確認")
        print("   3. タイムアウト付きで安全な処理")
    else:
        print("\n🤔 非同期処理で問題が継続しています")
        print("別のアプローチを検討する必要があります")

if __name__ == "__main__":
    main()