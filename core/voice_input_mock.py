#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音声入力モックモジュール - PyAudio不要のテスト用
WSL2環境での代替音声入力（開発・テスト用）
"""

import threading
import time

try:
    from pynput import keyboard
except ImportError:
    print("[警告] pynputが利用できません。pip install pynputを実行してください。")
    keyboard = None

class VoiceInputMock:
    def __init__(self):
        """モック音声入力システムの初期化"""
        print("[音声] モック音声入力システム初期化完了（PyAudio不要）")
        self.test_phrases = [
            "こんにちは",
            "今日はいい天気ですね", 
            "ありがとう",
            "元気ですか？",
            "さようなら"
        ]
        self.phrase_index = 0
    
    def listen(self, timeout=10, phrase_limit=10):
        """
        モック音声入力（予定されたフレーズを順次返す）
        
        Returns:
            str: テスト用フレーズ
        """
        print("[音声] 🎤 モック音声入力中...")
        time.sleep(1)  # リアルな感じにするため少し待機
        
        if self.phrase_index < len(self.test_phrases):
            phrase = self.test_phrases[self.phrase_index]
            self.phrase_index += 1
            print(f"[音声] ✅ モック認識結果: {phrase}")
            return phrase
        else:
            # 全てのフレーズを使い切ったら空文字を返す
            print("[音声] モックフレーズ終了")
            return ""
    
    def quick_listen(self):
        """高速モック音声入力"""
        return self.listen(timeout=5, phrase_limit=5)

class MockVoiceInput:
    def __init__(self):
        """リアルタイムモック音声入力システムの初期化"""
        # 録音制御
        self.is_recording = False
        
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
        
        # テスト用音声認識サンプル
        self.test_phrases = [
            "こんにちは、せつなです",
            "今日は良い天気ですね",
            "音声入力のテストをしています",
            "WSL2環境での動作確認中です",
            "音声対話システムは正常に動作しています",
            "ありがとうございます",
            "元気ですか？",
            "また後でお話しましょう"
        ]
        self.phrase_index = 0
        
        print("[音声] リアルタイムモック音声入力システム初期化完了")
        print("[音声] 実際の音声録音の代わりに、テスト用フレーズを使用します")
    
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
        """録音開始（モック）"""
        if self.is_recording:
            return
            
        print("[音声] 🎤 録音開始（モックモード）")
        self.is_recording = True
        
        # コールバック実行
        if self.on_recording_start:
            self.on_recording_start()
    
    def _stop_recording(self):
        """録音停止（モック）"""
        if not self.is_recording:
            return
            
        print("[音声] 🛑 録音停止（モックモード）")
        self.is_recording = False
        
        # コールバック実行
        if self.on_recording_stop:
            self.on_recording_stop()
        
        # モック音声認識を実行
        threading.Thread(target=self._mock_speech_recognition, daemon=True).start()
    
    def _mock_speech_recognition(self):
        """モック音声認識"""
        # 短い遅延でリアルな音声認識をシミュレート
        time.sleep(1.0)
        
        # テスト用フレーズを順番に使用
        test_text = self.test_phrases[self.phrase_index]
        self.phrase_index = (self.phrase_index + 1) % len(self.test_phrases)
        
        print(f"[音声] モック認識結果: {test_text}")
        
        # コールバック実行
        if self.on_speech_recognized:
            self.on_speech_recognized(test_text)
    
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
            print("[音声] ✅ Ctrl+Alt+Shift でのモック音声入力開始")
            print("[音声] ℹ️ 実際の音声の代わりにテスト用フレーズが使用されます")
            
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

# VoiceInputの代替として使用
VoiceInput = VoiceInputMock

if __name__ == "__main__":
    print("=== モック音声入力テスト ===")
    mock_input = VoiceInputMock()
    
    for i in range(6):  # 5フレーズ + 1空文字テスト
        result = mock_input.listen()
        print(f"結果 {i+1}: '{result}'")
    
    print("モック音声入力テスト完了")