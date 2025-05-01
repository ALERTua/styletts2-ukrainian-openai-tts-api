from __future__ import annotations

import io
import logging
import os
import time
from typing import Any, Literal

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response, StreamingResponse
from pydantic import BaseModel, Field

try:
    from .stress_recovery import recover_stress
except:  # noqa: E722
    from app.stress_recovery import recover_stress

import soundfile as sf
from dotenv import load_dotenv
from gradio_client import Client

load_dotenv()

STRESS_SYMBOL = "`"
STRESS_SYMBOL_REPLACEMENT = "\u0301"


def strtobool(val: str | bool | int) -> int:  # distutil strtobool
    """
    Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1", True, 1):
        return 1
    if val in ("n", "no", "f", "false", "off", "0", False, 0):
        return 0
    msg = f"invalid truth value {val!r}"
    raise ValueError(msg)


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
GRADIO_URL = os.getenv("GRADIO_URL", "http://gradio:7860")
AUTO_USE_VERBALIZER = strtobool(os.getenv("AUTO_USE_VERBALIZER", "1"))

type ResponseFormat = Literal["mp3", "flac", "wav", "pcm"]
SUPPORTED_RESPONSE_FORMATS = ("mp3", "wav")
UNSUPORTED_RESPONSE_FORMATS = ("opus", "aac", "flac", "pcm")
DEFAULT_RESPONSE_FORMAT = "wav"

DEFAULT_VOICE = "Марина Панас"

models = ["multi", "single"]
# noinspection PyTypeHints
type Model = Literal[*models]
DEFAULT_MODEL = models[0]

MIN_SAMPLE_RATE = 8000
MAX_SAMPLE_RATE = 48000
DEFAULT_SAMPLE_RATE = 24000

gr_client = None
while gr_client is None:
    try:
        gr_client = Client(GRADIO_URL)
    except Exception:
        LOG.exception("Failed to connect to gradio. Retrying in 10 seconds")
        time.sleep(10)


def convert_gradio_audio_to_streaming_response(
        filepath: str,
        response_format: ResponseFormat,
) -> StreamingResponse:
    """
    Convert a Gradio audio file to a streaming response.

    This function reads an audio file from the specified filepath, converts it to the
    specified response format, and returns it as a streaming response. The audio data
    is read using the `soundfile` library and written to an in-memory buffer, which is
    then used to create a `StreamingResponse`.

    Parameters
    ----------
    filepath : str
        The path to the audio file to be converted.
    response_format : ResponseFormat
        The format in which the audio data should be returned.

    Returns
    -------
    StreamingResponse
        A streaming response containing the audio data in the specified format.

    """
    audio_data, sample_rate = sf.read(filepath)
    audio_buffer = io.BytesIO()
    sf.write(audio_buffer, audio_data, samplerate=sample_rate, format=response_format)
    audio_buffer.seek(0)
    return StreamingResponse(audio_buffer, media_type=f"audio/{response_format}")


class CreateSpeechRequestBody(BaseModel):
    """
    Request body model for creating speech synthesis.

    This class represents the structure of the request body expected by the
    speech synthesis endpoint. It includes various attributes that define the
    parameters for generating speech, such as the text to be synthesized, the voice
    to be used, and other optional settings.

    Attributes
    ----------
    text : str
        The text to be synthesized into speech.
    voice : str
        The identifier of the voice to be used for synthesis.
    speed : float, optional
        The speed of the synthesized speech. Defaults to 1.0.
    pitch : float, optional
        The pitch of the synthesized speech. Defaults to 1.0.
    volume : float, optional
        The volume of the synthesized speech. Defaults to 1.0.

    """

    model: Model = Field(
        DEFAULT_MODEL,
        description=f"Model. Supported models are {', '.join(models)}.",
        examples=models,
    )
    input: str = Field(
        ...,
        description="The text to generate audio for. ",
        examples=[
            "A rainbow is an optical phenomenon caused by refraction,"
            " internal reflection and dispersion of light in water droplets resulting in a continuous spectrum"
            " of light appearing in the sky. The rainbow takes the form of a multicoloured circular arc."
            " Rainbows caused by sunlight always appear in the section of sky directly opposite the Sun."
            " Rainbows can be caused by many forms of airborne water."
            " These include not only rain, but also mist, spray, and airborne dew."
        ],
    )
    voice: str = Field(
        DEFAULT_VOICE,
        description="Audio voice name to use.",
    )
    language: Any | None = None
    response_format: ResponseFormat = Field(
        DEFAULT_RESPONSE_FORMAT,
        description=f"The format to audio in. Supported formats are"
                    f" {', '.join(SUPPORTED_RESPONSE_FORMATS)}."
                    f" {', '.join(UNSUPORTED_RESPONSE_FORMATS)} are not supported",
        examples=list(SUPPORTED_RESPONSE_FORMATS),
    )
    speed: float = Field(1.0)
    sample_rate: int | None = Field(DEFAULT_SAMPLE_RATE, ge=MIN_SAMPLE_RATE, le=MAX_SAMPLE_RATE)
    verbalize: bool | None = Field(AUTO_USE_VERBALIZER)


# https://platform.openai.com/docs/api-reference/audio/createSpeech
@app.post("/v1/audio/speech")
async def synthesize(body: CreateSpeechRequestBody) -> StreamingResponse:
    """
    Synthesize speech from the provided text.

    This endpoint takes a CreateSpeechRequestBody containing the text to be synthesized
    and returns a StreamingResponse with the synthesized audio.

    Parameters
    ----------
    body : CreateSpeechRequestBody
        The request body containing the text to be synthesized.

    Returns
    -------
    StreamingResponse
        A streaming response containing the synthesized audio.

    """
    input_ = body.input
    model_name = body.model
    speed = body.speed
    response_format = body.response_format
    sample_rate = body.sample_rate
    verbalize = body.verbalize
    voice = body.voice if model_name == "multi" else None

    LOG.info(f"{input_=}, {voice=}, {speed=}, {response_format=}, {sample_rate=}")
    if verbalize:
        original_input = input_
        try:
            verbalized_input = gr_client.predict(text=original_input.replace(STRESS_SYMBOL, ""), api_name="/verbalize")
            if STRESS_SYMBOL in original_input:
                input_ = recover_stress(original_input, verbalized_input, stress_symbol=STRESS_SYMBOL)
                input_ = input_.replace(STRESS_SYMBOL, STRESS_SYMBOL_REPLACEMENT)
                LOG.info(f"Verbalized and stress recovered input: {input_}")
            else:
                LOG.info(f"Verbalized input: {input_}")
        except Exception as e:
            msg = f"Error verbalizing speech: {e}"
            LOG.exception(msg)
            # noinspection PyTypeChecker
            return Response(content=msg, status_code=500)

        LOG.info(f"verbalized {input_=}, {voice=}, {speed=}, {response_format=}, {sample_rate=}")

    try:
        filepath = gr_client.predict(
            model_name=model_name,
            text=input_,
            speed=speed,
            voice_name=voice,
            api_name="/synthesize",
        )
    except Exception as e:
        msg = f"Error synthesizing speech: {e}"
        LOG.exception(msg)
        # noinspection PyTypeChecker
        return Response(content=msg, status_code=500)

    return convert_gradio_audio_to_streaming_response(filepath=filepath, response_format=response_format)


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
    ## Perform a Health Check.

    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).

    Returns
    -------
        HealthCheck: Returns a JSON response with the health status

    """
    return HealthCheck(status="OK")


@app.get("/")
async def root() -> RedirectResponse:
    """Redirect to the Gradio UI."""
    return RedirectResponse(url=GRADIO_URL)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("UVICORN_PORT", "8000")), log_level="debug")
