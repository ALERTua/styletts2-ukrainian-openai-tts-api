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

### Things to do that I have no knowledge on (help appreciated)

- Make this use less RAM
- Make this pronounce numbers

### Things to do that depend on the author's code

- Dynamic model loading depending on an environment variable
- As soon as the code can be executed as is, add it as a submodule to this repository

### Things to do that I have no experience in (help appreciated)

- Make it run fastapi and gradio at the same time or move the API to gradio

## TODO

- healthcheck endpoint

### Usage

- Install https://github.com/sfortis/openai_tts in your Home Assistant
- Provide it with the url to the container port with any api key, any model (they are hardcoded).
- These are the voices available: https://huggingface.co/spaces/patriotyk/styletts2-ukrainian/tree/main/voices (without .wav)
- Use `+` symbol before a vowel to stress it, e.g. `русн+я`.
- The model handles short messages poorly so at least end each syntax with a dot. 

### Endpoints

#### Synthesize Speech

**Endpoint:** `POST /v1/audio/speech`

This endpoint synthesizes speech from the given text using the specified voice and parameters.

**Example Request:**

```bash
curl -X POST "http://127.0.0.1:8000/v1/audio/speech" \
-H "accept: audio/wav" \
-H "Content-Type: application/json" \
-d '{
  "input": "Русн+я вже майже вся подохла. Залишилося ще трохи почекати, і перемога буде за нами.",
  "voice": 5,
  "speed": 1.0,
}'
```
#### Request Body Parameters

- **input** (string): The text to generate audio for.
- **voice** (string or int): The voice to use for synthesis. Can be either the voice name or index.
- **speed** (float): The speed of the speech. Default is `1.0`.
- ~~**response_format** (string): The format of the audio output. Supported formats are `wav` and `mp3`. Default is `wav`.~~
- ~~**sample_rate** (int): The sample rate of the audio. Default is `24000`.~~

#### List Voices

**Endpoint:** `GET /v1/audio/voices`

This endpoint returns a list of available voices with their indexes and names.

**Example Request:**

```bash
curl -X GET "http://127.0.0.1:8000/v1/audio/voices" -H "accept: application/json"
```

**Example Response:**

```json
{
  "voices": [
    {
      "index": 0,
      "name": "Анастасія Павленко"
    },
    {
      "index": 1,
      "name": "Чарівна Марина Панас"
    }
  ]
}
```

### Caveats

- The model does not handle numbers(!) so make sure to replace them with words.

```python
# pip install num2words

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

Я готовий розширити це readme будь-якою корисною інформацією, лише [скажіть](https://github.com/ALERTua/styletts2-ukrainian-openai-tts-api/discussions/new/choose), чого вам не вистачає.
