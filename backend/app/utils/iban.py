import re


def normalize_iban(iban: str) -> str:
    return re.sub(r"\s+", "", iban).upper()


def mask_iban(iban: str) -> str:
    iban = normalize_iban(iban)
    return f"{iban[:4]} {'*' * 4} {'*' * 4} {'*' * 4} {iban[-4:]}"


def validate_tr_iban(iban: str) -> bool:
    iban = normalize_iban(iban)
    if not iban.startswith("TR") or len(iban) != 26:
        return False
    rearranged = iban[4:] + iban[:4]
    numeric = ""
    for ch in rearranged:
        numeric += str(ord(ch) - 55) if ch.isalpha() else ch
    return int(numeric) % 97 == 1
