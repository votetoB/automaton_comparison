from automaton import Automaton


if __name__ == '__main__':
    with open('example.txt', 'r') as f:
        regexps = f.read().splitlines()

    a1 = Automaton.init_from_regex(regexps[0])
    # print(a1)
    a2 = Automaton.init_from_regex(regexps[1])
    # print(a2)

    if a1 == a2:
        print("Regexps %s %s are the same" % (regexps[0], regexps[1]))
    else:
        print("Regexps %s %s are different" % (regexps[0], regexps[1]))
