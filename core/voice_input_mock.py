#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音声入力モックモジュール - PyAudio不要のテスト用
"""

import time

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

# VoiceInputの代替として使用
VoiceInput = VoiceInputMock

if __name__ == "__main__":
    print("=== モック音声入力テスト ===")
    mock_input = VoiceInputMock()
    
    for i in range(6):  # 5フレーズ + 1空文字テスト
        result = mock_input.listen()
        print(f"結果 {i+1}: '{result}'")
    
    print("モック音声入力テスト完了")