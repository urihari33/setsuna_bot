#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音声監視システム
常時ローカル音声監視 + ホットキートリガー音声認識
"""

import pyaudio
import wave
import threading
import time
import tempfile
import os
import queue
import speech_recognition as sr
import numpy as np
from pynput import keyboard
from typing import Callable, Optional
import asyncio


class VoiceMonitorSystem:
    """常時音声監視＋ホットキートリガーシステム"""
    
    def __init__(self, bot_instance, voice_callback: Optional[Callable] = None):
        self.bot = bot_instance
        self.voice_callback = voice_callback
        
        # 監視状態
        self.is_monitoring = False
        self.is_hotkey_pressed = False
        self.is_recording_mode = False
        
        # 音声設定
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.record_seconds_buffer = 10  # 最大録音時間
        
        # 音声処理
        self.audio_queue = queue.Queue()
        self.recording_buffer = []
        self.silence_threshold = 500  # 音量閾値
        self.min_speech_duration = 0.5  # 最小発話時間（秒）
        
        # スレッド管理
        self.monitor_thread = None
        self.keyboard_thread = None
        
        # ホットキー設定
        self.pressed_keys = set()
        self.target_keys = {
            keyboard.Key.ctrl,
            keyboard.Key.shift,
            keyboard.Key.alt
        }
        
        # 音声認識
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        print("🎤 音声監視システム初期化完了")
    
    def start_monitoring(self) -> bool:
        """音声監視開始"""
        if self.is_monitoring:
            print("⚠️ 既に音声監視中です")
            return False
        
        try:
            self.is_monitoring = True
            
            # 音声監視スレッド開始
            self.monitor_thread = threading.Thread(
                target=self._audio_monitor_worker,
                daemon=True
            )
            self.monitor_thread.start()
            
            # キーボード監視スレッド開始
            self.keyboard_thread = threading.Thread(
                target=self._keyboard_monitor_worker,
                daemon=True
            )
            self.keyboard_thread.start()
            
            print("🎤 音声監視開始 - Ctrl+Shift+Alt でトリガー")
            return True
            
        except Exception as e:
            print(f"❌ 音声監視開始エラー: {e}")
            self.is_monitoring = False
            return False
    
    def stop_monitoring(self):
        """音声監視停止"""
        if not self.is_monitoring:
            return
        
        print("🛑 音声監視停止中...")
        self.is_monitoring = False
        self.is_hotkey_pressed = False
        
        # スレッド終了待機
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        
        if self.keyboard_thread and self.keyboard_thread.is_alive():
            self.keyboard_thread.join(timeout=2)
        
        print("✅ 音声監視停止完了")
    
    def _audio_monitor_worker(self):
        """音声監視ワーカー（メインスレッド）"""
        try:
            # PyAudio初期化
            p = pyaudio.PyAudio()
            
            # 音声ストリーム開始
            stream = p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            print("🎧 音声ストリーム開始")
            
            # 監視ループ
            while self.is_monitoring:
                try:
                    # 音声データ読み取り
                    audio_data = stream.read(self.chunk, exception_on_overflow=False)
                    
                    # 音声レベル計算
                    audio_level = self._calculate_audio_level(audio_data)
                    
                    # ホットキー押下時のみ録音バッファに追加
                    if self.is_hotkey_pressed:
                        if not self.is_recording_mode:
                            print("🔴 録音開始")
                            self.is_recording_mode = True
                            self.recording_buffer = []
                        
                        self.recording_buffer.append(audio_data)
                        
                        # バッファサイズ制限
                        max_frames = int(self.rate / self.chunk * self.record_seconds_buffer)
                        if len(self.recording_buffer) > max_frames:
                            self.recording_buffer.pop(0)
                    
                    elif self.is_recording_mode:
                        # ホットキー離上時の処理
                        print("⏹️ 録音終了 - 音声認識処理中...")
                        self.is_recording_mode = False
                        
                        # 音声認識処理を別スレッドで実行
                        if self.recording_buffer:
                            threading.Thread(
                                target=self._process_recorded_audio,
                                args=(self.recording_buffer.copy(),),
                                daemon=True
                            ).start()
                        
                        self.recording_buffer = []
                    
                    # 短時間待機
                    time.sleep(0.01)
                
                except Exception as e:
                    print(f"⚠️ 音声監視ループエラー: {e}")
                    time.sleep(0.1)
            
            # ストリーム終了
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except Exception as e:
            print(f"❌ 音声監視ワーカーエラー: {e}")
        finally:
            print("🎧 音声ストリーム終了")
    
    def _keyboard_monitor_worker(self):
        """キーボード監視ワーカー"""
        try:
            with keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            ) as listener:
                print("⌨️ キーボード監視開始")
                
                while self.is_monitoring:
                    time.sleep(0.1)
                
                listener.stop()
                
        except Exception as e:
            print(f"❌ キーボード監視エラー: {e}")
        finally:
            print("⌨️ キーボード監視終了")
    
    def _on_key_press(self, key):
        """キー押下イベント"""
        try:
            self.pressed_keys.add(key)
            
            # Ctrl+Shift+Alt同時押し検出
            if self.target_keys.issubset(self.pressed_keys):
                if not self.is_hotkey_pressed:
                    self.is_hotkey_pressed = True
                    # print("🎮 ホットキー押下検出")
        
        except Exception as e:
            print(f"❌ キー押下処理エラー: {e}")
    
    def _on_key_release(self, key):
        """キー離上イベント"""
        try:
            if key in self.pressed_keys:
                self.pressed_keys.remove(key)
            
            # いずれかのターゲットキーが離された場合
            if self.is_hotkey_pressed and not self.target_keys.issubset(self.pressed_keys):
                self.is_hotkey_pressed = False
                # print("🎮 ホットキー離上検出")
        
        except Exception as e:
            print(f"❌ キー離上処理エラー: {e}")
    
    def _calculate_audio_level(self, audio_data):
        """音声レベル計算（RMS）"""
        try:
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_np**2))
            return rms
        except:
            return 0
    
    def _is_speech_detected(self, audio_buffer):
        """発話検出（VAD: Voice Activity Detection）"""
        if not audio_buffer:
            return False
        
        # 全体の音声レベルを計算
        combined_audio = b''.join(audio_buffer)
        audio_level = self._calculate_audio_level(combined_audio)
        
        # 音量閾値チェック
        if audio_level < self.silence_threshold:
            return False
        
        # 最小発話時間チェック
        duration = len(audio_buffer) * self.chunk / self.rate
        if duration < self.min_speech_duration:
            return False
        
        return True
    
    def _process_recorded_audio(self, audio_buffer):
        """録音音声の処理"""
        try:
            if not self._is_speech_detected(audio_buffer):
                print("⚠️ 音声が検出されませんでした（無音またはノイズ）")
                return
            
            # WAVファイル作成
            combined_audio = b''.join(audio_buffer)
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(self.channels)
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(self.rate)
                    wav_file.writeframes(combined_audio)
                
                # 音声認識実行
                recognized_text = self._recognize_audio_file(temp_file.name)
                
                # 一時ファイル削除
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                
                if recognized_text:
                    print(f"✅ 音声認識成功: '{recognized_text}'")
                    
                    # 独り言フィルタリング
                    if self._is_valid_command(recognized_text):
                        # Botに音声メッセージ送信
                        if self.bot and hasattr(self.bot, 'loop'):
                            asyncio.run_coroutine_threadsafe(
                                self.bot.handle_voice_input(recognized_text),
                                self.bot.loop
                            )
                        
                        # コールバック実行
                        if self.voice_callback:
                            self.voice_callback(recognized_text)
                    else:
                        print(f"🔇 独り言として無視: '{recognized_text}'")
                else:
                    print("❌ 音声認識失敗")
        
        except Exception as e:
            print(f"❌ 音声処理エラー: {e}")
    
    def _recognize_audio_file(self, wav_file_path):
        """音声ファイルから文字認識"""
        try:
            with sr.AudioFile(wav_file_path) as source:
                # ノイズ調整
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                # 音声データ読み取り
                audio = self.recognizer.record(source)
            
            # Google音声認識
            text = self.recognizer.recognize_google(audio, language="ja-JP")
            return text.strip() if text else ""
            
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"❌ 音声認識APIエラー: {e}")
            return ""
        except Exception as e:
            print(f"❌ 音声認識エラー: {e}")
            return ""
    
    def _is_valid_command(self, text):
        """有効なコマンドかどうか判定（独り言フィルタリング）"""
        if not text or len(text.strip()) < 2:
            return False
        
        # せつなへの呼びかけキーワード
        valid_triggers = [
            "せつな", "セツナ", "こんにちは", "おはよう", "こんばんは",
            "ありがとう", "教えて", "どう思う", "聞いて", "話そう"
        ]
        
        text_lower = text.lower()
        for trigger in valid_triggers:
            if trigger in text_lower:
                return True
        
        # 疑問符や感嘆符を含む場合
        if "?" in text or "？" in text or "!" in text or "！" in text:
            return True
        
        # 一定以上の長さの発話
        if len(text) >= 8:
            return True
        
        return False
    
    def get_status(self):
        """監視状態取得"""
        return {
            'is_monitoring': self.is_monitoring,
            'is_hotkey_pressed': self.is_hotkey_pressed,
            'is_recording_mode': self.is_recording_mode,
            'buffer_size': len(self.recording_buffer) if hasattr(self, 'recording_buffer') else 0
        }


# テスト用関数
def test_voice_callback(recognized_text):
    """テスト用コールバック"""
    print(f"🗣️ 音声コールバック: {recognized_text}")


if __name__ == "__main__":
    print("🎤 音声監視システムテスト")
    
    # モックBot
    class MockBot:
        def __init__(self):
            self.loop = asyncio.get_event_loop()
        
        async def handle_voice_input(self, text):
            print(f"MockBot: 音声入力受信 - {text}")
    
    mock_bot = MockBot()
    monitor = VoiceMonitorSystem(mock_bot, test_voice_callback)
    
    try:
        print("音声監視を開始します...")
        print("Ctrl+Shift+Alt を押しながら話してください")
        print("Ctrl+C で終了")
        
        monitor.start_monitoring()
        
        # メインループ
        while True:
            time.sleep(1)
            status = monitor.get_status()
            if status['is_recording_mode']:
                print(f"🔴 録音中... バッファサイズ: {status['buffer_size']}")
            
    except KeyboardInterrupt:
        print("\n終了中...")
        monitor.stop_monitoring()
        print("✅ 終了完了")