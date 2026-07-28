@echo off
setlocal
title AIdle Openworld - Chon lai Art Style

set "GODOT=E:\AIdle_openworld\tools\Godot_v4.3-stable_win64.exe"
set "PROJ=E:\AIdle_openworld\game"
set "UDIR=%APPDATA%\Godot\app_userdata\AIdle Openworld"
set "META=%UDIR%\world_meta.cfg"

echo.
echo  ============================================
echo   AIdle Openworld - Chon lai Art Style
echo  ============================================
echo.
echo  Game dang bo qua man chon style vi file save da co
echo  san mot lua chon. Script nay DOI TEN file save do
echo  thanh ban sao luu - KHONG xoa - de man chon hien lai.
echo.

if not exist "%GODOT%" goto NOGODOT

if not exist "%META%" goto NOMETA

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%I"
echo  Tim thay file save:
echo    %META%
move /Y "%META%" "%UDIR%\world_meta.backup_%STAMP%.cfg" >nul 2>&1
if errorlevel 1 goto MOVEFAIL
echo  Da doi ten thanh: world_meta.backup_%STAMP%.cfg
echo  Muon quay lai: doi ten file backup do lai thanh world_meta.cfg
goto LAUNCH

:MOVEFAIL
echo  [CANH BAO] Khong doi ten duoc. Game co the van vao thang the gioi.
goto LAUNCH

:NOMETA
echo  Khong co file save - man chon style se tu hien.
goto LAUNCH

:LAUNCH
echo.
echo  Dang mo game...
start "" "%GODOT%" --path "%PROJ%"
echo.
echo  Chon "Cozy Cyber-Pixel / Dreamy Low-Poly" de xem bo kit
echo  Cozy dung mau: nen xanh la, ao xanh nuoc.
echo.
timeout /t 8 >nul
goto END

:NOGODOT
echo  [LOI] Khong tim thay Godot tai:
echo    %GODOT%
pause

:END
endlocal
