#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot Discord Bot版デモ
簡単なDiscord Bot実装例
"""

import discord
from discord.ext import commands
import asyncio
import sys
import os

# せつなBotコアモジュールのパス追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Discord Bot設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class SetsunaBotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conversation_count = 0
        self.voice_settings = {
            'speed': 1.2,
            'pitch': 0.0,
            'intonation': 1.0
        }
    
    @commands.command(name='chat')
    async def chat_command(self, ctx, *, message):
        """チャット機能"""
        response = self.generate_response(message)
        self.conversation_count += 1
        
        embed = discord.Embed(
            title="🤖 せつなBot",
            description=response,
            color=0x00ff88
        )
        embed.set_footer(text=f"対話回数: {self.conversation_count}回")
        
        await ctx.reply(embed=embed)
    
    @commands.command(name='status')
    async def status_command(self, ctx):
        """システム状態表示"""
        embed = discord.Embed(
            title="📊 システム状態",
            color=0x0099ff
        )
        embed.add_field(
            name="対話回数", 
            value=f"{self.conversation_count}回", 
            inline=True
        )
        embed.add_field(
            name="話速", 
            value=f"{self.voice_settings['speed']:.1f}x", 
            inline=True
        )
        embed.add_field(
            name="音程", 
            value=f"{self.voice_settings['pitch']:.2f}", 
            inline=True
        )
        embed.add_field(
            name="抑揚", 
            value=f"{self.voice_settings['intonation']:.1f}", 
            inline=True
        )
        
        await ctx.reply(embed=embed)
    
    @commands.command(name='voice')
    async def voice_settings(self, ctx, setting: str = None, value: float = None):
        """音声設定変更"""
        if setting is None:
            # 設定確認
            embed = discord.Embed(
                title="🎛️ 音声設定",
                color=0xff9900
            )
            embed.add_field(name="話速", value=f"{self.voice_settings['speed']:.1f}x", inline=True)
            embed.add_field(name="音程", value=f"{self.voice_settings['pitch']:.2f}", inline=True)
            embed.add_field(name="抑揚", value=f"{self.voice_settings['intonation']:.1f}", inline=True)
            embed.set_footer(text="使用例: !voice speed 1.5")
            
            await ctx.reply(embed=embed)
            return
        
        # 設定変更
        if setting.lower() == 'speed' and 0.5 <= value <= 2.0:
            self.voice_settings['speed'] = value
            await ctx.reply(f"✅ 話速を{value:.1f}xに設定しました")
        elif setting.lower() == 'pitch' and -0.15 <= value <= 0.15:
            self.voice_settings['pitch'] = value
            await ctx.reply(f"✅ 音程を{value:.2f}に設定しました")
        elif setting.lower() == 'intonation' and 0.5 <= value <= 2.0:
            self.voice_settings['intonation'] = value
            await ctx.reply(f"✅ 抑揚を{value:.1f}に設定しました")
        else:
            await ctx.reply("❌ 無効な設定です。`!voice`で設定確認")
    
    @commands.command(name='test')
    async def voice_test(self, ctx):
        """音声テスト"""
        embed = discord.Embed(
            title="🔊 音声テスト",
            description="音声テストを実行します...",
            color=0xff6600
        )
        embed.add_field(name="話速", value=f"{self.voice_settings['speed']:.1f}x", inline=True)
        embed.add_field(name="音程", value=f"{self.voice_settings['pitch']:.2f}", inline=True)
        embed.add_field(name="抑揚", value=f"{self.voice_settings['intonation']:.1f}", inline=True)
        
        message = await ctx.reply(embed=embed)
        
        # テストシミュレーション
        await asyncio.sleep(2)
        
        embed.description = "✅ 音声テスト完了！"
        embed.color = 0x00ff00
        await message.edit(embed=embed)
    
    def generate_response(self, user_input):
        """簡易応答生成"""
        responses = {
            "こんにちは": "こんにちは！元気ですか？",
            "おはよう": "おはようございます！今日も良い一日にしましょう！",
            "ありがとう": "どういたしまして！いつでもお手伝いします。",
            "さようなら": "また今度お話ししましょうね！",
            "元気": "それは良かったです！私も元気です。",
            "疲れた": "お疲れ様です。少し休憩してくださいね。",
        }
        
        for keyword, response in responses.items():
            if keyword in user_input:
                return response
        
        return f"「{user_input}」についてお話しするのは楽しいですね！他に何かありますか？"

@bot.event
async def on_ready():
    print(f'🤖 {bot.user} としてログインしました！')
    print(f'サーバー数: {len(bot.guilds)}')
    print('--- 利用可能なコマンド ---')
    print('!chat <メッセージ> - チャット')
    print('!status - システム状態')
    print('!voice [設定] [値] - 音声設定')
    print('!test - 音声テスト')
    print('!help - ヘルプ表示')

@bot.event
async def on_message(message):
    # Bot自身のメッセージは無視
    if message.author == bot.user:
        return
    
    # メンション応答
    if bot.user.mentioned_in(message):
        content = message.content.replace(f'<@{bot.user.id}>', '').strip()
        if content:
            cog = bot.get_cog('SetsunaBotCog')
            response = cog.generate_response(content)
            cog.conversation_count += 1
            
            embed = discord.Embed(
                title="🤖 せつなBot",
                description=response,
                color=0x00ff88
            )
            await message.reply(embed=embed)
    
    # コマンド処理
    await bot.process_commands(message)

async def main():
    """メイン関数"""
    # Cogを追加
    await bot.add_cog(SetsunaBotCog(bot))
    
    # Botトークンの確認
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ DISCORD_BOT_TOKENが設定されていません")
        print("以下の手順でDiscord Botを作成してください:")
        print("1. https://discord.com/developers/applications にアクセス")
        print("2. New Application → Bot → Token をコピー")
        print("3. export DISCORD_BOT_TOKEN='your_token_here'")
        return
    
    try:
        await bot.start(token)
    except discord.LoginFailure:
        print("❌ Discord Botトークンが無効です")
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    print("🚀 せつなBot Discord版起動中...")
    print("Ctrl+C で終了")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 せつなBot Discord版を終了します")