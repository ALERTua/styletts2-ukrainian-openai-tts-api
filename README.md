```
# install git lfs if needed
sudo apt install git-lfs
git lfs install

# clone the model repo
git clone https://huggingface.co/spaces/patriotyk/styletts2-ukrainian

# run the image, mounting the repo in its /data folder
docker run -v ./styletts2-ukrainian:/data ghcr.io/alertua/styletts2-ukrainian-openai-tts-api:latest
```
then in Home Assistant
https://github.com/sfortis/openai_tts
and use the 8000 port endpoint with any api key, any voice, any model
