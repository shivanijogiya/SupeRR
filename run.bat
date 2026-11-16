@echo off
setlocal enabledelayedexpansion
title Royal Insight - Pressure Performance and Auction Intelligence Platform
cd /d "%~dp0"

echo ==========================================================
echo   ROYAL INSIGHT - Starting up...
echo ==========================================================
echo.

REM ---------------------------------------------------------
REM 1. Check Python is installed
REM ---------------------------------------------------------
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python was not found on this computer.
    echo.
    echo Please install Python 3.10 or newer from https://www.python.org/downloads/
    echo IMPORTANT: during installation, tick "Add python.exe to PATH".
    echo Then double-click run.bat again.
    echo.
    pause
    exit /b 1
)

REM ---------------------------------------------------------
REM 1b. Check Python is 64-bit (32-bit Python cannot get a prebuilt
REM     numpy/pandas wheel on recent versions, which forces a doomed
REM     from-source compile and fails with a confusing meson error)
REM ---------------------------------------------------------
for /f "delims=" %%A in ('python -c "import struct; print(struct.calcsize('P')*8)"') do set PYBITS=%%A
if "%PYBITS%"=="32" (
    echo [ERROR] A 32-bit Python was found. Royal Insight needs a 64-bit Python
    echo         to install numpy/pandas from a prebuilt package.
    echo.
    echo Please install 64-bit Python 3.10-3.12 from:
    echo   https://www.python.org/downloads/windows/
    echo ^(choose "Windows installer ^(64-bit^)", NOT the x86 one^), tick
    echo "Add python.exe to PATH" during setup, then delete the "venv" folder
    echo in this project and double-click run.bat again.
    echo.
    pause
    exit /b 1
)

REM ---------------------------------------------------------
REM 2. Create a virtual environment if it does not exist yet
REM ---------------------------------------------------------
if not exist "venv\Scripts\activate.bat" (
    echo [1/4] Creating a local virtual environment ^(first run only^)...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Could not create the virtual environment. See the message above.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Virtual environment already exists - skipping creation.
)

REM ---------------------------------------------------------
REM 3. Activate the virtual environment
REM ---------------------------------------------------------
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Could not activate the virtual environment.
    pause
    exit /b 1
)

REM ---------------------------------------------------------
REM 4. Install dependencies only if needed (marker file trick,
REM    so we don't reinstall everything on every single launch)
REM ---------------------------------------------------------
set "MARKER=venv\.deps_installed"
if not exist "%MARKER%" (
    echo [2/4] Installing required packages ^(first run only, this can take a few minutes^)...
    python -m pip install --upgrade pip >nul
    REM --prefer-binary / --only-binary stop pip from attempting a slow,
    REM failure-prone from-source build of numpy/pandas and fail fast with
    REM a clear message instead, if no prebuilt wheel matches this Python.
    pip install --prefer-binary --only-binary=numpy,pandas,pyarrow -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install dependencies.
        echo.
        echo This is most often caused by an older or 32-bit Python, or a Python
        echo version too new for some packages to have a ready-made build yet.
        echo The safest fix is to install 64-bit Python 3.10, 3.11 or 3.12 from
        echo https://www.python.org/downloads/windows/ , delete the "venv" folder
        echo in this project, and double-click run.bat again.
        echo.
        pause
        exit /b 1
    )
    echo done > "%MARKER%"
) else (
    echo [2/4] Dependencies already installed - skipping.
)

REM ---------------------------------------------------------
REM 5. Launch the Streamlit app (opens the browser automatically)
REM ---------------------------------------------------------
echo [3/4] Launching Royal Insight...
echo [4/4] Your browser should open automatically at http://localhost:8501
echo.
echo ==========================================================
echo   Royal Insight is running. Close this window to stop it.
echo ==========================================================
echo.

streamlit run app.py --server.headless false --browser.gatherUsageStats false

if errorlevel 1 (
    echo.
    echo [ERROR] Streamlit exited with an error. Scroll up to see the details.
    pause
)

endlocal
