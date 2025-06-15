#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot シンプルテスト版
デバッグ用の最小限Discord Bot
"""

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# Bot設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Bot起動完了時"""
    print(f"🎉 {bot.user} としてDiscordに接続しました！")
    print(f"📊 参加サーバー数: {len(bot.guilds)}")
    print(f"🔑 Bot ID: {bot.user.id}")
    
    for guild in bot.guilds:
        print(f"   📍 {guild.name} (ID: {guild.id})")
    
    print("✅ テストBot 起動完了")

@bot.command(name='test')
async def test_command(ctx):
    """テストコマンド"""
    await ctx.send("🎉 せつなBot テスト版が正常に動作しています！")
    print(f"✅ テストコマンド実行: {ctx.author}")

@bot.command(name='ping')
async def ping(ctx):
    """応答テスト"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! 応答時間: {latency}ms")

if __name__ == "__main__":
    print("🚀 せつなBot テスト版 起動中...")
    
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
        print("\n✅ テストBot を正常終了しました")
    except Exception as e:
        print(f"❌ Bot起動エラー: {e}")
        import traceback
        traceback.print_exc()
        input("Enterキーで終了...")
    finally:
        print("👋 テストBot終了")