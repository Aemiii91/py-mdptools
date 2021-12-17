from ..types import (
    MarkovDecisionProcess as MDP,
    ActionMap,
    SetMethod,
    State,
    Callable,
)
from ..model import state

from .format_str import to_identifier
from .utils import id_register, minmax_register, write_file


def to_prism(
    mdp: MDP, file_path: str = None, set_method: SetMethod = None
) -> tuple[str, dict[State, ActionMap]]:
    """Compiles an MDP to the Prism Model Checler language"""
    pid = (
        {p: i for i, p in enumerate(mdp.processes)}
        if not mdp.is_process
        else {mdp: 0}
    )

    uid = [id_register() for _ in pid]
    uid_w = state_register(mdp, uid, pid)

    for p in mdp.processes:
        for s in p._get_states_from_transitions():
            uid[pid[p]](s)

    register = minmax_register()
    buffer = ""
    trs = []
    _ = uid_w(mdp.init)

    state_space = {}

    # Perform a breadth-first-search to collect all global transitions
    for s, act, _ in mdp.bfs(set_method=set_method, silent=True):
        state_space[s] = act
        # Compile string for the left side of the arrow
        pre = " & ".join(
            [uid_w(s)] + [f"{k}={register(k, v)}" for k, v in s.ctx.items()]
        )
        for a, distributions in act.items():
            for dist in distributions:
                # Compile string for the right side of the arrow
                post = []
                for s_prime, p_value in dist.items():
                    # Compile the update string
                    update = " & ".join(
                        [uid_w(s_prime, update=True)]
                        + [
                            f"({k}'={register(k, v)})"
                            for k, v in s_prime.ctx.items()
                            if k not in s.ctx or s.ctx[k] != v
                        ]
                    )
                    post += [
                        f"{p_value} : {update}"
                        if p_value != 1.0
                        else f"{update}"
                    ]
                # Add the global transition
                trs += [f"  [{a}] {pre} -> " + " + ".join(post) + ";\n"]

    buffer += "mdp\n"
    buffer += "\n"
    buffer += f"module {to_identifier(mdp.name)}\n"
    for name, last_id, state_ids in [
        (f"p{i}", *c()) for i, c in enumerate(uid)
    ]:
        buffer += f"  {name} : [0..{last_id}] init 0;\n"
        # List state names
        buffer += "".join(
            [
                f"  // {_id} : {state_name}\n"
                for state_name, _id in state_ids.items()
            ]
        )
    # List other variables (the objects of the system)
    buffer += "".join(
        [
            f"  {k} : [{_min}..{_max}] init {mdp.init.ctx.get(k, 0)};\n"
            for k, (_min, _max) in register().items()
        ]
    )
    buffer += "\n"
    # List the transitions
    buffer += "".join(trs)
    buffer += "endmodule"

    write_file(file_path, buffer)
    return (buffer, state_space)


def state_register(mdp: MDP, uid: list, pid: dict[MDP, int]) -> Callable:
    def on_process(s: State, update: bool = False) -> str:
        return (
            f"(s'={uid[0](state(s.s))})"
            if update
            else f"s={uid[0](state(s.s))}"
        )

    if mdp.is_process:
        return on_process

    def on_system(global_state: State, update: bool = False) -> str:
        local_states = [(p, global_state(p)) for p in pid.keys()]
        values = [(f"p{pid[p]}", uid[pid[p]](s)) for p, s in local_states]
        string = " & ".join(
            [f"({k}'={v})" if update else f"{k}={v}" for k, v in values]
        )
        return string

    return on_system
