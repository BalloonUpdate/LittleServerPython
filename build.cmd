@echo off

pyinstaller --noconfirm --icon icon.ico -c -F -n LittleServer LittleServerMain.py
del /f /s /q LittleServer.spec