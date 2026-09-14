# divide.py
def divide(a, b):
    # Return the quotient of a and b, raising on division errors
    try:
        return a / b
    except ZeroDivisionError as err:
        raise ValueError("division by zero is not allowed") from err