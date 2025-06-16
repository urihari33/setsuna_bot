@echo off
chcp 65001 > nul
echo ====================================
echo       せつなBot 自動起動版
echo ====================================
echo.
echo 🤖 せつなBot (自動起動版) を開始します...
echo.
echo ✨ 機能:
echo    - 起動と同時にDiscordボイスチャンネル参加
echo    - 自動でホットキーモード開始
echo    - Ctrl+Shift+Alt で音声入力
echo.
echo 📋 必要な設定:
echo    - .env ファイルにDISCORD_BOT_TOKEN設定済み
echo    - OpenAI API Key設定済み
echo    - VOICEVOX起動済み (Windows側)
echo.
echo 🔄 起動中...
echo.

REM 仮想環境の確認・作成
if not exist "setsuna_win_env\" (
    echo 🔧 Windows用仮想環境を作成中...
    python -m venv setsuna_win_env
    if errorlevel 1 (
        echo ❌ 仮想環境の作成に失敗しました
        pause
        exit /b 1
    )
)

echo 📦 仮想環境をアクティベート中...
call setsuna_win_env\Scripts\activate.bat

REM 必要なパッケージのインストール確認
echo 📦 必要なパッケージを確認中...
pip install --quiet discord.py openai python-dotenv SpeechRecognition pynput pygame requests

REM 環境変数チェック
if not exist ".env" (
    echo ❌ .env ファイルが見つかりません
    echo.
    echo 📝 .env ファイルを作成して以下を設定してください:
    echo    DISCORD_BOT_TOKEN=your_discord_bot_token_here
    echo    OPENAI_API_KEY=your_openai_api_key_here
    echo.
    pause
    exit /b 1
)

echo.
echo 🚀 せつなBot自動起動版を実行中...
echo.
echo 💡 使用方法:
echo    1. 自動でDiscordボイスチャンネルに参加します
echo    2. Ctrl+Shift+Alt を押しながら話しかけてください
echo    3. 音声がWindows環境で再生されます
echo    4. Ctrl+C で終了
echo.
echo ----------------------------------------

python setsuna_auto_discord.py

echo.
echo ✅ せつなBot終了しました
echo.
pause