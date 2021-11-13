import math

from .types import (
    MarkovDecisionProcess as MDP,
    ActionMap,
    State,
    SetMethod,
    Generator,
    Callable,
    Transition,
)
from .utils import (
    logger,
    log_info_enabled,
    highlight as _h,
    ordered_state_str,
    get_terminal_width,
)
from queue import Queue, LifoQueue, SimpleQueue


def search(
    mdp: MDP,
    s: State = None,
    set_method: SetMethod = None,
    include_level: bool = False,
    queue: Queue = LifoQueue,
    silent: bool = False,
) -> Generator[tuple[State, ActionMap], None, None]:
    """Performs a classic search on an MDP, or optionally a selective search if
    `set_method` is supplied
    """
    if set_method is None:
        set_method = mdp.set_method

    queue = queue()
    transition_map = {}

    if s is None:
        s = mdp.init

    _log_begin(mdp, s, set_method, silent)

    # Add the initial state
    queue.put((s, 0))

    while not queue.empty():
        s, level = queue.get()
        if s not in transition_map:
            # Register the global state
            transition_map[s] = {}
            # Check if s has enabled transitions
            trs = mdp.enabled(s)
            _log_visit(mdp, s, trs, set_method, level, silent)
            # Apply set_method if available and more than one transition is enabled in s
            if isinstance(set_method, Callable) and len(trs) > 1:
                trs = set_method(mdp, s)
            # Expand the transitions
            for tr in trs:
                # Get the successor states for the transition
                successors = tr.successors(s)
                transition_map[s][tr.action] = successors
                # Add the discovered states to the queue
                for succ in successors.keys():
                    queue.put((succ, level + 1))
                _log_enqueue(mdp, successors, silent)

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


def _log_begin(mdp: MDP, s: State, set_method: SetMethod, silent: bool):
    if not silent and log_info_enabled():
        line_width = get_terminal_width()
        set_method_name = (
            set_method.__name__
            if isinstance(set_method, Callable)
            else "classic"
        )
        title = f"SEARCH STARTED [{set_method_name}]"
        pad_left = int(math.floor((line_width - len(title)) / 2 - 2))
        pad_right = int(math.ceil((line_width - len(title)) / 2 - 2))
        logger.info(
            "\n%s %s [%s] %s\n",
            _h.comment("-" * pad_left),
            _h.ok("SEARCH STARTED"),
            _h.function(set_method_name),
            _h.comment("-" * pad_right),
        )
        logger.info(
            "Q <- %s",
            ordered_state_str(s, mdp, ",", lambda st: _h.state(st)),
        )


def _log_visit(
    mdp: MDP,
    s: State,
    T: list[Transition],
    set_method: SetMethod,
    level: int,
    silent: bool,
):
    if not silent and log_info_enabled():
        logger.info(
            "\n%s:%d {%s}%s",
            _h.function("VISIT"),
            level,
            ordered_state_str(s, mdp, ",", lambda st: _h.state(st)),
            f"\n-> <{next(iter(T))}>"
            if len(T) == 1
            else f" [{_h.error('DEADLOCK')}]"
            if len(T) == 0
            else "\n-> enabled(s)"
            if not isinstance(set_method, Callable)
            else "",
        )


def _log_enqueue(mdp: MDP, successors: dict[State, float], silent: bool):
    if not silent and log_info_enabled():
        logger.info(
            "Q <- {%s}",
            "}, {".join(
                ordered_state_str(s, mdp, ",", lambda st: _h.state(st))
                for s in successors.keys()
            ),
        )
