import mdp


def newline(): print('')


def exp_01():
    M1 = mdp.MDP({
        's0': { 'a': { 's1': .2, 's2': .8 }, 'b': { 's2': .7, 's3': .3 } },
        's1': 'tau_1',
        's2': { 'x', 'y', 'z' },
        's3': { 'x', 'z' }
    }, S='s0,s1,s2,s3', A='a,b,x,y,z,tau_1', name='M1')
    print(M1)

    M2 = mdp.MDP({
        'r0': { 'x': 'r1' },
        'r1': { 'y': 'r0', 'z': 'r1' }
    }, name='M2')
    print(M2)

    M3 = mdp.MDP({
        'w0': { 'c': 'w1', 'y': 'w0' },
        'w1': 'tau_2'
    }, name='M3')
    print(M3)

    M4 = mdp.MDP({
        'v0': { 'z': 'v1', 'y': 'v0' },
        'v1': 'z'
    }, name='M4')
    print(M4)


def exp_02():
    Ms = mdp.MDP({
        's0': { 'detect': { 's1': .8, 's2': .2 } },
        's1': { 'warn' : 's2' },
        's2': { 'shutdown': 's3' },
        's3': { 'off' }
    }, name='Ms')

    Md = mdp.MDP({
        't0': { 'warn': 't1', 'shutdown': { 't2': .9, 't3': .1 } },
        't1': { 'shutdown': 't2' },
        't2': { 'off' },
        't3': { 'fail' }
    }, name='Md')

    expected = mdp.MDP({
        's0_t0': { 'detect': { 's1_t0': .8, 's2_t0': .2 } },
        's1_t0': { 'warn': 's2_t1' },
        's2_t0': { 'shutdown': { 's3_t2': .9, 's3_t3': .1 } },
        's2_t1': { 'shutdown': 's3_t2' },
        's3_t2': { 'off' },
        's3_t3': { 'fail' }
    }, name='Ms||Md')

    actual = Ms + Md
    print('Actual:', actual)
    newline()
    print('expected == actual ->', actual == expected)


def exp_03():
    M1 = mdp.MDP({
        's0': { 'detect': { 's1': .8, 's2': .2 } },
        's1': { 'warn' : 's2' },
        's2': { 'shutdown': 's3' },
        's3': { 'off' }
    }, name='M1')
    print(M1)
    newline()

    print(M1 + M1.rn('s', 't'))
    newline()

    M2 = M1.__copy__()
    M2['s2, warn'] = 's2'
    M2.name = 'M2'
    print(M2)
    newline()

    print(M2 + M2.rn('s', 't'))


def main():
    mdp.use_colors()
    exp_03()


if __name__ == '__main__':
    main()