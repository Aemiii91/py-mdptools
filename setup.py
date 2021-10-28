from os import path
from setuptools import setup, find_packages

root = path.dirname(__file__)

with open(path.join(root, "README.md"), encoding="utf-8") as f:
    readme = f.read()

setup(
    name="mdptools",
    version="0.1.0",
    description="Tools for representing and manipulating Markov Decision Processes (MDP)",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/mholdg16/py-mdptools",
    author="Mathias Krog Holdgaard",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="mdp markov decision process probabilistic automata",
    packages=find_packages(include=["mdptools", "mdptools.*"]),
    python_requires=">=3.6, <4",
    install_requires=["numpy", "scipy", "graphviz"],
)
