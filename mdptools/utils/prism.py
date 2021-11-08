from ..types import MarkovDecisionProcess as MDP
from .format_str import to_identifier
from .utils import write_file


def to_prism(mdp: MDP, file_path: str = None) -> str:
    buffer = f"mdp\n\nmodule {to_identifier(mdp.name)}\n\ts : [0..{len(mdp)}] init {mdp._s_init};\n\n"

    for s, act in mdp.transition_map.items():
        for a, dist in act.items():
            buffer += f"\t[{a}] s={mdp.S[s]} -> "
            buffer += " + ".join(
                f"{p_value}:(s'={mdp.S[s_prime]})"
                for s_prime, p_value in dist.items()
            )
            buffer += ";\n"

    buffer += "endmodule"

    write_file(file_path, buffer)
    return buffer
