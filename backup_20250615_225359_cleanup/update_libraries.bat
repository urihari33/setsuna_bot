@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: ===================================================
::        🔄 せつなBot ライブラリアップデート
:: ===================================================

cd /d "%~dp0"
title せつなBot ライブラリアップデート

echo.
echo =========================================
echo   🔄 せつなBot ライブラリアップデート  
echo =========================================
echo 📅 %date% %time%
echo.

:: 仮想環境確認
if not exist "setsuna_win_env" (
    echo ❌ 仮想環境が見つかりません
    echo 💡 setup_environment.bat を先に実行してください
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

:: 現在のバージョン確認
echo.
echo 📋 現在インストール済みライブラリ:
echo ============================================
python -m pip list | findstr -i "discord openai pyaudio pynput pygame requests speechrecognition pydub"
echo ============================================
echo.

:: アップデート確認
echo 🔍 アップデート可能なパッケージ確認中...
python -m pip list --outdated > outdated.tmp 2>&1

if exist outdated.tmp (
    for /f %%i in ('find /c /v "" outdated.tmp') do set line_count=%%i
    if !line_count! gtr 2 (
        echo.
        echo 📦 アップデート可能なパッケージ:
        type outdated.tmp
        echo.
        
        set /p choice="🔄 これらのパッケージをアップデートしますか? (y/n): "
        if /i "!choice!"=="y" (
            echo.
            echo 🔄 パッケージアップデート実行中...
            
            :: 重要なパッケージを個別にアップデート
            echo 📦 discord.py アップデート...
            python -m pip install --upgrade discord.py
            
            echo 📦 openai アップデート...  
            python -m pip install --upgrade openai
            
            echo 📦 その他のパッケージアップデート...
            python -m pip install --upgrade requests pygame python-dotenv SpeechRecognition pydub pynput
            
            echo 📦 pip 自体をアップデート...
            python -m pip install --upgrade pip
            
            echo.
            echo ✅ アップデート完了
        ) else (
            echo.
            echo ⏭️  アップデートをスキップしました
        )
    ) else (
        echo ✅ 全てのパッケージが最新版です
    )
    del outdated.tmp
)

:: 最終バージョン確認
echo.
echo 📋 アップデート後のライブラリバージョン:
echo ============================================
python -m pip list | findstr -i "discord openai pyaudio pynput pygame requests speechrecognition pydub"
echo ============================================
echo.

:: PyAudio 特別対応
echo 🎤 PyAudio 状態確認...
python -c "import pyaudio; print('✅ PyAudio 正常動作')" 2>nul
if errorlevel 1 (
    echo ⚠️  PyAudio に問題があります
    echo 💡 再インストールを試行中...
    python -m pip uninstall pyaudio -y
    python -m pip install pyaudio
    
    python -c "import pyaudio; print('✅ PyAudio 再インストール成功')" 2>nul
    if errorlevel 1 (
        echo ❌ PyAudio 再インストール失敗
        echo 💡 手動インストールが必要な場合があります
        echo 💡 https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
    )
)

:: 依存関係チェック
echo.
echo 🔍 依存関係チェック中...
python -m pip check
if errorlevel 1 (
    echo ⚠️  依存関係に問題があります
    echo 💡 pip install --force-reinstall を検討してください
) else (
    echo ✅ 依存関係に問題なし
)

:: キャッシュクリア
echo.
echo 🧹 pip キャッシュクリア...
python -m pip cache purge

echo.
echo =========================================
echo    ✅ ライブラリアップデート完了
echo =========================================
echo.
echo 💡 次の手順:
echo 1. start_setsuna.bat でボット起動
echo 2. 動作確認を実施
echo 3. 問題があれば troubleshoot.bat を実行
echo.

pause