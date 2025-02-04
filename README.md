```
git clone https://huggingface.co/spaces/patriotyk/styletts2-ukrainian
docker run -v ./styletts2-ukrainian:/data ghcr.io/alertua/styletts2-ukrainian-openai-tts-api:latest
```
then in Home Assistant
https://github.com/sfortis/openai_tts
and use the 8000 port endpoint with any api key, any voice, any model
