#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音声入力モジュール - 新せつなBot
エラー音声なし・高速処理・WSL2最適化
"""

import speech_recognition as sr
import time

class VoiceInput:
    def __init__(self):
        """音声入力システムの初期化"""
        self.recognizer = sr.Recognizer()
        
        # PyAudio不要の実装
        try:
            self.microphone = sr.Microphone()
        except OSError:
            # PyAudioがない場合は後で手動設定
            print("[音声] PyAudio未検出、手動設定モードで起動")
            self.microphone = None
        
        # 設定最適化
        self.recognizer.energy_threshold = 300  # 音声検出感度
        self.recognizer.pause_threshold = 0.5   # 無音検出時間
        
        # 環境音調整（初回のみ）
        self._adjust_ambient_noise()
    
    def _adjust_ambient_noise(self):
        """環境音の調整（初期化時のみ）"""
        if not self.microphone:
            print("[音声] マイクロフォン未設定のため環境音調整をスキップ")
            return
            
        try:
            print("[音声] 環境音を調整中...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[音声] 環境音調整完了")
        except Exception as e:
            print(f"[音声] 環境音調整エラー: {e}")
    
    def listen(self, timeout=10, phrase_limit=10):
        """
        音声入力を取得
        
        Args:
            timeout: 音声待機のタイムアウト（秒）
            phrase_limit: 音声フレーズの最大長（秒）
            
        Returns:
            str: 認識されたテキスト（エラー時は空文字）
        """
        if not self.microphone:
            print("[音声] マイクロフォンが利用できません")
            return ""
            
        try:
            # 音声録音
            with self.microphone as source:
                print("[音声] 🎤 話してください...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_limit
                )
            
            # 音声認識
            print("[音声] 🔄 認識処理中...")
            text = self.recognizer.recognize_google(audio, language="ja-JP")
            
            if text.strip():
                print(f"[音声] ✅ 認識結果: {text}")
                return text.strip()
            else:
                return ""
                
        except sr.WaitTimeoutError:
            # タイムアウト（静かに空文字を返す）
            return ""
        except sr.UnknownValueError:
            # 認識できない（静かに空文字を返す）
            return ""
        except sr.RequestError:
            # サービスエラー（静かに空文字を返す）
            return ""
        except Exception:
            # その他のエラー（静かに空文字を返す）
            return ""
    
    def quick_listen(self):
        """高速音声入力（5秒でタイムアウト）"""
        return self.listen(timeout=5, phrase_limit=5)

# 簡単な使用例とテスト
if __name__ == "__main__":
    print("=" * 50)
    print("🎤 音声入力テスト")
    print("=" * 50)
    
    voice_input = VoiceInput()
    
    while True:
        print("\n音声入力テスト（5秒でタイムアウト）")
        print("何か話してください（quitで終了）...")
        
        result = voice_input.quick_listen()
        
        if result:
            print(f"結果: {result}")
            if "quit" in result.lower() or "終了" in result:
                break
        else:
            print("音声が認識されませんでした（続行中）")
    
    print("音声入力テスト終了")