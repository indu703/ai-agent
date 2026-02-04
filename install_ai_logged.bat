@echo off
setlocal
echo SETUP START: %date% %time% > install_ai.log
echo Setting up Visual Studio Build Environment... >> install_ai.log
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64 >> install_ai.log 2>&1
if %errorlevel% neq 0 (
    echo FAILED to set up VS environment. >> install_ai.log
    exit /b %errorlevel%
)

echo. >> install_ai.log
echo Checking for cl.exe... >> install_ai.log
where cl.exe >> install_ai.log 2>&1

echo. >> install_ai.log
echo Installing AI dependencies... >> install_ai.log
backend\venv\Scripts\pip install cmake dlib face_recognition insightface onnxruntime --no-cache-dir --verbose >> install_ai.log 2>&1
if %errorlevel% neq 0 (
    echo Installation failed. >> install_ai.log
    exit /b %errorlevel%
)

echo. >> install_ai.log
echo Installation SUCCESSFUL! >> install_ai.log
echo SETUP END: %date% %time% >> install_ai.log
endlocal
