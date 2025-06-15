#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord ボイスチャット簡易実装
FFmpeg不要のシンプルな音声機能
"""

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import sys

# 環境変数読み込み
load_dotenv()

# 既存のせつなBotコア機能をインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

# シンプルホットキー音声システムをインポート
try:
    from simple_hotkey_voice import SimpleHotkeyVoice
    print("✅ シンプルホットキー音声システムを読み込みました")
except ImportError as e:
    print(f"⚠️ シンプルホットキー音声システムの読み込みに失敗: {e}")
    SimpleHotkeyVoice = None

try:
    from setsuna_chat import SetsunaChat
    from voice_output import VoiceOutput
    print("✅ コア機能を正常に読み込みました")
except ImportError as e:
    print(f"⚠️  コア機能の読み込みに失敗: {e}")
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


class SetsunaDiscordBotSimple(commands.Bot):
    def __init__(self):
        # Bot設定
        intents = discord.Intents.default()
        intents.message_content = True  # メッセージ内容読み取り
        intents.voice_states = True     # 音声状態変更検知
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='せつなBot - 簡易音声対話AI'
        )
        
        # 音声関連
        self.voice_client = None
        self.setsuna_chat = None
        self.voice_output = None
        self.voice_dialog_active = False
        self.simple_hotkey_voice = None
        self.hotkey_voice_active = False
        
        # コア機能初期化
        try:
            self.setsuna_chat = SetsunaChat()
            self.voice_output = VoiceOutput()
            print("✅ せつなBotコア機能初期化完了")
        except Exception as e:
            print(f"⚠️  コア機能初期化エラー: {e}")
            self.setsuna_chat = SetsunaChat()  # フォールバック版を使用
            self.voice_output = VoiceOutput()  # フォールバック版を使用
        
        # シンプルホットキー音声システム初期化
        if SimpleHotkeyVoice:
            try:
                self.simple_hotkey_voice = SimpleHotkeyVoice(self)
                print("✅ シンプルホットキー音声システム初期化完了")
            except Exception as e:
                print(f"⚠️ ホットキー音声システム初期化エラー: {e}")
                self.simple_hotkey_voice = None
        
        print("🤖 せつなBot Discord版（簡易）初期化中...")
    
    async def on_ready(self):
        """Bot起動完了時"""
        print(f"🎉 {self.user} としてDiscordに接続しました！")
        print(f"📊 参加サーバー数: {len(self.guilds)}")
        
        # 登録済みコマンド確認
        print("📝 登録済みコマンド:")
        for command_name in self.all_commands.keys():
            print(f"   !{command_name}")
        
        # アクティビティ設定
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="音声対話 | !help でヘルプ"
        )
        await self.change_presence(activity=activity)
        
        print("✅ せつなBot 起動完了 - コマンド待機中...")
    
    async def on_message(self, message):
        """メッセージ受信時"""
        # Bot自身のメッセージは無視
        if message.author == self.user:
            return
        
        # コマンドの場合は処理しない（process_commandsに任せる）
        if message.content.startswith('!'):
            await self.process_commands(message)
            return
        
        # せつなへの言及またはDMの場合、チャット応答
        if self.user in message.mentions or isinstance(message.channel, discord.DMChannel):
            await self.handle_chat_message(message)
        
        # コマンド処理（既にコマンドの場合は上で処理済み）
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
                response = f"こんにちは！{message.author.mention}さん。せつなです。"
            
            # テキスト応答送信
            await message.reply(response)
            
            # 音声対話モードが有効で、ボイスチャンネルに接続中の場合
            if (self.voice_dialog_active and 
                self.voice_client and 
                self.voice_client.is_connected()):
                
                # 音声応答（ローカル再生のみ）
                await self.play_voice_response_local(response)
            
        except Exception as e:
            print(f"❌ チャット応答エラー: {e}")
            await message.reply("申し訳ありません、エラーが発生しました。")
    
    async def handle_simple_voice_input(self, recognized_text):
        """シンプルホットキー音声入力処理"""
        try:
            if not self.voice_dialog_active or not self.voice_client:
                print("⚠️ 音声対話モードが無効です")
                return
            
            print(f"🎤 ホットキー音声入力: {recognized_text}")
            
            # 応答生成
            if self.setsuna_chat:
                response = self.setsuna_chat.get_response(recognized_text)
            else:
                response = f"音声入力を受け取りました: {recognized_text}"
            
            # テキストチャンネルに結果表示
            guild = self.voice_client.guild
            text_channel = discord.utils.get(guild.text_channels, name='general')
            if not text_channel:
                text_channel = guild.text_channels[0] if guild.text_channels else None
            
            if text_channel:
                embed = discord.Embed(
                    title="🎮 ホットキー音声入力",
                    color=0x00ff00
                )
                embed.add_field(name="認識内容", value=recognized_text, inline=False)
                embed.add_field(name="せつなの応答", value=response, inline=False)
                embed.add_field(name="システム", value="PyAudio不要・軽量実装", inline=True)
                
                await text_channel.send(embed=embed)
            
            # 音声応答
            await self.play_voice_response_local(response)
            
        except Exception as e:
            print(f"❌ ホットキー音声入力処理エラー: {e}")
    
    async def play_voice_response_local(self, text):
        """音声応答（ローカル再生）"""
        try:
            print(f"🔊 VOICEVOX音声合成: {text}")
            
            if self.voice_output:
                # 別スレッドで音声合成・再生
                def voice_worker():
                    self.voice_output.speak(text)
                
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, voice_worker)
                print("✅ ローカル音声再生完了")
            else:
                print(f"🔊 音声応答（テキスト）: {text}")
                
        except Exception as e:
            print(f"❌ ローカル音声再生エラー: {e}")


# Bot コマンド定義
bot = SetsunaDiscordBotSimple()

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
    
    await ctx.send(f"✅ {channel.name} に参加しました！")

@bot.command(name='leave')
async def leave_voice(ctx):
    """ボイスチャンネルから退出"""
    if bot.voice_client is None:
        await ctx.send("❌ ボイスチャンネルに参加していません。")
        return
    
    # ホットキー音声入力も停止
    if bot.hotkey_voice_active and bot.simple_hotkey_voice:
        bot.simple_hotkey_voice.stop_listening()
        bot.hotkey_voice_active = False
    
    await bot.voice_client.disconnect()
    bot.voice_client = None
    bot.voice_dialog_active = False
    await ctx.send("👋 ボイスチャンネルから退出しました。")

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
        bot.voice_dialog_active = True
        
        embed = discord.Embed(
            title="🎤 音声対話モード開始",
            description="テキストメッセージに音声で応答します（ローカル再生）",
            color=0x7289da
        )
        embed.add_field(
            name="使用方法",
            value="1. @せつな メッセージを送信\n2. せつながローカルで音声応答\n3. `!voice_stop` で終了",
            inline=False
        )
        embed.add_field(
            name="注意",
            value="音声はあなたのPC（Windowsホスト）で再生されます",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ 音声対話開始エラー: {e}")

@bot.command(name='voice_stop')
async def stop_voice_dialog(ctx):
    """音声対話モード停止"""
    if not bot.voice_dialog_active:
        await ctx.send("❌ 音声対話モードが開始されていません")
        return
    
    bot.voice_dialog_active = False
    
    # ホットキー音声入力も停止
    if bot.hotkey_voice_active and bot.simple_hotkey_voice:
        bot.simple_hotkey_voice.stop_listening()
        bot.hotkey_voice_active = False
    
    await ctx.send("🛑 **音声対話モード停止**")

@bot.command(name='say')
async def voice_say(ctx, *, message):
    """音声対話のテスト"""
    try:
        # 応答生成
        if bot.setsuna_chat:
            response = bot.setsuna_chat.get_response(message)
        else:
            response = f"{ctx.author.display_name}さん、こんにちは！"
        
        # 結果表示
        embed = discord.Embed(
            title="🎤 音声対話テスト",
            color=0x7289da
        )
        embed.add_field(name="発言者", value=ctx.author.display_name, inline=True)
        embed.add_field(name="メッセージ", value=message, inline=False)
        embed.add_field(name="せつなの応答", value=response, inline=False)
        
        await ctx.send(embed=embed)
        
        # 音声応答
        if bot.voice_dialog_active and bot.voice_client:
            await bot.play_voice_response_local(response)
        
    except Exception as e:
        await ctx.send(f"❌ 音声対話エラー: {e}")

@bot.command(name='hotkey_start')
async def start_hotkey_voice(ctx):
    """ホットキー音声入力開始"""
    if not bot.voice_dialog_active:
        await ctx.send("❌ 先に `!voice_start` で音声対話モードを開始してください")
        return
    
    if not bot.simple_hotkey_voice:
        await ctx.send("❌ ホットキー音声システムが利用できません")
        return
    
    if bot.hotkey_voice_active:
        await ctx.send("❌ 既にホットキー音声入力が開始されています")
        return
    
    try:
        success = bot.simple_hotkey_voice.start_listening()
        
        if success:
            bot.hotkey_voice_active = True
            
            embed = discord.Embed(
                title="🎮 ホットキー音声入力開始",
                description="Ctrl+Shift+Alt 同時押しで音声録音（PyAudio不要）",
                color=0x00ff00
            )
            embed.add_field(
                name="✨ 軽量実装",
                value="• PyAudio依存なし\n• Windows標準機能を使用\n• テスト音声でフォールバック\n• 簡単なホットキー検出",
                inline=False
            )
            embed.add_field(
                name="使用方法",
                value="1. Ctrl+Shift+Alt を同時に押す\n2. 押している間に話す\n3. キーを離すと認識・応答",
                inline=False
            )
            embed.add_field(
                name="注意",
                value="ホットキーはDiscordフォーカス外でも動作します",
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
    if not bot.hotkey_voice_active:
        await ctx.send("❌ ホットキー音声入力が開始されていません")
        return
    
    if bot.simple_hotkey_voice:
        bot.simple_hotkey_voice.stop_listening()
    
    bot.hotkey_voice_active = False
    await ctx.send("🛑 **ホットキー音声入力停止**")

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
    
    # 音声対話
    dialog_status = "✅ 有効" if bot.voice_dialog_active else "❌ 無効"
    embed.add_field(name="🗣️ 音声対話", value=dialog_status, inline=True)
    
    # ホットキー音声
    hotkey_status = "✅ 有効" if bot.hotkey_voice_active else "❌ 無効"
    embed.add_field(name="🎮 ホットキー音声", value=hotkey_status, inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='guide')
async def help_command(ctx):
    """ヘルプ表示"""
    embed = discord.Embed(
        title="🤖 せつなBot ヘルプ（簡易版）",
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
        value="`!voice_start` - 音声対話モード開始\n`!voice_stop` - 音声対話モード停止\n`!say <メッセージ>` - 音声応答テスト",
        inline=False
    )
    
    embed.add_field(
        name="🎮 ホットキー音声入力",
        value="`!hotkey_start` - ホットキー音声入力開始\n`!hotkey_stop` - ホットキー音声入力停止\nCtrl+Shift+Alt - 音声録音",
        inline=False
    )
    
    embed.add_field(
        name="💬 テキストチャット",
        value="@せつな メッセージ - テキストで対話\nDM - ダイレクトメッセージでも対話可能",
        inline=False
    )
    
    embed.add_field(
        name="🗣️ 完全な音声対話の使い方",
        value="1. `!join` でボイスチャンネル参加\n2. `!voice_start` で音声対話開始\n3. `!hotkey_start` でホットキー音声入力開始\n4. Ctrl+Shift+Alt で音声入力\n5. 音声応答がローカル（Windows）で再生",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Bot起動
if __name__ == "__main__":
    print("🚀 せつなBot Discord版（簡易）起動中...")
    
    # Discord Bot Token確認
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token or token == "your_discord_bot_token_here":
        print("❌ DISCORD_BOT_TOKENが設定されていません")
        print("💡 .env ファイルでDiscord Bot Tokenを設定してください")
        exit(1)
    
    print("🔗 Discord接続試行中...")
    
    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        print("❌ Discord Bot Tokenが無効です")
    except KeyboardInterrupt:
        print("\n🛑 Bot終了中...")
        if bot.simple_hotkey_voice and bot.hotkey_voice_active:
            bot.simple_hotkey_voice.stop_listening()
        print("✅ Bot を正常終了しました")
    except Exception as e:
        print(f"❌ Bot起動エラー: {e}")
    finally:
        print("👋 せつなBot終了")