import difflib


def recover_stress(original_input: str, verbalized_text: str, stress_symbol: str) -> str:
    """
    Recovers stress symbols in the verbalized text based on the original input.

    This function takes an original input string with stress symbols, a verbalized text string without stress symbols,
    and a stress symbol. It aligns the de-stressed version of the original input with the verbalized text and then
    re-applies the stress symbols to the verbalized text where appropriate.

    Args:
        original_input (str): The original input string with stress symbols.
        verbalized_text (str): The verbalized text string without stress symbols.
        stress_symbol (str): The symbol used to indicate stress in the original input.

    Returns:
        str: The verbalized text with stress symbols re-applied where appropriate.

    """
    # Step 1: Tokenize original input and create de-stressed version
    original_tokens = original_input.split()
    original_de_stressed_tokens = [token.replace(stress_symbol, "") for token in original_tokens]

    # Step 2: Tokenize verbalized text
    verbalized_tokens = verbalized_text.split()

    # Step 3: Align de-stressed tokens with verbalized tokens
    matcher = difflib.SequenceMatcher(None, original_de_stressed_tokens, verbalized_tokens)
    alignment = matcher.get_opcodes()

    # Step 4: Prepare a list to hold the modified verbalized tokens
    modified_tokens = list(verbalized_tokens)

    # Step 5: Apply stress symbols to matching tokens
    for tag, i1, i2, j1, j2 in alignment:
        if tag == "equal":
            for i in range(i2 - i1):
                original_index = i1 + i
                verbalized_index = j1 + i

                if verbalized_index < len(modified_tokens):
                    # Replace the verbalized token with the original (with stress)
                    modified_tokens[verbalized_index] = original_tokens[original_index]

    # Step 6: Reconstruct the final text
    return " ".join(modified_tokens)
