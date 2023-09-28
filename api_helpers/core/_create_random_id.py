def _create_random_id(length: int) -> str:
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))