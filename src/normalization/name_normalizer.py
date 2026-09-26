import re
import unicodedata


# Common business-name abbreviations.
# Keep this mapping conservative to avoid over-normalization.
ABBREVIATIONS = {
    "pvt": "private",
    "pvt.": "private",
    "ltd": "limited",
    "ltd.": "limited",
    "corp": "corporation",
    "corp.": "corporation",
    "co": "company",
    "co.": "company",
    "inc": "incorporated",
    "inc.": "incorporated",
}


def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode text into a consistent representation.
    """
    return unicodedata.normalize("NFKC", text)


def normalize_business_name(text: str) -> str:
    """
    Normalize a business name while preserving Unicode scripts.

    The original business name is never modified.
    This function creates a separate normalized representation.
    """
    if text is None:
        return ""

    text = str(text).strip()

    if not text:
        return ""

    # Unicode normalization
    text = normalize_unicode(text)

    # Lowercase
    text = text.lower()

    # Normalize ampersand
    text = text.replace("&", " and ")

    # Preserve Unicode letters, digits, and combining marks.
    # Replace punctuation/symbols with spaces.
    cleaned = []

    for char in text:
        category = unicodedata.category(char)

        if char.isspace():
            cleaned.append(" ")
        elif char.isalnum() or category.startswith("M"):
            cleaned.append(char)
        else:
            cleaned.append(" ")

    text = "".join(cleaned)

    # Split into tokens
    tokens = text.split()

    # Normalize common abbreviations
    normalized_tokens = []

    for token in tokens:
        normalized_tokens.append(
            ABBREVIATIONS.get(token, token)
        )

    # Rebuild normalized text
    return " ".join(normalized_tokens)


def tokenize_business_name(text: str) -> list[str]:
    """
    Convert a business name into normalized tokens.
    """
    normalized = normalize_business_name(text)

    if not normalized:
        return []

    return normalized.split()


def generate_character_ngrams(
    text: str,
    n: int = 3,
) -> list[str]:
    """
    Generate character n-grams from a normalized business name.

    These can later be reused by blocking or matching stages.
    """
    normalized = normalize_business_name(text)

    if not normalized:
        return []

    compact = normalized.replace(" ", "")

    if len(compact) < n:
        return [compact]

    return [
        compact[i:i + n]
        for i in range(len(compact) - n + 1)
    ]


if __name__ == "__main__":
    examples = [
        "ABC Pvt. Ltd.",
        "ABC PRIVATE LIMITED",
        "B+ Retail Inc",
        "O'Reilly & Sons",
        "International South Consultants Private Ltd",
        "राम मार्केटिंग प्राइवेट लिमिटेड",
    ]

    print("BUSINESS NAME NORMALIZATION TEST")
    print("=" * 60)

    for value in examples:
        print(f"\nOriginal   : {value}")
        print(f"Normalized : {normalize_business_name(value)}")
        print(f"Tokens     : {tokenize_business_name(value)}")
        print(
            f"3-grams    : "
            f"{generate_character_ngrams(value)[:10]}"
        )