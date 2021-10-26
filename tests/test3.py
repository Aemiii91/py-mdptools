import mdp


def run():
    M1 = mdp.MDP({
        's0': { 'detect': { 's1': .8, 's2': .2 } },
        's1': { 'warn' : 's2' },
        's2': { 'shutdown': 's3' },
        's3': { 'off' }
    }, name='M1')
    print(M1, '\n')

    print(M1 + M1.rn('s', 't'), '\n')

    M2 = M1.__copy__()
    M2['s2, warn'] = 's2'
    M2.name = 'M2'
    print(M2, '\n')

    print(M2 + M2.rn('s', 't'))


if __name__ == '__main__':
    run()