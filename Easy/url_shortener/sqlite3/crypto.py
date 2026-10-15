import secrets
import string


ALPHABET = string.ascii_letters + string.digits    # a-z A-Z 0-9 = 62 symbols ("base62")
CODE_LENGTH = 7                                    # 62**7 is about 3.5 trillion possible codes

def create_code() -> str:
    # `secrets` is cryptographically secure, so codes can't be predicted. `random` is NOT safe for this.
    return ''.join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))
 

