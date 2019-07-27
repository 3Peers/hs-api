import random
import re
import string as string_base

VALID_EMAIL_REGEX = r'[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)' \
    r'*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?'


def generate_random_string(length=6):
    alpha_numeric_chars = string_base.ascii_letters + string_base.digits
    random_string = ''.join(random.choice(alpha_numeric_chars)
                            for i in range(length))

    return random_string


def is_valid_email(email: str):
    return email and len(email) > 6 and re.match(VALID_EMAIL_REGEX, email)
