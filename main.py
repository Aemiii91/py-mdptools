import mdp


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
    print(Ms)

    Md = mdp.MDP({
        't0': { 'warn': 't1', 'shutdown': { 't2': .9, 't3': .1 } },
        't1': { 'shutdown': 't2' },
        't2': { 'off' },
        't3': { 'fail' }
    }, name='Md')
    print(Md)


def main():
    exp_02()    


if __name__ == '__main__':
    main()