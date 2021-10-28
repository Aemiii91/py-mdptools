# %%
import sys
sys.path.append('..')
from IPython.display import Image, SVG, display
from mdptools import MDP, mdp

def display_graph(graph):
    image_path = f"{graph.filename}.{graph.format}"
    if graph.format == 'pdf':
        print(image_path)
    elif graph.format == 'svg':
        display(SVG(filename=image_path))
    else:
        display(Image(filename=image_path))

# %%
Ms = MDP({
    's0': { 'a': 's1' },
    's1': { 'b': { 's0': .5, 's2': .5 } },
    's2': 'c'
}, A='a, b, c', name='Ms')

Mt = Ms.remake((r'[a-z]([0-9])', r't\1'), ['x', 'y', 'z'], 'Mt')

display_graph(mdp.graph([Ms + Mt, Mt, Ms], 'graphs/graph_simple_composition.gv', rankdir='LR'))

# %%
# The 4 MDPs from fig 1 in Hansen2011
M1 = MDP({
    's0': { 'a': { 's1': .2, 's2': .8 }, 'b': { 's2': .7, 's3': .3 } },
    's1': 'tau_1',
    's2': { 'x', 'y', 'z' },
    's3': { 'x', 'z' }
}, S='s0,s1,s2,s3', A='a,b,x,y,z,tau_1', name='M1')
M2 = MDP({
    'r0': { 'x': 'r1' },
    'r1': { 'y': 'r0', 'z': 'r1' }
}, name='M2')
M3 = MDP({
    'w0': { 'c': 'w1', 'y': 'w0' },
    'w1': 'tau_2'
}, name='M3')
M4 = MDP({
    'v0': { 'z': 'v1', 'y': 'v0' },
    'v1': 'z'
}, name='M4')

display_graph(mdp.graph([M1, M2, M3, M4], 'graphs/multiple_graphs_test.gv'))

# %%
# Parallel composition of 4 MDPs
display_graph(mdp.graph(M1 + M2 + M3 + M4, 'graphs/graph_test.gv'))

# %%
