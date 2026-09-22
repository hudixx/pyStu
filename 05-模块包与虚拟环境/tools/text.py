"""tools 包里的子模块，对标 Java 的 com.xxx.tools.Text。"""


def shout(text: str) -> str:
    """把字符串变大写并加感叹号。"""
    return text.upper() + "!"
