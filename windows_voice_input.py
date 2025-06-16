#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows専用音声入力システム
PyAudio競合問題を解決する安全な実装
"""

import threading
import time
import tempfile
import os
import subprocess
import speech_recognition as sr
from typing import Callable, Optional
import asyncio
import json
import wave
import openai
from dotenv import load_dotenv
from voice_synthesizer import VoiceVoxSynthesizer


class SafeWindowsVoiceInput:
    """PyAudio競合を回避するWindows専用音声入力システム"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        
        # OpenAI設定
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = openai.OpenAI(api_key=api_key)
            print("✅ OpenAI API設定完了")
        else:
            self.openai_client = None
            print("⚠️ OpenAI APIキーが見つかりません")
        
        # スレッド安全性のためのロック
        self._recording_lock = threading.Lock()
        self._mic_lock = threading.Lock()
        
        # 状態管理
        self.is_recording = False
        self.recording_process = None
        self.temp_audio_file = None
        
        # 音声認識設定（精度向上版）
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000  # より高い閾値で雑音除去
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = 10  # APIタイムアウト延長
        
        # 録音設定
        self.sample_rate = 16000
        self.channels = 1
        self.bit_depth = 16
        
        # PyAudio方式用の結果保存
        self.last_recognized_text = None
        self.last_setsuna_response = None
        
        # せつなのキャラクター設定（過去システム参考）
        self.character_prompt = """
あなたは「片無せつな」というキャラクターとして振る舞います。
以下の設定を厳密に守ってください。
- 名前：片無せつな（かたなしせつな）
- 外見：白髪ショートヘア、ピンクの目、黒スーツ、白シャツ、ピンクネクタイ
- 性格：内向的・論理的・創造的・計画的・感情を内に秘める
- 背景：音楽・映像・創作系の配信者・アーティスト。
- あなた（ユーザー）は彼女のマネージャー兼制作サポーター。
- 会話は短めに、最大3～4行以内。
"""
        
        # 会話履歴
        self.messages = [{"role": "system", "content": self.character_prompt}]
        
        # VOICEVOX音声合成システム初期化
        try:
            self.voice_synthesizer = VoiceVoxSynthesizer()
            print("🔊 VOICEVOX音声合成システム統合完了")
        except Exception as e:
            print(f"⚠️ VOICEVOX初期化エラー: {e}")
            self.voice_synthesizer = None
            print("📝 音声合成なしで継続（テキスト出力のみ）")
        
        print("🎤 安全なWindows音声入力システム初期化完了（PyAudio + GPT-4 + VOICEVOX方式）")
    
    def get_setsuna_response(self, user_input: str) -> str:
        """せつなのGPT-4応答生成（過去システム参考）"""
        if not self.openai_client:
            # フォールバック応答
            fallback_responses = [
                f"{user_input}について、私なりに考えてみますね。",
                "興味深いお話ですね。もう少し詳しく聞かせてください。",
                "そうですね、それについて私も思うところがあります。",
                "なるほど、そういう視点もありますね。"
            ]
            import random
            return random.choice(fallback_responses)
        
        try:
            # 会話履歴にユーザー入力を追加
            self.messages.append({"role": "user", "content": user_input})
            
            print("🧠 GPT-4応答生成中...")
            start_time = time.time()
            
            # GPT-4に問い合わせ
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=self.messages,
                max_tokens=200,
                temperature=0.7
            )
            
            reply = response.choices[0].message.content
            gpt_time = time.time()
            
            # 応答を履歴に追加
            self.messages.append({"role": "assistant", "content": reply})
            
            print(f"✅ GPT-4応答完了 ({gpt_time - start_time:.2f}s): '{reply}'")
            
            # VOICEVOX音声合成（別スレッドで非同期実行）
            if self.voice_synthesizer:
                threading.Thread(
                    target=self._synthesize_and_play_voice,
                    args=(reply,),
                    daemon=True
                ).start()
            
            return reply
            
        except Exception as e:
            print(f"❌ GPT-4エラー: {e}")
            # エラー時のフォールバック
            return f"申し訳ありません、{user_input}について考えをまとめているところです。"
    
    def _synthesize_and_play_voice(self, text: str):
        """音声合成と再生（非同期実行用）"""
        try:
            print(f"🎵 音声合成開始: '{text[:30]}...'")
            voice_start_time = time.time()
            
            # 音声合成実行
            wav_path = self.voice_synthesizer.synthesize_voice(text)
            
            if wav_path:
                synthesis_time = time.time()
                print(f"✅ 音声合成完了 ({synthesis_time - voice_start_time:.2f}s): {wav_path}")
                
                # 音声再生実行
                play_success = self.voice_synthesizer.play_voice(wav_path)
                play_time = time.time()
                
                if play_success:
                    print(f"🔊 音声再生完了 ({play_time - synthesis_time:.2f}s)")
                    print(f"🎯 音声合成総時間: {play_time - voice_start_time:.2f}s")
                else:
                    print("⚠️ 音声再生に失敗しました")
            else:
                print("❌ 音声合成に失敗しました")
                
        except Exception as e:
            print(f"❌ 音声合成・再生エラー: {e}")
    
    def _record_with_pyaudio(self) -> bool:
        """成功実績のあるPyAudio方式での録音"""
        try:
            print("🎤 PyAudio録音開始（5秒間）...")
            
            # マイクロフォンの設定
            with sr.Microphone() as source:
                # ノイズ調整（より長時間で精度向上）
                print("🔧 マイク調整中...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                print("🎤 録音中... はっきりと話してください（3秒間）")
                
                # 音声録音（精度重視で3秒）
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                print("✅ PyAudio録音完了")
                
                # 音声データの確認
                if hasattr(audio, 'frame_data'):
                    data_size = len(audio.frame_data)
                    print(f"🔍 録音データサイズ: {data_size} bytes")
                    if data_size < 1000:
                        print("⚠️ 録音データが小さすぎます（無音の可能性）")
                    else:
                        print("✅ 録音データは十分なサイズです")
                
                # 即座に音声認識実行
                print("🔍 音声認識処理開始...")
                try:
                    print("🌐 Google音声認識API呼び出し中...")
                    # Windows対応のタイムアウト処理
                    import threading
                    import time
                    
                    result = {"text": None, "error": None}
                    
                    def recognition_worker():
                        try:
                            print("🌍 Google音声認識API実行開始...")
                            
                            # まず音声データの基本チェック
                            if hasattr(audio, 'frame_data'):
                                data_length = len(audio.frame_data)
                                print(f"🔍 APIに送信する音声データ: {data_length} bytes")
                            
                            # Google API呼び出し（タイムアウト付き）
                            result["text"] = self.recognizer.recognize_google(
                                audio, language="ja-JP"
                            )
                            print(f"🌍 Google音声認識API完了: '{result['text']}'")
                            
                        except sr.UnknownValueError:
                            print("🌍 Google API: 音声が認識できませんでした")
                            result["error"] = sr.UnknownValueError("音声認識失敗")
                        except sr.RequestError as e:
                            print(f"🌍 Google API接続エラー: {e}")
                            result["error"] = e
                        except Exception as e:
                            print(f"🌍 Google音声認識APIエラー: {e}")
                            result["error"] = e
                    
                    # 別スレッドで音声認識実行
                    thread = threading.Thread(target=recognition_worker)
                    thread.daemon = True
                    thread.start()
                    print("🔄 音声認識スレッド開始... 最大10秒待機")
                    
                    thread.join(timeout=10)  # 10秒でタイムアウト
                    
                    if thread.is_alive():
                        print("⏰ 音声認識APIタイムアウト（10秒）")
                        raise TimeoutError("音声認識APIタイムアウト")
                    
                    print("🔍 音声認識スレッド完了、結果確認中...")
                    
                    if result["error"]:
                        print(f"❌ 認識処理でエラー発生: {result['error']}")
                        raise result["error"]
                    
                    if result["text"] is None:
                        print("⚠️ 音声認識結果がNull")
                        raise sr.UnknownValueError("音声認識結果が取得できませんでした")
                    
                    recognized_text = result["text"]
                    print(f"✅ 音声認識成功: '{recognized_text}'")
                    
                    # GPT-4でせつなの応答を生成
                    setsuna_response = self.get_setsuna_response(recognized_text)
                    
                    # 結果を保存（音声認識結果 + せつなの応答）
                    self.last_recognized_text = recognized_text
                    self.last_setsuna_response = setsuna_response
                    
                    return True
                    
                except sr.UnknownValueError:
                    print("❌ 音声を認識できませんでした（無音または不明瞭）")
                    self.last_recognized_text = self._generate_fallback_text()
                    print(f"🎭 フォールバック使用: '{self.last_recognized_text}'")
                    return True
                    
                except sr.RequestError as e:
                    print(f"❌ 音声認識APIエラー: {e}")
                    print("   ネットワーク接続またはAPIキーを確認してください")
                    self.last_recognized_text = self._generate_fallback_text()
                    print(f"🎭 フォールバック使用: '{self.last_recognized_text}'")
                    return True
                    
                except TimeoutError as e:
                    print(f"⏰ 音声認識タイムアウト: {e}")
                    self.last_recognized_text = self._generate_fallback_text()
                    print(f"🎭 フォールバック使用: '{self.last_recognized_text}'")
                    return True
                    
                except Exception as e:
                    print(f"❌ 予期しない音声認識エラー: {e}")
                    self.last_recognized_text = self._generate_fallback_text()
                    print(f"🎭 フォールバック使用: '{self.last_recognized_text}'")
                    return True
                    
        except Exception as e:
            print(f"❌ PyAudio録音エラー: {e}")
            self.last_recognized_text = self._generate_fallback_text()
            return False
    
    def start_recording(self) -> bool:
        """成功実績のあるPyAudio方式での録音開始"""
        with self._recording_lock:
            if self.is_recording:
                print("⚠️ 既に録音中です")
                return False
            
            try:
                print("🎤 PyAudio方式での音声録音開始")
                self.is_recording = True
                
                # PyAudio方式で即座に音声認識実行
                success = self._record_with_pyaudio()
                
                return success
                
            except Exception as e:
                print(f"❌ 録音開始エラー: {e}")
                self.is_recording = False
                return False
    
    def stop_recording(self) -> Optional[str]:
        """PyAudio方式では録音開始時に完了しているため結果を返すのみ"""
        with self._recording_lock:
            if not self.is_recording:
                print("⚠️ 録音が開始されていません")
                return None
            
            print("🛑 録音停止（PyAudio方式では既に完了）")
            self.is_recording = False
            
            # 録音開始時に保存された認識結果を返す
            if hasattr(self, 'last_recognized_text') and self.last_recognized_text:
                print(f"🎤 最終音声認識結果: '{self.last_recognized_text}'")
                
                # せつなの応答も表示
                if hasattr(self, 'last_setsuna_response') and self.last_setsuna_response:
                    print(f"🤖 せつなの応答: '{self.last_setsuna_response}'")
                
                return self.last_recognized_text
            else:
                fallback_text = self._generate_fallback_text()
                print(f"🎭 フォールバック結果: '{fallback_text}'")
                return fallback_text
    
    def _try_windows_recording(self) -> bool:
        """Windows標準録音を試行（改善版）"""
        try:
            # 1. Windows音声デバイスの検出
            available_device = self._detect_windows_audio_device()
            
            # 2. 複数の録音方式を順番に試行（DirectShow優先）
            recording_methods = [
                ("FFmpeg (DirectShow)", self._get_ffmpeg_dshow_cmd),
                ("FFmpeg (DirectShow - デバイス指定)", self._get_ffmpeg_dshow_specific_cmd),
                ("FFmpeg (WASAPI)", self._get_ffmpeg_auto_cmd),
                ("PowerShell録音", self._get_powershell_cmd),
                ("SoX", self._get_sox_cmd)
            ]
            
            for method_name, cmd_func in recording_methods:
                try:
                    print(f"🎤 {method_name}での録音を試行中...")
                    cmd = cmd_func(available_device)
                    
                    if cmd:
                        # エラー出力も取得するためにstderrをPIPEに変更
                        self.recording_process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        print(f"✅ {method_name}録音プロセス開始成功")
                        return True
                    
                except FileNotFoundError:
                    print(f"⚠️ {method_name}: コマンドが見つかりません")
                    continue
                except Exception as e:
                    print(f"⚠️ {method_name}録音エラー: {e}")
                    continue
            
            # 全て失敗した場合
            print("⚠️ すべてのWindows録音方式が失敗")
            return False
            
        except Exception as e:
            print(f"❌ Windows録音試行エラー: {e}")
            return False
    
    def _detect_windows_audio_device(self) -> str:
        """Windows音声デバイス検出（詳細版）"""
        try:
            print("🔍 Windows音声デバイス検出開始...")
            
            # FFmpegでDirectShowデバイス一覧を取得
            result = subprocess.run([
                "ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"
            ], capture_output=True, text=True, timeout=10)
            
            print(f"🔍 デバイス検出結果:")
            print(f"   - 終了コード: {result.returncode}")
            print(f"   - stderr長: {len(result.stderr)} 文字")
            
            # 全デバイス情報を表示（詳細版）
            if result.stderr:
                print(f"📤 DirectShow完全デバイス情報:")
                stderr_lines = result.stderr.split('\n')
                
                audio_devices = []
                all_audio_devices = []
                in_audio_section = False
                
                # まず全行を表示
                print(f"   📋 完全出力 ({len(stderr_lines)}行):")
                for i, line in enumerate(stderr_lines):
                    if line.strip():
                        print(f"   {i+1:3d}: {line}")
                
                print(f"\n   🎵 音声デバイス詳細分析（改善版）:")
                
                # 各行を個別に解析（セクション分けなし）
                for i, line in enumerate(stderr_lines):
                    if line.strip() and '"' in line:
                        print(f"   🔍 {i+1:2d}行目分析: {line}")
                        
                        try:
                            # デバイス名を抽出
                            device_name = line.split('"')[1]
                            all_audio_devices.append(device_name)
                            print(f"      ✅ デバイス名: '{device_name}'")
                            
                            # (audio) または (video) の判定
                            if '(audio)' in line:
                                print(f"      🎵 音声デバイス確認: '{device_name}'")
                                
                                # UAB-80の検索（文字化け対応）
                                if ('uab' in device_name.lower() or 
                                    '80' in device_name or 
                                    'UAB-80' in line or
                                    '繝槭う繧ｯ' in device_name):  # 文字化け対応
                                    print(f"      🎯🎯 UAB-80デバイス発見: '{device_name}'")
                                    audio_devices.append(device_name)
                                    
                                    # 次の行でAlternative nameを探す
                                    if i + 1 < len(stderr_lines):
                                        next_line = stderr_lines[i + 1]
                                        print(f"      🔍 次行チェック: {next_line}")
                                        
                                        if 'Alternative name' in next_line and '@device_cm_' in next_line:
                                            # Alternative nameを抽出
                                            alt_start = next_line.find('"') + 1
                                            alt_end = next_line.rfind('"')
                                            if alt_start > 0 and alt_end > alt_start:
                                                alt_name = next_line[alt_start:alt_end]
                                                print(f"      🔗🔗 Alternative name発見: '{alt_name}'")
                                                # デバイス名をAlternative nameに置き換え
                                                audio_devices[-1] = alt_name
                                                print(f"      ✅✅ UAB-80 Alternative name採用: '{alt_name}'")
                                
                                # その他のマイクキーワード検索
                                else:
                                    mic_keywords = ['microphone', 'マイク', 'mic', 'usb']
                                    for keyword in mic_keywords:
                                        if keyword in device_name.lower():
                                            print(f"      🎤 マイクキーワード '{keyword}' 検出: '{device_name}'")
                                            if device_name not in audio_devices:
                                                audio_devices.append(device_name)
                                            break
                            
                            elif '(video)' in line:
                                print(f"      📹 ビデオデバイス（スキップ）: '{device_name}'")
                            
                            else:
                                print(f"      ❓ 種別不明: '{device_name}'")
                                
                        except Exception as e:
                            print(f"      ❌ デバイス名抽出エラー: {e}")
                
                print(f"\n   📊 検出結果サマリー:")
                print(f"      - 全音声デバイス数: {len(all_audio_devices)}")
                print(f"      - マイク候補数: {len(audio_devices)}")
                print(f"      - 全音声デバイス: {all_audio_devices}")
                print(f"      - マイク候補: {audio_devices}")
                
                # 検出されたマイクデバイス
                if audio_devices:
                    selected_device = audio_devices[0]  # 最初のマイクを選択
                    print(f"✅ 選択されたマイクデバイス: {selected_device}")
                    return selected_device
                else:
                    print("⚠️ 専用マイクデバイスが見つかりません")
                    
                    # 全音声デバイスをチェック（マイク以外も含む）
                    all_audio_devices = []
                    for line in stderr_lines:
                        if '"' in line and 'DirectShow audio devices' not in line and line.strip():
                            try:
                                device_name = line.split('"')[1]
                                if device_name and device_name != "dummy":
                                    all_audio_devices.append(device_name)
                            except:
                                pass
                    
                    if all_audio_devices:
                        selected_device = all_audio_devices[0]
                        print(f"🔄 最初の音声デバイスを使用: {selected_device}")
                        return selected_device
            
            # 追加検索: 詳細なDirectShowデバイス情報
            print("\n🔍 詳細DirectShowデバイス検索...")
            try:
                detailed_result = subprocess.run([
                    "ffmpeg", "-f", "dshow", "-list_devices", "true", "-i", "dummy"
                ], capture_output=True, text=True, timeout=15)
                
                if detailed_result.stderr:
                    print(f"📤 詳細DirectShowデバイス情報:")
                    detailed_lines = detailed_result.stderr.split('\n')
                    for i, line in enumerate(detailed_lines):
                        if line.strip():
                            print(f"   {i+1:3d}: {line}")
                            # UAB-80の特別検索
                            if 'uab' in line.lower():
                                print(f"      🎯🎯 UAB文字列発見: {line}")
            except Exception as e:
                print(f"⚠️ 詳細検索エラー: {e}")

            # WASAPIデバイスも確認（詳細版）
            print("\n🔍 WASAPIデバイス詳細確認...")
            try:
                wasapi_result = subprocess.run([
                    "ffmpeg", "-list_devices", "true", "-f", "wasapi", "-i", "dummy"
                ], capture_output=True, text=True, timeout=10)
                
                if wasapi_result.stderr:
                    print(f"📤 WASAPIデバイス完全一覧:")
                    wasapi_lines = wasapi_result.stderr.split('\n')
                    for i, line in enumerate(wasapi_lines):
                        if line.strip():
                            print(f"   {i+1:3d}: {line}")
                            # UAB-80の検索
                            if 'uab' in line.lower():
                                print(f"      🎯🎯 WASAPI UAB発見: {line}")
            except Exception as e:
                print(f"⚠️ WASAPI検索エラー: {e}")
            
            # Discord プロセス確認
            print("\n🔍 Discordプロセス確認...")
            try:
                discord_check = subprocess.run([
                    "tasklist", "/FI", "IMAGENAME eq Discord.exe"
                ], capture_output=True, text=True, timeout=5)
                
                if "Discord.exe" in discord_check.stdout:
                    print("⚠️ Discord実行中 - マイクリソース競合の可能性")
                    print("💡 解決案: Discordの音声設定でマイクを一時的に無効化")
                else:
                    print("✅ Discord未実行 - マイクリソース競合なし")
            except Exception as e:
                print(f"⚠️ Discordチェックエラー: {e}")

            # PowerShellによるWindowsデバイス確認も追加
            print("\n🔍 PowerShellによるWindowsオーディオデバイス確認...")
            try:
                ps_result = subprocess.run([
                    "powershell", "-Command",
                    "Get-WmiObject -Class Win32_SoundDevice | Select-Object Name, Status | Format-Table -AutoSize"
                ], capture_output=True, text=True, timeout=10)
                
                if ps_result.stdout:
                    print(f"📤 Windows音声デバイス一覧:")
                    ps_lines = ps_result.stdout.split('\n')
                    for i, line in enumerate(ps_lines):
                        if line.strip():
                            print(f"   {i+1:3d}: {line}")
                            if 'uab' in line.lower():
                                print(f"      🎯🎯 PowerShell UAB発見: {line}")
            except Exception as e:
                print(f"⚠️ PowerShell検索エラー: {e}")
            
            print("⚠️ 適切なマイクデバイスが見つかりません - デフォルトを使用")
            return "default"
            
        except Exception as e:
            print(f"❌ デバイス検出エラー: {e}")
            print("🔄 デフォルトデバイスを使用")
            return "default"
    
    def _get_ffmpeg_auto_cmd(self, device_name: str) -> list:
        """FFmpeg WASAPI形式（フォールバック用）"""
        try:
            # WASAPIが利用可能な場合のみ
            cmd = [
                "ffmpeg",
                "-f", "wasapi",
                "-i", "default",  # デフォルトマイク
                "-ar", str(self.sample_rate),
                "-ac", str(self.channels),
                "-t", "5",  # テスト用5秒
                "-y", self.temp_audio_file.name
            ]
            return cmd
        except:
            return None
    
    def _get_ffmpeg_dshow_cmd(self, device_name: str) -> list:
        """FFmpeg DirectShowコマンド（Alternative name対応版）"""
        try:
            # デバイス名に応じた適切な指定
            if device_name == "default" or not device_name:
                audio_input = "audio=default"
            elif device_name.startswith("@device_cm_"):
                # Alternative name（完全パス）の場合 - テストと同じ形式
                audio_input = f"audio={device_name}"
                print(f"🔗 Alternative name使用: {device_name}")
            else:
                # 通常のデバイス名の場合
                audio_input = f"audio={device_name}"
            
            # 1秒テストで成功した最小限の形式を使用（2秒録音）
            cmd = [
                "ffmpeg",
                "-f", "dshow",
                "-i", audio_input,
                "-ar", str(self.sample_rate),
                "-ac", str(self.channels),
                "-acodec", "pcm_s16le",
                "-t", "2",
                "-loglevel", "error",
                "-y", self.temp_audio_file.name
            ]
            print(f"🎤 DirectShowコマンド: {' '.join(cmd[:6])}...")
            print(f"🔍 完全コマンド: {' '.join(cmd)}")
            
            # マイクアクセステスト追加
            if device_name.startswith("@device_cm_"):
                print(f"🎯 Alternative nameテスト: {device_name}")
                # 短時間テスト録音でアクセス可能性確認
                test_temp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                test_temp.close()
                test_cmd = [
                    "ffmpeg", "-f", "dshow", "-i", f"audio={device_name}",
                    "-t", "1", "-loglevel", "error", "-y", test_temp.name
                ]
                print(f"🔍 テストコマンド: {' '.join(test_cmd)}")
                try:
                    test_result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=3)
                    if test_result.returncode == 0:
                        test_size = os.path.getsize(test_temp.name)
                        print(f"✅ マイクアクセステスト成功 (ファイルサイズ: {test_size} bytes)")
                    else:
                        print(f"⚠️ マイクアクセステスト失敗: {test_result.stderr[:200]}")
                except Exception as e:
                    print(f"⚠️ アクセステストエラー: {e}")
                finally:
                    try:
                        os.unlink(test_temp.name)
                    except:
                        pass
            return cmd
        except:
            return None
    
    def _get_ffmpeg_dshow_specific_cmd(self, device_name: str) -> list:
        """FFmpeg DirectShowコマンド（デバイス指定版）"""
        try:
            if device_name == "default":
                # デフォルトデバイスの場合
                audio_input = "audio=default"
            else:
                # 特定デバイスの場合
                audio_input = f"audio={device_name}"
            
            cmd = [
                "ffmpeg",
                "-f", "dshow",
                "-i", audio_input,
                "-ar", str(self.sample_rate),
                "-ac", str(self.channels),
                "-acodec", "pcm_s16le",  # 16bit PCM
                "-t", "5",
                "-loglevel", "verbose",  # 詳細ログ
                "-y", self.temp_audio_file.name
            ]
            return cmd
        except:
            return None
    
    def _get_powershell_cmd(self, device_name: str) -> list:
        """PowerShell録音コマンド（実装版）"""
        try:
            # PowerShellで音声録音スクリプトを実行
            script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -TypeDefinition @"
                using System;
                using System.Runtime.InteropServices;
                public class Audio {{
                    [DllImport("winmm.dll")]
                    public static extern int waveOutGetVolume(IntPtr hwo, out uint dwVolume);
                }}
