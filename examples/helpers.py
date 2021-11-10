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


def display_graph(*mdp, file_path: str, **kw):
    from mdptools import graph

    display_dot(graph(*mdp, file_path=at_root(file_path), **kw))
