import doctest


def repeat(text: str, times: int) -> str:
    if times < 0:
        raise ValueError('times cannot be negative')
    return text*times


if __name__ == '__main__':
    print(repeat("ab", 2))