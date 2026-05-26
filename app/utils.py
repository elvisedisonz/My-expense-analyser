import re


REMOVE_WORDS = {
    "UPI", "NEFT", "IMPS", "MB", "TRANSFER", "TO", "BY",
    "BANK", "PAYMENT", "DR", "CR", "WDL", "TFR", "DBSS",
    "SBIN", "YESB", "HDFC", "ICICI", "AXIS", "KKBK",
    "UBIN", "PYTM", "APL", "TXN", "INFO", "CNRB", "AT",
}


def clean_name(text: str) -> str:
    text = str(text).strip()

    if "UPI/DR/" in text.upper():
        parts = [p.strip() for p in text.split("/")]

        try:
            dr_index = parts.index("DR")
            remaining = parts[dr_index + 1:]

            if len(remaining) >= 5:
                name_parts = remaining[1:-3]
                name = "/".join(name_parts).strip()

                if name:
                    name = re.sub(r"\s+", " ", name)
                    return name.title()

        except Exception:
            pass

    text = text.upper()
    text = re.sub(r"[/_:.-]", " ", text)
    text = re.sub(r"[^A-Z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    words = [
        w for w in text.split()
        if w not in REMOVE_WORDS
        and not re.fullmatch(r"\d{6,}", w)
        and len(w) > 2
    ]

    return " ".join(words[:3]).title() if words else "Unknown"


def extract_notes(text: str) -> str:
    text = str(text).strip()

    if "/" not in text:
        return ""

    return text.rsplit("/", 1)[-1].split()[0].strip()


def build_tx_id(index: int, details: str) -> str:
    details = str(details)

    upi_match = re.search(r"([A-Z0-9._-]+@[A-Z]+)", details.upper())

    if upi_match:
        return f"{upi_match.group(1)}_{index}"

    return f"TX_{index}"
