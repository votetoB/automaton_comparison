from automaton import Automaton


if __name__ == '__main__':
    with open('example.txt', 'r') as f:
        regexps = f.read().splitlines()

    # a1 = Automaton.init_from_regex(regexps[0])
    # # print(a1)
    # a2 = Automaton.init_from_regex(regexps[1])
    # # print(a2)
    a1 = Automaton(states=[1, 2, 3, 4], final_states=[2, 4], alphabet="ab",
                   matrix={1: {'a': 2, 'b': None}, 2: {'a': None, 'b': 3}, 3: {'a': 4, 'b': None},
                           4: {'a': None, 'b': 3}})
    a2 = Automaton(states=[1, 2], final_states=[2], alphabet="ab",
                   matrix={1: {'a': 2, 'b': None}, 2: {'a': None, 'b': 1}})

    if a1 == a2:
        print("Automatons %s \n %s are the same" % (a1, a2))
    else:
        print("Automatons %s %s are different" % (a1, a2))
