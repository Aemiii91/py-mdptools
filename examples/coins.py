from mdptools import MarkovDecisionProcess as MDP
from mdptools.set_methods import stubborn_sets
from helpers import at_root, display_graph, display_dot


def make_coin(i: int, p: float) -> MDP:
    return MDP(
        [
            (
                f"flip_{i}",
                f"u_{i}",
                {f"h_{i}": round(p, 2), f"t_{i}": round(1 - p, 2)},
            )
        ],
        name=f"C{i}",
    )


p_values = [0.5, 0.8]
n = len(p_values)

coins = [make_coin(i + 1, p) for i, p in enumerate(p_values)]
hand = MDP(
    [
        (f"flip_{i}", f"count_{c}", f"count_{c-1}")
        for c in range(n, 0, -1)
        for i in range(1, n + 1)
    ]
    + [("done", "count_0")],
    name="H",
)

# %%
display_graph(*coins, hand, file_path="out/graphs/coins.gv")


# %%
handful_of_coins = MDP(*coins, hand)
print(handful_of_coins)
display_graph(handful_of_coins, file_path="out/graphs/handful_of_coins.gv")
# display_dot(
#     handful_of_coins.to_graph(
#         at_root("out/graphs/handful_of_coins.gv"),
#         set_method=stubborn_sets,
#         highlight=True,
#     )
# )
