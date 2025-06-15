@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: ===================================================
::           🤖 せつなBot 起動スクリプト
:: ===================================================

cd /d "%~dp0"
title せつなBot Discord版 - Windows

echo.
echo =========================================
echo    🤖 せつなBot Discord版 (Windows)
echo =========================================
echo 📅 %date% %time%
echo 📁 作業ディレクトリ: %CD%
echo.

:: 環境チェック
echo 🔍 環境チェック中...
if not exist "setsuna_win_env" (
    echo ❌ 仮想環境が見つかりません
    echo 💡 setup_environment.bat を先に実行してください
    pause
    exit /b 1
)

if not exist ".env" (
    echo ❌ .env ファイルが見つかりません
    echo 💡 Discord Bot Token を設定してください
    pause
    exit /b 1
)

:: VOICEVOX確認
echo 🔊 VOICEVOX接続確認中...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:50021/version' -UseBasicParsing -TimeoutSec 3; Write-Host '✅ VOICEVOX接続OK' } catch { Write-Host '⚠️  VOICEVOX未起動または未接続' }"

:: 仮想環境アクティベート
echo 🔧 仮想環境アクティベート中...
call setsuna_win_env\Scripts\activate
if errorlevel 1 (
    echo ❌ 仮想環境のアクティベートに失敗
    pause
    exit /b 1
)

:: 環境変数設定
set PYTHONIOENCODING=utf-8
set PYTHONPATH=%CD%

echo.
echo ✅ 環境準備完了
echo.
echo 🎤 利用可能な機能:
echo    • リアルタイム音声認識 (Ctrl+Shift+Alt)
echo    • VOICEVOX音声合成
echo    • Discord音声チャット
echo.
echo 🚀 せつなBot起動中...
echo.
echo ================================================
echo  Discord でコマンドを試してください:
echo  !join          - ボイスチャンネル参加
echo  !voice_start   - 音声対話モード開始  
echo  !hotkey_start  - ホットキー音声入力開始
echo  !guide         - 全コマンド表示
echo ================================================
echo.

echo 🤖 起動オプションを選択してください:
echo 1. 完全版 (音声機能付き)
echo 2. テスト版 (基本機能のみ)
echo.
set /p mode="選択 (1 または 2): "

if "%mode%"=="2" (
    echo 🧪 テスト版で起動中...
    python test_bot_simple.py
) else (
    echo 🎤 完全版で起動中...
    python setsuna_discord_bot.py
)
set exit_code=%errorlevel%

echo.
if %exit_code% equ 0 (
    echo ✅ せつなBot が正常に終了しました
) else (
    echo ❌ せつなBot がエラーで終了しました (終了コード: %exit_code%)
    echo.
    echo 🔍 トラブルシューティング:
    echo 1. VOICEVOX が起動しているか確認
    echo 2. Discord Bot Token が正しく設定されているか確認
    echo 3. インターネット接続を確認
    echo 4. troubleshoot.bat を実行してください
)

echo.
pause