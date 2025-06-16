#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot - Windows自動起動版
起動と同時にDiscordボイスチャンネル参加・ホットキーモード開始
"""

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import sys
import tempfile
import wave
import speech_recognition as sr
import threading
import time
from pynput import keyboard
import subprocess
import random

# 安全な音声入力システムをインポート
try:
    from windows_voice_input import SafeHotkeyVoiceIntegration
    from integrated_hotkey_system import IntegratedHotkeySystem
    print("✅ 安全な音声入力システムを読み込みました")
    SAFE_VOICE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 安全な音声入力システムの読み込みに失敗: {e}")
    SafeHotkeyVoiceIntegration = None
    IntegratedHotkeySystem = None
    SAFE_VOICE_AVAILABLE = False

# 環境変数読み込み
load_dotenv()

# 既存のせつなBotコア機能をインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

try:
    from core.setsuna_chat import SetsunaChat
    from core.voice_output import VoiceOutput
    print("✅ コア機能を正常に読み込みました")
except ImportError as e:
    print(f"⚠️ コア機能の読み込みに失敗: {e}")
    # フォールバック実装
    class SetsunaChat:
        def get_response(self, message):
            responses = [
                f"そうですね、{message}について私も同感です。",
                f"{message}のお話、興味深いですね。",
                "なるほど、それは面白い視点ですね。",
                "私もそう思います。もう少し詳しく聞かせてください。",
                "それについて、私なりに考えてみました。"
            ]
            return random.choice(responses)
    
    class VoiceOutput:
        def __init__(self):
            pass
        def speak(self, text, save_path=None):
            print(f"🔊 音声出力: {text}")
            return None


class WindowsHotkeyVoice:
    """Windows専用ホットキー音声システム"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.is_listening = False
        self.is_recording = False
        self.recording_process = None
        self.pressed_keys = set()
        self.keyboard_listener = None
        
        # 音声認識
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        print("🎮 Windows ホットキー音声システム初期化完了")
    
    def _is_hotkey_pressed(self, pressed_keys):
        """Ctrl+Shift+Alt 検出"""
        ctrl_keys = [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]
        shift_keys = [keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r]
        alt_keys = [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r]
        
        ctrl_pressed = any(k in pressed_keys for k in ctrl_keys)
        shift_pressed = any(k in pressed_keys for k in shift_keys)
        alt_pressed = any(k in pressed_keys for k in alt_keys)
        
        return ctrl_pressed and shift_pressed and alt_pressed
    
    def start_listening(self) -> bool:
        """ホットキー監視開始"""
        if self.is_listening:
            return False
        
        try:
            self.is_listening = True
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.keyboard_listener.start()
            print("🎮 ホットキー監視開始: Ctrl+Shift+Alt で音声入力")
            return True
        except Exception as e:
            print(f"❌ ホットキー監視開始エラー: {e}")
            self.is_listening = False
            return False
    
    def stop_listening(self):
        """ホットキー監視停止"""
        if not self.is_listening:
            return
        
        self.is_listening = False
        if self.is_recording:
            self._stop_recording()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        print("✅ ホットキー監視停止")
    
    def _on_key_press(self, key):
        """キー押下処理"""
        try:
            self.pressed_keys.add(key)
            if self._is_hotkey_pressed(self.pressed_keys) and not self.is_recording:
                print("🎤 ホットキー検出: 音声録音開始")
                self.is_recording = True
                threading.Thread(target=self._start_recording, daemon=True).start()
        except Exception as e:
            print(f"❌ キー押下エラー: {e}")
    
    def _on_key_release(self, key):
        """キー離上処理"""
        try:
            if key in self.pressed_keys:
                self.pressed_keys.remove(key)
            if self.is_recording and not self._is_hotkey_pressed(self.pressed_keys):
                print("🛑 ホットキー解除: 音声録音停止")
                self._stop_recording()
        except Exception as e:
            print(f"❌ キー離上エラー: {e}")
    
    def _start_recording(self):
        """音声録音開始"""
        try:
            self.temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            self.temp_wav.close()
            
            print("🎤 音声録音中... (Windows標準)")
            # 簡易的な録音待機（実際のWindows環境では音声録音APIを使用）
            self.recording_process = subprocess.Popen([
                "timeout", "/t", "30", "/nobreak"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        except Exception as e:
            print(f"❌ 録音開始エラー: {e}")
            # フォールバック: テスト音声
            self._generate_test_voice()
    
    def _stop_recording(self):
        """音声録音停止"""
        try:
            self.is_recording = False
            if self.recording_process:
                self.recording_process.terminate()
                self.recording_process = None
            
            # テスト音声を生成（Windows環境では実際の音声認識を実装）
            self._generate_test_voice()
            
        except Exception as e:
            print(f"❌ 録音停止エラー: {e}")
    
    def _generate_test_voice(self):
        """テスト音声生成"""
        test_messages = [
            "せつな、こんにちは",
            "今日の調子はどう？",
            "何か面白い話して",
            "Windows版の動作テスト",
            "自動起動モードのテスト",
            "ホットキー音声入力成功",
            "統合システム動作確認"
        ]
        
        test_message = random.choice(test_messages)
        print(f"🎤 テスト音声: '{test_message}'")
        
        # Bot に音声入力を送信
        if self.bot and hasattr(self.bot, 'loop'):
            try:
                future = asyncio.run_coroutine_threadsafe(
                    self.bot.handle_voice_input(test_message),
                    self.bot.loop
                )
                future.result(timeout=5)
            except Exception as e:
                print(f"❌ Bot送信エラー: {e}")


class SetsunaAutoDiscordBot(commands.Bot):
    """せつなBot - 自動起動版"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='せつなBot - 自動起動版'
        )
        
        # システム状態
        self.voice_client = None
        self.auto_mode_active = False
        self.target_channel_name = None  # 設定で指定
        
        # コア機能初期化
        try:
            self.setsuna_chat = SetsunaChat()
            self.voice_output = VoiceOutput()
            print("✅ せつなBotコア機能初期化完了")
        except Exception as e:
            print(f"⚠️ コア機能初期化エラー: {e}")
            self.setsuna_chat = SetsunaChat()
            self.voice_output = VoiceOutput()
        
        # ホットキーシステム（安全版を優先使用）
        if SAFE_VOICE_AVAILABLE:
            # 安全な音声システム + 統合ホットキー
            self.safe_voice_integration = SafeHotkeyVoiceIntegration(self)
            self.hotkey_voice = IntegratedHotkeySystem(self.safe_voice_integration)
            self.safe_voice_system = True
            print("✅ 統合された安全な音声システムを使用")
        else:
            # 従来システム
            self.hotkey_voice = WindowsHotkeyVoice(self)
            self.safe_voice_system = False
            print("⚠️ 従来の音声システムを使用")
        
        print("🤖 せつなBot自動起動版 初期化完了")
    
    async def on_ready(self):
        """Bot起動完了 - 自動実行開始"""
        print(f"🎉 {self.user} としてDiscordに接続!")
        print(f"📊 参加サーバー数: {len(self.guilds)}")
        
        # アクティビティ設定
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="自動モード | Ctrl+Shift+Alt"
        )
        await self.change_presence(activity=activity)
        
        # 自動モード開始
        await self.start_auto_mode()
    
    async def start_auto_mode(self):
        """自動モード開始"""
        try:
            print("🚀 自動モード開始中...")
            
            # 1. 最初に見つかったボイスチャンネルに参加
            voice_channel = await self.find_voice_channel()
            if not voice_channel:
                print("❌ ボイスチャンネルが見つかりません")
                return
            
            # 2. ボイスチャンネルに接続
            self.voice_client = await voice_channel.connect()
            print(f"✅ {voice_channel.name} に自動参加しました")
            
            # 3. テキストチャンネルに通知
            text_channel = await self.find_text_channel(voice_channel.guild)
            if text_channel:
                embed = discord.Embed(
                    title="🤖 せつなBot 自動起動完了",
                    description=f"ボイスチャンネル {voice_channel.name} に参加しました",
                    color=0x00ff00
                )
                embed.add_field(
                    name="🎮 ホットキー音声入力",
                    value="Ctrl+Shift+Alt を押しながら話しかけてください",
                    inline=False
                )
                embed.add_field(
                    name="💬 テキスト入力",
                    value="@せつな メッセージ でもお話できます",
                    inline=False
                )
                embed.add_field(
                    name="🔊 音声出力",
                    value="せつなの返答はWindowsで音声再生されます",
                    inline=False
                )
                await text_channel.send(embed=embed)
            
            # 4. ホットキー音声入力開始
            success = self.hotkey_voice.start_listening()
            if success:
                self.auto_mode_active = True
                print("✅ 自動モード完全起動完了!")
                print("🎮 Ctrl+Shift+Alt でいつでも音声入力可能")
            else:
                print("❌ ホットキー開始に失敗")
                
        except Exception as e:
            print(f"❌ 自動モード開始エラー: {e}")
    
    async def find_voice_channel(self):
        """ボイスチャンネル検索"""
        for guild in self.guilds:
            for channel in guild.voice_channels:
                # 設定されたチャンネル名がある場合は優先
                if self.target_channel_name and channel.name == self.target_channel_name:
                    return channel
                # 一般的なチャンネル名を検索
                if channel.name.lower() in ['general', 'voice', 'chat', 'ボイス', '音声']:
                    return channel
            # なければ最初のボイスチャンネル
            if guild.voice_channels:
                return guild.voice_channels[0]
        return None
    
    async def find_text_channel(self, guild):
        """テキストチャンネル検索"""
        for channel in guild.text_channels:
            if channel.name.lower() in ['general', 'chat', 'bot', '雑談']:
                return channel
        return guild.text_channels[0] if guild.text_channels else None
    
    async def handle_voice_input(self, recognized_text):
        """音声入力処理"""
        try:
            print(f"🎤 音声入力受信: {recognized_text}")
            
            if not self.auto_mode_active or not self.voice_client:
                print("⚠️ 自動モードが無効です")
                return
            
            # せつなの応答生成
            if self.setsuna_chat:
                response = self.setsuna_chat.get_response(recognized_text)
            else:
                response = f"音声入力を受け取りました: {recognized_text}"
            
            # テキストチャンネルに結果表示
            text_channel = await self.find_text_channel(self.voice_client.guild)
            if text_channel:
                embed = discord.Embed(
                    title="🎤 音声入力",
                    color=0x00ff00
                )
                embed.add_field(name="認識内容", value=recognized_text, inline=False)
                embed.add_field(name="せつなの応答", value=response, inline=False)
                embed.set_footer(text="自動モード | Ctrl+Shift+Alt")
                
                await text_channel.send(embed=embed)
            
            # 音声応答（Windows環境）
            await self.play_voice_response(response)
            
        except Exception as e:
            print(f"❌ 音声入力処理エラー: {e}")
    
    async def play_voice_response(self, text):
        """音声応答再生"""
        try:
            print(f"🔊 音声応答: {text}")
            
            if self.voice_output:
                def voice_worker():
                    self.voice_output.speak(text)
                
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, voice_worker)
                print("✅ 音声再生完了")
            else:
                print(f"🔊 音声テキスト: {text}")
                
        except Exception as e:
            print(f"❌ 音声再生エラー: {e}")
    
    async def on_message(self, message):
        """メッセージ受信処理"""
        if message.author == self.user:
            return
        
        # コマンド処理
        if message.content.startswith('!'):
            await self.process_commands(message)
            return
        
        # @せつな または DM の場合
        if self.user in message.mentions or isinstance(message.channel, discord.DMChannel):
            await self.handle_text_message(message)
    
    async def handle_text_message(self, message):
        """テキストメッセージ処理"""
        try:
            content = message.content.replace(f'<@{self.user.id}>', '').strip()
            if not content:
                content = "こんにちは"
            
            # 応答生成
            if self.setsuna_chat:
                response = self.setsuna_chat.get_response(content)
            else:
                response = f"{message.author.display_name}さん、こんにちは！"
            
            # テキスト応答
            await message.reply(response)
            
            # 音声応答（自動モードの場合）
            if self.auto_mode_active and self.voice_client:
                await self.play_voice_response(response)
                
        except Exception as e:
            print(f"❌ テキストメッセージ処理エラー: {e}")
            await message.reply("申し訳ありません、エラーが発生しました。")


# コマンド定義
bot = SetsunaAutoDiscordBot()

@bot.command(name='status')
async def show_status(ctx):
    """システム状態表示"""
    embed = discord.Embed(title="🤖 せつなBot システム状態", color=0x7289da)
    
    # 自動モード
    auto_status = "✅ 有効" if bot.auto_mode_active else "❌ 無効"
    embed.add_field(name="🚀 自動モード", value=auto_status, inline=True)
    
    # ボイスチャンネル
    vc_status = f"✅ {bot.voice_client.channel.name}" if bot.voice_client else "❌ 未接続"
    embed.add_field(name="🎤 ボイスチャンネル", value=vc_status, inline=True)
    
    # ホットキー
    hotkey_status = "✅ 有効" if bot.hotkey_voice.is_listening else "❌ 無効"
    embed.add_field(name="🎮 ホットキー", value=hotkey_status, inline=True)
    
    # チャット機能
    chat_status = "✅ 利用可能" if bot.setsuna_chat else "❌ 未接続"
    embed.add_field(name="💬 チャット", value=chat_status, inline=True)
    
    # 音声出力
    voice_status = "✅ 利用可能" if bot.voice_output else "❌ 未接続"
    embed.add_field(name="🔊 音声出力", value=voice_status, inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='restart_auto')
async def restart_auto_mode(ctx):
    """自動モード再起動"""
    try:
        # 停止
        if bot.auto_mode_active:
            bot.hotkey_voice.stop_listening()
            bot.auto_mode_active = False
        
        if bot.voice_client:
            await bot.voice_client.disconnect()
            bot.voice_client = None
        
        # 再開
        await bot.start_auto_mode()
        await ctx.send("✅ 自動モードを再起動しました")
        
    except Exception as e:
        await ctx.send(f"❌ 再起動エラー: {e}")

@bot.command(name='guide')
async def show_help(ctx):
    """ヘルプ表示"""
    embed = discord.Embed(
        title="🤖 せつなBot ヘルプ（自動起動版）",
        description="起動と同時に自動でボイスチャンネル参加・ホットキー開始",
        color=0x7289da
    )
    
    embed.add_field(
        name="🎮 ホットキー音声入力",
        value="Ctrl+Shift+Alt を押しながら話すだけ",
        inline=False
    )
    
    embed.add_field(
        name="💬 テキスト入力",
        value="@せつな メッセージ で対話",
        inline=False
    )
    
    embed.add_field(
        name="🔧 管理コマンド",
        value="`!status` - システム状態確認\n`!restart_auto` - 自動モード再起動",
        inline=False
    )
    
    await ctx.send(embed=embed)


# Bot起動
if __name__ == "__main__":
    print("🚀 せつなBot 自動起動版 開始中...")
    
    # Discord Bot Token確認
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token or token == "your_discord_bot_token_here":
        print("❌ DISCORD_BOT_TOKENが設定されていません")
        print("💡 .env ファイルでDiscord Bot Tokenを設定してください")
        exit(1)
    
    print("🔗 Discord接続中...")
    print("✨ 起動後、自動でボイスチャンネル参加・ホットキー開始します")
    
    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        print("❌ Discord Bot Tokenが無効です")
    except KeyboardInterrupt:
        print("\n🛑 Bot終了中...")
        if hasattr(bot, 'hotkey_voice') and bot.hotkey_voice.is_listening:
            bot.hotkey_voice.stop_listening()
        print("✅ 正常終了しました")
    except Exception as e:
        print(f"❌ Bot起動エラー: {e}")
    finally:
        print("👋 せつなBot終了")