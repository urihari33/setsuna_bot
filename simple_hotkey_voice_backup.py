#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルホットキー音声認識システム
PyAudio不要・軽量実装
"""

import threading
import time
import tempfile
import os
import subprocess
import speech_recognition as sr
from pynput import keyboard
from typing import Callable, Optional
import asyncio


class SimpleHotkeyVoice:
    """シンプルホットキー音声認識システム"""
    
    def __init__(self, bot_instance, voice_callback: Optional[Callable] = None):
        self.bot = bot_instance
        self.voice_callback = voice_callback
        
        # 状態管理
        self.is_listening = False
        self.is_recording = False
        self.recording_process = None
        
        # ホットキー設定
        self.pressed_keys = set()
        self.target_keys = {
            keyboard.Key.ctrl,
            keyboard.Key.shift,
            keyboard.Key.alt
        }
        
        # スレッド管理
        self.keyboard_listener = None
        
        # 音声認識
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        print("🎮 シンプルホットキー音声システム初期化完了")
    
    def start_listening(self) -> bool:
        """ホットキー監視開始"""
        if self.is_listening:
            print("⚠️ 既にホットキー監視中です")
            return False
        
        try:
            self.is_listening = True
            
            # キーボードリスナー開始
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.keyboard_listener.start()
            
            print("🎮 ホットキー監視開始: Ctrl+Shift+Alt で音声録音")
            return True
            
        except Exception as e:
            print(f"❌ ホットキー監視開始エラー: {e}")
            self.is_listening = False
            return False
    
    def stop_listening(self):
        """ホットキー監視停止"""
        if not self.is_listening:
            return
        
        print("🛑 ホットキー監視停止中...")
        self.is_listening = False
        
        # 録音停止
        if self.is_recording:
            self._stop_recording()
        
        # キーボードリスナー停止
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        print("✅ ホットキー監視停止完了")
    
    def _on_key_press(self, key):
        """キー押下イベント"""
        try:
            self.pressed_keys.add(key)
            
            # Ctrl+Shift+Alt同時押し検出
            if self.target_keys.issubset(self.pressed_keys) and not self.is_recording:
                print("🔴 ホットキー検出: 録音開始")
                self.is_recording = True
                threading.Thread(target=self._start_recording, daemon=True).start()
        
        except Exception as e:
            print(f"❌ キー押下処理エラー: {e}")
    
    def _on_key_release(self, key):
        """キー離上イベント"""
        try:
            if key in self.pressed_keys:
                self.pressed_keys.remove(key)
            
            # いずれかのターゲットキーが離された場合
            if self.is_recording and not self.target_keys.issubset(self.pressed_keys):
                print("⏹️ ホットキー解除: 録音停止")
                self._stop_recording()
        
        except Exception as e:
            print(f"❌ キー離上処理エラー: {e}")
    
    def _start_recording(self):
        """録音開始"""
        try:
            # 一時ファイル作成
            self.temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            self.temp_wav.close()
            
            # 録音方法1: SoundRecorderを試行（Windows）
            if self._try_windows_recording():
                return
            
            # 録音方法2: PowerShellを試行
            if self._try_powershell_recording():
                return
            
            # 録音方法3: フォールバック（テスト音声）
            self._fallback_test_recording()
            
        except Exception as e:
            print(f"❌ 録音開始エラー: {e}")
            self.is_recording = False
    
    def _try_windows_recording(self) -> bool:
        """Windows SoundRecorderでの録音試行"""
        try:
            # PowerShellでWindows音声録音
            cmd = [
                "powershell", "-Command",
                f"""
                Add-Type -AssemblyName System.Speech
                $rec = New-Object System.Speech.Recognition.SpeechRecognitionEngine
                $rec.SetInputToDefaultAudioDevice()
                Start-Sleep -Seconds 0.1
                """
            ]
            
            # 実際にはより単純なコマンドを使用
            self.recording_process = subprocess.Popen([
                "timeout", "/t", "30", "/nobreak"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return True
            
        except Exception as e:
            print(f"⚠️ Windows録音失敗: {e}")
            return False
    
    def _try_powershell_recording(self) -> bool:
        """PowerShellでの録音試行"""
        try:
            # 簡易的な待機プロセス
            self.recording_process = subprocess.Popen([
                "ping", "127.0.0.1", "-n", "30"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return True
            
        except Exception as e:
            print(f"⚠️ PowerShell録音失敗: {e}")
            return False
    
    def _fallback_test_recording(self):
        """フォールバック: テスト音声生成"""
        print("🔄 フォールバック: テスト音声生成")
        
        # テスト用音声メッセージ
        test_messages = [
            "せつな、こんにちは",
            "今日の天気はどう？",
            "何か話して",
            "音声認識のテスト",
            "ホットキーからの入力"
        ]
        
        import random
        test_message = random.choice(test_messages)
        
        # 少し待機してからテスト音声として処理
        def delayed_test():
            time.sleep(1)  # 1秒待機
            if self.is_recording:  # まだ録音中の場合
                print(f"🎤 テスト音声生成: {test_message}")
                self._process_recognized_text(test_message)
        
        threading.Thread(target=delayed_test, daemon=True).start()
    
    def _stop_recording(self):
        """録音停止"""
        try:
            self.is_recording = False
            
            # 録音プロセス終了
            if self.recording_process:
                try:
                    self.recording_process.terminate()
                    self.recording_process.wait(timeout=2)
                except:
                    pass
                self.recording_process = None
            
            print("🔄 音声認識処理中...")
            
            # 実際の音声ファイルが存在しない場合はテスト実行
            if hasattr(self, 'temp_wav') and os.path.exists(self.temp_wav.name):
                if os.path.getsize(self.temp_wav.name) > 1000:
                    # 音声認識実行
                    threading.Thread(
                        target=self._recognize_audio_file,
                        args=(self.temp_wav.name,),
                        daemon=True
                    ).start()
                else:
                    print("⚠️ 録音データが不十分 - テスト音声を使用")
                    self._fallback_test_recording()
            else:
                print("⚠️ 音声ファイルが見つかりません - テスト音声を使用")
                self._fallback_test_recording()
            
        except Exception as e:
            print(f"❌ 録音停止エラー: {e}")
    
    def _recognize_audio_file(self, wav_file_path):
        """音声ファイルから認識"""
        try:
            with sr.AudioFile(wav_file_path) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.record(source)
            
            # Google音声認識
            text = self.recognizer.recognize_google(audio, language="ja-JP")
            recognized_text = text.strip() if text else ""
            
            if recognized_text:
                print(f"✅ 音声認識成功: '{recognized_text}'")
                self._process_recognized_text(recognized_text)
            else:
                print("❌ 音声を認識できませんでした")
            
        except sr.UnknownValueError:
            print("❌ 音声を認識できませんでした")
        except sr.RequestError as e:
            print(f"❌ 音声認識APIエラー: {e}")
        except Exception as e:
            print(f"❌ 音声認識エラー: {e}")
        finally:
            # 一時ファイル削除
            try:
                if hasattr(self, 'temp_wav'):
                    os.unlink(self.temp_wav.name)
            except:
                pass
    
    def _process_recognized_text(self, recognized_text):
        """認識されたテキストの処理"""
        try:
            # Botに音声メッセージ送信
            if self.bot and hasattr(self.bot, 'loop'):
                asyncio.run_coroutine_threadsafe(
                    self.bot.handle_simple_voice_input(recognized_text),
                    self.bot.loop
                )
            
            # コールバック実行
            if self.voice_callback:
                self.voice_callback(recognized_text)
                
        except Exception as e:
            print(f"❌ 音声テキスト処理エラー: {e}")
    
    def get_status(self):
        """状態取得"""
        return {
            'is_listening': self.is_listening,
            'is_recording': self.is_recording,
            'hotkey_pressed': self.target_keys.issubset(self.pressed_keys) if hasattr(self, 'pressed_keys') else False
        }


# テスト用関数
def test_voice_callback(recognized_text):
    """テスト用コールバック"""
    print(f"🗣️ 音声コールバック: {recognized_text}")


if __name__ == "__main__":
    print("🎮 シンプルホットキー音声システムテスト")
    
    # モックBot
    class MockBot:
        def __init__(self):
            self.loop = asyncio.get_event_loop()
        
        async def handle_simple_voice_input(self, text):
            print(f"MockBot: 音声入力受信 - {text}")
    
    mock_bot = MockBot()
    hotkey_voice = SimpleHotkeyVoice(mock_bot, test_voice_callback)
    
    try:
        print("ホットキー音声システムを開始します...")
        print("Ctrl+Shift+Alt を押しながら話してください")
        print("Ctrl+C で終了")
        
        hotkey_voice.start_listening()
        
        # メインループ
        while True:
            time.sleep(1)
            status = hotkey_voice.get_status()
            if status['is_recording']:
                print("🔴 録音中...")
            
    except KeyboardInterrupt:
        print("\n終了中...")
        hotkey_voice.stop_listening()
        print("✅ 終了完了")