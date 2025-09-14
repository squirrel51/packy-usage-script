@echo off
setlocal enabledelayedexpansion

echo Installing packy-usage-monitor...
echo.

REM Check if executable exists
if not exist "dist\packy-usage-monitor.exe" (
    echo [ERROR] Cannot find packy-usage-monitor.exe in dist directory
    echo Please make sure you are running this script from the project root directory
    pause
    exit /b 1
)

REM Create target directory
set "INSTALL_DIR=%LOCALAPPDATA%\packy-usage-monitor"
echo Creating installation directory: %INSTALL_DIR%

if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to create directory: %INSTALL_DIR%
        pause
        exit /b 1
    )
    echo [SUCCESS] Directory created
) else (
    echo [INFO] Directory already exists, skipping creation
)

REM Copy executable
echo Copying executable file...
copy "dist\packy-usage-monitor.exe" "%INSTALL_DIR%\" >nul
if errorlevel 1 (
    echo [ERROR] File copy failed
    pause
    exit /b 1
)
echo [SUCCESS] File copied successfully

REM Create batch wrapper in Windows directory (if accessible)
echo Creating system wrapper...
set "WRAPPER_CREATED=0"

REM Try to create wrapper in Windows directory
echo @echo off > "%WINDIR%\packy-usage-monitor.bat" 2>nul
echo "%INSTALL_DIR%\packy-usage-monitor.exe" %%* >> "%WINDIR%\packy-usage-monitor.bat" 2>nul
if not errorlevel 1 (
    echo [SUCCESS] System wrapper created - you can run 'packy-usage-monitor' anywhere
    set "WRAPPER_CREATED=1"
) else (
    REM Try System32 directory
    echo @echo off > "%WINDIR%\System32\packy-usage-monitor.bat" 2>nul
    echo "%INSTALL_DIR%\packy-usage-monitor.exe" %%* >> "%WINDIR%\System32\packy-usage-monitor.bat" 2>nul
    if not errorlevel 1 (
        echo [SUCCESS] System32 wrapper created - you can run 'packy-usage-monitor' anywhere
        set "WRAPPER_CREATED=1"
    )
)

REM Create uninstaller
echo Creating uninstall script...
(
    echo @echo off
    echo echo Uninstalling packy-usage-monitor...
    echo echo.
    echo REM Delete executable
    echo if exist "%INSTALL_DIR%\packy-usage-monitor.exe" ^(
    echo     del "%INSTALL_DIR%\packy-usage-monitor.exe"
    echo     echo [SUCCESS] Executable deleted
    echo ^)
    echo echo.
    echo REM Remove wrapper files
    echo if exist "%WINDIR%\packy-usage-monitor.bat" ^(
    echo     del "%WINDIR%\packy-usage-monitor.bat" 2^>nul
    echo     echo [INFO] Wrapper removed from Windows directory
    echo ^)
    echo if exist "%WINDIR%\System32\packy-usage-monitor.bat" ^(
    echo     del "%WINDIR%\System32\packy-usage-monitor.bat" 2^>nul
    echo     echo [INFO] Wrapper removed from System32 directory
    echo ^)
    echo echo.
    echo REM Remove directory
    echo if exist "%INSTALL_DIR%" ^(
    echo     rmdir "%INSTALL_DIR%" 2^>nul
    echo     if exist "%INSTALL_DIR%" ^(
    echo         echo [WARNING] Directory not empty, not removed: %INSTALL_DIR%
    echo     ^) else ^(
    echo         echo [SUCCESS] Installation directory removed
    echo     ^)
    echo ^)
    echo echo.
    echo echo Uninstallation completed!
    echo pause
) > "%INSTALL_DIR%\uninstall.bat"

echo [SUCCESS] Uninstall script created: %INSTALL_DIR%\uninstall.bat

REM Create PATH helper script
echo Creating PATH setup helper...
(
    echo @echo off
    echo echo PATH Setup Helper for packy-usage-monitor
    echo echo.
    echo echo Current installation directory:
    echo echo %INSTALL_DIR%
    echo echo.
    echo echo Copy the above path and follow these steps:
    echo echo 1. Press Win+R, type: sysdm.cpl
    echo echo 2. Click "Environment Variables"
    echo echo 3. In "User variables", find "Path" and click "Edit"
    echo echo 4. Click "New" and paste the installation path
    echo echo 5. Click OK to save
    echo echo.
    echo echo Alternative: Run the executable directly:
    echo echo %INSTALL_DIR%\packy-usage-monitor.exe
    echo echo.
    echo pause
) > "%INSTALL_DIR%\setup-path.bat"

echo [SUCCESS] PATH setup helper created: %INSTALL_DIR%\setup-path.bat

echo.
echo ============================================
echo Installation completed!
echo.
echo Install location: %INSTALL_DIR%
echo Executable: packy-usage-monitor.exe
echo Uninstaller: %INSTALL_DIR%\uninstall.bat
echo PATH Helper: %INSTALL_DIR%\setup-path.bat
echo.

if "%WRAPPER_CREATED%"=="1" (
    echo [GOOD NEWS] You can now run 'packy-usage-monitor' from anywhere!
    echo Just open a new command prompt and type: packy-usage-monitor
) else (
    echo [INFO] Could not create system wrapper automatically.
    echo.
    echo To run from anywhere, either:
    echo 1. Run: %INSTALL_DIR%\setup-path.bat for PATH setup help
    echo 2. Or run directly: %INSTALL_DIR%\packy-usage-monitor.exe
)

echo ============================================
echo.

pause