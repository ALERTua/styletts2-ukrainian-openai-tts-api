import string


def is_number(token: str, stress_symbol: str) -> bool:
    cleaned = token.replace(stress_symbol, '')
    cleaned = cleaned.rstrip(string.punctuation)
    return cleaned.isdigit()


def clean_token(token: str, stress_symbol: str) -> str:
    cleaned = token.replace(stress_symbol, '')
    return cleaned.rstrip(string.punctuation)


def apply_stress(original_token: str, verbalized_word: str, stress_symbol: str) -> str:
    stress_positions = [i for i, c in enumerate(original_token) if c == stress_symbol]
    base = original_token.replace(stress_symbol, '')
    if base != verbalized_word:
        return verbalized_word

    chars = list(verbalized_word)
    for pos in reversed(stress_positions):
        if pos <= len(chars):
            chars.insert(pos, stress_symbol)

    return ''.join(chars)


def recover_stress(original_input: str, verbalized_text: str, stress_symbol: str) -> str:
    original_tokens = original_input.split()
    verbalized_words = verbalized_text.split()

    i = 0
    j = 0
    result = []

    while i < len(original_tokens) and j < len(verbalized_words):
        current_orig = original_tokens[i]
        if is_number(current_orig, stress_symbol=stress_symbol):
            next_non_number_idx = i + 1
            while (next_non_number_idx < len(original_tokens) and
                   is_number(original_tokens[next_non_number_idx], stress_symbol=stress_symbol)):
                next_non_number_idx += 1
            if next_non_number_idx < len(original_tokens):
                next_non_number_token = original_tokens[next_non_number_idx]
                cleaned_next = clean_token(next_non_number_token, stress_symbol=stress_symbol)
                pos = None
                for k in range(j, len(verbalized_words)):
                    if clean_token(verbalized_words[k], stress_symbol=stress_symbol) == cleaned_next:
                        pos = k
                        break

                if pos is not None:
                    result.extend(verbalized_words[j:pos])
                    j = pos
                    i = next_non_number_idx
                else:
                    result.extend(verbalized_words[j:])
                    j = len(verbalized_words)
                    i = next_non_number_idx
            else:
                result.extend(verbalized_words[j:])
                j = len(verbalized_words)
                i = len(original_tokens)
        else:
            cleaned_orig = clean_token(current_orig, stress_symbol=stress_symbol)
            if (j < len(verbalized_words) and
                    clean_token(verbalized_words[j], stress_symbol=stress_symbol) == cleaned_orig):
                stressed_word = apply_stress(current_orig, verbalized_words[j],
                                             stress_symbol=stress_symbol)
                result.append(stressed_word)
                j += 1
                i += 1
            else:
                result.append(verbalized_words[j])
                j += 1

    result.extend(verbalized_words[j:])
    return ' '.join(result)


if __name__ == '__main__':
    original = "правильно читати `оцет, а не оц`ет. 25 разів повторював про той оцет."
    verbalized = "правильно читати оцет, а не оцет. двадцять п'ять разів повторював про той оцет."

    print(recover_stress(original, verbalized, '`'))
