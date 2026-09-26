import re
import unicodedata


# Conservative address abbreviations.
ADDRESS_ABBREVIATIONS = {
    "rd": "road",
    "rd.": "road",
    "st": "street",
    "st.": "street",
    "ave": "avenue",
    "ave.": "avenue",
    "av": "avenue",
    "blvd": "boulevard",
    "blvd.": "boulevard",
    "dr": "drive",
    "dr.": "drive",
    "ln": "lane",
    "ln.": "lane",
    "hwy": "highway",
    "hwy.": "highway",
    "pkwy": "parkway",
    "pkwy.": "parkway",
    "ct": "court",
    "ct.": "court",
    "pl": "place",
    "pl.": "place",
}


def normalize_unicode(text: str) -> str:
    """Normalize Unicode while preserving multilingual text."""
    return unicodedata.normalize("NFKC", text)


def normalize_business_address(text: str) -> str:
    """
    Normalize a business address.

    The original address is never modified.
    """
    if text is None:
        return ""

    text = str(text).strip()

    if not text:
        return ""

    text = normalize_unicode(text)

    # Lowercase
    text = text.lower()

    # Normalize ampersand
    text = text.replace("&", " and ")

    # Preserve Unicode letters, digits, and combining marks.
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

    # Tokenize
    tokens = text.split()

    # Normalize common address abbreviations
    normalized_tokens = []

    for token in tokens:
        normalized_tokens.append(
            ADDRESS_ABBREVIATIONS.get(token, token)
        )

    return " ".join(normalized_tokens)


def tokenize_address(text: str) -> list[str]:
    """Return normalized address tokens."""
    normalized = normalize_business_address(text)

    if not normalized:
        return []

    return normalized.split()


def extract_address_numbers(text: str) -> list[str]:
    """
    Extract numeric clues from an address.

    Examples:
        17560 Ellis Road -> ['17560']
        1111 Church Street, Unit 2007 -> ['1111', '2007']
    """
    if text is None:
        return []

    text = str(text)

    return re.findall(r"\d+", text)


def extract_postal_codes(text: str) -> list[str]:
    """
    Extract likely postal/PIN codes from the END of an address.

    Supported patterns:
    - US ZIP code: 5 digits
    - US ZIP+4: 12345-6789
    - Indian PIN code: 6 digits

    Restricting the match to the end prevents a house number such as
    17560 from being incorrectly treated as a postal code.
    """
    if text is None:
        return []

    text = str(text).strip()

    if not text:
        return []

    # Normalize repeated whitespace
    text = re.sub(r"\s+", " ", text)

    matches = []

    # US ZIP / ZIP+4 at the end of the address
    us_matches = re.findall(
        r"(?:^|[\s,])(\d{5}(?:-\d{4})?)(?:\s*$)",
        text,
    )

    matches.extend(us_matches)

    # Indian PIN at the end of the address
    india_matches = re.findall(
        r"(?:^|[\s,])(\d{6})(?:\s*$)",
        text,
    )

    matches.extend(india_matches)

    # Remove duplicates while preserving order
    return list(dict.fromkeys(matches))


if __name__ == "__main__":
    examples = [
        "12 Gandhi Road, Coimbatore",
        "12 Gandhi Rd., Coimbatore",
        "105 ELM ST, MORGANTON, NC",
        "No. 45, Anna Nagar, Chennai 600040",
        "17560 Ellis Road, Tahlequah, OK",
        "Mack Rd, Haltom City, Texas",
        "",
        "Near SBI ATM, Main Road",
    ]

    print("BUSINESS ADDRESS NORMALIZATION TEST")
    print("=" * 70)

    for value in examples:
        print(f"\nOriginal   : {value}")
        print(f"Normalized : {normalize_business_address(value)}")
        print(f"Tokens     : {tokenize_address(value)}")
        print(f"Numbers    : {extract_address_numbers(value)}")
        print(f"Postal/PIN : {extract_postal_codes(value)}")