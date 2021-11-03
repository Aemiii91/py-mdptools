from os import makedirs, path

from .types import MarkovDecisionProcess as MDP
from .stringify import to_identifier


def to_prism(mdp: MDP, file_path: str = None) -> str:
    buffer = f"mdp\nmodule {to_identifier(mdp.name)}\n\ts : [0..{len(mdp)}] init {mdp._s_init};\n\n"

    for s, act in mdp.transition_map.items():
        for a, dist in act.items():
            buffer += f"\t[{a}] s={mdp.S[s]} -> "
            buffer += " + ".join(
                f"{p_value}:(s'={mdp.S[s_prime]})"
                for s_prime, p_value in dist.items()
            )
            buffer += ";\n"

    buffer += "endmodule"

    if file_path is not None:
        d = path.dirname(file_path)
        if d != "" and not path.exists(d):
            makedirs(d)

        with open(file_path, "w+", encoding="utf-8") as f:
            f.write(buffer)

    return buffer
