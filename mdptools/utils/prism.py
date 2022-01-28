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
    mdp: MDP,
    file_path: str = None,
    set_method: SetMethod = None,
    process_id: int = 0,
    no_header: bool = False,
    convert_goal_states: bool = False,
) -> tuple[str, dict[State, ActionMap]]:
    """Compiles an MDP to the Prism Model Checler language"""
    pid = (
        {p: i for i, p in enumerate(mdp.processes)}
        if not mdp.is_process
        else {mdp: process_id}
    )

    uid_w = state_register(mdp, pid)

    register = minmax_register()
    buffer = ""
    trs = []

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

    if not no_header:
        buffer += "mdp\n"
        buffer += "\n"

    buffer += f"module {to_identifier(mdp.name)}\n"

    converted_goal_states = [[] for _ in mdp.goal_states]

    for i, uid_i in uid_w():
        name, last_id, state_ids = (f"p{i}", *uid_i())
        process = mdp.processes[i - process_id]
        s_init = state(mdp.init(process))
        real_names = {
            _id: state_name.to_str(parent=process)
            for state_name, _id in state_ids.items()
        }
        buffer += f"  {name} : [0..{last_id}] init {uid_i(s_init)};\n"
        # List state names
        buffer += "".join(
            [
                f"  // {_id} : {real_name}\n"
                for _id, real_name in real_names.items()
            ]
        )
        for idx, goal_state in enumerate(mdp.goal_states):
            for _id, real_name in real_names.items():
                if real_name in goal_state:
                    converted_goal_states[idx] += [f"{name}={_id}"]

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

    if convert_goal_states:
        return (buffer, state_space, converted_goal_states)

    return (buffer, state_space)


def to_prism_components(mdp: MDP, file_path: str = None) -> str:
    buffer = "mdp\n\n"
    buffer += "\n\n".join(
        to_prism(process, process_id=pid, no_header=True)[0]
        for pid, process in enumerate(mdp.processes)
    )
    write_file(file_path, buffer)
    return buffer


def state_register(mdp: MDP, pid: dict[MDP, int]) -> Callable:
    uid = {i: id_register() for i in pid.values()}

    for p, i in pid.items():
        local_states = p._get_states_from_transitions()
        for s in local_states:
            uid[i](state(s))

    def on_process(s: State = None, update: bool = False) -> str:
        if not s:
            return uid.items()
        i = list(pid.values())[0]
        value = uid[i](state(s.s))
        return f"(p{i}'={value})" if update else f"p{i}={value}"

    if mdp.is_process:
        return on_process

    def on_system(global_state: State = None, update: bool = False) -> str:
        if not global_state:
            return uid.items()
        local_states = [(i, state(global_state(p))) for p, i in pid.items()]
        values = [(f"p{i}", uid[i](s)) for i, s in local_states]
        string = " & ".join(
            [f"({k}'={v})" if update else f"{k}={v}" for k, v in values]
        )
        return string

    return on_system
