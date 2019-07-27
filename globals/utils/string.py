from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
import random
import string as string_base


def generate_random_string(length=6):
    alpha_numeric_chars = string_base.ascii_letters + string_base.digits
    random_string = ''.join(random.choice(alpha_numeric_chars)
                            for i in range(length))

    return random_string


def is_valid_email(email: str):
    is_valid = True
    try:
        EmailValidator()(email)
    except ValidationError:
        is_valid = False

    return is_valid
