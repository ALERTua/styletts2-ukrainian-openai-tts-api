@echo off
setlocal enabledelayedexpansion enableextensions

if exist .python-version (
    uv sync --locked || goto :end
    if not exist uv.lock uv lock || goto :end
) else if exist pyproject.toml (
    poetry check || goto :end
    if not exist poetry.lock poetry lock || goto :end
)

if not defined DOCKER_BUILDKIT set DOCKER_BUILDKIT=1
if not defined DOCKERFILE set DOCKERFILE=Dockerfile
if not defined DOCKER_REGISTRY set DOCKER_REGISTRY=registry.alertua.duckdns.org
echo DOCKER_REGISTRY: %DOCKER_REGISTRY%

set prevdir=%CD%
echo prevdir: %prevdir%

cd /d %~dp0

for %%I in ("%CD%") do set "curdir=%%~nxI"
set "curdir_prefix=!curdir:~0,6!"
if /I "%curdir_prefix%"=="script" cd ..
for %%I in ("%CD%") do set "curdir=%%~nxI"
echo curdir: %curdir%

if not defined IMAGE_NAME set IMAGE_NAME=%curdir%
echo IMAGE_NAME: %IMAGE_NAME%

if not defined IMAGE_TAG set IMAGE_TAG=latest
echo IMAGE_TAG: %IMAGE_TAG%

if not defined BUILD_TAG set BUILD_TAG=%DOCKER_REGISTRY%/%IMAGE_NAME%:%IMAGE_TAG%
echo BUILD_TAG: %BUILD_TAG%

if not defined BUILD_PATH set "BUILD_PATH=%CD%"
echo BUILD_PATH: %BUILD_PATH%
pushd %BUILD_PATH%

if not defined DOCKER_EXE set DOCKER_EXE=docker
rem set DOCKER_OPTS=--insecure-registry=%DOCKER_REGISTRY%
if not defined DOCKER_OPTS set DOCKER_OPTS=--max-concurrent-uploads=10 --max-concurrent-downloads=10

"%DOCKER_EXE%" --version

echo DOCKER_REMOTE: %DOCKER_REMOTE%
if defined DOCKER_HOST echo DOCKER_HOST: %DOCKER_HOST%

@REM choice /C YN /m "Proceed?"
@REM if ["%errorlevel%"] NEQ ["1"] goto :end
timeout /t 7

if not defined DOCKER_REMOTE (
    if not defined DOCKER_SERVICE set DOCKER_SERVICE=com.docker.service
    where %DOCKER_EXE% >nul || set "DOCKER_EXE=%ProgramFiles%\Docker\Docker\resources\bin\docker.exe"

    sc query %DOCKER_SERVICE% | findstr /IC:"running" >nul || (
        echo starting Docker service %DOCKER_SERVICE%
        sudo net start %DOCKER_SERVICE% || (
            echo "Error starting docker service %DOCKER_SERVICE%
            goto :end
        )
    )

    tasklist | findstr /IC:"Docker Desktop.exe" >nul || (
        start "" "%ProgramFiles%\Docker\Docker\Docker Desktop.exe"
        :loop
            call docker info >nul 2>nul || (
                timeout /t 1 >nul
                goto loop
            )
        rem timeout /t 60
    )
)

"%DOCKER_EXE%" --version
"%DOCKER_EXE%" build -t %BUILD_TAG% %BUILD_PATH% --target production %* || goto :end
"%DOCKER_EXE%" push %DOCKER_REGISTRY%/%IMAGE_NAME% || goto :end

@REM net stop %DOCKER_SERVICE% || goto :end

goto :end

:end
cd /d %prevdir%
exit /b
