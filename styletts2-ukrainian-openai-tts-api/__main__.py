import os
import io
import logging
from pathlib import Path
from typing import Any, Literal

import torch
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status
from pydantic import BaseModel, Field
import gradio as gr
import soundfile as sf
import spaces
import numpy as np

os.chdir(Path(__file__).parent.parent / 'styletts2-ukrainian')

from infer import split_to_parts, device, _inf, compute_style, models as infer_models  # noqa: E504
from app import prompts_dir, demo  # noqa: E504

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger("app")

app = FastAPI()
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

type ResponseFormat = Literal["mp3", "flac", "wav", "pcm"]
SUPPORTED_RESPONSE_FORMATS = ("mp3", "wav")
UNSUPORTED_RESPONSE_FORMATS = ("opus", "aac", "flac", "pcm")
DEFAULT_RESPONSE_FORMAT = "wav"

voices = Path(prompts_dir).glob("*.wav")
voices = {_.stem: _ for _ in voices}
voice_names: list[str] = list(voices.keys())
# noinspection PyTypeHints
type Voice = Literal[*voice_names] | int
DEFAULT_VOICE = 0

models = list(infer_models.keys())
# noinspection PyTypeHints
type Model = Literal[*models]
DEFAULT_MODEL = models[0]

MIN_SAMPLE_RATE = 8000
MAX_SAMPLE_RATE = 48000
DEFAULT_SAMPLE_RATE = 24000


@spaces.GPU
def inference(model, text, voice_audio, speed: float | int = 1, alpha=0.4, beta=0.4, diffusion_steps=10,
              embedding_scale=1.2):
    wavs = []
    s_prev = None
    phonemes = ''

    sentences = split_to_parts(text)
    noise = torch.randn(1, 1, 256).to(device)
    ref_s = compute_style(voice_audio) if voice_audio else None
    for text in sentences:
        if text.strip() == "":
            continue

        wav, s_prev, ps = _inf(model, text, ref_s, speed, s_prev, noise, alpha=alpha,
                               beta=beta, diffusion_steps=diffusion_steps, embedding_scale=embedding_scale)
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
    model: Model = Field(
        DEFAULT_MODEL,
        description=f"Model. Supported models are {', '.join(models)}.",
        examples=models,
    )
    input: str = Field(
        ...,
        description="The text to generate audio for. ",
        examples=[
            "A rainbow is an optical phenomenon caused by refraction, internal reflection and dispersion of light in water droplets resulting in a continuous spectrum of light appearing in the sky. The rainbow takes the form of a multicoloured circular arc. Rainbows caused by sunlight always appear in the section of sky directly opposite the Sun. Rainbows can be caused by many forms of airborne water. These include not only rain, but also mist, spray, and airborne dew."  # noqa: E501
        ],
    )
    voice: Voice = Field(
        DEFAULT_VOICE,
        description=f"Audio voice. Supported voices are {', '.join(voice_names)}.",
        examples=voice_names,
    )
    language: Any | None = None
    response_format: ResponseFormat = Field(
        DEFAULT_RESPONSE_FORMAT,
        description=f"The format to audio in. Supported formats are {', '.join(SUPPORTED_RESPONSE_FORMATS)}. {', '.join(UNSUPORTED_RESPONSE_FORMATS)} are not supported",  # noqa: E501
        examples=list(SUPPORTED_RESPONSE_FORMATS),
    )
    speed: float = Field(1.0)
    sample_rate: int | None = Field(DEFAULT_SAMPLE_RATE, ge=MIN_SAMPLE_RATE, le=MAX_SAMPLE_RATE)


class VoiceListItem(BaseModel):
    index: int
    name: str


class VoiceListResponse(BaseModel):
    voices: list[VoiceListItem]


@app.get("/v1/audio/voices", response_model=VoiceListResponse)
async def list_voices():
    """
    Endpoint to list available voices with their indexes.
    """
    voice_list = [VoiceListItem(index=i, name=name) for i, name in enumerate(voice_names)]
    return VoiceListResponse(voices=voice_list)


# https://platform.openai.com/docs/api-reference/audio/createSpeech
@app.post("/v1/audio/speech")
async def synthesize(body: CreateSpeechRequestBody) -> StreamingResponse:
    input_ = body.input

    model = body.model
    # model = 'multi'

    speed = body.speed

    # response_format = body.response_format
    response_format = DEFAULT_RESPONSE_FORMAT

    # sample_rate = body.sample_rate
    sample_rate = DEFAULT_SAMPLE_RATE

    voice = body.voice
    if str(voice).isdecimal():
        voice = voice_names[int(voice)]
    voice_path: Path = voices[voice]

    LOG.info(f"input: {input}, {voice=}, {speed=}, {response_format=}, {sample_rate=}")
    if model == 'multi':
        wavs, phonemes = inference(model=model, text=input_, voice_audio=voice_path, speed=speed, alpha=0, beta=0,
                                   diffusion_steps=20, embedding_scale=1.0)
    else:
        wavs, phonemes = inference(model=model, text=input_, voice_audio=voice_path, speed=speed, alpha=1, beta=0,
                                   diffusion_steps=4, embedding_scale=1.0)
    # noinspection PyTypeChecker
    audio = gr.Audio((sample_rate, wavs), label="Audio:", autoplay=False, streaming=False, type="numpy",
                     format=response_format)
    # noinspection PyTypeChecker
    return convert_gradio_audio_to_streaming_response(audio=audio, response_format=response_format)


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).

    Returns
    -------
        HealthCheck: Returns a JSON response with the health status

    """
    return HealthCheck(status="OK")


if __name__ == '__main__':
    import uvicorn

    app = gr.mount_gradio_app(app, demo, path="/")
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv('PORT', 8000)), log_level="debug")
