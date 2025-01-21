import sys

import os

if sys.platform == 'win32':
    os.chdir('styletts2-ukrainian')
else:
    os.chdir('/data')

from infer import split_to_parts, device, _inf

from typing import Any, Literal

import gradio as gr
import numpy as np
import torch
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel, Field
import io
import soundfile as sf
import spaces

app = FastAPI()
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MIN_SAMPLE_RATE = 8000
MAX_SAMPLE_RATE = 48000
type ResponseFormat = Literal["mp3", "flac", "wav", "pcm"]
SUPPORTED_RESPONSE_FORMATS = ("mp3", "wav")
UNSUPORTED_RESPONSE_FORMATS = ("opus", "aac", "flac", "pcm")
DEFAULT_RESPONSE_FORMAT = "wav"


@spaces.GPU
def inference(text, speed=1.0, alpha=0.7, diffusion_steps=10, embedding_scale=1.2):
    wavs = []
    s_prev = None
    sentences = split_to_parts(text)
    # print(sentences)
    phonemes = ''
    noise = torch.randn(1, 1, 256).to(device)
    for text in sentences:
        if text.strip() == "":
            continue

        wav, s_prev, ps = _inf(text, speed, s_prev, noise, alpha=alpha,
                               diffusion_steps=diffusion_steps, embedding_scale=embedding_scale)
        wavs.append(wav)
        phonemes += ' ' + ps
    return np.concatenate(wavs), phonemes


def convert_gradio_audio_to_streaming_response(audio: gr.Audio, response_format: ResponseFormat) -> StreamingResponse:
    filepath = audio.temp_files.pop()
    audio_data, sample_rate = sf.read(filepath)
    audio_buffer = io.BytesIO()
    sf.write(audio_buffer, audio_data, samplerate=sample_rate, format=response_format)
    audio_buffer.seek(0)
    return StreamingResponse(audio_buffer, media_type=f"audio/{response_format}")


class CreateSpeechRequestBody(BaseModel):
    model: str = ''
    input: str = Field(
        ...,
        description="The text to generate audio for. ",
        examples=[
            "A rainbow is an optical phenomenon caused by refraction, internal reflection and dispersion of light in water droplets resulting in a continuous spectrum of light appearing in the sky. The rainbow takes the form of a multicoloured circular arc. Rainbows caused by sunlight always appear in the section of sky directly opposite the Sun. Rainbows can be caused by many forms of airborne water. These include not only rain, but also mist, spray, and airborne dew."  # noqa: E501
        ],
    )
    voice: str = ''
    language: Any | None = None
    response_format: ResponseFormat = Field(
        DEFAULT_RESPONSE_FORMAT,
        description=f"The format to audio in. Supported formats are {', '.join(SUPPORTED_RESPONSE_FORMATS)}. {', '.join(UNSUPORTED_RESPONSE_FORMATS)} are not supported",  # noqa: E501
        examples=list(SUPPORTED_RESPONSE_FORMATS),
    )
    speed: float = Field(1.0)
    sample_rate: int | None = Field(24000, ge=MIN_SAMPLE_RATE, le=MAX_SAMPLE_RATE)


# https://platform.openai.com/docs/api-reference/audio/createSpeech
@app.post("/v1/audio/speech")
async def synthesize(body: CreateSpeechRequestBody) -> StreamingResponse:
    text = body.input
    speed = body.speed
    response_format = body.response_format
    sample_rate = body.sample_rate
    wavs, phonemes = inference(text, speed=speed, alpha=1.0, diffusion_steps=6, embedding_scale=1.0)
    # noinspection PyTypeChecker
    audio = gr.Audio((sample_rate, wavs), label="Audio:", autoplay=False, streaming=False, type="numpy",
                     format=response_format)
    return convert_gradio_audio_to_streaming_response(audio, response_format)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv('PORT', 8000)), log_level="info")
