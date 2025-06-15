#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSL2対応音声入力モジュール - せつなBot
PyAudio不要の音声入力実装
"""

import os
import subprocess
import tempfile
import threading
import time
import requests
import json
from pathlib import Path

try:
    from pynput import keyboard
except ImportError:
    print("[警告] pynputが利用できません。pip install pynputを実行してください。")
    keyboard = None

class WSL2VoiceInput:
    def __init__(self):
        """WSL2対応音声入力システムの初期化"""
        # 録音制御
        self.is_recording = False
        self.recording_process = None
        
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
        
        # 一時ファイルディレクトリ
        self.temp_dir = Path(tempfile.gettempdir())
        
        print("[音声] WSL2対応音声入力システム初期化完了")
    
    def _check_recording_capability(self):
        """録音機能の確認"""
        try:
            # arecordコマンドの確認
            result = subprocess.run(['which', 'arecord'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("[音声] ✅ arecordコマンド利用可能")
                return True
            
            # ffmpegの確認
            result = subprocess.run(['which', 'ffmpeg'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("[音声] ✅ ffmpegコマンド利用可能")
                return True
            
            print("[音声] ❌ 録音コマンド（arecord/ffmpeg）が見つかりません")
            return False
            
        except Exception as e:
            print(f"[音声] 録音機能確認エラー: {e}")
            return False
    
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
        if self.is_recording:
            return
            
        print("[音声] 🎤 録音開始")
        self.is_recording = True
        
        # コールバック実行
        if self.on_recording_start:
            self.on_recording_start()
        
        # 録音スレッド開始
        threading.Thread(target=self._recording_worker, daemon=True).start()
    
    def _stop_recording(self):
        """録音停止"""
        if not self.is_recording:
            return
            
        print("[音声] 🛑 録音停止")
        self.is_recording = False
        
        # コールバック実行
        if self.on_recording_stop:
            self.on_recording_stop()
        
        # 録音プロセス終了
        if self.recording_process:
            try:
                self.recording_process.terminate()
                self.recording_process.wait(timeout=2)
            except Exception as e:
                print(f"[音声] 録音プロセス終了エラー: {e}")
    
    def _recording_worker(self):
        """録音ワーカー（WSL2対応）"""
        temp_file = self.temp_dir / f"voice_recording_{int(time.time())}.wav"
        
        try:
            # WSL2でWindows側のマイクアクセスを試行
            cmd = [
                'arecord',
                '-f', 'cd',  # CD品質 (16bit, 44.1kHz, ステレオ)
                '-t', 'wav',
                str(temp_file)
            ]
            
            # arecordが利用できない場合の代替
            if not self._check_recording_capability():
                print("[音声] ❌ 録音機能が利用できません")
                self._use_fallback_recording(temp_file)
                return
            
            print(f"[音声] 録音開始: {temp_file}")
            self.recording_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 録音終了まで待機
            while self.is_recording:
                time.sleep(0.1)
            
            # プロセス終了
            if self.recording_process:
                self.recording_process.terminate()
                self.recording_process.wait()
            
            # 録音ファイルが存在する場合、音声認識実行
            if temp_file.exists() and temp_file.stat().st_size > 1000:  # 最小サイズチェック
                self._recognize_audio_file(temp_file)
            else:
                print("[音声] 録音ファイルが見つからないか、サイズが小さすぎます")
                
        except Exception as e:
            print(f"[音声] 録音エラー: {e}")
        finally:
            # 一時ファイル削除
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception:
                pass
    
    def _use_fallback_recording(self, temp_file):
        """フォールバック録音（テスト用音声ファイル作成）"""
        print("[音声] フォールバック: テスト用空音声ファイルを作成")
        
        # 空のWAVファイルを作成（テスト用）
        try:
            # 簡単なサイレンス音声ファイルを作成
            import wave
            import numpy as np
            
            sample_rate = 44100
            duration = 1  # 1秒
            samples = np.zeros(int(sample_rate * duration), dtype=np.int16)
            
            with wave.open(str(temp_file), 'w') as wav_file:
                wav_file.setnchannels(1)  # モノラル
                wav_file.setsampwidth(2)  # 16bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(samples.tobytes())
            
            print(f"[音声] テスト音声ファイル作成: {temp_file}")
            
        except Exception as e:
            print(f"[音声] フォールバック録音エラー: {e}")
    
    def _recognize_audio_file(self, audio_file):
        """音声ファイルの認識"""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(str(audio_file)) as source:
                audio = recognizer.record(source)
            
            # Google Speech Recognition で音声認識
            text = recognizer.recognize_google(audio, language="ja-JP")
            
            if text.strip():
                print(f"[音声] 認識結果: {text}")
                
                # コールバック実行
                if self.on_speech_recognized:
                    self.on_speech_recognized(text.strip())
            else:
                print("[音声] 音声が認識されませんでした")
                
        except sr.UnknownValueError:
            print("[音声] 音声を認識できませんでした")
        except sr.RequestError as e:
            print(f"[音声] 認識サービスエラー: {e}")
        except Exception as e:
            print(f"[音声] 音声認識エラー: {e}")
    
    def start_listening(self):
        """ホットキーリスニング開始"""
        if not keyboard:
            print("[音声] ❌ pynputが利用できないため、ホットキー機能は無効です")
            return
            
        if self.key_listener:
            print("[音声] 既にリスニング中です")
            return
        
        # 録音機能確認
        if not self._check_recording_capability():
            print("[音声] ⚠️ 録音機能が制限されています（テストモードで動作）")
        
        try:
            self.key_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            
            self.key_listener.start()
            print("[音声] ✅ Ctrl+Alt+Shift でのWSL2音声入力開始")
            
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
    print("=== WSL2音声入力テスト ===")
    print("Ctrl+Alt+Shift を押している間、音声を録音します")
    print("Ctrl+C で終了")
    
    def on_speech(text):
        print(f"🗣️ 認識された音声: {text}")
    
    def on_rec_start():
        print("🔴 録音開始")
    
    def on_rec_stop():
        print("⚫ 録音停止")
    
    voice_input = WSL2VoiceInput()
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