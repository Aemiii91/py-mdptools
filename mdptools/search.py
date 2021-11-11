from .types import (
    MarkovDecisionProcess as MDP,
    ActionMap,
    State,
    SetMethod,
    Generator,
    Callable,
)
from queue import Queue, LifoQueue, SimpleQueue


def search(
    mdp: MDP,
    s: State = None,
    set_method: SetMethod = None,
    include_level: bool = False,
    queue: Queue = LifoQueue,
) -> Generator[tuple[State, ActionMap], None, None]:
    """Performs a classic search on an MDP, or optionally a selective search if
    `set_method` is supplied
    """
    from .mdp import MarkovDecisionProcess

    if set_method is None:
        set_method = mdp.set_method
    if not isinstance(set_method, Callable):
        set_method = MarkovDecisionProcess.enabled

    queue = queue()
    transition_map = {}

    # Add the initial state
    queue.put((s or mdp.init, 0))

    while not queue.empty():
        s, level = queue.get()
        if s not in transition_map:
            # Register the global state
            transition_map[s] = {}
            # Iterate all transitions returned by `set_method`
            for tr in set_method(mdp, s):
                # Get the successor states for the transition
                successors = tr.successors(s)
                transition_map[s][tr.action] = successors
                # Add the discovered states to the queue
                for succ in successors.keys():
                    queue.put((succ, level + 1))

            ret = (s, transition_map[s])
            if include_level:
                ret = (*ret, level)
            yield ret


def bfs(
    mdp: MDP, s: State = None, **kw
) -> Generator[tuple[State, ActionMap, int], None, None,]:
    """Performs a breadth-first-search on an MDP"""
    kw = {"include_level": True, **kw, "queue": SimpleQueue}
    return search(mdp, s, **kw)
