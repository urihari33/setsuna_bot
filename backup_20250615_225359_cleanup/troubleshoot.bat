@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: ===================================================
::       🔍 せつなBot トラブルシューティング
:: ===================================================

cd /d "%~dp0"
title せつなBot トラブルシューティング

echo.
echo =========================================
echo   🔍 せつなBot トラブルシューティング
echo =========================================
echo 📅 %date% %time%
echo.

:: ログファイル作成
set LOG_FILE=troubleshoot_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%.log
echo 🗃️  診断結果: %LOG_FILE% に出力中...
echo.

:: 診断開始
(
echo ============ 診断開始 ============
echo 日時: %date% %time%
echo 作業ディレクトリ: %CD%
echo.

echo ============ システム情報 ============
systeminfo | findstr /C:"OS Name" /C:"OS Version" /C:"System Type"
echo.

echo ============ Python 環境 ============
python --version 2>&1
echo.
echo Python パス:
where python 2>&1
echo.

echo ============ 仮想環境確認 ============
if exist "setsuna_win_env" (
    echo ✅ 仮想環境ディレクトリ存在
    if exist "setsuna_win_env\Scripts\activate.bat" (
        echo ✅ アクティベートスクリプト存在
        call setsuna_win_env\Scripts\activate
        echo 仮想環境 Python:
        python --version 2>&1
        echo.
        echo インストール済みパッケージ:
        python -m pip list 2>&1
    ) else (
        echo ❌ アクティベートスクリプト不在
    )
) else (
    echo ❌ 仮想環境ディレクトリ不在
)
echo.

echo ============ 設定ファイル確認 ============
if exist ".env" (
    echo ✅ .env ファイル存在
    echo ファイルサイズ:
    for %%F in (.env) do echo %%~zF bytes
    echo.
    echo .env 内容 (機密情報はマスク済み):
    for /f "tokens=1,* delims==" %%a in (.env) do (
        if /i "%%a"=="OPENAI_API_KEY" (
            echo OPENAI_API_KEY=****masked****
        ) else if /i "%%a"=="DISCORD_BOT_TOKEN" (
            echo DISCORD_BOT_TOKEN=****masked****
        ) else (
            echo %%a=%%b
        )
    )
) else (
    echo ❌ .env ファイル不在
)
echo.

echo ============ 重要ファイル確認 ============
if exist "setsuna_discord_bot.py" (
    echo ✅ setsuna_discord_bot.py 存在
) else (
    echo ❌ setsuna_discord_bot.py 不在
)

if exist "core\voice_output.py" (
    echo ✅ voice_output.py 存在
) else (
    echo ❌ voice_output.py 不在
)

if exist "hotkey_voice_input.py" (
    echo ✅ hotkey_voice_input.py 存在
) else (
    echo ❌ hotkey_voice_input.py 不在
)
echo.

echo ============ ネットワーク確認 ============
echo Discord API 接続テスト:
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://discord.com/api/v10/gateway' -UseBasicParsing -TimeoutSec 5; Write-Host '✅ Discord API 接続OK' } catch { Write-Host '❌ Discord API 接続失敗:' $_.Exception.Message }"

echo.
echo OpenAI API 接続テスト:
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://api.openai.com/' -UseBasicParsing -TimeoutSec 5; Write-Host '✅ OpenAI API 接続OK' } catch { Write-Host '❌ OpenAI API 接続失敗:' $_.Exception.Message }"

echo.
echo VOICEVOX 接続テスト:
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:50021/version' -UseBasicParsing -TimeoutSec 3; Write-Host '✅ VOICEVOX 接続OK -' $response.Content } catch { Write-Host '❌ VOICEVOX 接続失敗:' $_.Exception.Message }"
echo.

echo ============ 音声デバイス確認 ============
powershell -Command "Get-WmiObject -Class Win32_SoundDevice | Select-Object Name, Status"
echo.

echo ============ プロセス確認 ============
echo Python プロセス:
tasklist | findstr python.exe
echo.
echo VOICEVOX プロセス:
tasklist | findstr VOICEVOX
echo.

echo ============ 診断完了 ============
echo 診断終了時刻: %date% %time%
) > %LOG_FILE% 2>&1

:: 画面表示
echo 🔍 診断実行中...
echo.

:: 重要な項目を画面にも表示
echo 📊 重要項目チェック:
echo.

echo 🐍 Python 環境:
python --version
if errorlevel 1 (
    echo    ❌ Python が見つかりません
) else (
    echo    ✅ Python 利用可能
)

echo.
echo 📦 仮想環境:
if exist "setsuna_win_env" (
    echo    ✅ 仮想環境存在
) else (
    echo    ❌ 仮想環境不在 - setup_environment.bat を実行してください
)

echo.
echo 🔑 設定ファイル:
if exist ".env" (
    echo    ✅ .env ファイル存在
    findstr /C:"your_" .env > nul
    if errorlevel 1 (
        echo    ✅ API キーが設定されています
    ) else (
        echo    ⚠️  API キーが未設定の可能性があります
    )
) else (
    echo    ❌ .env ファイル不在
)

echo.
echo 🔊 VOICEVOX:
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:50021/version' -UseBasicParsing -TimeoutSec 3; Write-Host '    ✅ VOICEVOX 起動中' } catch { Write-Host '    ❌ VOICEVOX 未起動または接続不可' }"

echo.
echo =========================================
echo    📋 診断結果サマリー
echo =========================================
echo.
echo 📁 詳細ログ: %LOG_FILE%
echo.

:: 推奨アクション
echo 💡 推奨アクション:
if not exist "setsuna_win_env" (
    echo • setup_environment.bat を実行して環境をセットアップ
)
if not exist ".env" (
    echo • .env ファイルで API キーを設定
)
echo • VOICEVOX を起動 (http://localhost:50021)
echo • start_setsuna.bat でボット起動
echo.

echo 🆘 サポートが必要な場合:
echo • %LOG_FILE% ファイルを確認
echo • GitHub Issues に問題を報告
echo.

pause