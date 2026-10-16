ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)
INDEX = {c: i for i, c in enumerate(ALPHABET)}


def encode(n: int) -> str:
    """int -> code. 1_000_000 -> '4c92'  (62^3 = 238,328 values fit in 4 chars)."""
    if n == 0:
        return ALPHABET[0]
    digits = []
    while n:
        n, r = divmod(n, BASE)
        digits.append(ALPHABET[r])
    return "".join(reversed(digits))


def decode(code: str) -> int:
    """code -> int. '4c92' -> 1_000_000  (recover the row's id)."""
    n = 0
    for c in code:
        n = n * BASE + INDEX[c]
    return n