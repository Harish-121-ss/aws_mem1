import unicodedata


def normalize_country(value: str) -> str:
    """
    Normalize a country label without restricting it to
    a fixed list of countries.

    Examples:
        India -> india
        INDIA -> india
        France -> france
    """
    if value is None:
        return ""

    value = str(value).strip()

    if not value:
        return ""

    value = unicodedata.normalize("NFKC", value)

    return " ".join(value.lower().split())


if __name__ == "__main__":
    examples = [
        "India",
        " INDIA ",
        "india",
        "France",
        "FRANCE",
        "",
    ]

    print("COUNTRY NORMALIZATION TEST")
    print("=" * 60)

    for value in examples:
        print(f"Original   : {repr(value)}")
        print(f"Normalized : {repr(normalize_country(value))}")
        print()