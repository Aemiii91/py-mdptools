from ..types import MarkovDecisionProcess as MDP, SetMethod
from .format_str import to_identifier
from .utils import id_bank, minmax_bank, write_file, ordered_state_str


def to_prism(
    mdp: MDP, file_path: str = None, set_method: SetMethod = None
) -> str:
    get_id = id_bank()
    register = minmax_bank()

    trs = []
    init = get_id(mdp.init.s)

    for s, act, _ in mdp.bfs(set_method=set_method):
        pre = " & ".join(
            [f"s={get_id(s.s)}"]
            + [f"{k}={register(k, v)}" for k, v in s.ctx.items()]
        )
        for a, dist in act.items():
            post = []
            for s_prime, p_value in dist.items():
                update = " & ".join(
                    [f"(s'={get_id(s_prime.s)})"]
                    + [
                        f"({k}'={register(k, v)})"
                        for k, v in s_prime.ctx.items()
                        if k not in s.ctx or s.ctx[k] != v
                    ]
                )
                post += [
                    f"{p_value} : {update}" if p_value != 1.0 else f"{update}"
                ]
            trs += [f"  [{a}] {pre} -> " + " + ".join(post) + ";\n"]

    last_id, state_ids = get_id()

    buffer = "mdp\n"
    buffer += "\n"
    buffer += f"module {to_identifier(mdp.name)}\n"
    buffer += f"  s : [0..{last_id}] init {init};\n"
    buffer += "".join(
        [
            f"  // {_id} : {ordered_state_str(s, mdp, ', ')}\n"
            for s, _id in state_ids.items()
        ]
    )
    buffer += "".join(
        [
            f"  {k} : [{_min}..{_max}] init {mdp.init.ctx.get(k, 0)};\n"
            for k, (_min, _max) in register().items()
        ]
    )
    buffer += "\n"
    buffer += "".join(trs)
    buffer += "endmodule"

    write_file(file_path, buffer)
    return buffer
