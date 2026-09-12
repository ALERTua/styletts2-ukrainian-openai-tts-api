import pytest

from app.voices import (
    parse_voices,
)

API_NAME = "/synthesize"
PARAMETER_NAME = "voice_name"


def api_info(parameters) -> dict:
    return {"named_endpoints": {API_NAME: {"parameters": parameters}}}


def voice_parameter(parameter_type) -> dict:
    return {"parameter_name": PARAMETER_NAME, "type": parameter_type}


test_cases = [
    # The shape the live Gradio app returns: other parameters first, the voices last
    (
        api_info(
            [
                {"parameter_name": "model_name", "type": {"type": "string"}},
                voice_parameter({"type": "string", "enum": ["Марина Панас", "Гаська Шиян"]}),
            ],
        ),
        ["Марина Панас", "Гаська Шиян"],
    ),
    # Entries that are not usable names are dropped one by one, the rest survive
    (api_info([voice_parameter({"enum": [None, "", 5, "Гаська Шиян"]})]), ["Гаська Шиян"]),
    # The parameter is there but advertises no choices at all
    (api_info([voice_parameter({"enum": []})]), []),
    (api_info([voice_parameter({"type": "string"})]), []),
    (api_info([voice_parameter("string")]), []),
    # The parameter itself is missing
    (api_info([{"parameter_name": "model_name", "type": {"enum": ["multi"]}}]), []),
    (api_info([]), []),
    # Shapes the description is not supposed to have, but must not raise on
    (api_info(["voice_name"]), []),
    (api_info({"voice_name": {}}), []),
    (api_info(None), []),
    ({"named_endpoints": {}}, []),
    ({"named_endpoints": {API_NAME: {}}}, []),
    ({}, []),
    ([], []),
    (None, []),
]


@pytest.mark.parametrize(("info", "expected"), test_cases)
def test_parse_voices(info, expected):
    assert parse_voices(info, API_NAME, PARAMETER_NAME) == expected
