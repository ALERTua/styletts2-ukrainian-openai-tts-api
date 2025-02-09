[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
[![Made in Ukraine](https://img.shields.io/badge/made_in-Ukraine-ffd700.svg?labelColor=0057b7)](https://stand-with-ukraine.pp.ua)
[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://stand-with-ukraine.pp.ua)
[![Russian Warship Go Fuck Yourself](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/RussianWarship.svg)](https://stand-with-ukraine.pp.ua)


[![Docker Image Latest](https://github.com/ALERTua/styletts2-ukrainian-openai-tts-api/actions/workflows/docker-image.yml/badge.svg)](https://github.com/ALERTua/styletts2-ukrainian-openai-tts-api/actions/workflows/docker-image.yml)

Docker image for the [patriotyk/styletts2-ukrainian](https://huggingface.co/spaces/patriotyk/styletts2-ukrainian) gradio app with an OpenAI TTS API endpoint to use it with Home Assistant.

I didn't mean to make a "product" image, but it's a temporary solution until a better option arrives. 
By better option I mean a model of at least the same quality but in Piper-compatible format for easy Home Assistant usage.

```
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
  -v './styletts2-ukrainian-openai-tts-api-data/':'/data':'rw' \
  -e 'NVIDIA_VISIBLE_DEVICES'='all' \
  -e 'NVIDIA_DRIVER_CAPABILITIES'='all' \
  --gpus=all \
  --runtime=nvidia \
  'ghcr.io/alertua/styletts2-ukrainian-openai-tts-api:latest'
```

then in Home Assistant use https://github.com/sfortis/openai_tts and provide it with the 8000 port endpoint with any api key, any voice, any model (they are hardcoded).

Use `+` symbol before the stressed vowel to stress it, e.g. `русн+я`.

The model handles short messages poorly so at least end each syntax with a dot. 

The model does not handle numbers(!) so make sure to replace them with words.
```
pip install num2words

cases = [
    "nominative",
    "genitive",
    "dative",
    "accusative",
    "instrumental",
    "locative"
]
    
a = num2words(42, lang='uk', to='ordinal') # сорок другий
c = num2words(42, lang='uk', to='cardinal', gender='feminine', case="genitive")  # сорока двох
d = num2words(1442, lang='uk', to='year')  # одна тисяча чотириста сорок два
e = num2words(1444.10, lang='uk', to='currency', currency='USD', cents=False, separator='', adjective=True)  # одна тисяча чотириста сорок чотири долари 10 центів
```
