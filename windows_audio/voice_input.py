#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows専用音声入力システム
PyAudio・WASAPI最適化、リアルタイム音声認識
"""

import pyaudio
import wave
import threading
import time
import tempfile
import os
import queue
import speech_recognition as sr
from typing import Optional, Callable, Dict, Any
import numpy as np

try:
    from .device_manager import WindowsAudioDeviceManager
    from .permissions import WindowsPermissionManager
except ImportError:
    # 直接実行時の対応
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from device_manager import WindowsAudioDeviceManager
    from permissions import WindowsPermissionManager


class WindowsVoiceInput:
    """Windows最適化音声入力クラス"""
    
    def __init__(self, callback: Optional[Callable[[str], None]] = None):
        self.callback = callback
        self.is_recording = False
        self.is_listening = False
        self.recording_thread = None
        self.recognition_thread = None
        
        # デバイス・権限管理
        self.device_manager = WindowsAudioDeviceManager()
        self.permission_manager = WindowsPermissionManager()
        
        # 音声認識設定
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # 環境ノイズ調整
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # 無音判定時間
        
        # 録音設定
        self.audio_queue = queue.Queue()
        self.current_stream = None
        self.recording_params = None
        
        # 初期化
        self._initialize_recording_params()
        print("🎤 Windows音声入力システム初期化完了")
    
    def _initialize_recording_params(self):
        """録音パラメータ初期化"""
        # デバイス権限確認
        permissions = self.permission_manager.check_microphone_permissions()
        if not all(permissions.values()):
            print("⚠️  音声権限に問題があります")
            print(self.permission_manager.get_permission_status_report())
        
        # 最適録音パラメータ取得
        self.recording_params = self.device_manager.get_optimal_recording_params()
        print(f"⚙️  録音パラメータ: {self.recording_params}")
    
    def start_continuous_recognition(self) -> bool:
        """連続音声認識開始"""
        if self.is_listening:
            print("⚠️  既に音声認識中です")
            return False
        
        # 権限・デバイス確認
        if not self._check_prerequisites():
            return False
        
        try:
            self.is_listening = True
            
            # 認識スレッド開始
            self.recognition_thread = threading.Thread(
                target=self._continuous_recognition_worker,
                daemon=True
            )
            self.recognition_thread.start()
            
            print("✅ 連続音声認識開始")
            return True
            
        except Exception as e:
            print(f"❌ 音声認識開始エラー: {e}")
            self.is_listening = False
            return False
    
    def stop_continuous_recognition(self):
        """連続音声認識停止"""
        if not self.is_listening:
            return
        
        self.is_listening = False
        
        # ストリーム停止
        if self.current_stream:
            try:
                self.current_stream.stop_stream()
                self.current_stream.close()
                self.current_stream = None
            except Exception as e:
                print(f"⚠️  ストリーム停止エラー: {e}")
        
        # スレッド終了待機
        if self.recognition_thread and self.recognition_thread.is_alive():
            self.recognition_thread.join(timeout=2.0)
        
        print("🛑 連続音声認識停止")
    
    def record_once(self, duration: float = 5.0) -> Optional[str]:
        """ワンショット録音・認識"""
        if self.is_recording:
            print("⚠️  既に録音中です")
            return None
        
        try:
            self.is_recording = True
            print(f"🎤 {duration}秒間録音中...")
            
            # 録音実行
            audio_data = self._record_audio(duration)
            
            if audio_data:
                # 音声認識
                recognized_text = self._recognize_audio_data(audio_data)
                return recognized_text
            
            return None
            
        except Exception as e:
            print(f"❌ ワンショット録音エラー: {e}")
            return None
        finally:
            self.is_recording = False
    
    def _check_prerequisites(self) -> bool:
        """前提条件チェック"""
        # デバイス確認
        if not self.device_manager.default_input_device:
            print("❌ 利用可能な入力デバイスがありません")
            return False
        
        # 権限確認
        permissions = self.permission_manager.check_microphone_permissions()
        if not permissions.get('microphone_device_available', False):
            print("❌ マイクデバイスが利用できません")
            return False
        
        # PyAudio確認
        if not self.device_manager.pyaudio_instance:
            print("❌ PyAudioが初期化されていません")
            return False
        
        return True
    
    def _continuous_recognition_worker(self):
        """連続音声認識ワーカー"""
        try:
            # マイクストリーム作成
            self.current_stream = self.device_manager.pyaudio_instance.open(
                **self.recording_params,
                input=True,
                stream_callback=self._audio_callback
            )
            
            # ストリーム開始
            self.current_stream.start_stream()
            print("🎤 音声ストリーム開始")
            
            # 音声データ処理ループ
            while self.is_listening:
                try:
                    # 音声データ取得（タイムアウト付き）
                    audio_chunk = self.audio_queue.get(timeout=1.0)
                    
                    # 音声認識処理
                    if len(audio_chunk) > 0:
                        self._process_audio_chunk(audio_chunk)
                        
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"⚠️  音声処理エラー: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ 連続音声認識ワーカーエラー: {e}")
        finally:
            if self.current_stream:
                self.current_stream.stop_stream()
                self.current_stream.close()
                self.current_stream = None
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """音声ストリームコールバック"""
        if status:
            print(f"⚠️  音声ストリーム警告: {status}")
        
        # 音声データをキューに追加
        if self.is_listening:
            self.audio_queue.put(in_data)
        
        return (None, pyaudio.paContinue)
    
    def _process_audio_chunk(self, audio_data: bytes):
        """音声チャンク処理"""
        try:
            # 音量レベル確認（簡易VAD）
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            volume = np.sqrt(np.mean(audio_np**2))
            
            # 音量閾値チェック
            if volume < 100:  # 調整可能
                return
            
            # WAVファイル作成
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(self.recording_params['channels'])
                    wav_file.setsampwidth(
                        self.device_manager.pyaudio_instance.get_sample_size(
                            self.recording_params['format']
                        )
                    )
                    wav_file.setframerate(self.recording_params['rate'])
                    wav_file.writeframes(audio_data)
                
                # 音声認識
                recognized_text = self._recognize_audio_file(temp_file.name)
                
                # 一時ファイル削除
                os.unlink(temp_file.name)
                
                # コールバック実行
                if recognized_text and self.callback:
                    self.callback(recognized_text)
        
        except Exception as e:
            print(f"⚠️  音声チャンク処理エラー: {e}")
    
    def _record_audio(self, duration: float) -> Optional[bytes]:
        """指定時間音声録音"""
        try:
            frames = []
            
            stream = self.device_manager.pyaudio_instance.open(
                **self.recording_params,
                input=True
            )
            
            stream.start_stream()
            
            # 録音実行
            frames_to_record = int(
                self.recording_params['rate'] / 
                self.recording_params['frames_per_buffer'] * duration
            )
            
            for _ in range(frames_to_record):
                data = stream.read(
                    self.recording_params['frames_per_buffer'],
                    exception_on_overflow=False
                )
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            return b''.join(frames)
            
        except Exception as e:
            print(f"❌ 音声録音エラー: {e}")
            return None
    
    def _recognize_audio_data(self, audio_data: bytes) -> Optional[str]:
        """音声データから文字認識"""
        try:
            # WAVファイル作成
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(self.recording_params['channels'])
                    wav_file.setsampwidth(
                        self.device_manager.pyaudio_instance.get_sample_size(
                            self.recording_params['format']
                        )
                    )
                    wav_file.setframerate(self.recording_params['rate'])
                    wav_file.writeframes(audio_data)
                
                # ファイルから認識
                result = self._recognize_audio_file(temp_file.name)
                
                # 一時ファイル削除
                os.unlink(temp_file.name)
                
                return result
        
        except Exception as e:
            print(f"❌ 音声認識エラー: {e}")
            return None
    
    def _recognize_audio_file(self, file_path: str) -> Optional[str]:
        """音声ファイルから文字認識"""
        try:
            with sr.AudioFile(file_path) as source:
                # 環境ノイズ調整
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                
                # 音声データ読み込み
                audio = self.recognizer.record(source)
            
            # Google音声認識（日本語）
            try:
                text = self.recognizer.recognize_google(audio, language='ja-JP')
                print(f"✅ 音声認識成功: '{text}'")
                return text
                
            except sr.UnknownValueError:
                print("⚠️  音声を認識できませんでした")
                return None
            except sr.RequestError as e:
                print(f"❌ Google音声認識サービスエラー: {e}")
                return None
        
        except Exception as e:
            print(f"❌ 音声ファイル認識エラー: {e}")
            return None
    
    def test_microphone(self) -> bool:
        """マイクテスト"""
        print("🎤 マイクテスト開始...")
        
        # デバイステスト
        if not self.device_manager.test_input_device():
            return False
        
        # 短時間録音テスト
        test_audio = self._record_audio(1.0)
        if not test_audio:
            print("❌ テスト録音失敗")
            return False
        
        print("✅ マイクテスト成功")
        return True
    
    def get_status_info(self) -> Dict[str, Any]:
        """状態情報取得"""
        permissions = self.permission_manager.check_microphone_permissions()
        
        return {
            'is_listening': self.is_listening,
            'is_recording': self.is_recording,
            'permissions': permissions,
            'default_device': self.device_manager.default_input_device,
            'recording_params': self.recording_params
        }
    
    def cleanup(self):
        """リソースクリーンアップ"""
        self.stop_continuous_recognition()
        self.device_manager.cleanup()
        print("🧹 Windows音声入力クリーンアップ完了")


# テスト用関数
def test_callback(recognized_text: str):
    """テスト用コールバック"""
    print(f"🗣️  認識されたテキスト: {recognized_text}")


def main():
    """Windows音声入力テスト"""
    print("🎤 Windows音声入力システムテスト")
    
    # 音声入力初期化
    voice_input = WindowsVoiceInput(callback=test_callback)
    
    # 状態確認
    status = voice_input.get_status_info()
    print(f"📊 システム状態: {status}")
    
    # マイクテスト
    if voice_input.test_microphone():
        print("\\n🎤 5秒間話してください...")
        result = voice_input.record_once(5.0)
        
        if result:
            print(f"✅ 認識結果: '{result}'")
        else:
            print("❌ 音声認識失敗")
    
    # クリーンアップ
    voice_input.cleanup()


if __name__ == "__main__":
    main()