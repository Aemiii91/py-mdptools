from mdptools import graph
from mdptools.mdp import MarkovDecisionProcess
from mdptools.utils.utils import tree_walker
from prism.prismCompiler import PrismCompiler


def at_root(filename: str) -> str:
    from os.path import join, dirname

    return join(dirname(__file__), "..", filename)


def display_dot(dot):
    from IPython.display import Image, SVG, display

    image_path = f"{dot.filename}.{dot.format}"

    if dot.format == "pdf":
        print(image_path)
    elif dot.format == "svg":
        display(SVG(filename=image_path))
    else:
        display(Image(filename=image_path))


def display_graph(mdp, file_path):
    display_dot(graph(mdp, at_root(file_path)))


def prism_file(mdp: MarkovDecisionProcess, file_path: str) -> None:
    compiler = PrismCompiler(mdp, file_path)
    tree_walker(compiler.mdp.transition_map, compiler.callback)
    compiler.finish()
