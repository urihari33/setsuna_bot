@echo off
chcp 65001
cd /d D:\setsuna_bot
call setsuna_win_env\Scripts\activate
set PYTHONIOENCODING=utf-8
echo.
echo =========================================
echo    🤖 せつなBot Discord版 (Windows)
echo =========================================
echo.
echo 🔊 VOICEVOX が起動していることを確認してください
echo 🎤 真の音声入力機能が利用可能です
echo.
echo 起動中...
echo.
python setsuna_discord_bot.py
pause