@echo off
REM VoiceVoxサーバーが起動してなければ起動する
tasklist | findstr /i voicevox_engine.exe > nul
if errorlevel 1 (
    start "" "C:\Users\coszi\AppData\Local\Programs\VOICEVOX\VOICEVOX.exe" --use_gpu --load_all_models
    timeout /t 3
)
REM Dドライブに移動
D:
cd D:\setsuna_bot

REM 仮想環境をアクティベートして実行
call setsuna_env\Scripts\activate
python setsuna_gui.py

REM 実行終了後一時停止（閉じないように）
pause
