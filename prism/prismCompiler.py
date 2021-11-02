from typing import Dict
from mdptools.mdp import MarkovDecisionProcess
from os import makedirs, path


class PrismCompiler:
    mdp: MarkovDecisionProcess = None
    stateMap: Dict[str, int] = None
    filePath: str = None

    _fileContent = ""
    _currentState = -1
    _currentTransition = ""
    _currentTargetState = -1
    _nextStateId = 0
    _hasVisitedState = False

    def __init__(self, mdp: MarkovDecisionProcess, filePath: str):
        self.mdp = mdp
        self.stateMap = {}
        self.filePath = filePath
        self.initPrismFile(mdp)

    def callback(self, path: list[str], value: float) -> None:
        print(path, "----", value)
        result = ""
        if (
            self._currentState != self.getStateId(path[0])
            or self._currentTransition != path[1]
        ):
            result = ";" if self._hasVisitedState else result
            result += "\n\t"
            self._hasVisitedState = True
            self._currentState = self.getStateId(path[0])
            self._currentTransition = path[1]
            result += f"[{path[1]}] s={self.getStateId(path[0])} -> {self.getTransitionString(value, path[2])}"
        else:
            result = f"+ {self.getTransitionString(value, path[2])}"

        print(result)
        print("\n")
        self._fileContent += result

    def getStateId(self, state) -> int:
        if state not in self.stateMap:
            self.stateMap[state] = self._nextStateId
            self._nextStateId = self._nextStateId + 1

        return self.stateMap[state]

    def getTransitionString(self, value: int, to: str) -> str:
        return str(value) + " : (s'= " + str(self.getStateId(to)) + ")"

    def initPrismFile(self, mdp: MarkovDecisionProcess) -> None:
        content = f"mdp\nmodule generated\n\ts : [0..{len(mdp.S)}] init 0;\n"

        self._fileContent += content

    def finish(self) -> None:
        self._fileContent += (
            ";" if self._hasVisitedState else self._fileContent
        )
        self._fileContent += "\nendmodule"
        self.writeToFile(self._fileContent)

    def writeToFile(
        self,
        content: str,
    ) -> None:
        at_root = lambda filename: path.join(
            path.dirname(__file__), "..", filename
        )

        if not path.exists(at_root("prismFiles/")):
            makedirs(at_root("prismFiles/"))

        with open(
            at_root(f"prismFiles/{self.filePath}"),
            "w+",
            encoding="utf-8",
        ) as f:
            f.write(content)
