from IPython.display import Image, SVG, display

import mdp


def display_graph(graph):
    image_path = f"{graph.filename}.{graph.format}"
    if graph.format == 'pdf':
        print(image_path)
    elif graph.format == 'svg':
        display(SVG(filename=image_path))
    else:
        display(Image(filename=image_path))


mdp.use_colors()


# %%
(M1 := mdp.MDP({
    's0': { 'a': { 's1': .2, 's2': .8 }, 'b': { 's2': .7, 's3': .3 } },
    's1': 'tau_1',
    's2': { 'x', 'y', 'z' },
    's3': { 'x', 'z' }
}, S='s0,s1,s2,s3', A='a,b,x,y,z,tau_1', name='M1'))

# %%
(M2 := mdp.MDP({
    'r0': { 'x': 'r1' },
    'r1': { 'y': 'r0', 'z': 'r1' }
}, name='M2'))

# %%
(M3 := mdp.MDP({
    'w0': { 'c': 'w1', 'y': 'w0' },
    'w1': 'tau_2'
}, name='M3'))

# %%
(M4 := mdp.MDP({
    'v0': { 'z': 'v1', 'y': 'v0' },
    'v1': 'z'
}, name='M4'))


# %%
# Parallel composition of 4 MDPs
(M := M1 + M2 + M3 + M4)


# %%
display_graph(mdp.graph([M1, M2, M3, M4], 'renders/multiple_graphs_test.gv'))


# %%
# Render the MDP graph:
display_graph(mdp.graph(M, 'renders/graph_test.gv'))