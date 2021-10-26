try: import mdp
except: from helper import mdp


def run():
    M1 = mdp.MDP({
        's0': { 'a': 's1' },
        's1': { 'b': { 's0': .5, 's2': .5 } },
        's2': 'c'
    }, name='M1')
    print(M1, '\n')
    
    M2 = mdp.MDP({
        't0': { 'x': 't1' },
        't1': { 'y': { 't0': .5, 't2': .5 } },
        't2': 'z'
    }, name='M2')
    print(M2, '\n')

    M = M1 + M2
    print(M, '\n')
    print('Assert: len(M.S) == 9 ->', len(M.S) == 9)


if __name__ == '__main__':
    run()