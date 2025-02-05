[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
[![Made in Ukraine](https://img.shields.io/badge/made_in-Ukraine-ffd700.svg?labelColor=0057b7)](https://stand-with-ukraine.pp.ua)
[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://stand-with-ukraine.pp.ua)
[![Russian Warship Go Fuck Yourself](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/RussianWarship.svg)](https://stand-with-ukraine.pp.ua)


[![Docker Image Latest](https://github.com/ALERTua/styletts2-ukrainian-openai-tts-api/actions/workflows/docker-image.yml/badge.svg)](https://github.com/ALERTua/styletts2-ukrainian-openai-tts-api/actions/workflows/docker-image.yml)

Docker image for the [patriotyk/styletts2-ukrainian](https://huggingface.co/spaces/patriotyk/styletts2-ukrainian) gradio app with an OpenAI TTS API endpoint to use it with Home Assistant.

I didn't mean to make a "product" image, but it's a temporary solution until a better option arrives. 

```
# install git lfs to clone the original repo
sudo apt install git-lfs
git lfs install

# clone the model repo in ./styletts2-ukrainian
git clone https://huggingface.co/spaces/patriotyk/styletts2-ukrainian --depth=1

# run the image, mounting the cloned repo in its /data folder, and opening port 8000

# --gpus=all and --runtime=nvidia binds your NVidia GPU to the container
# replace them with --device=/dev/dri for Intel GPUs
# or remove them for full CPU

docker run \
  -d \
  --name='styletts2-ukrainian-openai-tts-api' \
  --net='bridge' \
  -e 'PORT'='8000' \
  -p '8000:8000/tcp' \
  -v './styletts2-ukrainian/':'/data':'ro' \
  -e 'NVIDIA_VISIBLE_DEVICES'='all' \
  -e 'NVIDIA_DRIVER_CAPABILITIES'='all' \
  --gpus=all \
  --runtime=nvidia \
  'ghcr.io/alertua/styletts2-ukrainian-openai-tts-api:latest'
```

then in Home Assistant
https://github.com/sfortis/openai_tts
and use the 8000 port endpoint with any api key, any voice, any model
