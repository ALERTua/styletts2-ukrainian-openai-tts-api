
@if not defined DOCKER_HOSTNAME set DOCKER_HOSTNAME=docker
@if not defined DOCKER_HOST set DOCKER_HOST=tcp://%DOCKER_HOSTNAME%:2375
@if not defined STAGE set STAGE=production
@if not defined CONTAINER_NAME set CONTAINER_NAME=test
@if not defined DOCKERFILE set DOCKERFILE=Dockerfile

docker kill %CONTAINER_NAME%
docker rm %CONTAINER_NAME%
docker build -f %DOCKERFILE% --target %STAGE% -t %CONTAINER_NAME%:latest . || exit /b 1
docker run --init --env-file="%~dp0..\.env" --name %CONTAINER_NAME% %* -t -d %CONTAINER_NAME% %* || exit /b 1
where nircmd >nul 2>nul && nircmd beep 500 500
docker logs %CONTAINER_NAME%
@echo "Container accessible at hostname: %DOCKER_HOSTNAME%"
docker exec -it %CONTAINER_NAME% bash
