try: import mdp
except: from helper import mdp


def run():
    M1 = mdp.MDP({
        's0': { 'a': { 's1': .2, 's2': .8 }, 'b': { 's2': .7, 's3': .3 } },
        's1': 'tau_1',
        's2': { 'x', 'y', 'z' },
        's3': { 'x', 'z' }
    }, S='s0,s1,s2,s3', A='a,b,x,y,z,tau_1', name='M1')
    print(M1, '\n')

    M2 = mdp.MDP({
        'r0': { 'x': 'r1' },
        'r1': { 'y': 'r0', 'z': 'r1' }
    }, name='M2')
    print(M2, '\n')

    M3 = mdp.MDP({
        'w0': { 'c': 'w1', 'y': 'w0' },
        'w1': 'tau_2'
    }, name='M3')
    print(M3, '\n')

    M4 = mdp.MDP({
        'v0': { 'z': 'v1', 'y': 'v0' },
        'v1': 'z'
    }, name='M4')
    print(M4, '\n')

    M = M1 + M2 + M3 + M4
    print(M, '\n')
    print('Assert: M.is_valid ->', M.is_valid)


if __name__ == '__main__':
    run()