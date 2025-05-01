import pytest

from app.stress_recovery import (
    recover_stress,
)

test_cases = [
    # Basic case with stress symbols and number conversion
    (
        "правильно читати `оцет, а не оц`ет. 25 разів повторював про той оцет.",
        "правильно читати оцет, а не оцет. двадцять п'ять разів повторював про той оцет.",
        "правильно читати `оцет, а не оц`ет. двадцять п'ять разів повторював про той оцет.",
    ),
    (
        "правильно читати `оцет, а не оц`ет. 25 разів повторював про той оцет.",
        "правильно читати оцет, а не оцет. двадцять п'ять разів повторював про той оцет.",
        "правильно читати `оцет, а не оц`ет. двадцять п'ять разів повторював про той оцет.",
    ),
    # Additional stress symbol at the end of a word
    (
        "правильно читати `оцет, а не оц`ет. 25 разів повторював про той `оцет.",
        "правильно читати оцет, а не оцет. двадцять п'ять разів повторював про той оцет.",
        "правильно читати `оцет, а не оц`ет. двадцять п'ять разів повторював про той `оцет.",
    ),
    # Stress in different positions and number conversion
    (
        "правильно читати `оцет, а не 23 оц`ет. 25 разів повторював про той оц`ет.",
        "правильно читати оцет, а не двадцять три оцет. двадцять п'ять разів повторював про той оцет.",
        "правильно читати `оцет, а не двадцять три оц`ет. двадцять п'ять разів повторював про той оц`ет.",
    ),
    # Single word with stress
    ("оцет`", "оцет", "оцет`"),
    # Number converted to multiple words, stress on following word
    ("25 разів`", "двадцять п'ять разів", "двадцять п'ять разів`"),
    # Multiple words with stress
    ("привіт` світ`", "привіт світ", "привіт` світ`"),
    # Punctuation handling
    ("оцет`, оцет.", "оцет, оцет.", "оцет`, оцет."),
    # Stress on number (should not propagate)
    ("25` разів`", "двадцять п'ять разів", "двадцять п'ять разів`"),
]


# Parametrize the test function
@pytest.mark.parametrize("original, verbalized, expected", test_cases)
def test_recover_stress(original, verbalized, expected):
    stress_symbol = "`"
    result = recover_stress(original, verbalized, stress_symbol)
    assert result == expected, f"Expected:\n{expected}\nGot:\n{result}"
