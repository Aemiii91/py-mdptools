from .types import Iterable
from . import bcolors


class Highlight:
    def __init__(self):
        self.bc = bcolors.disabled

    def __getitem__(self, indices) -> str:
        color, text = indices
        return color + text + self.bc.RESET

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
            self.bc = bcolors.enabled
        else:
            self.bc = bcolors.disabled


highlight = Highlight()
