#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フォールバック処理デバッグ
なぜテスト音声がBotに届かないのかを詳細調査
"""

import threading
import time
import asyncio

print("🔧 フォールバック処理デバッグ")
print("=" * 40)

class DebugBot:
    """デバッグ用Bot"""
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.received_messages = []
        
        self.loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.loop_thread.start()
        time.sleep(0.5)
        print("✅ DebugBot初期化完了")
    
    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    async def handle_simple_voice_input(self, text):
        print(f"📱 DebugBot受信: '{text}'")
        self.received_messages.append(text)
        return f"受信確認: {text}"

def debug_callback(text):
    """デバッグ用コールバック"""
    print(f"📞 デバッグコールバック: '{text}'")

class DebugFallbackSystem:
    """フォールバック処理デバッグ版"""
    
    def __init__(self, bot, callback):
        self.bot = bot
        self.voice_callback = callback
        self.is_recording = True  # 常に録音中として扱う
    
    def debug_fallback_test_recording(self):
        """デバッグ版フォールバック"""
        print("🔄 デバッグ版フォールバック開始")
        
        test_message = "デバッグテスト音声"
        print(f"🎤 テスト音声設定: '{test_message}'")
        
        def delayed_test():
            print("⏳ 1秒待機開始...")
            time.sleep(1)
            print("⏳ 1秒待機完了")
            
            if self.is_recording:
                print(f"✅ 録音状態確認OK - テスト音声処理開始")
                print(f"🎤 テスト音声生成: '{test_message}'")
                self.debug_process_recognized_text(test_message)
            else:
                print("❌ 録音状態がFalse - 処理をスキップ")
        
        print("🧵 デバッグスレッド開始...")
        thread = threading.Thread(target=delayed_test, daemon=True)
        thread.start()
        print("🧵 デバッグスレッド開始完了")
        
        # メインスレッドで少し待機
        time.sleep(2)
        print("🔄 デバッグ版フォールバック完了")
    
    def debug_process_recognized_text(self, recognized_text):
        """デバッグ版テキスト処理"""
        try:
            print(f"📝 デバッグテキスト処理開始: '{recognized_text}'")
            
            # Bot送信テスト
            if self.bot and hasattr(self.bot, 'loop'):
                print("🤖 Bot確認OK - 非同期送信開始")
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        self.bot.handle_simple_voice_input(recognized_text),
                        self.bot.loop
                    )
                    print("📤 非同期タスクスケジュール完了")
                    
                    # 結果待機
                    print("⏳ 結果待機中...")
                    result = future.result(timeout=5)
                    print(f"✅ Bot送信成功: {result}")
                    
                except Exception as e:
                    print(f"❌ Bot送信エラー: {e}")
                    import traceback
                    print(f"📋 エラー詳細: {traceback.format_exc()}")
            else:
                print("❌ Bot確認失敗")
            
            # コールバックテスト
            if self.voice_callback:
                print("📞 コールバック実行開始")
                try:
                    self.voice_callback(recognized_text)
                    print("✅ コールバック実行成功")
                except Exception as e:
                    print(f"❌ コールバック実行エラー: {e}")
            else:
                print("❌ コールバック未設定")
                
        except Exception as e:
            print(f"❌ デバッグテキスト処理エラー: {e}")
            import traceback
            print(f"📋 エラー詳細: {traceback.format_exc()}")

def test_step_by_step():
    """段階的テスト"""
    print("\n📋 段階的デバッグテスト開始")
    
    # Step 1: Bot作成
    print("\nStep 1: Bot作成")
    bot = DebugBot()
    
    # Step 2: デバッグシステム作成
    print("\nStep 2: デバッグシステム作成")
    debug_system = DebugFallbackSystem(bot, debug_callback)
    
    # Step 3: フォールバック実行
    print("\nStep 3: フォールバック実行")
    debug_system.debug_fallback_test_recording()
    
    # Step 4: 結果確認
    print(f"\nStep 4: 結果確認")
    print(f"   Bot受信メッセージ数: {len(bot.received_messages)}件")
    if bot.received_messages:
        for i, msg in enumerate(bot.received_messages, 1):
            print(f"     {i}. '{msg}'")
    
    # Step 5: 直接テスト
    print(f"\nStep 5: 直接処理テスト")
    debug_system.debug_process_recognized_text("直接テスト音声")
    
    time.sleep(1)  # 処理完了待機
    
    print(f"\n📊 最終結果:")
    print(f"   最終メッセージ数: {len(bot.received_messages)}件")
    
    if len(bot.received_messages) >= 2:
        print("✅ デバッグテスト成功 - 問題を特定可能")
    else:
        print("❌ デバッグテストで問題継続 - 詳細調査必要")

if __name__ == "__main__":
    test_step_by_step()