#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音声出力モジュール - 新せつなBot
VOICEVOX統合・WSL2最適化・軽量実装
"""

import hashlib
import os
import requests
import pygame.mixer
import subprocess
import time

class VoiceOutput:
    def __init__(self):
        """音声出力システムの初期化"""
        # VOICEVOX設定
        self.voicevox_url = self._get_voicevox_url()
        self.speaker_id = 20  # せつなのボイス
        
        # 音声設定
        self.voice_settings = {
            "speedScale": 1.2,      # 話速
            "pitchScale": 0.0,      # 音程
            "intonationScale": 1.0  # 抑揚
        }
        
        # キャッシュディレクトリ
        self.cache_dir = "voice_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 音声再生の初期化
        self._initialize_audio()
        
        # 接続テスト
        self._test_connection()
    
    def _get_voicevox_url(self):
        """WSL2環境でのVOICEVOX URL取得"""
        try:
            # WSL2のデフォルトゲートウェイ（Windows側IP）を取得
            result = subprocess.run(
                ['ip', 'route', 'show', 'default'], 
                capture_output=True, text=True, timeout=3
            )
            
            if result.returncode == 0:
                parts = result.stdout.strip().split()
                for i, part in enumerate(parts):
                    if part == "via" and i + 1 < len(parts):
                        host_ip = parts[i + 1]
                        url = f"http://{host_ip}:50021"
                        print(f"[音声] Windows ホストIP検出: {host_ip}")
                        return url
        except Exception:
            pass
        
        # フォールバック
        print("[音声] デフォルトlocalhost使用")
        return "http://localhost:50021"
    
    def _initialize_audio(self):
        """音声再生システムの初期化"""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print("[音声] Pygame音声バックエンド初期化完了")
        except Exception as e:
            print(f"[音声] 音声バックエンド初期化エラー: {e}")
    
    def _test_connection(self):
        """VOICEVOX接続テスト"""
        try:
            response = requests.get(f"{self.voicevox_url}/version", timeout=3)
            if response.status_code == 200:
                version = response.json()
                print(f"[音声] ✅ VOICEVOX接続成功 (v{version.get('version', 'unknown')})")
                return True
            else:
                print(f"[音声] ❌ VOICEVOX接続失敗: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"[音声] ❌ VOICEVOX接続エラー: {e}")
            return False
    
    def _get_cache_path(self, text):
        """テキストからキャッシュファイルパスを生成"""
        text_hash = hashlib.sha1(text.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, f"{text_hash}.wav")
    
    def synthesize(self, text):
        """
        音声合成（キャッシュ対応）
        
        Args:
            text: 合成するテキスト
            
        Returns:
            str: 音声ファイルパス（失敗時はNone）
        """
        if not text.strip():
            return None
        
        # キャッシュチェック
        cache_path = self._get_cache_path(text)
        if os.path.exists(cache_path):
            print(f"[音声] 🔄 キャッシュから取得: {os.path.basename(cache_path)}")
            return cache_path
        
        try:
            start_time = time.time()
            
            # 音声クエリ生成
            query_response = requests.post(
                f"{self.voicevox_url}/audio_query",
                params={"text": text, "speaker": self.speaker_id},
                timeout=5
            )
            query_response.raise_for_status()
            query = query_response.json()
            
            # 音声パラメータ適用
            query.update(self.voice_settings)
            
            # 音声合成
            synthesis_response = requests.post(
                f"{self.voicevox_url}/synthesis",
                params={"speaker": self.speaker_id},
                json=query,
                timeout=10
            )
            synthesis_response.raise_for_status()
            
            # キャッシュ保存
            with open(cache_path, "wb") as f:
                f.write(synthesis_response.content)
            
            synthesis_time = time.time() - start_time
            print(f"[音声] ✅ 合成完了: {synthesis_time:.2f}s")
            return cache_path
            
        except Exception as e:
            print(f"[音声] ❌ 合成エラー: {e}")
            return None
    
    def play(self, audio_path):
        """
        音声ファイル再生
        
        Args:
            audio_path: 音声ファイルパス
        """
        if not audio_path or not os.path.exists(audio_path):
            print("[音声] ❌ 音声ファイルが見つかりません")
            return
        
        try:
            sound = pygame.mixer.Sound(audio_path)
            sound.play()
            
            # 再生完了まで待機
            while pygame.mixer.get_busy():
                time.sleep(0.1)
            
            print(f"[音声] 🔊 再生完了: {os.path.basename(audio_path)}")
            
        except Exception as e:
            print(f"[音声] ❌ 再生エラー: {e}")
    
    def speak(self, text):
        """
        テキストを音声で再生（合成+再生の統合関数）
        
        Args:
            text: 話すテキスト
        """
        if not text.strip():
            return
        
        print(f"[音声] 🗣️  '{text}'")
        
        # 音声合成
        audio_path = self.synthesize(text)
        
        if audio_path:
            # 音声再生
            self.play(audio_path)
        else:
            print("[音声] ❌ 音声合成失敗")
    
    def update_settings(self, speed=None, pitch=None, intonation=None):
        """音声パラメータの更新"""
        if speed is not None:
            self.voice_settings["speedScale"] = speed
        if pitch is not None:
            self.voice_settings["pitchScale"] = pitch
        if intonation is not None:
            self.voice_settings["intonationScale"] = intonation
        
        print(f"[音声] 設定更新: {self.voice_settings}")

# 簡単な使用例とテスト
if __name__ == "__main__":
    print("=" * 50)
    print("🔊 音声出力テスト")
    print("=" * 50)
    
    voice_output = VoiceOutput()
    
    # テスト音声
    test_texts = [
        "こんにちは、せつなです。",
        "音声合成のテストをしています。",
        "システムが正常に動作していますね。"
    ]
    
    for text in test_texts:
        print(f"\n再生テスト: {text}")
        voice_output.speak(text)
        time.sleep(1)  # 次の音声まで少し間隔を空ける
    
    print("\n音声出力テスト完了")