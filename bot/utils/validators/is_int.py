from validators.utils import validator
import string


@validator
def is_int(value):
    digit = string.digits
    for s in value:
        if s not in digit:
            return not s
    return True
