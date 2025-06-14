@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   片無せつな - ホットキーモード起動
echo ========================================

REM VOICEVOXサーバーの起動チェック
echo [1/4] VOICEVOX エンジンを確認中...
tasklist | findstr /i voicevox_engine.exe > nul
if errorlevel 1 (
    echo VOICEVOX エンジンが見つかりません。起動を試みます...
    
    REM 複数の可能なVOICEVOXパスを試行
    set "voicevox_found=0"
    
    REM パス1: ユーザーディレクトリ
    if exist "C:\Users\%USERNAME%\AppData\Local\Programs\VOICEVOX\VOICEVOX.exe" (
        echo VOICEVOX を起動中... [ユーザーディレクトリ]
        start "" "C:\Users\%USERNAME%\AppData\Local\Programs\VOICEVOX\VOICEVOX.exe" --use_gpu --load_all_models
        set "voicevox_found=1"
    )
    
    REM パス2: Program Files
    if !voicevox_found!==0 if exist "C:\Program Files\VOICEVOX\VOICEVOX.exe" (
        echo VOICEVOX を起動中... [Program Files]
        start "" "C:\Program Files\VOICEVOX\VOICEVOX.exe" --use_gpu --load_all_models
        set "voicevox_found=1"
    )
    
    REM パス3: Program Files (x86)
    if !voicevox_found!==0 if exist "C:\Program Files (x86)\VOICEVOX\VOICEVOX.exe" (
        echo VOICEVOX を起動中... [Program Files x86]
        start "" "C:\Program Files (x86)\VOICEVOX\VOICEVOX.exe" --use_gpu --load_all_models
        set "voicevox_found=1"
    )
    
    if !voicevox_found!==0 (
        echo [警告] VOICEVOX が見つかりませんでした。手動で起動してください。
        echo 一般的な場所:
        echo - %%USERPROFILE%%\AppData\Local\Programs\VOICEVOX\
        echo - C:\Program Files\VOICEVOX\
        echo 5秒後に続行します...
        timeout /t 5
    ) else (
        echo VOICEVOX 起動完了。エンジン開始を待機中...
        timeout /t 5
    )
) else (
    echo VOICEVOX エンジンは既に起動しています。
)

REM ディレクトリ移動
echo [2/4] プロジェクトディレクトリに移動中...
D:
if errorlevel 1 (
    echo [エラー] Dドライブにアクセスできません。
    pause
    exit /b 1
)

cd D:\setsuna_bot
if errorlevel 1 (
    echo [エラー] D:\setsuna_bot ディレクトリが見つかりません。
    pause
    exit /b 1
)
echo 現在のディレクトリ: %CD%

REM 仮想環境の確認とアクティベート
echo [3/4] 仮想環境をアクティベート中...
if not exist "setsuna_env\Scripts\activate.bat" (
    echo [エラー] 仮想環境が見つかりません: setsuna_env\Scripts\activate.bat
    echo 仮想環境を作成するか、パスを確認してください。
    pause
    exit /b 1
)

call setsuna_env\Scripts\activate
if errorlevel 1 (
    echo [エラー] 仮想環境のアクティベートに失敗しました。
    pause
    exit /b 1
)

REM Python環境の確認
echo Python環境を確認中...
python --version
if errorlevel 1 (
    echo [エラー] Python が見つかりません。
    pause
    exit /b 1
)

REM 必要な依存関係の確認
echo 依存関係を確認中...
python -c "import openai, tkinter; print('主要モジュールOK')" 2>nul
if errorlevel 1 (
    echo [警告] 一部の依存関係が不足している可能性があります。
    echo 続行しますが、エラーが発生する場合があります。
)

REM アプリケーション起動
echo [4/4] せつなGUIを起動中...
echo ========================================
echo   起動完了 - Ctrl+Shift+Alt で音声入力
echo ========================================
python setsuna_gui.py

REM 終了処理
echo.
echo アプリケーションが終了しました。
pause