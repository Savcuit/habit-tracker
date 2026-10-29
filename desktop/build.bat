@echo off
setlocal
cd /d "%~dp0"

echo === Habit Tracker build ===
where py >nul 2>nul
if %errorlevel%==0 (set PY=py) else (set PY=python)

%PY% --version || goto :fail
echo Installing build tools...
%PY% -m pip install --upgrade pip pyinstaller --quiet || goto :fail

echo Building the executable...
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "HabitTracker" ^
  --icon "assets\icon.ico" ^
  --add-data "assets;assets" ^
  habit_tracker.py || goto :fail

echo.
echo Done. The program is at dist\HabitTracker.exe
echo Copy it anywhere you like - it keeps its data in %%APPDATA%%\NexusHabitTracker
pause
exit /b 0

:fail
echo.
echo Build failed. Read the messages above.
pause
exit /b 1
