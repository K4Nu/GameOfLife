@echo off
echo ========================================
echo    Building GameOfLife.exe
echo ========================================
echo.

REM Sprawdz czy PyInstaller jest zainstalowany
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [1/3] Installing PyInstaller...
    pip install pyinstaller
) else (
    echo [1/3] PyInstaller already installed
)

echo.
echo [2/3] Building executable...
echo.

REM Zbuduj .exe
pyinstaller --onefile ^
    --windowed ^
    --add-data "assets;assets" ^
    --name "GameOfLife" ^
    --icon=NONE ^
    main.py

echo.
echo [3/3] Cleaning up...

REM Opcjonalnie: wyczysc smieci
REM rmdir /s /q build
REM del GameOfLife.spec

echo.
echo ========================================
echo    BUILD COMPLETE!
echo ========================================
echo.
echo Executable location: dist\GameOfLife.exe
echo.
echo To test, run: dist\GameOfLife.exe
echo.
pause