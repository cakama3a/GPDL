@echo off
setlocal EnableDelayedExpansion

:: =====================================================================
:: КОНФІГУРАЦІЯ - Змініть ці параметри за потреби
:: =====================================================================
set "USE_NOCONSOLE=false"                    :: Змініть на true щоб приховати консоль
set "SIGN_WITH_YUBIKEY=true"                 :: Встановіть true для підпису EXE з YubiKey
set "REQUIRED_PACKAGES=pygame numpy requests colorama tqdm pyserial" :: Необхідні Python пакети
:: =====================================================================

:: Встановлюємо UTF-8 кодування
chcp 65001 >nul

:: Визначаємо основні шляхи
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
for %%F in ("%SCRIPT_DIR%") do set "OUTPUT_NAME=%%~nxF"

:: Створюємо лог-файл
set "LOG_FILE=%SCRIPT_DIR%\build_log.txt"
echo Build started at %DATE% %TIME% > "%LOG_FILE%"
echo Build started at %DATE% %TIME%

:: Очищуємо старі тимчасові директорії
echo Cleaning up old temporary directories...
echo Cleaning up old temporary directories... >> "%LOG_FILE%"
for /d %%D in ("%TEMP%\%OUTPUT_NAME%Build_*") do rd /s /q "%%D" 2>nul

:: Налаштування шляхів
echo Using OUTPUT_NAME: %OUTPUT_NAME%
echo Using OUTPUT_NAME: %OUTPUT_NAME% >> "%LOG_FILE%"

set "PYTHON_SCRIPT=%SCRIPT_DIR%\GPDL.py"
set "TEMP_DIR=%TEMP%\%OUTPUT_NAME%Build_%RANDOM%"
set "ICON_ICO_PATH=%SCRIPT_DIR%\icon.ico"
set "EXE_PATH=%TEMP_DIR%\dist\%OUTPUT_NAME%.exe"
set "FINAL_EXE_PATH=%SCRIPT_DIR%\%OUTPUT_NAME%.exe"

:: Перевірка наявності Python.py
if not exist "%PYTHON_SCRIPT%" (
    echo Error: File %PYTHON_SCRIPT% not found!
    echo Error: File %PYTHON_SCRIPT% not found! >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: Пошук Python
set "PYTHON="
where py >nul 2>nul && set "PYTHON=py"
if "%PYTHON%"=="" where python >nul 2>nul && set "PYTHON=python"
if "%PYTHON%"=="" (
    echo Error: Python not found! Make sure Python is installed and added to PATH.
    echo Error: Python not found! >> "%LOG_FILE%"
    pause
    exit /b 1
)
echo Found Python executable: %PYTHON%
echo Found Python executable: %PYTHON% >> "%LOG_FILE%"

:: Створення віртуального середовища
echo Creating virtual environment...
echo Creating virtual environment... >> "%LOG_FILE%"
set "VENV_DIR=%TEMP_DIR%\venv"
%PYTHON% -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to create virtual environment!
    echo Error: Failed to create virtual environment! >> "%LOG_FILE%"
    pause
    exit /b 1
)
call "%VENV_DIR%\Scripts\activate.bat"

:: Встановлення пакетів
echo Upgrading pip...
echo Upgrading pip... >> "%LOG_FILE%"
pip install --upgrade pip >> "%LOG_FILE%" 2>&1

set "PACKAGES_TO_INSTALL=%REQUIRED_PACKAGES% nuitka"
echo Installing packages: %PACKAGES_TO_INSTALL%
echo Installing packages: %PACKAGES_TO_INSTALL% >> "%LOG_FILE%"
pip install %PACKAGES_TO_INSTALL% >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install packages!
    echo Error: Failed to install packages! >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: Створення тимчасової директорії для ресурсів
mkdir "%TEMP_DIR%" 2>nul

:: Збір файлів ресурсів для включення в EXE
set "DATA_FILES="
for %%E in (png jpg) do (
    for %%F in ("%SCRIPT_DIR%\*.%%E") do (
        echo Including resource: %%~nxF
        echo Including resource: %%~nxF >> "%LOG_FILE%"
        set "DATA_FILES=!DATA_FILES! --include-data-file="%%F"=%%~nxF"
    )
)

:: Формування команди Nuitka
set "NUITKA_CMD=python -m nuitka --standalone --onefile --output-dir="%TEMP_DIR%\dist" --output-filename="%OUTPUT_NAME%.exe" --assume-yes-for-downloads"

:: Додавання опцій консолі
if "%USE_NOCONSOLE%"=="true" (
    set "NUITKA_CMD=!NUITKA_CMD! --windows-console-mode=disable"
)

