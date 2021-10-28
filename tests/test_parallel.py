"""Unit-tests for the `parallel` module
"""
from mdptools import MDP, parallel


def test_simple_composition():
    M1 = MDP({
        's0': { 'a': 's1' },
        's1': { 'b': { 's0': .5, 's2': .5 } },
        's2': 'c'
    }, A='a, b, c', name='M1')

    M2 = M1.remake((r'[a-z]([0-9])', r't\1'), ['x', 'y', 'z'], 'M2')

    M = parallel(M1, M2, 'M')

    assert M.is_valid
    assert len(M.S) == 9
    assert M.name == 'M'


def test_parallel_composition_kwiatkowska2013():
    Ms = MDP({
        's0': { 'detect': { 's1': .8, 's2': .2 } },
        's1': { 'warn' : 's2' },
        's2': { 'shutdown': 's3' },
        's3': { 'off' }
    }, name='Ms')

    Md = MDP({
        't0': { 'warn': 't1', 'shutdown': { 't2': .9, 't3': .1 } },
        't1': { 'shutdown': 't2' },
        't2': { 'off' },
        't3': { 'fail' }
    }, name='Md')

    expected = MDP({
        's0_t0': { 'detect': { 's1_t0': .8, 's2_t0': .2 } },
        's1_t0': { 'warn': 's2_t1' },
        's2_t0': { 'shutdown': { 's3_t2': .9, 's3_t3': .1 } },
        's2_t1': { 'shutdown': 's3_t2' },
        's3_t2': { 'off' },
        's3_t3': { 'fail' }
    }, name='Ms||Md (Expected)')

    actual = parallel(Ms, Md, 'Ms||Md (Actual)')

    assert actual == expected


def test_complex_composition():
    M1 = MDP({
        's0': { 'a': { 's1': .2, 's2': .8 }, 'b': { 's2': .7, 's3': .3 } },
        's1': 'tau_1',
        's2': { 'x', 'y', 'z' },
        's3': { 'x', 'z' }
    }, name='M1')

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

    M = M1 + M2 + M3 + M4

    assert M.is_valid and len(M.S) == 16
