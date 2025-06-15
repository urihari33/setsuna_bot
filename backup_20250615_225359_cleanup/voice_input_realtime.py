#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リアルタイム音声入力モジュール - せつなBot
キー押下中の連続録音・音声認識機能
"""

import speech_recognition as sr
import threading
import time
import queue
import io
try:
    from pynput import keyboard
except ImportError:
    print("[警告] pynputが利用できません。pip install pynputを実行してください。")
    keyboard = None

class RealtimeVoiceInput:
    def __init__(self):
        """リアルタイム音声入力システムの初期化"""
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        # 録音制御
        self.is_recording = False
        self.recording_thread = None
        self.audio_queue = queue.Queue()
        
        # キーボードリスナー
        self.key_listener = None
        if keyboard:
            self.hotkey_combination = {
                keyboard.Key.ctrl_l,
                keyboard.Key.alt_l, 
                keyboard.Key.shift_l
            }
        else:
            self.hotkey_combination = set()
        self.current_keys = set()
        
        # コールバック
        self.on_speech_recognized = None
        self.on_recording_start = None
        self.on_recording_stop = None
        
        # 初期化
        self._initialize_microphone()
        self._setup_recognizer()
        
    def _initialize_microphone(self):
        """マイクロフォンの初期化"""
        try:
            self.microphone = sr.Microphone()
            print("[音声] マイクロフォン初期化完了")
            
            # 環境音調整
            print("[音声] 環境音調整中...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[音声] 環境音調整完了")
            
        except Exception as e:
            print(f"[音声] マイクロフォン初期化エラー: {e}")
            self.microphone = None
    
    def _setup_recognizer(self):
        """音声認識設定"""
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.5
        self.recognizer.dynamic_energy_threshold = True
    
    def _on_key_press(self, key):
        """キー押下イベント"""
        self.current_keys.add(key)
        
        # ホットキー組み合わせ確認
        if self.hotkey_combination.issubset(self.current_keys):
            if not self.is_recording:
                self._start_recording()
    
    def _on_key_release(self, key):
        """キー離しイベント"""
        try:
            self.current_keys.discard(key)
        except KeyError:
            pass
        
        # ホットキーが離された場合、録音停止
        if not self.hotkey_combination.issubset(self.current_keys):
            if self.is_recording:
                self._stop_recording()
    
    def _start_recording(self):
        """録音開始"""
        if not self.microphone:
            print("[音声] マイクロフォンが利用できません")
            return
        
        if self.is_recording:
            return
            
        print("[音声] 🎤 録音開始")
        self.is_recording = True
        
        # コールバック実行
        if self.on_recording_start:
            self.on_recording_start()
        
        # 録音スレッド開始
        self.recording_thread = threading.Thread(
            target=self._recording_worker,
            daemon=True
        )
        self.recording_thread.start()
    
    def _stop_recording(self):
        """録音停止"""
        if not self.is_recording:
            return
            
        print("[音声] 🛑 録音停止")
        self.is_recording = False
        
        # コールバック実行
        if self.on_recording_stop:
            self.on_recording_stop()
        
        # 録音スレッド終了待機
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2)
    
    def _recording_worker(self):
        """録音ワーカースレッド"""
        try:
            with self.microphone as source:
                while self.is_recording:
                    try:
                        # 短時間の音声を録音
                        audio = self.recognizer.listen(
                            source, 
                            timeout=0.5, 
                            phrase_time_limit=None
                        )
                        
                        if self.is_recording:  # 録音中断チェック
                            # 音声認識を別スレッドで実行
                            threading.Thread(
                                target=self._recognize_audio,
                                args=(audio,),
                                daemon=True
                            ).start()
                            
                    except sr.WaitTimeoutError:
                        # タイムアウトは正常（続行）
                        continue
                    except Exception as e:
                        print(f"[音声] 録音エラー: {e}")
                        break
                        
        except Exception as e:
            print(f"[音声] 録音ワーカーエラー: {e}")
        finally:
            print("[音声] 録音ワーカー終了")
    
    def _recognize_audio(self, audio):
        """音声認識処理"""
        try:
            # Google Speech Recognition で音声認識
            text = self.recognizer.recognize_google(audio, language="ja-JP")
            
            if text.strip():
                print(f"[音声] 認識結果: {text}")
                
                # コールバック実行
                if self.on_speech_recognized:
                    self.on_speech_recognized(text.strip())
                    
        except sr.UnknownValueError:
            # 認識できない音声（無視）
            pass
        except sr.RequestError as e:
            print(f"[音声] 認識サービスエラー: {e}")
        except Exception as e:
            print(f"[音声] 認識エラー: {e}")
    
    def start_listening(self):
        """ホットキーリスニング開始"""
        if not keyboard:
            print("[音声] ❌ pynputが利用できないため、ホットキー機能は無効です")
            return
            
        if self.key_listener:
            print("[音声] 既にリスニング中です")
            return
        
        try:
            self.key_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            
            self.key_listener.start()
            print("[音声] ✅ Ctrl+Alt+Shift でのリアルタイム音声入力開始")
            
        except Exception as e:
            print(f"[音声] リスニング開始エラー: {e}")
    
    def stop_listening(self):
        """ホットキーリスニング停止"""
        # 録音停止
        if self.is_recording:
            self._stop_recording()
        
        # キーリスナー停止
        if self.key_listener:
            try:
                self.key_listener.stop()
                self.key_listener = None
                print("[音声] リスニング停止")
            except Exception as e:
                print(f"[音声] リスニング停止エラー: {e}")
    
    def is_listening_active(self):
        """リスニング状態確認"""
        return self.key_listener is not None
    
    def is_recording_active(self):
        """録音状態確認"""
        return self.is_recording

# テスト用
if __name__ == "__main__":
    print("=== リアルタイム音声入力テスト ===")
    print("Ctrl+Alt+Shift を押している間、音声を録音します")
    print("Ctrl+C で終了")
    
    def on_speech(text):
        print(f"🗣️ 認識された音声: {text}")
    
    def on_rec_start():
        print("🔴 録音開始")
    
    def on_rec_stop():
        print("⚫ 録音停止")
    
    voice_input = RealtimeVoiceInput()
    voice_input.on_speech_recognized = on_speech
    voice_input.on_recording_start = on_rec_start
    voice_input.on_recording_stop = on_rec_stop
    
    try:
        voice_input.start_listening()
        
        # メインスレッドで待機
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n終了中...")
        voice_input.stop_listening()
        print("テスト終了")