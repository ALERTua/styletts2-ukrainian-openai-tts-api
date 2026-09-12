def parse_voices(api_info: dict, api_name: str, parameter_name: str) -> list[str]:
    """
    Return the voice names a Gradio API description advertises for one parameter.

    Never raises: any shape the description does not have yields an empty list.
    """
    try:
        parameters = api_info["named_endpoints"][api_name]["parameters"]
    except (AttributeError, IndexError, KeyError, TypeError):
        return []

    if not isinstance(parameters, list):
        return []

    for parameter in parameters:
        if not isinstance(parameter, dict) or parameter.get("parameter_name") != parameter_name:
            continue

        parameter_type = parameter.get("type")
        choices = parameter_type.get("enum") if isinstance(parameter_type, dict) else None
        if not isinstance(choices, list):
            return []

        return [choice for choice in choices if isinstance(choice, str) and choice]

    return []
