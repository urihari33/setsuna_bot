#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプル音声テスト
PyAudio + SpeechRecognition の基本動作確認
"""

import pyaudio
import wave
import speech_recognition as sr
import tempfile
import os

def test_pyaudio_devices():
    """PyAudioデバイステスト"""
    print("🔍 PyAudio デバイス確認")
    
    p = pyaudio.PyAudio()
    
    print(f"総デバイス数: {p.get_device_count()}")
    
    # 入力デバイス確認
    input_devices = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            input_devices.append({
                'index': i,
                'name': info['name'],
                'channels': info['maxInputChannels']
            })
            print(f"  入力デバイス {i}: {info['name']}")
    
    p.terminate()
    return input_devices

def test_simple_recording(duration=3):
    """シンプル録音テスト"""
    print(f"🎤 {duration}秒録音テスト開始...")
    
    # 録音設定
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    
    p = pyaudio.PyAudio()
    
    try:
        # ストリーム開始
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        print("録音中... 話してください")
        frames = []
        
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
        
        print("録音完了")
        
        stream.stop_stream()
        stream.close()
        
        return b''.join(frames)
        
    except Exception as e:
        print(f"❌ 録音エラー: {e}")
        return None
    finally:
        p.terminate()

def test_speech_recognition(audio_data):
    """音声認識テスト"""
    if not audio_data:
        return None
    
    print("🧠 音声認識中...")
    
    # WAVファイル作成
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
        with wave.open(tmp_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16bit = 2 bytes
            wf.setframerate(16000)
            wf.writeframes(audio_data)
        
        # 音声認識
        r = sr.Recognizer()
        try:
            with sr.AudioFile(tmp_file.name) as source:
                audio = r.record(source)
            
            # Google音声認識（日本語）
            text = r.recognize_google(audio, language='ja-JP')
            print(f"✅ 認識結果: '{text}'")
            return text
            
        except sr.UnknownValueError:
            print("⚠️  音声を認識できませんでした")
        except sr.RequestError as e:
            print(f"❌ 音声認識サービスエラー: {e}")
        except Exception as e:
            print(f"❌ 音声認識エラー: {e}")
        finally:
            try:
                os.unlink(tmp_file.name)
            except PermissionError:
                pass  # 一時ファイル削除失敗は無視
    
    return None

def main():
    """メイン実行"""
    print("🎤 シンプル音声テスト開始")
    print("=" * 40)
    
    # 1. デバイス確認
    input_devices = test_pyaudio_devices()
    
    if not input_devices:
        print("❌ 利用可能な入力デバイスがありません")
        return
    
    print(f"✅ {len(input_devices)}個の入力デバイスが利用可能")
    
    # 2. 録音テスト
    audio_data = test_simple_recording(3)
    
    if not audio_data:
        print("❌ 録音に失敗しました")
        return
    
    print("✅ 録音成功")
    
    # 3. 音声認識テスト
    recognized_text = test_speech_recognition(audio_data)
    
    if recognized_text:
        print("🎉 音声入力システム正常動作確認!")
    else:
        print("⚠️  音声認識は失敗しましたが、録音は成功しています")

if __name__ == "__main__":
    main()