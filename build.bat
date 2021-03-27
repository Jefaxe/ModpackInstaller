@echo off
%localappdata%\Programs\Python\Python39\Scripts\pip install pyinstaller
%localappdata%\Programs\Python\Python39\Scripts\pyinstaller --onefile --noconsole --icon icon.ico ModpackInstaller.pyw
robocopy . dist /XF ModpackInstaller.pyw icon.ico build.bat ModpackInstaller.spec