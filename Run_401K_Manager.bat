@echo off
echo Starting 401K Manager...
echo Please wait while the application loads (this may take 15-30 seconds on first launch)

REM Check if the exe exists
if not exist "401K_Manager.exe" (
    echo Error: 401K_Manager.exe not found!
    echo Please make sure you're running this from the correct folder.
    pause
    exit
)

REM Try to start the application
start "" "401K_Manager.exe"

REM Wait a moment to see if it launched
timeout /t 5 /nobreak > nul

echo If a browser window doesn't open automatically in the next few seconds,
echo please open your web browser and go to: http://localhost:8501

echo.
echo To close the application completely, close this window and your browser.
echo. 