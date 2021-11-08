from ..types import MarkovDecisionProcess as MDP
from .format_str import to_identifier
from .utils import id_bank, write_file


def to_prism(mdp: MDP, file_path: str = None) -> str:
    get_id = id_bank()

    trs = []

    for s, act in mdp.search():
        pre = f"s={get_id(s)}"
        for a, dist in act.items():
            post = []
            for s_prime, p_value in dist.items():
                update = f"s'={get_id(s_prime)}"
                post += [
                    f"{p_value}:({update})"
                    if p_value != 1.0
                    else f"({update})"
                ]
            trs += [f"  [{a}] {pre} -> " + " + ".join(post) + ";\n"]

    buffer = "mdp\n"
    buffer += "\n"
    buffer += f"module {to_identifier(mdp.name)}\n"
    buffer += f"  s : [0..{get_id()}] init {get_id(mdp.init.s)};\n"
    buffer += "\n"
    buffer += "".join(trs)
    buffer += "endmodule"

    write_file(file_path, buffer)
    return buffer
