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
where cl.exe
if %errorlevel% neq 0 (
    echo cl.exe NOT FOUND in path after setup.
    exit /b 1
)

echo.
echo Installing AI dependencies...
backend\venv\Scripts\pip install cmake dlib face_recognition insightface onnxruntime
if %errorlevel% neq 0 (
    echo Installation failed.
    exit /b %errorlevel%
)

echo.
echo Installation SUCCESSFUL!
endlocal
