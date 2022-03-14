from string import ascii_lowercase, ascii_uppercase, ascii_uppercase
"""
Validator functions for input data validation
"""


def username_validator(username):
    """
    Function that validates username input data
    """
    counter = 0
    special_characters = "-_"
    for char in username:
        if char.isdigit() or char.isalpha() or char in special_characters:
            counter += 1
    return counter == len(username)


def password_validator(password):
    """
    Function that valitades password input data
    """
    counter = 0
    for char in password:
        if char.isdigit() or char.isalpha():
            counter += 1
    return counter == len(password)


def country_set_validator(value):
    counter = 0
    for char in value:
        if char in ascii_uppercase or char in ascii_lowercase or char == ",":
            counter += 1
    return counter == len(value)


def country_validator(value):
    counter = 0
    for char in value:
        if char in ascii_uppercase or char in ascii_lowercase:
            counter += 1
    return counter == len(value)
