
@echo off
if not defined DOCKER_HOSTNAME set DOCKER_HOSTNAME=docker
if not defined DOCKER_HOST set DOCKER_HOST=tcp://%DOCKER_HOSTNAME%:2375
if not defined STAGE set STAGE=production
if not defined CONTAINER_NAME set CONTAINER_NAME=test
if not defined DOCKERFILE set DOCKERFILE=Dockerfile

set TAG=ghcr.io/alertua/styletts2-ukrainian-openai-tts-api:latest

docker build -f %DOCKERFILE% --target %STAGE% -t %TAG% .

echo PUSH IT WITH:
echo docker push %TAG%
