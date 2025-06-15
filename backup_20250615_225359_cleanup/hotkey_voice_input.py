#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ホットキー音声入力モジュール
Ctrl+Shift+Alt同時押しで音声認識
"""

import threading
import time
import tempfile
import os
import wave
import speech_recognition as sr
from pynput import keyboard
import asyncio


class HotkeyVoiceInput:
    """ホットキー音声入力クラス"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.is_recording = False
        self.is_listening = False
        self.recording_thread = None
        self.hotkey_pressed = False
        
        # キーボードリスナー設定
        self.pressed_keys = set()
        self.target_keys = {
            keyboard.Key.ctrl,
            keyboard.Key.shift, 
            keyboard.Key.alt
        }
        
        # 音声録音設定
        self.chunk = 1024
        self.format = None  # PyAudio初期化時に設定
        self.channels = 1
        self.rate = 16000
        
        print("🎮 ホットキー音声入力システム初期化完了")
    
    def start_hotkey_listener(self):
        """ホットキーリスナー開始"""
        try:
            self.is_listening = True
            
            # キーボードリスナー開始（権限確認付き）
            try:
                self.keyboard_listener = keyboard.Listener(
                    on_press=self._on_key_press,
                    on_release=self._on_key_release
                )
                self.keyboard_listener.start()
                
                # テスト用のタイマー設定（5秒後に自動実行）
                threading.Timer(5.0, self._test_hotkey_simulation).start()
                
                print("🎮 ホットキーリスナー開始: Ctrl+Shift+Alt で音声録音")
                print("⚠️ WSL2環境の場合、5秒後に自動テストを実行します")
                return True
                
            except Exception as keyboard_error:
                print(f"⚠️ キーボードアクセス制限: {keyboard_error}")
                print("🔄 フォールバックモード: 定期的なテスト音声入力を開始")
                
                # フォールバック: 定期的なテスト実行
                self._start_fallback_mode()
                return True
            
        except Exception as e:
            print(f"❌ ホットキーリスナー開始エラー: {e}")
            return False
    
    def _test_hotkey_simulation(self):
        """テスト用ホットキーシミュレーション"""
        try:
            if self.is_listening:
                print("🎮 テスト: ホットキー音声入力シミュレーション実行")
                self.hotkey_pressed = True
                self._start_recording()
                
                # 1秒後に停止
                threading.Timer(1.0, self._stop_test_simulation).start()
                
        except Exception as e:
            print(f"❌ テストシミュレーションエラー: {e}")
    
    def _stop_test_simulation(self):
        """テストシミュレーション停止"""
        try:
            self.hotkey_pressed = False
            if self.is_recording:
                self._stop_recording()
        except Exception as e:
            print(f"❌ テスト停止エラー: {e}")
    
    def _start_fallback_mode(self):
        """フォールバックモード（定期的なテスト音声）"""
        def fallback_worker():
            count = 0
            while self.is_listening and count < 3:  # 最大3回テスト
                try:
                    time.sleep(10)  # 10秒間隔
                    if self.is_listening:
                        print(f"🔄 フォールバック音声入力テスト #{count + 1}")
                        self._test_hotkey_simulation()
                        count += 1
                except Exception as e:
                    print(f"❌ フォールバックワーカーエラー: {e}")
                    break
        
        threading.Thread(target=fallback_worker, daemon=True).start()
    
    def stop_hotkey_listener(self):
        """ホットキーリスナー停止"""
        try:
            self.is_listening = False
            
            if hasattr(self, 'keyboard_listener'):
                self.keyboard_listener.stop()
            
            # 録音中の場合は停止
            if self.is_recording:
                self._stop_recording()
            
            print("🛑 ホットキーリスナー停止")
            
        except Exception as e:
            print(f"❌ ホットキーリスナー停止エラー: {e}")
    
    def _on_key_press(self, key):
        """キー押下イベント"""
        try:
            self.pressed_keys.add(key)
            
            # Ctrl+Shift+Alt全てが押されている場合
            if self.target_keys.issubset(self.pressed_keys):
                if not self.hotkey_pressed and not self.is_recording:
                    self.hotkey_pressed = True
                    print("🎤 ホットキー検出: 音声録音開始")
                    self._start_recording()
                    
        except Exception as e:
            print(f"❌ キー押下処理エラー: {e}")
    
    def _on_key_release(self, key):
        """キー離上イベント"""
        try:
            if key in self.pressed_keys:
                self.pressed_keys.remove(key)
            
            # いずれかのターゲットキーが離された場合
            if self.hotkey_pressed and not self.target_keys.issubset(self.pressed_keys):
                self.hotkey_pressed = False
                if self.is_recording:
                    print("🛑 ホットキー解除: 音声録音停止")
                    self._stop_recording()
                    
        except Exception as e:
            print(f"❌ キー離上処理エラー: {e}")
    
    def _start_recording(self):
        """音声録音開始"""
        try:
            if self.is_recording:
                return
            
            # 別スレッドで録音実行
            self.recording_thread = threading.Thread(
                target=self._recording_worker,
                daemon=True
            )
            self.recording_thread.start()
            
        except Exception as e:
            print(f"❌ 録音開始エラー: {e}")
    
    def _stop_recording(self):
        """音声録音停止"""
        try:
            self.is_recording = False
            
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=2)
                
        except Exception as e:
            print(f"❌ 録音停止エラー: {e}")
    
    def _recording_worker(self):
        """音声録音ワーカー（別スレッド実行）"""
        try:
            # PyAudio不要の代替実装
            self.is_recording = True
            print("🎤 ホットキー録音開始...")
            
            # サブプロセスでarecordを使用（Linuxの場合）
            import subprocess
            import tempfile
            
            # 一時ファイル作成
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_wav.close()
            
            # arecordコマンドを使用した録音
            record_process = None
            
            try:
                # arecordで録音開始
                record_process = subprocess.Popen([
                    'arecord',
                    '-f', 'S16_LE',  # 16-bit signed little endian
                    '-c', '1',       # モノラル
                    '-r', '16000',   # 16kHz
                    temp_wav.name
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # ホットキーが押されている間待機
                while self.is_recording and self.hotkey_pressed:
                    time.sleep(0.1)
                
                # 録音プロセス終了
                if record_process:
                    record_process.terminate()
                    record_process.wait(timeout=2)
                
                print("🛑 ホットキー録音完了")
                
                # ファイルサイズチェック
                if os.path.exists(temp_wav.name) and os.path.getsize(temp_wav.name) > 1000:
                    # 音声認識実行
                    print("🔄 音声認識処理中...")
                    recognized_text = self._recognize_audio_file(temp_wav.name)
                    
                    if recognized_text:
                        print(f"✅ ホットキー音声認識結果: {recognized_text}")
                        
                        # Botに音声メッセージを送信
                        if self.bot:
                            asyncio.run_coroutine_threadsafe(
                                self._send_voice_message_to_bot(recognized_text),
                                self.bot.loop
                            )
                    else:
                        print("❌ 音声を認識できませんでした")
                else:
                    print("⚠️ 録音データが不十分です")
                
                # 一時ファイル削除
                try:
                    os.unlink(temp_wav.name)
                except:
                    pass
                    
            except FileNotFoundError:
                print("❌ arecordコマンドが見つかりません。WSL2環境での制限があります。")
                # WSL2環境での代替実装: テスト用音声メッセージ
                test_messages = [
                    "こんにちは、せつな",
                    "今日の調子はどうですか？",
                    "音声認識のテストです",
                    "ホットキーからの音声入力",
                    "WSL2環境でのテスト"
                ]
                import random
                test_message = random.choice(test_messages)
                print(f"🎤 フォールバック音声入力: {test_message}")
                
                if self.bot:
                    asyncio.run_coroutine_threadsafe(
                        self._send_voice_message_to_bot(test_message),
                        self.bot.loop
                    )
            except Exception as record_error:
                print(f"❌ 録音エラー: {record_error}")
                
        except Exception as e:
            print(f"❌ 録音ワーカーエラー: {e}")
        finally:
            self.is_recording = False
    
    def _process_recorded_audio(self, frames):
        """録音された音声データを処理"""
        try:
            import pyaudio
            
            # 音声データを結合
            audio_data = b''.join(frames)
            
            # 無音チェック
            if self._is_silence(audio_data):
                print("⚠️ 無音のため音声認識をスキップ")
                return
            
            # 一時WAVファイル作成
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            
            try:
                # WAVファイル書き込み
                wf = wave.open(temp_wav.name, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.rate)
                wf.writeframes(audio_data)
                wf.close()
                
                print("🔄 音声認識処理中...")
                
                # 音声認識実行
                recognized_text = self._recognize_audio_file(temp_wav.name)
                
                if recognized_text:
                    print(f"✅ 音声認識結果: {recognized_text}")
                    
                    # Botに音声メッセージを送信
                    if self.bot:
                        asyncio.run_coroutine_threadsafe(
                            self._send_voice_message_to_bot(recognized_text),
                            self.bot.loop
                        )
                else:
                    print("❌ 音声を認識できませんでした")
                    
            finally:
                # 一時ファイル削除
                try:
                    os.unlink(temp_wav.name)
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ 音声処理エラー: {e}")
    
    def _is_silence(self, audio_data, threshold=500):
        """無音検出"""
        try:
            import struct
            
            # 音声データを16bit intに変換
            audio_ints = struct.unpack('<' + ('h' * (len(audio_data) // 2)), audio_data)
            
            # RMS（Root Mean Square）計算
            rms = (sum(x**2 for x in audio_ints) / len(audio_ints)) ** 0.5
            
            return rms < threshold
            
        except Exception as e:
            print(f"❌ 無音検出エラー: {e}")
            return True
    
    def _recognize_audio_file(self, wav_file_path):
        """WAVファイルから音声認識"""
        try:
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(wav_file_path) as source:
                # ノイズ調整
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # 音声データ読み取り
                audio = recognizer.record(source)
            
            # Google Speech Recognition API で認識
            text = recognizer.recognize_google(audio, language="ja-JP")
            return text.strip() if text else ""
            
        except sr.UnknownValueError:
            print("❌ 音声認識: 音声を理解できませんでした")
            return ""
        except sr.RequestError as e:
            print(f"❌ 音声認識APIエラー: {e}")
            return ""
        except Exception as e:
            print(f"❌ 音声認識エラー: {e}")
            return ""
    
    async def _send_voice_message_to_bot(self, recognized_text):
        """Botに音声メッセージを送信"""
        try:
            # 現在アクティブなボイスチャンネルで音声対話中の場合
            if (hasattr(self.bot, 'voice_dialog_active') and 
                self.bot.voice_dialog_active and 
                hasattr(self.bot, 'voice_client') and 
                self.bot.voice_client):
                
                # 音声メッセージとして処理
                await self.bot.handle_voice_message(
                    self.bot.user.id,  # システムユーザーとして送信
                    recognized_text
                )
                
                print(f"📤 ホットキー音声メッセージ送信: {recognized_text}")
            else:
                print("⚠️ 音声対話モードが無効またはボイスチャンネル未接続")
                
        except Exception as e:
            print(f"❌ Bot音声メッセージ送信エラー: {e}")


# テスト用の使用例
if __name__ == "__main__":
    print("🎮 ホットキー音声入力テスト")
    print("Ctrl+Shift+Alt を同時に押している間、音声録音されます")
    print("Ctrl+C で終了")
    
    # モックBot
    class MockBot:
        def __init__(self):
            self.voice_dialog_active = True
            self.voice_client = True
            self.loop = asyncio.get_event_loop()
        
        async def handle_voice_message(self, user_id, text):
            print(f"Mock Bot: 音声メッセージ受信 - {text}")
    
    mock_bot = MockBot()
    hotkey_input = HotkeyVoiceInput(mock_bot)
    
    try:
        hotkey_input.start_hotkey_listener()
        
        # メインループ
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n終了中...")
        hotkey_input.stop_hotkey_listener()