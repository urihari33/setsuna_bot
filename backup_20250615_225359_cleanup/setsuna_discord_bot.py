#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot Discord版
音声対話機能付きDiscord Bot
"""

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import sys
import speech_recognition as sr
import io
import wave
from pydub import AudioSegment
import tempfile
import threading
import time
import hashlib

# 環境変数読み込み
load_dotenv()

# 既存のせつなBotコア機能をインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

# コア機能のインポートを試行
try:
    from setsuna_chat import SetsunaChat
    from voice_output import VoiceOutput
    print("✅ コア機能を正常に読み込みました")
except ImportError as e:
    print(f"⚠️  コア機能の読み込みに失敗: {e}")
    print("💡 一部機能が制限される可能性があります")
    # フォールバック実装
    class SetsunaChat:
        def get_response(self, message):
            return "申し訳ございません。現在、せつなの心が少し不安定で、お返事ができません。"
    
    class VoiceOutput:
        def __init__(self):
            pass
        def speak(self, text, save_path=None):
            print(f"音声: {text}")
            return None

class VoiceRecordingSink:
    """Discord音声録音用カスタムSinkクラス"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.recording_data = {}  # ユーザーIDごとの音声データ
        self.is_recording = False
        self.recognizer = sr.Recognizer()
        
    def want_opus(self):
        """Opusデータを要求"""
        return False
    
    def write(self, data, user):
        """音声データの書き込み処理"""
        if not self.is_recording:
            return
            
        user_id = user.id if user else 0
        
        # ユーザーの音声データを蓄積
        if user_id not in self.recording_data:
            self.recording_data[user_id] = {
                'user': user,
                'audio_data': [],
                'start_time': time.time()
            }
        
        # PCMデータを蓄積
        self.recording_data[user_id]['audio_data'].append(data.pcm)
        
    def cleanup(self):
        """クリーンアップ処理"""
        self.is_recording = False
        
    def start_recording(self):
        """録音開始"""
        self.is_recording = True
        self.recording_data = {}
        print("🎤 Discord音声録音開始")
        
    def stop_recording_and_process(self):
        """録音停止と音声認識処理"""
        self.is_recording = False
        print("🛑 Discord音声録音停止、音声認識処理開始")
        
        # 各ユーザーの音声データを処理
        for user_id, data in self.recording_data.items():
            if data['audio_data'] and data['user']:
                threading.Thread(
                    target=self._process_user_audio,
                    args=(data['user'], data['audio_data']),
                    daemon=True
                ).start()
        
        self.recording_data = {}
    
    def _process_user_audio(self, user, audio_data_list):
        """ユーザーの音声データを処理"""
        try:
            print(f"🎵 {user.display_name}の音声を処理中...")
            
            # PCMデータを結合
            combined_audio = b''.join(audio_data_list)
            
            if len(combined_audio) < 1024:  # 音声データが短すぎる場合
                print(f"⚠️ {user.display_name}: 音声データが短すぎます")
                return
            
            # PCMからWAVファイルを作成
            wav_data = self._pcm_to_wav(combined_audio)
            
            if not wav_data:
                print(f"❌ {user.display_name}: WAV変換に失敗")
                return
            
            # 音声認識実行
            recognized_text = self._recognize_audio(wav_data)
            
            if recognized_text:
                print(f"✅ {user.display_name}: '{recognized_text}'")
                # 音声メッセージ処理を非同期で実行
                asyncio.run_coroutine_threadsafe(
                    self.bot.handle_voice_message(user.id, recognized_text),
                    self.bot.loop
                )
            else:
                print(f"❌ {user.display_name}: 音声認識失敗")
                
        except Exception as e:
            print(f"❌ {user.display_name}: 音声処理エラー: {e}")
    
    def _pcm_to_wav(self, pcm_data, sample_rate=48000, channels=2, sample_width=2):
        """PCMデータをWAVフォーマットに変換"""
        try:
            # WAVファイルをメモリ上で作成
            wav_buffer = io.BytesIO()
            
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(pcm_data)
            
            wav_buffer.seek(0)
            return wav_buffer.getvalue()
            
        except Exception as e:
            print(f"❌ PCM→WAV変換エラー: {e}")
            return None
    
    def _recognize_audio(self, wav_data):
        """WAVデータから音声認識"""
        try:
            # WAVデータをAudioFileに変換
            audio_buffer = io.BytesIO(wav_data)
            
            with sr.AudioFile(audio_buffer) as source:
                # ノイズ調整
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # 音声データ読み取り
                audio = self.recognizer.record(source)
            
            # Google Speech Recognition API で認識
            text = self.recognizer.recognize_google(audio, language="ja-JP")
            return text.strip() if text else ""
            
        except sr.UnknownValueError:
            print("❌ 音声認識: 音声を理解できませんでした")
            return ""
        except sr.RequestError as e:
            print(f"❌ 音声認識APIエラー: {e}")
            return ""
        except Exception as e:
            print(f"❌ 音声認識エラー: {e}")
            return ""

