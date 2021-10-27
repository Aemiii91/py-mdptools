# %%
from graphviz import Digraph
from IPython.display import Image, SVG, display

def show(path: str, format: str):
    image_path = f"{path}.{format}"
    if format == 'pdf':
        print(image_path)
    elif format == 'svg':
        display(SVG(filename=image_path))
    else:
        display(Image(filename=image_path))


import mdp

mdp.use_colors()
mdp.set_parallel_separator('')

# %%
# Parallel composition of 4 MDPs

M1 = mdp.MDP({
    's₀': { 'a': { 's₁': .2, 's₂': .8 }, 'b': { 's₂': .7, 's₃': .3 } },
    's₁': 'τ₁',
    's₂': { 'x', 'y', 'z' },
    's₃': { 'x', 'z' }
}, name='M1')
M2 = mdp.MDP({
    'r₀': { 'x': 'r₁' },
    'r₁': { 'y': 'r₀', 'z': 'r₁' }
}, name='M2')
M3 = mdp.MDP({
    'w₀': { 'c': 'w₁', 'y': 'w₀' },
    'w₁': 'τ₂'
}, name='M3')
M4 = mdp.MDP({
    'v₀': { 'z': 'v₁', 'y': 'v₀' },
    'v₁': 'z'
}, name='M4')

M = M1 + M2 + M3 + M4
M

# %%
# Draft/rough render of the composed MDP
path = 'renders/graph_test.gv'
dot = Digraph()

for s, act in M.transition_map.items():
    dot.node(s)
    for a, dist in act.items():
        for s_prime, p in dist.items():
            dot.edge(s, s_prime, a if p == 1 else f"{a} [{p}]")

dot.format = 'png'
dot.render(path)
show(path, dot.format)

# %%
