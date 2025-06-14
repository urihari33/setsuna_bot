@echo off
echo VOICEVOX WSL2対応起動スクリプト
echo ===============================

REM VOICEVOXのインストールパスを自動検出
set VOICEVOX_PATH="%LOCALAPPDATA%\Programs\VOICEVOX"
set ENGINE_PATH="%LOCALAPPDATA%\Programs\VOICEVOX\vv-engine"

REM VOICEVOXエンジンをWSL2対応モードで起動
echo VOICEVOXエンジンを起動中... (WSL2対応)
echo ホスト: 0.0.0.0:50021
echo.

if exist %ENGINE_PATH%\run.exe (
    echo エンジンのみ起動モード
    cd /d %ENGINE_PATH%
    start "VOICEVOX Engine" run.exe --host 0.0.0.0 --port 50021
) else if exist %VOICEVOX_PATH%\VOICEVOX.exe (
    echo VOICEVOX全体起動モード
    cd /d %VOICEVOX_PATH%
    start "VOICEVOX" VOICEVOX.exe --host 0.0.0.0 --port 50021
) else (
    echo エラー: VOICEVOXが見つかりません
    echo 以下のパスにVOICEVOXがインストールされているか確認してください:
    echo %VOICEVOX_PATH%
    pause
    exit /b 1
)

echo WSL2対応でVOICEVOXを起動しました
echo ポート50021で外部接続を受け付けています
echo.
echo 起動完了まで10-15秒お待ちください...
timeout /t 15 /nobreak

echo 接続テスト実行中...
curl -s http://localhost:50021/version > nul
if %errorlevel% == 0 (
    echo ✅ VOICEVOX正常起動
) else (
    echo ⚠️  起動確認中... もう少しお待ちください
)

pause