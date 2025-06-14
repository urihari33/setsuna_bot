@echo off
echo Starting VOICEVOX for WSL2...

REM Check common VOICEVOX installation paths
set VOICEVOX_ENGINE="%LOCALAPPDATA%\Programs\VOICEVOX\vv-engine\run.exe"
set VOICEVOX_MAIN="%LOCALAPPDATA%\Programs\VOICEVOX\VOICEVOX.exe"

if exist %VOICEVOX_ENGINE% (
    echo Found VOICEVOX Engine at %VOICEVOX_ENGINE%
    cd /d "%LOCALAPPDATA%\Programs\VOICEVOX\vv-engine"
    echo Starting VOICEVOX Engine with host 0.0.0.0:50021...
    start "VOICEVOX Engine WSL2" run.exe --host 0.0.0.0 --port 50021
    goto :success
)

if exist %VOICEVOX_MAIN% (
    echo Found VOICEVOX Main at %VOICEVOX_MAIN%
    cd /d "%LOCALAPPDATA%\Programs\VOICEVOX"
    echo Starting VOICEVOX with host 0.0.0.0:50021...
    start "VOICEVOX WSL2" VOICEVOX.exe --host 0.0.0.0 --port 50021
    goto :success
)

echo ERROR: VOICEVOX not found!
echo Please check if VOICEVOX is installed at:
echo   %LOCALAPPDATA%\Programs\VOICEVOX\
echo.
echo Or try manual startup:
echo   cd "%%LOCALAPPDATA%%\Programs\VOICEVOX\vv-engine"
echo   run.exe --host 0.0.0.0 --port 50021
goto :end

:success
echo VOICEVOX started successfully for WSL2 access
echo Listening on 0.0.0.0:50021
echo.
echo Please wait 15-30 seconds for startup to complete...
timeout /t 20 /nobreak > nul
echo.
echo Testing connection...
curl -s http://localhost:50021/version > nul 2>&1
if %errorlevel% == 0 (
    echo SUCCESS: VOICEVOX is running and accessible
) else (
    echo NOTICE: Still starting up, please wait a bit more...
)

:end
echo.
echo Press any key to continue...
pause > nul