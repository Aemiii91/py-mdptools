try: import mdp
except: from helper import mdp


def run():
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
    print('')
    print('expected == actual ->', actual == expected)


if __name__ == '__main__':
    run()