:: Додавання іконки
if exist "%ICON_ICO_PATH%" (
    set "NUITKA_CMD=!NUITKA_CMD! --windows-icon-from-ico="%ICON_ICO_PATH%""
)

:: Додавання файлів ресурсів
if defined DATA_FILES (
    set "NUITKA_CMD=!NUITKA_CMD! !DATA_FILES!"
)

:: Додавання необхідних модулів
for %%P in (%REQUIRED_PACKAGES%) do (
    set "MODULE_NAME=%%P"
    if /I "%%P"=="pillow" set "MODULE_NAME=PIL"
    if /I "%%P"=="pyserial" set "MODULE_NAME=serial"
    set "NUITKA_CMD=!NUITKA_CMD! --include-module=!MODULE_NAME!"
)

:: Додавання основного скрипту
set "NUITKA_CMD=!NUITKA_CMD! "%PYTHON_SCRIPT%""

:: Виконання Nuitka
echo.
echo =====================================================================
echo Running Nuitka compilation...
echo =====================================================================
echo.
echo Running Nuitka... >> "%LOG_FILE%"
%NUITKA_CMD% >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Nuitka failed! Check build_log.txt for details.
    echo Error: Nuitka failed! >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: Перевірка створення EXE
if not exist "%EXE_PATH%" (
    echo Error: .exe was not created!
    echo Error: .exe was not created! >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: Підпис EXE з YubiKey (якщо увімкнено)
if "%SIGN_WITH_YUBIKEY%"=="true" (
    echo.
    echo =====================================================================
    echo Signing EXE with YubiKey... A prompt for your PIN will appear
    echo =====================================================================
    echo.
    echo Signing EXE with YubiKey... >> "%LOG_FILE%"

    powershell -ExecutionPolicy Bypass -Command "$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Select-Object -First 1; if ($cert) { Write-Host 'Found certificate:' $cert.Subject; Set-AuthenticodeSignature -FilePath '%EXE_PATH%' -Certificate $cert -TimestampServer 'http://timestamp.digicert.com' } else { Write-Host 'No code signing certificate found.'; exit 1 }" >> "%LOG_FILE%" 2>&1

    if %ERRORLEVEL% neq 0 (
        echo Warning: Failed to sign EXE file!
        echo Warning: Failed to sign EXE file! >> "%LOG_FILE%"
        echo Make sure YubiKey is connected and you entered the correct PIN.
        choice /C YN /M "Continue without signature"
        if !ERRORLEVEL! equ 2 (
            pause
            exit /b 1
        )
    ) else (
        echo EXE file signed successfully.
        echo EXE file signed successfully. >> "%LOG_FILE%"

        REM Перевірка підпису
        echo Verifying signature...
        echo Verifying signature... >> "%LOG_FILE%"
        powershell -ExecutionPolicy Bypass -Command "if ((Get-AuthenticodeSignature -FilePath '%EXE_PATH%').Status -eq 'Valid') { Write-Host 'Signature verification: OK' } else { Write-Host 'Signature verification: FAILED'; exit 1 }" >> "%LOG_FILE%" 2>&1
        if %ERRORLEVEL% neq 0 (
            echo Warning: Signature verification failed!
            echo Warning: Signature verification failed! >> "%LOG_FILE%"
        ) else (
            echo Signature verified successfully.
            echo Signature verified successfully. >> "%LOG_FILE%"
        )
    )
)

:: Переміщення EXE до директорії проекту
echo.
echo Moving final EXE to project directory...
echo Moving final EXE to project directory... >> "%LOG_FILE%"
if exist "%FINAL_EXE_PATH%" del "%FINAL_EXE_PATH%"
move "%EXE_PATH%" "%FINAL_EXE_PATH%" >> "%LOG_FILE%" 2>&1

if not exist "%FINAL_EXE_PATH%" (
    echo Error: Failed to move .exe to final destination!
    echo Error: Failed to move .exe to final destination! >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: Очищення тимчасових файлів
echo Cleaning up temporary files...
echo Cleaning up temporary files... >> "%LOG_FILE%"
call "%VENV_DIR%\Scripts\deactivate.bat" 2>nul
rd /s /q "%TEMP_DIR%" 2>nul

:: Успішне завершення
echo.
echo =====================================================================
echo Build successful!
echo File created at: %FINAL_EXE_PATH%
echo Build completed at %DATE% %TIME%
echo =====================================================================
echo.
echo Build completed at %DATE% %TIME% >> "%LOG_FILE%"
pause