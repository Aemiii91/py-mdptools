class bcolors:
    RESET = '\033[0m'
    BOLD = '\033[01m'
    DISABLE = '\033[02m'
    UNDERLINE = '\033[04m'
    REVERSE = '\033[07m'
    STRIKETHROUGH = '\033[09m'
    INVISIBLE = '\033[08m'

    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    ORANGE = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    LIGHTGREY = '\033[37m'
    DARKGREY = '\033[90m'
    LIGHTRED = '\033[91m'
    LIGHTGREEN = '\033[92m'
    YELLOW = '\033[93m'
    LIGHTBLUE = '\033[94m'
    PINK = '\033[95m'
    LIGHTCYAN = '\033[96m'

    class bg:
        BLACK = '\033[40m'
        RED = '\033[41m'
        GREEN = '\033[42m'
        ORANGE = '\033[43m'
        BLUE = '\033[44m'
        PURPLE = '\033[45m'
        CYAN = '\033[46m'
        LIGHTGREY = '\033[47m'


class bcolors_disable:
    RESET = ''
    BOLD = ''
    DISABLE = ''
    UNDERLINE = ''
    REVERSE = ''
    STRIKETHROUGH = ''
    INVISIBLE = ''

    BLACK = ''
    RED = ''
    GREEN = ''
    ORANGE = ''
    BLUE = ''
    PURPLE = ''
    CYAN = ''
    LIGHTGREY = ''
    DARKGREY = ''
    LIGHTRED = ''
    LIGHTGREEN = ''
    YELLOW = ''
    LIGHTBLUE = ''
    PINK = ''
    LIGHTCYAN = ''

    class bg:
        BLACK = ''
        RED = ''
        GREEN = ''
        ORANGE = ''
        BLUE = ''
        PURPLE = ''
        CYAN = ''
        LIGHTGREY = ''


bc = bcolors

_marks = ['RESET', 'BOLD', 'DISABLE', 'UNDERLINE', 'REVERSE', 'STRIKETHROUGH', 'INVISIBLE']

if __name__ == '__main__':
    for color in dir(bc):
        if not color.startswith("_") and isinstance((attr := getattr(bc, color)), str) and color not in _marks:
            row_format = attr + "{:<14}" + " ".join([attr + getattr(bc, mark) + "{}" + bc.RESET for mark in _marks])
            print(row_format.format(color, *_marks))
# %%
