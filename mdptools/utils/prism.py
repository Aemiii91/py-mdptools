from ..types import MarkovDecisionProcess as MDP, SetMethod
from .format_str import to_identifier
from .utils import id_register, minmax_register, write_file, ordered_state_str
from ..model import state


def to_prism(
    mdp: MDP, file_path: str = None, set_method: SetMethod = None
) -> str:
    """Compiles an MDP to the Prism Model Checler language"""
    uid = id_register()
    uid_w = lambda s: uid(state(s.s))
    register = minmax_register()
    buffer = ""
    trs = []
    init = uid_w(mdp.init)

    # Perform a breadth-first-search to collect all global transitions
    for s, act, _ in mdp.bfs(set_method=set_method):
        # Compile string for the left side of the arrow
        pre = " & ".join(
            [f"s={uid_w(s)}"]
            + [f"{k}={register(k, v)}" for k, v in s.ctx.items()]
        )
        for a, dist in act.items():
            # Compile string for the right side of the arrow
            post = []
            for s_prime, p_value in dist.items():
                # Compile the update string
                update = " & ".join(
                    [f"(s'={uid_w(s_prime)})"]
                    + [
                        f"({k}'={register(k, v)})"
                        for k, v in s_prime.ctx.items()
                        if k not in s.ctx or s.ctx[k] != v
                    ]
                )
                post += [
                    f"{p_value} : {update}" if p_value != 1.0 else f"{update}"
                ]
            # Add the global transition
            trs += [f"  [{a}] {pre} -> " + " + ".join(post) + ";\n"]

    last_id, state_ids = uid()

    buffer += "mdp\n"
    buffer += "\n"
    buffer += f"module {to_identifier(mdp.name)}\n"
    buffer += f"  s : [0..{last_id}] init {init};\n"
    # List state names
    buffer += "".join(
        [
            f"  // {_id} : {ordered_state_str(s, mdp, ', ')}\n"
            for s, _id in state_ids.items()
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
    return buffer
