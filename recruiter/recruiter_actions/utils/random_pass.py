import random
import string

def random_password_generation(length=10, allowed_chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(allowed_chars) for _ in range(length))