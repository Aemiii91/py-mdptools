# pylint: disable=too-few-public-methods,missing-docstring
class COLORS_ENABLED:
    RESET = "\033[0m"
    BOLD = "\033[01m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    ORANGE = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    LIGHTGREY = "\033[37m"
    DARKGREY = "\033[90m"
    LIGHTRED = "\033[91m"
    LIGHTGREEN = "\033[92m"
    YELLOW = "\033[93m"
    LIGHTBLUE = "\033[94m"
    PINK = "\033[95m"
    LIGHTCYAN = "\033[96m"


class COLORS_DISABLED:
    RESET = ""
    BOLD = ""

    BLACK = ""
    RED = ""
    GREEN = ""
    ORANGE = ""
    BLUE = ""
    PURPLE = ""
    CYAN = ""
    LIGHTGREY = ""
    DARKGREY = ""
    LIGHTRED = ""
    LIGHTGREEN = ""
    YELLOW = ""
    LIGHTBLUE = ""
    PINK = ""
    LIGHTCYAN = ""


class Highlight:
    def __init__(self):
        self.bc = COLORS_DISABLED

    def __call__(self, color: str, text: str) -> str:
        return color + f"{text}" + self.bc.RESET

    def state(self, text: str):
        return self.__call__(self.bc.LIGHTCYAN, text)

    def action(self, text: str):
        return self.__call__(self.bc.LIGHTGREEN, text)

    def function(self, text: str):
        return self.__call__(self.bc.LIGHTBLUE, text)

    def variable(self, text: str):
        return self.__call__(self.bc.PINK, text)

    def string(self, text: str):
        return self.__call__(self.bc.YELLOW, text)

    def comment(self, text: str):
        return self.__call__(self.bc.LIGHTGREY, text)

    def ok(self, text: str):
        return self.__call__(self.bc.LIGHTGREEN, text)

    def fail(self, text: str):
        return self.__call__(self.bc.LIGHTRED, text)

    def error(self, text: str):
        return self.__call__(self.bc.RED, text)

    def numeral(self, text: str):
        return self.__call__(self.bc.ORANGE, text)

    def types(self, text: str):
        return self.__call__(self.bc.GREEN, text)

    def note(self, text: str):
        return self.__call__(self.bc.PURPLE, text)

    def use_colors(self, value: bool = True):
        if value:
            self.bc = COLORS_ENABLED
        else:
            self.bc = COLORS_DISABLED


highlight = Highlight()
