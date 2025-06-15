#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡易音声入力モジュール - 新せつなBot
PyAudio依存なし・システムコマンド使用
"""

import subprocess
import tempfile
import os
import requests
import time

class VoiceInputSimple:
    def __init__(self):
        """簡易音声入力システムの初期化"""
        print("[音声] PyAudio不要の簡易音声入力システム初期化")
        self.temp_dir = tempfile.mkdtemp()
        
    def listen(self, timeout=10, phrase_limit=10):
        """
        システムコマンドを使用した音声入力
        
        Args:
            timeout: 音声待機のタイムアウト（秒）
            phrase_limit: 音声フレーズの最大長（秒）
            
        Returns:
            str: 認識されたテキスト（エラー時は空文字）
        """
        try:
            print("[音声] 🎤 音声録音開始（Enterで録音停止）...")
            
            # テンポラリファイル
            audio_file = os.path.join(self.temp_dir, f"voice_{int(time.time())}.wav")
            
            # ffmpegを使用した音声録音（WSL2で利用可能）
            cmd = [
                "timeout", str(timeout),
                "arecord", 
                "-f", "cd",
                "-t", "wav",
                audio_file
            ]
            
            # 録音プロセス起動
            print("録音中... (Ctrl+Cで停止)")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
            
            if os.path.exists(audio_file) and os.path.getsize(audio_file) > 1000:
                print("[音声] 🔄 Google Speech Recognition で認識中...")
                
                # Google Speech Recognition APIを直接呼び出し
                text = self._recognize_with_google_api(audio_file)
                
                # クリーンアップ
                os.remove(audio_file)
                
                if text:
                    print(f"[音声] ✅ 認識結果: {text}")
                    return text.strip()
                else:
                    return ""
            else:
                print("[音声] 音声データが不十分です")
                return ""
                
        except KeyboardInterrupt:
            print("\n[音声] 録音を停止しました")
            return ""
        except Exception as e:
            print(f"[音声] エラー: {e}")
            return ""
    
    def _recognize_with_google_api(self, audio_file):
        """Google Speech Recognition APIでの音声認識"""
        try:
            # 注: 実際の実装では音声ファイルをGoogle APIに送信
            # ここでは代替として固定メッセージを返す
            print("[音声] ⚠️ Google API未実装、テストメッセージを返します")
            return "こんにちは"  # テスト用
            
        except Exception as e:
            print(f"[音声] 認識エラー: {e}")
            return ""
    
    def quick_listen(self):
        """高速音声入力（5秒でタイムアウト）"""
        return self.listen(timeout=5, phrase_limit=5)

# テスト用の代替実装
if __name__ == "__main__":
    print("=== 簡易音声入力テスト ===")
    voice_input = VoiceInputSimple()
    result = voice_input.quick_listen()
    print(f"結果: {result}")