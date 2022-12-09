from random import choice

base64_alphabet = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
    'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
    'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '/',
]


def rand_base64(length: int) -> str:
    """ Returns a random base64 string of specified length (in chars)"""
    output = ''
    for i in range(0, length):
        output += choice(base64_alphabet)
    return output


def hex_to_bin(hex_num: str) -> str:
    """ Converts an hex str value into a str bin value """
    return bin(int('1' + hex_num, 16))[3:]


def has_leading_zeros(s: str, x: int) -> bool:
    """ Returns True if there are x leading zeros in a string, else False """
    return '1' not in s[0:x]  # Check if there is no '1' in the string s from char 0 to char x


def replace_all(s: str, charlist: list[str], new: str):
    out = s
    for ch in charlist:
        out = out.replace(ch, new)
    return out


def clean_filename(filename: str):
    """ Returns a safe string to be used as filename """
    return replace_all(filename[0:255], ['\\', '/', ':', '*', '?', '"', '<', '>', '|'], '_')
