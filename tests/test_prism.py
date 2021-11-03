"""Unit-tests for the `Prism Compiler` module
"""
import pytest
from mdptools import MarkovDecisionProcess, validate

from mdptools.utils.utils import tree_walker
from prism.prismCompiler import PrismCompiler


def test_compile():
    m1 = MarkovDecisionProcess(
        {
            "s0": {"a": {"s1": 0.2, "s2": 0.8}, "b": {"s2": 0.7, "s3": 0.3}},
            "s1": "tau_1",
            "s2": {"x", "y", "z"},
            "s3": {"x", "z"},
        },
        S="s0,s1,s2,s3",
        A="a,b,x,y,z,tau_1",
        name="M1",
    )

    compiler = PrismCompiler(m1, "")
    tree_walker(compiler.mdp.transition_map, compiler.callback)
    prismString = compiler.getResultString()

    prismCorrectString = """mdp
module generated
	s : [0..4] init 0;

	[b] s=0 -> 0.7 : (s'= 1)+ 0.3 : (s'= 2);
	[a] s=0 -> 0.2 : (s'= 3)+ 0.8 : (s'= 1);
	[tau_1] s=3 -> 1.0 : (s'= 3);
	[y] s=1 -> 1.0 : (s'= 1);
	[z] s=1 -> 1.0 : (s'= 1);
	[x] s=1 -> 1.0 : (s'= 1);
	[z] s=2 -> 1.0 : (s'= 2);
	[x] s=2 -> 1.0 : (s'= 2);
endmodule"""

    assert prismString == prismString