class VoiceRecognitionHandler:
    """音声認識処理クラス（シンプル版）"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.recognizer = sr.Recognizer()
        self.is_listening = False
    
    async def start_voice_detection(self, voice_client, channel):
        """音声検出開始（簡易版）"""
        print("🎤 音声検出開始...")
        self.is_listening = True
        
        # 実際の音声認識は手動トリガーで実行
        return True
    
    def stop_voice_detection(self):
        """音声検出停止"""
        print("🛑 音声検出停止")
        self.is_listening = False
    
    async def process_voice_command(self, user, text):
        """音声コマンド処理（テスト用）"""
        try:
            print(f"🎤 {user.display_name}: {text}")
            
            # 応答生成
            if self.bot.setsuna_chat:
                response = self.bot.setsuna_chat.get_response(text)
            else:
                response = f"{user.display_name}さん、こんにちは！「{text}」ですね。"
            
            return response
            
        except Exception as e:
            print(f"❌ 音声コマンド処理エラー: {e}")
            return "申し訳ありません、エラーが発生しました。"

class SetsunaDiscordBot(commands.Bot):
    def __init__(self):
        # Bot設定
        intents = discord.Intents.default()
        intents.message_content = True  # メッセージ内容読み取り
        intents.voice_states = True     # 音声状態変更検知
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='せつなBot - 音声対話AI'
        )
        
        # 音声関連
        self.voice_client = None
        self.setsuna_chat = None
        self.voice_output = None
        self.voice_handler = VoiceRecognitionHandler(self)
        self.voice_sink = VoiceRecordingSink(self)
        self.is_recording = False
        self.voice_dialog_active = False
        self.voice_recognition_active = False
        
        # ホットキー音声入力
        self.hotkey_voice_input = None
        
        # コア機能初期化
        try:
            self.setsuna_chat = SetsunaChat()
            self.voice_output = VoiceOutput()
            print("✅ せつなBotコア機能初期化完了")
        except Exception as e:
            print(f"⚠️  コア機能初期化エラー: {e}")
            self.setsuna_chat = SetsunaChat()  # フォールバック版を使用
            self.voice_output = VoiceOutput()  # フォールバック版を使用
        
        print("🤖 せつなBot Discord版 初期化中...")
    
    async def setup_hook(self):
        """Bot起動時の初期化"""
        print("🔧 せつなBot コンポーネント初期化中...")
        await self.setup_setsuna_components()
        
        # コマンド同期（スラッシュコマンド用）
        try:
            print("🔄 コマンド同期中...")
            # 注意: これはスラッシュコマンド用。プレフィックスコマンドには不要
            # await self.tree.sync()
            print("✅ コマンド準備完了")
        except Exception as e:
            print(f"⚠️ コマンド同期エラー（プレフィックスコマンドは正常動作）: {e}")
        
        print("✅ せつなBot Discord版 初期化完了")
    
    async def setup_setsuna_components(self):
        """せつなBotコア機能の初期化"""
        try:
            # せつなチャット初期化
            try:
                from setsuna_chat import SetsunaChat
                self.setsuna_chat = SetsunaChat()
                print("✅ せつなチャットシステム初期化完了")
            except Exception as e:
                print(f"⚠️ せつなチャット初期化エラー: {e}")
                self.setsuna_chat = None
            
            # 音声出力初期化
            try:
                from voice_output import VoiceOutput
                self.voice_output = VoiceOutput()
                print("✅ VOICEVOX音声出力システム初期化完了")
            except Exception as e:
                print(f"⚠️ 音声出力初期化エラー: {e}")
                self.voice_output = None
            
            # ホットキー音声入力初期化
            try:
                from hotkey_voice_input import HotkeyVoiceInput
                self.hotkey_voice_input = HotkeyVoiceInput(self)
                print("✅ ホットキー音声入力システム初期化完了")
            except Exception as e:
                print(f"⚠️ ホットキー音声入力初期化エラー: {e}")
                self.hotkey_voice_input = None
        
        except Exception as e:
            print(f"❌ コンポーネント初期化エラー: {e}")
    
    async def on_ready(self):
        """Bot起動完了時"""
        print(f"🎉 {self.user} としてDiscordに接続しました！")
        print(f"📊 参加サーバー数: {len(self.guilds)}")
        print(f"🔑 Bot ID: {self.user.id}")
        
        # サーバー情報表示
        for guild in self.guilds:
            print(f"   📍 {guild.name} (ID: {guild.id})")
        
        # 機能状態確認
        print("🔍 システム状態:")
        print(f"   💬 チャット機能: {'✅ 有効' if self.setsuna_chat else '❌ 無効'}")
        print(f"   🔊 音声機能: {'✅ 有効' if self.voice_output else '❌ 無効'}")
        
        # 登録済みコマンド確認
        print("📝 登録済みコマンド:")
        for command_name in self.all_commands.keys():
            print(f"   !{command_name}")
        
        # アクティビティ設定
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="音声対話 | !guide でヘルプ"
        )
        await self.change_presence(activity=activity)
        
        print("✅ せつなBot 起動完了 - コマンド待機中...")
        print("💡 !guide コマンドで使い方を確認できます")
    
    async def on_message(self, message):
        """メッセージ受信時"""
        # Bot自身のメッセージは無視
        if message.author == self.user:
            return
        
        # せつなへの言及またはDMの場合、チャット応答
        if self.user in message.mentions or isinstance(message.channel, discord.DMChannel):
            await self.handle_chat_message(message)
        
        # コマンド処理
        await self.process_commands(message)
    
    async def handle_chat_message(self, message):
        """チャットメッセージ処理"""
        try:
            # メッセージからメンションを除去
            content = message.content.replace(f'<@{self.user.id}>', '').strip()
            
            if not content:
                content = "こんにちは"
            
            # 応答生成
            if self.setsuna_chat:
                response = self.setsuna_chat.get_response(content)
            else:
                response = f"こんにちは！{message.author.mention}さん。せつなです。音声チャットでお話しませんか？"
            
            # テキスト応答送信
            await message.reply(response)
            
            # 音声対話モードが有効で、ボイスチャンネルに接続中の場合、音声でも応答
            if self.voice_dialog_active and self.voice_client and self.voice_client.is_connected():
                print(f"🔊 音声対話モード: 音声応答を開始")
                await self.play_voice_response(response)
            
        except Exception as e:
            print(f"❌ チャット応答エラー: {e}")
            await message.reply("申し訳ありません、エラーが発生しました。")
    
    async def handle_voice_message(self, user_id, recognized_text):
        """音声メッセージ処理"""
        try:
            # ユーザー情報取得
            user = self.get_user(user_id)
            if not user:
                print(f"❌ ユーザーID {user_id} が見つかりません")
                return
            
            print(f"🎤 {user.display_name}: {recognized_text}")
            
            # 応答生成
            if self.setsuna_chat:
                response = self.setsuna_chat.get_response(recognized_text)
            else:
                response = f"{user.display_name}さん、こんにちは！音声でのメッセージをありがとうございます。"
            
            # テキストでも応答送信（デバッグ用）
            if self.voice_client and self.voice_client.channel:
                # ボイスチャンネルに対応するテキストチャンネルを探す
                guild = self.voice_client.guild
                text_channel = discord.utils.get(guild.text_channels, name='general')
                if not text_channel:
                    text_channel = guild.text_channels[0] if guild.text_channels else None
                
                if text_channel:
                    embed = discord.Embed(
                        title="🎤 音声認識結果",
                        color=0x7289da
                    )
                    embed.add_field(name="発言者", value=user.display_name, inline=True)
                    embed.add_field(name="認識内容", value=recognized_text, inline=False)
                    embed.add_field(name="せつなの応答", value=response, inline=False)
                    
                    await text_channel.send(embed=embed)
            
            # 音声応答（将来実装）
            if self.voice_output:
                # VOICEVOXで音声合成してDiscordで再生
                await self.play_voice_response(response)
            
        except Exception as e:
            print(f"❌ 音声メッセージ処理エラー: {e}")
    
    async def play_voice_response(self, text):
        """音声応答の再生"""
        try:
            if not self.voice_client or not self.voice_output:
                print(f"🔊 音声応答（テキスト）: {text}")
                return
            
            print(f"🔊 VOICEVOX音声合成開始: {text}")
            
            # VOICEVOXで音声合成
            audio_file_path = await self._synthesize_voice(text)
            
            if audio_file_path and os.path.exists(audio_file_path):
                # Discordで音声再生（FFmpeg不要の方法）
                if not self.voice_client.is_playing():
                    try:
                        # WAVファイルをPCMに変換してDiscordで再生
                        source = await self._create_discord_audio_source(audio_file_path)
                        if source:
                            self.voice_client.play(source)
                            print(f"✅ Discord音声再生開始")
                            
                            # 再生完了まで待機
                            while self.voice_client.is_playing():
                                await asyncio.sleep(0.1)
                            
                            print("✅ Discord音声再生完了")
                        else:
                            print("❌ 音声ソース作成失敗")
                    except Exception as play_error:
                        print(f"❌ 音声再生失敗: {play_error}")
                        # フォールバック: ローカル再生
                        await self._fallback_local_audio_play(audio_file_path)
                else:
                    print("⚠️ Discord音声再生中のため、スキップ")
                
                # 一時ファイル削除
                try:
                    os.unlink(audio_file_path)
                except:
                    pass
            else:
                print("❌ 音声合成ファイルが見つかりません")
                
        except Exception as e:
            print(f"❌ Discord音声再生エラー: {e}")
    
    async def _synthesize_voice(self, text):
        """VOICEVOX音声合成（非同期対応）"""
        try:
            def synthesis_worker():
                if self.voice_output:
                    # 一時ファイルパスを取得
                    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                    temp_file.close()
                    
                    # VOICEVOX音声合成を実行
                    self.voice_output.speak(text, save_path=temp_file.name)
                    return temp_file.name
                return None
            
            # 別スレッドで音声合成実行
            loop = asyncio.get_event_loop()
            audio_path = await loop.run_in_executor(None, synthesis_worker)
            return audio_path
            
        except Exception as e:
            print(f"❌ VOICEVOX音声合成エラー: {e}")
            return None

    async def _start_manual_recording(self, ctx):
        """手動録音実装（discord.pyの制限回避）"""
        try:
            # この実装は現在のdiscord.pyバージョンでは制限があるため
            # リアルタイム音声録音の代わりに、定期的な音声キャプチャを実装
            await ctx.send("🎤 **手動録音モード開始**\n音声録音は制限されていますが、テキスト入力による対話は利用できます。")
            
            # 将来的には、discord.pyの最新版への更新または
            # 別の音声録音ライブラリの使用を検討
            
            return True
            
        except Exception as e:
            print(f"❌ 手動録音実装エラー: {e}")
            raise e
    
    async def _create_discord_audio_source(self, wav_file_path):
        """WAVファイルからDiscord用音声ソースを作成（FFmpeg不使用）"""
        try:
            # pydubを使用してWAVファイルをPCMに変換
            from pydub import AudioSegment
            from pydub.utils import make_chunks
            import io
            
            # WAVファイル読み込み
            audio = AudioSegment.from_wav(wav_file_path)
            
            # Discord用に変換（48kHz, 16-bit, 2ch stereo）
            audio = audio.set_frame_rate(48000).set_channels(2).set_sample_width(2)
            
            # PCMデータ取得
            pcm_data = audio.raw_data
            
            # BytesIOでラップ
            pcm_io = io.BytesIO(pcm_data)
            
            # DiscordのPCMAudioSourceを作成
            source = discord.PCMAudio(pcm_io)
            return source
            
        except Exception as e:
            print(f"❌ Discord音声ソース作成エラー: {e}")
            return None
    
    async def _fallback_local_audio_play(self, audio_file_path):
        """フォールバック: ローカル音声再生"""
        try:
            print("🔊 フォールバック: ローカル音声再生")
            
            def local_play():
                if self.voice_output:
                    self.voice_output.play(audio_file_path)
            
            # 別スレッドでローカル再生
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, local_play)
            
        except Exception as e:
            print(f"❌ ローカル音声再生エラー: {e}")
    
    async def _start_manual_voice_recording(self, ctx, duration):
        """マニュアル音声録音（時間指定）"""
        try:
            import pyaudio
            import wave
            
            await ctx.send(f"🎤 **{duration}秒間の音声録音を開始します**\nマイクに向かって話してください...")
            
            self.is_recording = True
            
            # PyAudio設定
            chunk = 1024
            format = pyaudio.paInt16
            channels = 1
            rate = 16000
            
            # PyAudio初期化
            p = pyaudio.PyAudio()
            
            # 録音ストリーム開始
            stream = p.open(format=format,
                          channels=channels,
                          rate=rate,
                          input=True,
                          frames_per_buffer=chunk)
            
            print(f"🎤 録音開始: {duration}秒")
            frames = []
            
            # 指定時間録音
            for i in range(0, int(rate / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)
            
            print("🛑 録音完了")
            
            # 録音停止
            stream.stop_stream()
            stream.close()
            p.terminate()
            self.is_recording = False
            
            # WAVファイル保存
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            wf = wave.open(temp_wav.name, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            await ctx.send("🔄 **音声認識処理中...**")
            
            # 音声認識実行
            recognized_text = await self._recognize_audio_file(temp_wav.name)
            
            if recognized_text:
                await ctx.send(f"✅ **音声認識結果:** {recognized_text}")
                
                # 音声対話処理
                await self.handle_voice_message(ctx.author.id, recognized_text)
            else:
                await ctx.send("❌ 音声を認識できませんでした")
            
            # 一時ファイル削除
            try:
                os.unlink(temp_wav.name)
            except:
                pass
                
        except ImportError:
            await ctx.send("❌ PyAudioがインストールされていません。\nLinux環境では `!hotkey_start` コマンドをお試しください。")
        except Exception as e:
            self.is_recording = False
            print(f"❌ マニュアル録音エラー: {e}")
            await ctx.send(f"❌ 録音エラー: {e}")
    
    async def _start_realtime_voice_recognition(self, ctx):
        """リアルタイム音声認識開始"""
        try:
            import pyaudio
            
            await ctx.send("🎤 **リアルタイム音声認識開始**\n`!stop_listen` で停止")
            
            self.is_recording = True
            self.voice_recognition_active = True
            
            # 別スレッドで音声認識ループを開始
            threading.Thread(
                target=self._voice_recognition_loop,
                args=(ctx,),
                daemon=True
            ).start()
            
        except ImportError:
            await ctx.send("❌ PyAudioがインストールされていません。\n`!hotkey_start` コマンドをお試しください。")
        except Exception as e:
            self.is_recording = False
            print(f"❌ リアルタイム音声認識開始エラー: {e}")
            raise e
    
    async def _stop_realtime_voice_recognition(self, ctx):
        """リアルタイム音声認識停止"""
        self.is_recording = False
        self.voice_recognition_active = False
        await ctx.send("🛑 **リアルタイム音声認識停止**")
    
    def _voice_recognition_loop(self, ctx):
        """音声認識ループ（別スレッド実行）"""
        try:
            import pyaudio
            import wave
            
            # PyAudio設定
            chunk = 1024
            format = pyaudio.paInt16
            channels = 1
            rate = 16000
            
            p = pyaudio.PyAudio()
            stream = p.open(format=format,
                          channels=channels,
                          rate=rate,
                          input=True,
                          frames_per_buffer=chunk)
            
            print("🎤 音声認識ループ開始")
            
            while getattr(self, 'voice_recognition_active', False):
                try:
                    # 3秒間の音声データを取得
                    frames = []
                    for i in range(0, int(rate / chunk * 3)):
                        if not getattr(self, 'voice_recognition_active', False):
                            break
                        data = stream.read(chunk, exception_on_overflow=False)
                        frames.append(data)
                    
                    if not frames:
                        continue
                    
                    # 音声レベルチェック（無音検出）
                    audio_data = b''.join(frames)
                    if self._is_silence(audio_data):
                        continue
                    
                    # WAVファイル作成
                    temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                    wf = wave.open(temp_wav.name, 'wb')
                    wf.setnchannels(channels)
                    wf.setsampwidth(p.get_sample_size(format))
                    wf.setframerate(rate)
                    wf.writeframes(audio_data)
                    wf.close()
                    
                    # 音声認識実行
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    recognized_text = loop.run_until_complete(
                        self._recognize_audio_file(temp_wav.name)
                    )
                    loop.close()
                    
                    if recognized_text:
                        print(f"🎤 認識: {recognized_text}")
                        # 音声メッセージ処理を非同期で実行
                        asyncio.run_coroutine_threadsafe(
                            self.handle_voice_message(ctx.author.id, recognized_text),
                            self.loop
                        )
                    
                    # 一時ファイル削除
                    try:
                        os.unlink(temp_wav.name)
                    except:
                        pass
                        
                except Exception as e:
                    print(f"❌ 音声認識ループエラー: {e}")
                    time.sleep(1)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            print("🛑 音声認識ループ終了")
            
        except Exception as e:
            print(f"❌ 音声認識ループ致命的エラー: {e}")
    
    def _is_silence(self, audio_data, threshold=500):
        """無音検出"""
        import struct
        
        # 音声データを16bit intに変換
        audio_ints = struct.unpack('<' + ('h' * (len(audio_data) // 2)), audio_data)
        
        # RMS（Root Mean Square）計算
        rms = (sum(x**2 for x in audio_ints) / len(audio_ints)) ** 0.5
        
        return rms < threshold
    
    async def _recognize_audio_file(self, wav_file_path):
        """WAVファイルから音声認識"""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(wav_file_path) as source:
                # ノイズ調整
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # 音声データ読み取り
                audio = recognizer.record(source)
            
            # Google Speech Recognition API で認識
            text = recognizer.recognize_google(audio, language="ja-JP")
            return text.strip() if text else ""
            
        except sr.UnknownValueError:
            print("❌ 音声認識: 音声を理解できませんでした")
            return ""
        except sr.RequestError as e:
            print(f"❌ 音声認識APIエラー: {e}")
            return ""
        except Exception as e:
            print(f"❌ 音声認識エラー: {e}")
            return ""

# Bot コマンド定義
bot = SetsunaDiscordBot()

@bot.command(name='join')
async def join_voice(ctx):
    """ボイスチャンネルに参加"""
    if ctx.author.voice is None:
        await ctx.send("❌ ボイスチャンネルに参加してから呼び出してください。")
        return
    
    channel = ctx.author.voice.channel
    
    if bot.voice_client is not None:
        await bot.voice_client.move_to(channel)
    else:
        bot.voice_client = await channel.connect()
    
    await ctx.send(f"✅ {channel.name} に参加しました！音声で話しかけてください。")

@bot.command(name='leave')
async def leave_voice(ctx):
    """ボイスチャンネルから退出"""
    if bot.voice_client is None:
        await ctx.send("❌ ボイスチャンネルに参加していません。")
        return
    
    # 録音停止
    if bot.is_recording:
        bot.voice_client.stop_recording()
        bot.is_recording = False
    
    await bot.voice_client.disconnect()
    bot.voice_client = None
    await ctx.send("👋 ボイスチャンネルから退出しました。")

@bot.command(name='listen')
async def start_listening(ctx):
    """音声検出開始"""
    if bot.voice_client is None:
        await ctx.send("❌ 先にボイスチャンネルに参加してください（`!join`）")
        return
    
    if bot.is_recording:
        await ctx.send("❌ 既に音声検出中です")
        return
    
    try:
        # 音声検出開始
        success = await bot.voice_handler.start_voice_detection(bot.voice_client, ctx.channel)
        
        if success:
            bot.is_recording = True
            await ctx.send("🎤 音声検出を開始しました！`!say <メッセージ>` で音声対話をシミュレートできます。")
        else:
            await ctx.send("❌ 音声検出開始に失敗しました")
        
    except Exception as e:
        await ctx.send(f"❌ 音声検出開始エラー: {e}")

@bot.command(name='stop')
async def stop_listening(ctx):
    """音声検出停止"""
    if not bot.is_recording:
        await ctx.send("❌ 音声検出していません")
        return
    
    try:
        bot.voice_handler.stop_voice_detection()
        bot.is_recording = False
        await ctx.send("🛑 音声検出を停止しました")
        
    except Exception as e:
        await ctx.send(f"❌ 音声検出停止エラー: {e}")

@bot.command(name='say')
async def voice_say(ctx, *, message):
    """音声対話のシミュレート"""
    try:
        # 音声コマンド処理
        response = await bot.voice_handler.process_voice_command(ctx.author, message)
        
        # 結果表示
        embed = discord.Embed(
            title="🎤 音声対話シミュレーション",
            color=0x7289da
        )
        embed.add_field(name="発言者", value=ctx.author.display_name, inline=True)
        embed.add_field(name="音声内容", value=message, inline=False)
        embed.add_field(name="せつなの応答", value=response, inline=False)
        
        await ctx.send(embed=embed)
        
        # 音声対話モードが有効で、ボイスチャンネルに接続中の場合、音声でも応答
        if bot.voice_dialog_active and bot.voice_client and bot.voice_client.is_connected():
            print(f"🔊 !sayコマンド: 音声応答を開始")
            await bot.play_voice_response(response)
        
    except Exception as e:
        await ctx.send(f"❌ 音声対話エラー: {e}")

@bot.command(name='status')
async def bot_status(ctx):
    """Bot状態確認"""
    embed = discord.Embed(title="🤖 せつなBot ステータス", color=0x7289da)
    
    # チャット機能
    chat_status = "✅ 利用可能" if bot.setsuna_chat else "❌ 未接続"
    embed.add_field(name="💬 チャット機能", value=chat_status, inline=True)
    
    # 音声出力
    voice_status = "✅ 利用可能" if bot.voice_output else "❌ 未接続"
    embed.add_field(name="🔊 音声出力", value=voice_status, inline=True)
    
    # ボイスチャンネル
    vc_status = "✅ 接続中" if bot.voice_client else "❌ 未接続"
    embed.add_field(name="🎤 ボイスチャンネル", value=vc_status, inline=True)
    
    # 音声録音
    recording_status = "🔴 録音中" if bot.is_recording else "⚫ 停止中"
    embed.add_field(name="🎙️ 音声録音", value=recording_status, inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='voice_start')
async def start_voice_dialog(ctx):
    """音声対話モード開始"""
    if bot.voice_client is None:
        await ctx.send("❌ 先にボイスチャンネルに参加してください（`!join`）")
        return
    
    if bot.voice_dialog_active:
        await ctx.send("❌ 既に音声対話モードが開始されています")
        return
    
    try:
        # 現在のdiscord.py 2.5.2では録音機能が制限されているため
        # 音声合成による応答のみを有効にします
        bot.voice_dialog_active = True
        bot.is_recording = False  # 録音は無効
        
        embed = discord.Embed(
            title="🎤 音声対話モード開始",
            description="現在、音声録音機能は制限されていますが、音声応答は利用できます。",
            color=0x7289da
        )
        embed.add_field(
            name="利用可能な機能",
            value="• テキスト入力 → 音声応答\n• `!say <メッセージ>` コマンド\n• VOICEVOX音声合成",
            inline=False
        )
        embed.add_field(
            name="使用方法",
            value="1. テキストでメッセージを送信\n2. せつなが音声で応答します\n3. `!voice_stop` で終了",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ 音声対話開始エラー: {e}")
        print(f"詳細なエラー: {e}")

@bot.command(name='voice_stop')
async def stop_voice_dialog(ctx):
    """音声対話モード停止"""
    if not bot.voice_dialog_active:
        await ctx.send("❌ 音声対話モードが開始されていません")
        return
    
    try:
        # discord.pyバージョンに応じた録音停止
        if hasattr(bot.voice_client, 'stop_recording'):
            bot.voice_client.stop_recording()
        
        bot.voice_sink.stop_recording_and_process()
        bot.voice_dialog_active = False
        bot.is_recording = False
        
        await ctx.send("🛑 **音声対話モード停止**\n音声認識処理を実行中...")
        
    except Exception as e:
        await ctx.send(f"❌ 音声対話停止エラー: {e}")

@bot.command(name='record')
async def start_voice_recording(ctx, duration: int = 5):
    """音声録音開始（コマンドベース）"""
    if bot.voice_client is None:
        await ctx.send("❌ 先にボイスチャンネルに参加してください（`!join`）")
        return
    
    if bot.is_recording:
        await ctx.send("❌ 既に録音中です")
        return
    
    if duration < 1 or duration > 30:
        await ctx.send("❌ 録音時間は1〜30秒の間で指定してください")
        return
    
    try:
        # マニュアル録音開始
        await bot._start_manual_voice_recording(ctx, duration)
        
    except Exception as e:
        await ctx.send(f"❌ 音声録音開始エラー: {e}")

@bot.command(name='listen_realtime')
async def start_listening_mode(ctx):
    """リアルタイム音声認識開始"""
    if bot.voice_client is None:
        await ctx.send("❌ 先にボイスチャンネルに参加してください（`!join`）")
        return
    
    if bot.is_recording:
        await ctx.send("❌ 既に音声認識中です")
        return
    
    try:
        # リアルタイム音声認識開始
        await bot._start_realtime_voice_recognition(ctx)
        
    except Exception as e:
        await ctx.send(f"❌ リアルタイム音声認識エラー: {e}")

@bot.command(name='stop_listen')
async def stop_listening_mode(ctx):
    """リアルタイム音声認識停止"""
    if not bot.is_recording:
        await ctx.send("❌ 音声認識していません")
        return
    
    try:
        # リアルタイム音声認識停止
        await bot._stop_realtime_voice_recognition(ctx)
        
    except Exception as e:
        await ctx.send(f"❌ 音声認識停止エラー: {e}")

@bot.command(name='hotkey_start')
async def start_hotkey_voice(ctx):
    """ホットキー音声入力開始"""
    if not bot.hotkey_voice_input:
        await ctx.send("❌ ホットキー音声入力システムが利用できません")
        return
    
    if bot.voice_client is None:
        await ctx.send("❌ 先にボイスチャンネルに参加してください（`!join`）")
        return
    
    try:
        # ホットキーリスナー開始
        success = bot.hotkey_voice_input.start_hotkey_listener()
        
        if success:
            embed = discord.Embed(
                title="🎮 ホットキー音声入力開始",
                description="WSL2環境に対応した音声入力システムが開始されました",
                color=0x00ff00
            )
            embed.add_field(
                name="動作モード",
                value="• **理想:** Ctrl+Shift+Alt で音声録音\n• **WSL2:** 自動テスト音声入力（5秒後）\n• **フォールバック:** 定期的なテスト実行",
                inline=False
            )
            embed.add_field(
                name="WSL2環境での制限",
                value="• マイクアクセスが制限されている場合があります\n• テスト用音声メッセージで動作確認できます\n• Windowsネイティブ環境では正常動作します",
                inline=False
            )
            embed.add_field(
                name="終了",
                value="`!hotkey_stop` でホットキー機能を停止",
                inline=False
            )
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ ホットキーリスナーの開始に失敗しました")
        
    except Exception as e:
        await ctx.send(f"❌ ホットキー音声入力開始エラー: {e}")

@bot.command(name='hotkey_stop')
async def stop_hotkey_voice(ctx):
    """ホットキー音声入力停止"""
    if not bot.hotkey_voice_input:
        await ctx.send("❌ ホットキー音声入力システムが利用できません")
        return
    
    try:
        # ホットキーリスナー停止
        bot.hotkey_voice_input.stop_hotkey_listener()
        
        await ctx.send("🛑 **ホットキー音声入力停止**\nCtrl+Shift+Alt による音声認識を終了しました")
        
    except Exception as e:
        await ctx.send(f"❌ ホットキー音声入力停止エラー: {e}")

@bot.command(name='voice_test')
async def test_voice_input(ctx):
    """音声入力テスト（手動実行）"""
    if not bot.hotkey_voice_input:
        await ctx.send("❌ ホットキー音声入力システムが利用できません")
        return
    
    if not bot.voice_dialog_active:
        await ctx.send("❌ 先に `!voice_start` で音声対話モードを開始してください")
        return
    
    try:
        await ctx.send("🎤 **音声入力テスト実行中...**")
        
        # テスト用音声入力をシミュレート
        bot.hotkey_voice_input._test_hotkey_simulation()
        
        await ctx.send("✅ 音声入力テストを実行しました。数秒後に結果が表示されます。")
        
    except Exception as e:
        await ctx.send(f"❌ 音声入力テストエラー: {e}")

@bot.command(name='voice_settings')
async def voice_settings_command(ctx, setting=None, value=None):
    """音声設定変更"""
    if not bot.voice_output:
        await ctx.send("❌ 音声システムが利用できません")
        return
    
    if not setting or not value:
        # 現在の設定表示
        embed = discord.Embed(title="🎛️ 現在の音声設定", color=0x7289da)
        embed.add_field(name="話速", value="1.2x", inline=True)
        embed.add_field(name="音程", value="0.0", inline=True)
        embed.add_field(name="抑揚", value="1.0", inline=True)
        embed.add_field(
            name="使用方法",
            value="`!voice_settings speed 1.5` - 話速設定\n`!voice_settings pitch 0.1` - 音程設定\n`!voice_settings intonation 1.2` - 抑揚設定",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    try:
        value_float = float(value)
        
        if setting == "speed" and 0.5 <= value_float <= 2.0:
            await ctx.send(f"✅ 話速を {value_float}x に設定しました")
        elif setting == "pitch" and -0.15 <= value_float <= 0.15:
            await ctx.send(f"✅ 音程を {value_float} に設定しました")
        elif setting == "intonation" and 0.5 <= value_float <= 2.0:
            await ctx.send(f"✅ 抑揚を {value_float} に設定しました")
        else:
            await ctx.send("❌ 設定値が範囲外です")
            
    except ValueError:
        await ctx.send("❌ 数値を入力してください")

@bot.command(name='guide')
async def guide_command(ctx):
    """ヘルプ表示"""
    embed = discord.Embed(
        title="🤖 せつなBot ヘルプ",
        description="音声対話ができるAI Botです",
        color=0x7289da
    )
    
    embed.add_field(
        name="📝 基本コマンド",
        value="`!join` - ボイスチャンネルに参加\n`!leave` - ボイスチャンネルから退出\n`!status` - Bot状態確認\n`!guide` - このヘルプ表示",
        inline=False
    )
    
    embed.add_field(
        name="🎤 音声対話",
        value="`!voice_start` - 音声対話モード開始\n`!voice_stop` - 音声対話モード停止\n`!voice_settings` - 音声設定確認・変更",
        inline=False
    )
    
    embed.add_field(
        name="🎙️ 音声入力",
        value="`!record [秒]` - 指定時間音声録音\n`!listen_realtime` - リアルタイム音声認識\n`!stop_listen` - 音声認識停止",
        inline=False
    )
    
    embed.add_field(
        name="🎮 ホットキー音声（推奨）",
        value="`!hotkey_start` - Ctrl+Shift+Alt音声入力開始\n`!hotkey_stop` - ホットキー音声入力停止\n`!voice_test` - 音声入力テスト実行",
        inline=False
    )
    
    embed.add_field(
        name="💬 テキストチャット",
        value="@せつな メッセージ - テキストで対話\nDM - ダイレクトメッセージでも対話可能",
        inline=False
    )
    
    embed.add_field(
        name="🗣️ 音声対話の使い方",
        value="**基本:** `!join` → `!voice_start`\n**コマンド:** `!record 5` で5秒録音\n**ホットキー:** `!hotkey_start` → Ctrl+Shift+Alt押下で録音\n**終了:** `!voice_stop` / `!hotkey_stop`",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Bot起動
if __name__ == "__main__":
    print("🚀 せつなBot Discord版 起動中...")
    
    # Discord Bot Token確認
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token or token == "your_discord_bot_token_here":
        print("❌ DISCORD_BOT_TOKENが設定されていません")
        print("💡 .env ファイルでDiscord Bot Tokenを設定してください")
        input("Enterキーで終了...")
        exit(1)
    
    print(f"🔑 Bot Token: {token[:20]}...")
    print("🔗 Discord接続試行中...")
    
    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        print("❌ Discord Bot Tokenが無効です")
        print("💡 Discord Developer Portal でTokenを確認してください")
        input("Enterキーで終了...")
    except KeyboardInterrupt:
        print("\n✅ Bot を正常終了しました")
    except Exception as e:
        print(f"❌ Bot起動エラー: {e}")
        print("🔍 詳細エラー情報:")
        import traceback
        traceback.print_exc()
        input("Enterキーで終了...")
    finally:
        print("👋 せつなBot終了")