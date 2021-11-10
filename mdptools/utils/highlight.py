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

    @property
    def state(self):
        return self.bc.LIGHTCYAN

    @property
    def action(self):
        return self.bc.LIGHTGREEN

    @property
    def function(self):
        return self.bc.LIGHTBLUE

    @property
    def variable(self):
        return self.bc.PINK

    @property
    def string(self):
        return self.bc.YELLOW

    @property
    def comment(self):
        return self.bc.LIGHTGREY

    @property
    def ok(self):
        return self.bc.LIGHTGREEN

    @property
    def fail(self):
        return self.bc.LIGHTRED

    @property
    def error(self):
        return self.bc.RED

    @property
    def numeral(self):
        return self.bc.ORANGE

    @property
    def types(self):
        return self.bc.GREEN

    @property
    def note(self):
        return self.bc.PURPLE

    @property
    def reset(self):
        return self.bc.RESET

    def use_colors(self, value: bool = True):
        if value:
            self.bc = COLORS_ENABLED
        else:
            self.bc = COLORS_DISABLED


highlight = Highlight()
