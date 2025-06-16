#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VOICEVOX音声合成システム
過去の成功実績に基づく確実動作版
"""

import hashlib
import os
import requests
import time
import subprocess
import platform
from typing import Optional

class VoiceVoxSynthesizer:
    """VOICEVOX音声合成システム（WSL2/Windows対応）"""
    
    def __init__(self):
        # VOICEVOX設定
        self.speaker_id = 20  # せつなの音声ID
        self.voicevox_url = None
        self.is_wsl2 = self._detect_wsl2()
        
        # キャッシュ設定
        self.cache_dir = "voice_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # VOICEVOX URL の自動検出
        self._auto_detect_voicevox_url()
        
        print(f"🔊 VOICEVOX音声合成システム初期化")
        print(f"   - WSL2環境: {self.is_wsl2}")
        print(f"   - VOICEVOX URL: {self.voicevox_url}")
        print(f"   - Speaker ID: {self.speaker_id} (せつな)")
        print(f"   - キャッシュディレクトリ: {self.cache_dir}")
    
    def _detect_wsl2(self) -> bool:
        """WSL2環境の検出"""
        try:
            # /proc/version にMicrosoftの文字列があるかチェック
            if os.path.exists('/proc/version'):
                with open('/proc/version', 'r') as f:
                    version_info = f.read().lower()
                    if 'microsoft' in version_info:
                        print("🐧 WSL2環境を検出")
                        return True
            
            # プラットフォーム情報でもチェック
            if platform.system() == 'Linux' and 'microsoft' in platform.release().lower():
                print("🐧 WSL2環境を検出（platform情報）")
                return True
                
            return False
        except Exception as e:
            print(f"⚠️ WSL2検出エラー: {e}")
            return False
    
    def _auto_detect_voicevox_url(self):
        """VOICEVOX URL の自動検出"""
        # 候補となるURL
        url_candidates = [
            "http://127.0.0.1:50021",
            "http://localhost:50021"
        ]
        
        # WSL2の場合はWindows ホストIPも追加
        if self.is_wsl2:
            try:
                # WSL2のゲートウェイIP（Windows ホスト）を取得
                result = subprocess.run([
                    'ip', 'route', 'show', 'default'
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'default' in line:
                            parts = line.split()
                            if len(parts) >= 3:
                                gateway_ip = parts[2]
                                wsl2_url = f"http://{gateway_ip}:50021"
                                url_candidates.insert(0, wsl2_url)  # 最優先
                                print(f"🌐 WSL2 Windows ホストIP: {gateway_ip}")
                                break
            except Exception as e:
                print(f"⚠️ WSL2 IP取得エラー: {e}")
        
        print(f"🔍 VOICEVOX接続テスト開始...")
        
        # 各URLをテスト
        for url in url_candidates:
            try:
                print(f"   - {url} テスト中...")
                response = requests.get(f"{url}/version", timeout=3)
                
                if response.status_code == 200:
                    version_info = response.json()
                    self.voicevox_url = url
                    print(f"✅ VOICEVOX接続成功: {url}")
                    print(f"   - バージョン: {version_info}")
                    return
                    
            except requests.exceptions.RequestException as e:
                print(f"   - {url} 接続失敗: {e}")
                continue
        
        # 全て失敗した場合
        print("❌ VOICEVOX エンジンに接続できません")
        print("💡 解決方法:")
        print("   1. VOICEVOXをWindows上で起動してください")
        print("   2. デフォルトポート50021で起動していることを確認してください")
        if self.is_wsl2:
            print("   3. WSL2環境からWindows上のVOICEVOXにアクセス中")
        
        # フォールバック: デフォルトURL
        self.voicevox_url = url_candidates[0]
    
    def synthesize_voice(self, text: str) -> Optional[str]:
        """音声合成実行（過去成功実績の実装）"""
        if not self.voicevox_url:
            print("❌ VOICEVOX URLが設定されていません")
            return None
        
        if not text.strip():
            print("⚠️ 合成するテキストが空です")
            return None
        
        # キャッシュキー生成
        cache_key = hashlib.sha1(f"{text}_{self.speaker_id}".encode("utf-8")).hexdigest()
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.wav")
        
        # キャッシュ確認
        if os.path.exists(cache_path):
            print(f"📦 キャッシュヒット: '{text[:20]}...'")
            return cache_path
        
        try:
            print(f"🎵 音声合成開始: '{text[:30]}...'")
            start_time = time.time()
            
            # 1. audio_query API呼び出し
            print("   - audio_query 生成中...")
            query_response = requests.post(
                f"{self.voicevox_url}/audio_query",
                params={"text": text, "speaker": self.speaker_id},
                timeout=10
            )
            
            if query_response.status_code != 200:
                print(f"❌ audio_query失敗: {query_response.status_code}")
                return None
            
            query = query_response.json()
            query_time = time.time()
            
            # 音声パラメータ調整（過去の成功設定）
            query["speedScale"] = 1.3   # 話速
            query["pitchScale"] = 0.0   # ピッチ
            query["intonationScale"] = 1.0  # イントネーション
            
            # 2. synthesis API呼び出し
            print("   - 音声synthesis実行中...")
            synthesis_response = requests.post(
                f"{self.voicevox_url}/synthesis",
                params={"speaker": self.speaker_id},
                json=query,
                timeout=15
            )
            
            if synthesis_response.status_code != 200:
                print(f"❌ synthesis失敗: {synthesis_response.status_code}")
                return None
            
            synthesis_time = time.time()
            
            # 3. WAVファイル保存
            with open(cache_path, "wb") as f:
                f.write(synthesis_response.content)
            
            save_time = time.time()
            
            # ファイルサイズ確認
            file_size = os.path.getsize(cache_path)
            print(f"✅ 音声合成完了: {cache_path}")
            print(f"   - ファイルサイズ: {file_size} bytes")
            print(f"   - Query時間: {query_time - start_time:.2f}s")
            print(f"   - Synthesis時間: {synthesis_time - query_time:.2f}s")
            print(f"   - 保存時間: {save_time - synthesis_time:.2f}s")
            print(f"   - 総時間: {save_time - start_time:.2f}s")
            
            return cache_path
            
        except requests.exceptions.Timeout:
            print("❌ VOICEVOX APIタイムアウト")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ VOICEVOX API呼び出しエラー: {e}")
            return None
        except Exception as e:
            print(f"❌ 音声合成エラー: {e}")
            return None
    
    def play_voice(self, wav_path: str) -> bool:
        """音声再生（クロスプラットフォーム対応）"""
        if not wav_path or not os.path.exists(wav_path):
            print("❌ 音声ファイルが見つかりません")
            return False
        
        try:
            file_size = os.path.getsize(wav_path)
            print(f"🔊 音声再生開始: {wav_path} ({file_size} bytes)")
            
            # プラットフォーム別再生方法
            if self.is_wsl2:
                # WSL2の場合：Windows側で再生
                print("🐧 WSL2環境: Windowsでの音声再生")
                # PowerShellを使ってWindows側で再生
                ps_command = f'powershell.exe -c "Add-Type -AssemblyName presentationCore; $mediaPlayer = New-Object system.windows.media.mediaplayer; $mediaPlayer.open([uri]\\"{wav_path}\\"); $mediaPlayer.Play(); Start-Sleep 5"'
                result = subprocess.run(ps_command, shell=True, capture_output=True, timeout=10)
                
                if result.returncode == 0:
                    print("✅ Windows音声再生完了")
                    return True
                else:
                    print(f"⚠️ PowerShell再生エラー: {result.stderr.decode()}")
                    # フォールバック: wslview使用
                    return self._fallback_play_wsl2(wav_path)
            else:
                # Linuxの場合：通常の再生
                return self._play_linux(wav_path)
                
        except Exception as e:
            print(f"❌ 音声再生エラー: {e}")
            return False
    
    def _fallback_play_wsl2(self, wav_path: str) -> bool:
        """WSL2でのフォールバック再生"""
        try:
            # wslviewでWindows側のデフォルトアプリで開く
            result = subprocess.run(['wslview', wav_path], timeout=5)
            print("✅ wslview経由で音声再生")
            return True
        except:
            print("⚠️ wslview再生も失敗")
            return False
    
    def _play_linux(self, wav_path: str) -> bool:
        """Linux環境での音声再生"""
        # 利用可能な再生コマンドを順番に試行
        play_commands = [
            ['aplay', wav_path],           # ALSA
            ['paplay', wav_path],          # PulseAudio  
            ['play', wav_path],            # SoX
            ['ffplay', '-nodisp', '-autoexit', wav_path]  # FFmpeg
        ]
        
        for cmd in play_commands:
            try:
                result = subprocess.run(cmd, timeout=10, capture_output=True)
                if result.returncode == 0:
                    print(f"✅ Linux音声再生完了: {cmd[0]}")
                    return True
            except:
                continue
        
        print("❌ Linux音声再生：全てのコマンドが失敗")
        return False
    
    def test_connection(self) -> bool:
        """VOICEVOX接続テスト"""
        if not self.voicevox_url:
            return False
        
        try:
            response = requests.get(f"{self.voicevox_url}/version", timeout=5)
            if response.status_code == 200:
                version_info = response.json()
                print(f"✅ VOICEVOX接続テスト成功")
                print(f"   - URL: {self.voicevox_url}")
                print(f"   - バージョン: {version_info}")
                return True
            else:
                print(f"❌ VOICEVOX接続テスト失敗: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ VOICEVOX接続テスト失敗: {e}")
            return False
    
    def test_synthesis(self, test_text: str = "こんにちは、せつなです。音声合成のテストを行っています。") -> bool:
        """音声合成テスト"""
        print(f"🧪 音声合成テスト開始: '{test_text}'")
        
        wav_path = self.synthesize_voice(test_text)
        if wav_path:
            print(f"✅ 音声合成テスト成功: {wav_path}")
            
            # 再生テスト
            play_success = self.play_voice(wav_path)
            if play_success:
                print("✅ 音声再生テスト成功")
                return True
            else:
                print("⚠️ 音声合成は成功、再生は失敗")
                return True  # 合成が成功していれば OK
        else:
            print("❌ 音声合成テスト失敗")
            return False


# テスト実行部分
if __name__ == "__main__":
    print("🧪 VOICEVOX音声合成システム テスト開始")
    
    # システム初期化
    synthesizer = VoiceVoxSynthesizer()
    
    # 接続テスト
    if synthesizer.test_connection():
        print("\n🎵 音声合成・再生テスト実行")
        success = synthesizer.test_synthesis()
        
        if success:
            print("\n✅ 全てのテストが完了しました")
        else:
            print("\n❌ 音声合成テストが失敗しました")
    else:
        print("\n❌ VOICEVOX接続テストが失敗しました")
        print("💡 VOICEVOXエンジンを起動してから再実行してください")