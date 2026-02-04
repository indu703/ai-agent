@echo off
setlocal
echo Setting up Visual Studio Build Environment...
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
if %errorlevel% neq 0 (
    echo FAILED to set up VS environment.
    exit /b %errorlevel%
)

echo.
echo Checking for cl.exe...
cl /?
if %errorlevel% neq 0 (
    echo cl.exe FAILED to respond.
    exit /b %errorlevel%
)

echo.
echo cl.exe is READY!
endlocal
