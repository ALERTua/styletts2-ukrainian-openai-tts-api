
@echo off
setlocal enabledelayedexpansion enableextensions

if not defined DOCKER_HOSTNAME set DOCKER_HOSTNAME=docker
if not defined DOCKER_HOST set DOCKER_HOST=tcp://%DOCKER_HOSTNAME%:2375
if not defined STAGE set STAGE=production
if not defined CONTAINER_NAME set CONTAINER_NAME=test
if not defined DOCKERFILE set DOCKERFILE=Dockerfile
set TAG_BASE=ghcr.io/alertua/styletts2-ukrainian-openai-tts-api

choice /C YN /m "latest?"
if "%errorlevel%"=="1" (
    set TAG=%TAG_BASE%:latest
) else (
    choice /C YN /m "all?"
    if "!errorlevel!"=="1" (
        set TAG=%TAG_BASE%:all
    ) else (
        echo no option given
        exit /b 1
    )

)

choice /C YN /d N /T 15 /m "Build %TAG%?"
if "%errorlevel%"=="1" (
    docker build -f %DOCKERFILE% --target %STAGE% -t %TAG% .
)

choice /C YN /m "Push %TAG%?"
if "%errorlevel%"=="1" (
    docker push %TAG%
)
