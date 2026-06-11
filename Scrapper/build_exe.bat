@echo off
cd /d "%~dp0"
"d:\0_YG Project\0_Python Practice\.venv\Scripts\python.exe" -m pip install --upgrade pip pyinstaller
"d:\0_YG Project\0_Python Practice\.venv\Scripts\python.exe" -m PyInstaller --noconfirm --onefile --console --name scraper_app main.py
if exist dist\scraper_app.exe (
  echo.
  echo EXE created: dist\scraper_app.exe
) else (
  echo.
  echo Build failed.
)
