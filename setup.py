from setuptools import setup, find_packages


with open('README.md', encoding='utf8') as f:
    readme = f.read()

with open('LICENSE', encoding='utf8') as f:
    license_text = f.read()

setup(
    name='py-mdptools',
    version='1.0.0',
    description='Tools for representing and manipulating Markov Decision Processes (MDP)',
    long_description=readme,
    author='Mathias Krog Holdgaard',
    url='https://github.com/mholdg16/py-mdptools',
    license=license_text,
    packages=find_packages(exclude=('tests', 'examples'))
)
