import enum
import logging
from typing import Final

class TextFormat(enum.IntEnum):
    BOLD = 1
    FAINT = 2 
    ITALIC = 3
    UNDERLINE = 4
    STRIKETHROUGH = 9

class Color8(enum.IntEnum):
    # The basic 8 colors that will be supported by *any* terminal
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    DEFAULT_C = 39

class Formats:
    RESET: Final[str] = "\x1b[0m"

    @staticmethod
    def rich_txt(*args: TextFormat | Color8 | int) -> str:
        codes = [str(n.value) if isinstance(n, enum.IntEnum) else str(n) for n in args]
        return f"\x1b[{";".join(codes)}m"

    @staticmethod
    def background_8(color: Color8) -> int:
        return color + 10
    
    @staticmethod
    def foreground_256(color: int) -> str:
        return f"\x1b[38;5;{color}m"

    @staticmethod
    def background_256(color: int) -> str:
        return f"\x1b[48;5;{color}m]"
    
    @staticmethod
    def foreground_truecolor(r: int, g: int, b: int) -> str:
        return f"\x1b[38;2;{r};{g};{b}m"

    @staticmethod
    def background_truecolor(r: int, g: int, b: int) -> str:
        return f"\x1b[48;2;{r};{g};{b}m"
    
    @staticmethod
    def clear_screen() -> str:
        return "\x1b[2J"
    
    @staticmethod
    def reset_cursor() -> str:
        return "\x1b[H"
    
    @staticmethod
    def clear_line() -> str:
        return "\x1b[2K\r"
    
    @staticmethod
    def get_log_color(level: int) -> str:
        match(level):
            case logging.DEBUG:
                return Formats.rich_txt(TextFormat.BOLD, Color8.MAGENTA)
            case logging.INFO:
                return Formats.rich_txt(Color8.DEFAULT_C)
            case logging.WARNING:
                return Formats.rich_txt(TextFormat.BOLD, Color8.YELLOW)
            case logging.ERROR:
                return Formats.rich_txt(TextFormat.BOLD, Color8.RED)
            case logging.CRITICAL:
                return Formats.rich_txt(Formats.background_8(Color8.RED), TextFormat.BOLD, Color8.WHITE)
            case _:
                return ""