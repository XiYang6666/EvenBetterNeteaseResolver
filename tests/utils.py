import random
import string

RAND_CHARS = string.ascii_letters + string.digits


def random_str(length: int | None = None):
    length = random.randint(5, 20) if length is None else length
    return "".join(random.choice(RAND_CHARS) for _ in range(length))
