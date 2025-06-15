@echo off
chcp 65001 > nul
cd /d "%~dp0"
title せつなBot シンプルテスト

echo.
echo ========================================
echo    🧪 せつなBot シンプルテスト
echo ========================================
echo.

:: 環境チェック
if not exist "setsuna_win_env" (
    echo ❌ 仮想環境が見つかりません
    echo 💡 setup_environment.bat を先に実行してください
    pause
    exit /b 1
)

if not exist ".env" (
    echo ❌ .env ファイルが見つかりません
    pause
    exit /b 1
)

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

echo 🚀 シンプルテストBot起動中...
echo.
echo Discord で以下のコマンドをテストしてください:
echo   !test  - 動作確認
echo   !ping  - 応答時間確認
echo.

:: Bot起動
python test_bot_simple.py

echo.
pause