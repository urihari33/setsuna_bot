@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: ===================================================
::           🤖 せつなBot ランチャー
:: ===================================================

cd /d "%~dp0"
title せつなBot ランチャー

:main_menu
cls
echo.
echo ███████╗███████╗████████╗███████╗██╗   ██╗███╗   ██╗ █████╗ 
echo ██╔════╝██╔════╝╚══██╔══╝██╔════╝██║   ██║████╗  ██║██╔══██╗
echo ███████╗█████╗     ██║   ███████╗██║   ██║██╔██╗ ██║███████║
echo ╚════██║██╔══╝     ██║   ╚════██║██║   ██║██║╚██╗██║██╔══██║
echo ███████║███████╗   ██║   ███████║╚██████╔╝██║ ╚████║██║  ██║
echo ╚══════╝╚══════╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝
echo.
echo =========================================
echo        🤖 せつなBot ランチャー
echo =========================================
echo 📅 %date% %time%
echo 📁 %CD%
echo.

:: 環境状態チェック
call :check_environment

echo.
echo 📋 メニュー:
echo.
echo  1. 🚀 せつなBot を起動
echo  2. 🔧 初回環境セットアップ
echo  3. 🔄 ライブラリアップデート
echo  4. 🔍 トラブルシューティング
echo  5. 📝 設定ファイル編集
echo  6. 🔊 VOICEVOX 起動
echo  7. 📖 ヘルプ・使い方
echo  8. 🚪 終了
echo.

set /p choice="選択してください (1-8): "

if "%choice%"=="1" goto start_bot
if "%choice%"=="2" goto setup_env
if "%choice%"=="3" goto update_libs
if "%choice%"=="4" goto troubleshoot
if "%choice%"=="5" goto edit_config
if "%choice%"=="6" goto start_voicevox
if "%choice%"=="7" goto show_help
if "%choice%"=="8" goto exit_launcher

echo ❌ 無効な選択です
timeout /t 2 > nul
goto main_menu

:start_bot
echo.
echo 🚀 せつなBot を起動しています...
call start_setsuna.bat
pause
goto main_menu

:setup_env
echo.
echo 🔧 環境セットアップを実行しています...
call setup_environment.bat
pause
goto main_menu

:update_libs
echo.
echo 🔄 ライブラリアップデートを実行しています...
call update_libraries.bat
pause
goto main_menu

:troubleshoot
echo.
echo 🔍 トラブルシューティングを実行しています...
call troubleshoot.bat
pause
goto main_menu

:edit_config
echo.
echo 📝 設定ファイルを編集します...
if exist ".env" (
    notepad .env
) else (
    echo ❌ .env ファイルが見つかりません
    echo 💡 まず「初回環境セットアップ」を実行してください
    pause
)
goto main_menu

:start_voicevox
echo.
echo 🔊 VOICEVOX を起動しています...
echo 💡 VOICEVOX がインストールされている場合のみ動作します
start "" "VOICEVOX.exe" 2>nul
if errorlevel 1 (
    echo ❌ VOICEVOX.exe が見つかりません
    echo 💡 VOICEVOX をダウンロード・インストールしてください
    echo 💡 https://voicevox.hiroshiba.jp/
    start "" "https://voicevox.hiroshiba.jp/"
)
pause
goto main_menu

:show_help
cls
echo.
echo =========================================
echo        📖 せつなBot ヘルプ
echo =========================================
echo.
echo 🎯 せつなBot について:
echo Discord上で音声対話ができるAIボットです
echo VOICEVOX音声合成とOpenAI GPTを使用
echo.
echo 📋 セットアップ手順:
echo 1. 「初回環境セットアップ」を実行
echo 2. .env ファイルにAPI キーを設定
echo    - DISCORD_BOT_TOKEN: Discord Bot Token
echo    - OPENAI_API_KEY: OpenAI API Key
echo 3. VOICEVOX をダウンロード・起動
echo 4. 「せつなBot を起動」で実行
echo.
echo 🎤 Windows版の特徴:
echo • リアルタイム音声認識 (Ctrl+Shift+Alt)
echo • マイクからの音声録音
echo • VOICEVOX音声合成
echo • Discord音声チャット統合
echo.
echo 💬 Discord コマンド:
echo !join          - ボイスチャンネル参加
echo !voice_start   - 音声対話モード開始
echo !hotkey_start  - ホットキー音声入力開始
echo !guide         - 全コマンド表示
echo.
echo 🔗 関連リンク:
echo • Discord Developer Portal: https://discord.com/developers/applications
echo • OpenAI API: https://platform.openai.com/api-keys
echo • VOICEVOX: https://voicevox.hiroshiba.jp/
echo.
echo 🆘 サポート:
echo 問題が発生した場合は「トラブルシューティング」を実行
echo.
pause
goto main_menu

:check_environment
:: 環境状態をチェックして表示
echo 🔍 環境状態:
if exist "setsuna_win_env" (
    echo    ✅ Python仮想環境
) else (
    echo    ❌ Python仮想環境 - セットアップが必要
)

if exist ".env" (
    findstr /C:"your_" .env > nul 2>&1
    if errorlevel 1 (
        echo    ✅ 設定ファイル - API キー設定済み
    ) else (
        echo    ⚠️  設定ファイル - API キー要設定
    )
) else (
    echo    ❌ 設定ファイル - 作成が必要
)

powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:50021/version' -UseBasicParsing -TimeoutSec 2 | Out-Null; Write-Host '    ✅ VOICEVOX 接続OK' } catch { Write-Host '    ❌ VOICEVOX 未起動' }" 2>nul
goto :eof

:exit_launcher
echo.
echo 👋 せつなBot ランチャーを終了します
echo 🎤 音声対話をお楽しみください！
timeout /t 2 > nul
exit