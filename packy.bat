@echo off
REM Set UTF-8 encoding for Chinese support
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM Set console properties for better Unicode display
for /f "tokens=2 delims=:" %%a in ('chcp') do set current_cp=%%a
if not "%current_cp%"==" 65001" (
    echo [INFO] Console encoding set to UTF-8 for Chinese character support
)
title Packy Usage Monitor - Interactive Mode

set "APP_DIR=%~dp0"
set "EXE_PATH=%APP_DIR%dist\packy-usage-monitor.exe"

echo.
echo ================================================
echo    Packy Usage Monitor - Interactive Shell
echo ================================================
echo.
echo Available commands:
echo   check      - Check usage status (for CI/CD)
echo   config     - Configuration settings
echo   diagnose   - System diagnostics
echo   perf-test  - Performance testing
echo   status     - Show current usage status
echo   tray       - Launch system tray app
echo   watch      - Real-time monitoring mode
echo   version    - Show version info
echo   help       - Show help information
echo   exit       - Exit this program
echo.

:interactive_loop
set /p "user_input=packy> "

REM Handle empty input
if "!user_input!"=="" goto interactive_loop

REM Convert to lowercase for comparison
set "cmd=!user_input!"
for %%i in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do call set "cmd=%%cmd:%%i=%%i%%"

REM Handle built-in commands
if "!cmd!"=="exit" goto exit_program
if "!cmd!"=="quit" goto exit_program
if "!cmd!"=="q" goto exit_program

if "!cmd!"=="help" (
    echo.
    echo Available commands: check, config, diagnose, perf-test, status, tray, watch, version, help, exit
    echo.
    goto interactive_loop
)

if "!cmd!"=="version" (
    echo.
    echo Executing: packy-usage-monitor.exe --version
    echo.
    "%EXE_PATH%" --version 2>nul || echo [Error] Failed to get version info
    echo.
    goto interactive_loop
)

REM Handle main program commands
set "valid_commands=check config diagnose perf-test status tray watch"
set "is_valid=0"

for %%c in (%valid_commands%) do (
    if "!cmd!"=="%%c" set "is_valid=1"
)

if "!is_valid!"=="1" (
    echo.
    echo Executing: packy-usage-monitor.exe !user_input!
    echo ----------------------------------------

    REM Set UTF-8 encoding for the subprocess
    "%EXE_PATH%" !user_input! 2>nul || echo [Error] Command failed or encoding issue detected

    echo ----------------------------------------
    echo.
    goto interactive_loop
) else (
    echo.
    echo [Error] Unknown command: !user_input!
    echo Type 'help' to see available commands.
    echo.
    goto interactive_loop
)

:exit_program
echo.
echo Thanks for using Packy Usage Monitor! Goodbye!
timeout 2 >nul
exit /b 0