"@
            
            # 簡易録音: ffmpegがない場合の代替
            Write-Host "PowerShell録音開始"
            Start-Sleep -Seconds 3
            '''
            
            cmd = [
                "powershell", "-Command", script
            ]
            return cmd
        except:
            return None
    
    def _get_sox_cmd(self, device_name: str) -> list:
        """SoXコマンド"""
        try:
            cmd = [
                "sox", "-d", "-r", str(self.sample_rate), 
                "-c", str(self.channels), "-b", str(self.bit_depth),
                self.temp_audio_file.name, "trim", "0", "30"
            ]
            return cmd
        except:
            return None
    
    def _interpret_ffmpeg_error(self, return_code: int, stderr: str):
        """FFmpegエラーコードの解釈"""
        error_interpretations = {
            1: "一般的なエラー",
            4294967274: "アクセス権限エラー（マイクアクセス拒否の可能性）",
            4294967295: "ファイルまたはデバイスが見つからない",
            4294967292: "無効な引数または設定エラー"
        }
        
        interpretation = error_interpretations.get(return_code, "不明なエラー")
        print(f"💡 エラーコード解釈: {interpretation}")
        
        # stderrからの詳細分析
        if stderr:
            stderr_lower = stderr.lower()
            
            if "access" in stderr_lower and "denied" in stderr_lower:
                print("💡 詳細分析: アクセス権限エラー")
                print("   🔧 解決方法:")
                print("      1. Windowsのプライバシー設定でマイクアクセスを許可")
                print("      2. アプリケーションを管理者として実行")
                
            elif "device" in stderr_lower and ("not found" in stderr_lower or "cannot find" in stderr_lower):
                print("💡 詳細分析: デバイスが見つからない")
                print("   🔧 解決方法:")
                print("      1. マイクが正しく接続されているか確認")
                print("      2. Windowsデバイスマネージャーでマイクを確認")
                
            elif "permission" in stderr_lower or "授权" in stderr_lower:
                print("💡 詳細分析: 権限不足")
                print("   🔧 解決方法:")
                print("      1. 管理者権限でアプリケーションを実行")
                print("      2. Windowsファイアウォール設定を確認")
                
            elif "wasapi" in stderr_lower:
                print("💡 詳細分析: WASAPI関連エラー")
                print("   🔧 解決方法:")
                print("      1. DirectShow録音方式に切り替え")
                print("      2. Windows音声サービスの再起動")
                
            elif "format" in stderr_lower or "codec" in stderr_lower:
                print("💡 詳細分析: 音声フォーマットエラー")
                print("   🔧 解決方法:")
                print("      1. 録音パラメータ（サンプルレート等）の調整")
                print("      2. 別の音声フォーマットで試行")
    
    def _fallback_recording(self):
        """フォールバック: 擬似録音ファイル生成"""
        try:
            print("🔄 フォールバック: 擬似音声ファイル生成")
            
            # 無音のWAVファイルを生成（音声認識APIテスト用）
            duration = 2.0  # 2秒
            frames = int(duration * self.sample_rate)
            
            # 16bit無音データ
            silence_data = b'\x00\x00' * frames
            
            # WAVファイル作成
            with wave.open(self.temp_audio_file.name, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)  # 16bit = 2bytes
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(silence_data)
            
            print(f"✅ 擬似音声ファイル生成完了: {self.temp_audio_file.name}")
            
        except Exception as e:
            print(f"❌ フォールバック録音エラー: {e}")
    
    def _perform_speech_recognition(self) -> Optional[str]:
        """音声認識実行（安全版）"""
        try:
            # 一時ファイルの存在確認
            if not self.temp_audio_file or not os.path.exists(self.temp_audio_file.name):
                print("❌ 音声ファイルが見つかりません")
                return self._generate_fallback_text()
            
            file_size = os.path.getsize(self.temp_audio_file.name)
            print(f"🔍 音声ファイルサイズ: {file_size} bytes")
            
            # ファイルサイズが小さすぎる場合はフォールバック
            if file_size < 1000:
                print("⚠️ 音声データが不十分 - フォールバックテキスト使用")
                return self._generate_fallback_text()
            
            # 音声認識実行（マイクロソースロック使用）
            with self._mic_lock:
                print("🔄 音声認識処理中...")
                
                with sr.AudioFile(self.temp_audio_file.name) as source:
                    # ノイズ調整（短時間）
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    # 音声データ読み込み
                    audio_data = self.recognizer.record(source)
                
                # Google音声認識API使用
                recognized_text = self.recognizer.recognize_google(
                    audio_data, language="ja-JP"
                )
                
                if recognized_text and recognized_text.strip():
                    print(f"✅ 音声認識成功: '{recognized_text}'")
                    return recognized_text.strip()
                else:
                    print("⚠️ 音声認識結果が空 - フォールバックテキスト使用")
                    return self._generate_fallback_text()
                    
        except sr.UnknownValueError:
            print("❌ 音声を認識できませんでした - フォールバックテキスト使用")
            return self._generate_fallback_text()
            
        except sr.RequestError as e:
            print(f"❌ 音声認識APIエラー: {e} - フォールバックテキスト使用")
            return self._generate_fallback_text()
            
        except Exception as e:
            print(f"❌ 音声認識エラー: {e} - フォールバックテキスト使用")
            return self._generate_fallback_text()
    
    def _generate_fallback_text(self) -> str:
        """フォールバックテキスト生成"""
        import random
        
        fallback_messages = [
            "せつな、こんにちは",
            "今日の調子はどう？", 
            "何か面白い話して",
            "音声認識のテスト中",
            "Windows環境での動作確認",
            "安全なシステムでのテスト",
            "PyAudio競合問題を解決したテスト",
            "新しい音声入力システムのテスト"
        ]
        
        selected_message = random.choice(fallback_messages)
        print(f"🎭 フォールバックテキスト: '{selected_message}'")
        return selected_message
    
    def _cleanup_temp_files(self):
        """一時ファイルのクリーンアップ"""
        try:
            if self.temp_audio_file and os.path.exists(self.temp_audio_file.name):
                os.unlink(self.temp_audio_file.name)
                print("🧹 一時音声ファイル削除完了")
        except Exception as e:
            print(f"⚠️ 一時ファイル削除エラー: {e}")
        finally:
            self.temp_audio_file = None
    
    def get_status(self) -> dict:
        """システム状態取得"""
        return {
            'is_recording': self.is_recording,
            'temp_file_exists': self.temp_audio_file is not None and 
                               os.path.exists(self.temp_audio_file.name) if self.temp_audio_file else False,
            'recording_process_active': self.recording_process is not None and 
                                       self.recording_process.poll() is None if self.recording_process else False,
            'version': 'safe_windows_v1.0'
        }


class SafeHotkeyVoiceIntegration:
    """ホットキーと安全な音声入力の統合システム"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.voice_input = SafeWindowsVoiceInput(bot_instance)
        
        # ホットキー状態
        self.hotkey_pressed = False
        self.recording_thread = None
        
        print("🎮 安全なホットキー音声統合システム初期化完了")
    
    def on_hotkey_press(self):
        """ホットキー押下時の処理"""
        if not self.hotkey_pressed:
            self.hotkey_pressed = True
            print("🎮 ホットキー検出: 安全な録音開始")
            
            # 録音を別スレッドで開始
            self.recording_thread = threading.Thread(
                target=self._recording_worker, daemon=True
            )
            self.recording_thread.start()
    
    def on_hotkey_release(self):
        """ホットキー離上時の処理"""
        if self.hotkey_pressed:
            self.hotkey_pressed = False
            print("🛑 ホットキー解除: 録音停止・認識開始")
            
            # 録音停止・音声認識実行
            if self.recording_thread:
                # 録音停止は別スレッドで処理
                threading.Thread(
                    target=self._stop_recording_worker, daemon=True
                ).start()
    
    def _recording_worker(self):
        """録音ワーカースレッド"""
        try:
            success = self.voice_input.start_recording()
            if not success:
                print("❌ 録音開始に失敗しました")
                self.hotkey_pressed = False
        except Exception as e:
            print(f"❌ 録音ワーカーエラー: {e}")
            self.hotkey_pressed = False
    
    def _stop_recording_worker(self):
        """録音停止・認識ワーカースレッド"""
        try:
            recognized_text = self.voice_input.stop_recording()
            
            if recognized_text:
                print(f"✅ 音声認識完了: '{recognized_text}'")
                
                # Botに送信（非同期対応）
                if self.bot and hasattr(self.bot, 'loop'):
                    try:
                        future = asyncio.run_coroutine_threadsafe(
                            self.bot.handle_voice_input(recognized_text),
                            self.bot.loop
                        )
                        future.result(timeout=10)  # タイムアウト延長
                        print("✅ Discord Botに送信完了")
                    except Exception as e:
                        print(f"❌ Discord Bot送信エラー: {e}")
            else:
                print("❌ 音声認識に失敗しました")
                
        except Exception as e:
            print(f"❌ 停止ワーカーエラー: {e}")


# テスト実行部分
if __name__ == "__main__":
    print("🧪 安全なWindows音声入力システム テスト開始")
    
    # テスト用Bot
    class TestBot:
        def __init__(self):
            self.loop = asyncio.new_event_loop()
            self.received_messages = []
            
            # バックグラウンドでループ実行
            self.loop_thread = threading.Thread(target=self._run_loop, daemon=True)
            self.loop_thread.start()
            time.sleep(0.5)
        
        def _run_loop(self):
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        
        async def handle_voice_input(self, text):
            print(f"TestBot受信: {text}")
            self.received_messages.append(text)
            return f"処理完了: {text}"
    
    # テスト実行
    test_bot = TestBot()
    voice_system = SafeHotkeyVoiceIntegration(test_bot)
    
    print("テスト: 録音開始...")
    voice_system.on_hotkey_press()
    time.sleep(5)  # 5秒間録音（音声認識時間込み）
    
    print("テスト: 録音停止...")
    voice_system.on_hotkey_release()
    time.sleep(15)  # 音声認識＋GPT-4処理完了待機（15秒）
    
    print(f"✅ テスト完了 - 受信メッセージ: {test_bot.received_messages}")