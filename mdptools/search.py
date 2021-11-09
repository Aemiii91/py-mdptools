from .types import (
    MarkovDecisionProcess as MDP,
    ActionMap,
    State,
    SetMethod,
    Generator,
)
from queue import Queue, LifoQueue, SimpleQueue


def search(
    mdp: MDP,
    s: State = None,
    set_method: SetMethod = None,
    include_level: bool = False,
    queue: Queue = LifoQueue,
) -> Generator[tuple[State, ActionMap], SetMethod, None]:
    from .mdp import MarkovDecisionProcess

    if s is None:
        s = mdp.init
    if set_method is None:
        set_method = MarkovDecisionProcess.enabled

    queue = queue()
    transition_map = {}

    queue.put((s, 0))

    while not queue.empty():
        s, level = queue.get()
        if s not in transition_map:
            # Register the global state
            transition_map[s] = {}
            # Iterate transitions returned by callback
            for tr in set_method(mdp, s):
                # Get the successor states for the transition
                successors = tr.successors(s)
                transition_map[s][tr.action] = successors
                # Add the discovered states to the stack
                for succ in successors.keys():
                    queue.put((succ, level + 1))

            ret = (s, transition_map[s])
            if include_level:
                ret = (*ret, level)
            receive_change = yield ret

            if receive_change is not None:
                set_method = receive_change


def bfs(
    mdp: MDP, s: State = None, **kw
) -> Generator[tuple[State, ActionMap, int], SetMethod, None,]:
    return search(mdp, s, include_level=True, **kw, queue=SimpleQueue)
