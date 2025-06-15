@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: ===================================================
::        🔧 せつなBot 環境セットアップ
:: ===================================================

cd /d "%~dp0"
title せつなBot 環境セットアップ

echo.
echo =========================================
echo   🔧 せつなBot 環境セットアップ
echo =========================================
echo.

:: Python確認
echo 🐍 Python バージョン確認...
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python が見つかりません
    echo 💡 https://python.org から Python 3.9+ をインストールしてください
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version') do set PYTHON_VERSION=%%v
echo ✅ Python %PYTHON_VERSION% が利用可能

:: 仮想環境作成
echo.
echo 📦 仮想環境作成中...
if exist "setsuna_win_env" (
    echo ⚠️  既存の仮想環境を削除中...
    rmdir /s /q setsuna_win_env
)

python -m venv setsuna_win_env
if errorlevel 1 (
    echo ❌ 仮想環境作成に失敗
    pause
    exit /b 1
)
echo ✅ 仮想環境作成完了

:: 仮想環境アクティベート
echo.
echo 🔧 仮想環境アクティベート中...
call setsuna_win_env\Scripts\activate
if errorlevel 1 (
    echo ❌ 仮想環境アクティベートに失敗
    pause
    exit /b 1
)

:: pipアップグレード
echo.
echo 🔄 pip アップグレード中...
python -m pip install --upgrade pip > install.log 2>&1

:: 必須ライブラリインストール
echo.
echo 📚 ライブラリインストール中...
echo    (詳細ログ: install.log に出力中...)

echo 📦 基本ライブラリ...
python -m pip install discord.py openai requests pygame python-dotenv >> install.log 2>&1
if errorlevel 1 (
    echo ❌ 基本ライブラリインストール失敗
    echo 詳細: install.log を確認してください
    pause
    exit /b 1
)

echo 🎤 音声関連ライブラリ...
python -m pip install SpeechRecognition pydub >> install.log 2>&1

echo 🎮 ホットキーライブラリ...
python -m pip install pynput >> install.log 2>&1

echo 🔊 音声録音ライブラリ...
python -m pip install pyaudio >> install.log 2>&1
if errorlevel 1 (
    echo ⚠️  PyAudio インストールに失敗しました
    echo 💡 手動でインストールが必要な場合があります
    echo 💡 それでも基本的な音声機能は動作します
) else (
    echo ✅ PyAudio インストール成功 - 完全な音声機能が利用可能
)

:: .env ファイル確認
echo.
echo 🔑 設定ファイル確認...
if not exist ".env" (
    echo 📝 .env ファイルを作成中...
    echo # OpenAI API設定 > .env
    echo OPENAI_API_KEY=your_openai_api_key_here >> .env
    echo. >> .env
    echo # Discord Bot設定 >> .env
    echo DISCORD_BOT_TOKEN=your_discord_bot_token_here >> .env
    echo. >> .env
    echo # VOICEVOX設定 >> .env
    echo VOICEVOX_URL=http://localhost:50021 >> .env
    
    echo ⚠️  .env ファイルを作成しました
    echo 💡 Discord Bot Token と OpenAI API Key を設定してください
    notepad .env
) else (
    echo ✅ .env ファイルが存在します
)

:: インストール完了
echo.
echo =========================================
echo    ✅ セットアップ完了
echo =========================================
echo.
echo 📋 次のステップ:
echo 1. .env ファイルに API キーを設定
echo 2. VOICEVOX を起動
echo 3. start_setsuna.bat でボット起動
echo.
echo 📁 作成されたファイル:
echo • setsuna_win_env\     - Python仮想環境
echo • .env                 - 設定ファイル
echo • install.log          - インストールログ
echo.

:: ライブラリ一覧表示
echo 📦 インストール済みライブラリ:
python -m pip list | findstr -i "discord openai pyaudio pynput"

echo.
echo 🎉 セットアップが完了しました！
pause