# %%
from graphviz import Digraph
from IPython.display import Image

import mdp

mdp.use_colors()

M1 = mdp.MDP({
    's0': { 'a': { 's1': .2, 's2': .8 }, 'b': { 's2': .7, 's3': .3 } },
    's1': 'tau_1',
    's2': { 'x', 'y', 'z' },
    's3': { 'x', 'z' }
}, S='s0,s1,s2,s3', A='a,b,x,y,z,tau_1', name='M1')
M2 = mdp.MDP({
    'r0': { 'x': 'r1' },
    'r1': { 'y': 'r0', 'z': 'r1' }
}, name='M2')
M3 = mdp.MDP({
    'w0': { 'c': 'w1', 'y': 'w0' },
    'w1': 'tau_2'
}, name='M3')
M4 = mdp.MDP({
    'v0': { 'z': 'v1', 'y': 'v0' },
    'v1': 'z'
}, name='M4')

M = M1 + M2 + M3 + M4
M

# %%
path = 'renders/graph_test.gv'
dot = Digraph()

for s, act in M.transition_map.items():
    dot.node(s)
    for a, dist in act.items():
        for s_prime, p in dist.items():
            dot.edge(s, s_prime, a if p == 1 else f"{a} [{p}]")

dot.format = 'png'
dot.render(path)
Image(filename=f"{path}.png") 