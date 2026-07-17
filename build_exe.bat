@echo off
cd /d "%~dp0"
echo ==============================================
echo  Building Shuhaagan Sarees Billing System .exe
echo ==============================================

echo Installing/updating dependencies...
python -m pip install -r requirements.txt --quiet

echo Cleaning previous build...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo Running PyInstaller...
python -m PyInstaller billing_system.spec --clean

echo Copying data files into dist folder...
copy /Y billing_data.xlsx dist\billing_system\billing_data.xlsx
mkdir dist\billing_system\invoices 2>nul
mkdir dist\billing_system\qr_codes 2>nul
copy /Y README_dist.txt dist\billing_system\README.txt

echo Zipping final distributable...
powershell -Command "Compress-Archive -Path 'dist\billing_system' -DestinationPath 'billing_system_windows.zip' -Force"

echo.
echo Done! See billing_system_windows.zip
pause
