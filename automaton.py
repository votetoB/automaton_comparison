import copy
from warnings import warn
from functools import partial, reduce


ALPHABET = 'abcdefghijklmnopqrstuvwxyz0123456789'
ALPHABET = 'ab'


class Automaton(object):
    def __init__(self, states, final_states, matrix, alphabet):
        """
        :param states:
        :param final_states:
        :param matrix:
        :param alphabet:
        """
        # TODO: assertion required
        self.states = states
        self.matrix = matrix
        self.alphabet = alphabet
        self.final_states = final_states

    def minimize(self, equality_comparison=None):
        equality_matrix = [
            [not ((state1 in self.final_states) ^ (state0 in self.final_states))
             for state1 in self.states] for state0 in self.states]

        while True:
            prev_equality_matrix = copy.deepcopy(equality_matrix)

            for state0 in self.states:
                for state1 in self.states:
                    if equality_matrix[state0 - 1][state1 - 1]:
                        def compare(letter):
                            delta0 = self.delta(state0, letter)
                            delta1 = self.delta(state1, letter)
                            return delta0 == delta1 or (delta1 is not None and delta0 is not None and equality_matrix[delta0 - 1][delta1 - 1])

                        equality_matrix[state0 - 1][state1 - 1] = all(map(compare, self.alphabet))


            if prev_equality_matrix == equality_matrix:
                break
        if equality_comparison:
            # If we need to compare to specific states
            return equality_matrix[equality_comparison[0]][equality_comparison[1]]
        else:
            states_to_remove = set()

            for state0 in self.states:
                for state1 in self.states:
                    if equality_matrix[state0 - 1][state1 - 1] and state0 < state1:
                        states_to_remove.add(state0)

            map(self.remove_state, states_to_remove)

    def __eq__(self, other):
        if not type(other) == Automaton:
            warn("Comparing Automaton to non-automaton")
            return False

        if self.alphabet != other.alphabet:
            return False

        merged_automaton = Automaton.merge_two(self, other)

        return merged_automaton.minimize(equality_comparison=[1, len(self.states) + 1])

    @classmethod
    def merge_two(cls, left, right):
        ll = len(left.states)
        new_states = left.states + [s + ll for s in right.states]
        new_final_states = left.final_states + [s + ll for s in right.final_states]
        assert left.alphabet == right.alphabet
        new_matrix = dict.fromkeys(new_states)
        for k, v in left.matrix.iteritems():
            new_matrix[k] = v

        for k, v in right.matrix.iteritems():
            new_v = dict.fromkeys(right.alphabet)
            for letter, ns in v.iteritems():
                new_v[letter] = ns + ll if ns else None

            new_matrix[k + ll] = new_v

        return cls(states=new_states, matrix=new_matrix, final_states=new_final_states, alphabet=left.alphabet)

    @classmethod
    def init_from_regex(cls, regex):
        """
        :param regex: VALIDATED REGEX
        :return: Automaton
        """

        # element_types = ('letter', 'automaton', 'optional_character', 'quantifier')
        elements = list()

        # FIRST OF ALL - get all the ()-brackets and build automaton for them recursively (NOT IMPLEMENTED)

        # if regex[0] == '^':
        #     obligatory_start = True
        #     regex = regex[1:]
        # else:
        #     obligatory_start = False
        #
        # if regex[-1] == '$':
        #      obligatory_finish = True
        #     regex = regex[:-1]
        # else:
        #     obligatory_finish = False

        i = 0
        while i < len(regex):
            el = regex[i]
            if el in ALPHABET:
                elements.append((el, 'letter'))
            elif el == '.':
                elements.append((ALPHABET, 'optional_character'))
            elif el == '[':
                options = ''
                while True:
                    i += 1
                    el = regex[i]
                    if el == ']':
                        break
                    else:
                        if el in ALPHABET:
                            options += el
                        else:
                            raise AssertionError("wrong character")

                elements.append((options, 'optional_character'))

            elif el == '+':
                elements.append((1, 'inf', 'quantifier'))
            elif el == '*':
                elements.append((0, 'inf', 'quantifier'))
            elif el == '!':
                elements.append((0, 1, 'quantifier'))

            # WARNING, ONLY SUPPORTS SINGLE-DIGIT QUANTIFIERS
            elif el == '{':
                assert regex[i + 2] == ','
                assert regex[i + 4] == '}'
                if regex[i + 3] == '*':
                    second_q = 'inf'
                else:
                    second_q = int(regex[i + 3])
                elements.append((int(regex[i + 1]), second_q, 'quantifier'))
                i += 4

            else:
                raise AssertionError("wrong character")
            i += 1

        # ADD OPTIONAL CHARACTER - we got one-letter automatons on this step
        for i in range(len(elements)):
            if elements[i][-1] in ['letter', 'optional_character']:
                new_automaton = cls.one_letter_automaton(elements[i][0])
                elements[i] = (new_automaton, 'automaton')

        # we will get quantified elements on this step
        final_elements = list()

        for i in range(len(elements)):
            if i + 1 < len(elements) and elements[i + 1][-1] == "quantifier":
                assert elements[i][-1] == 'automaton', "Quantifiers in a row exception"
                final_elements.append(elements[i][0].quantify(elements[i + 1][:-1]))
            else:
                if elements[i][-1] == "automaton":
                    final_elements.append(elements[i][0])

        # for el in final_elements:
        #     print(el)

        return reduce(cls.join_two, final_elements)

    def delta(self, state, element):
        if state in self.states and element in self.alphabet:
            return self.matrix[state][element]
        else:
            raise TypeError("You have to pass proper state and/or element")

    def remove_state(self, state):
        raise NotImplementedError
        # self.states.remove(state)
        # if state in self.final_states:
        #     self.final_states.remove(state)
        # del self.matrix[state]

    @classmethod
    def one_letter_automaton(cls, letters):
        first_state_matrix_dict = dict.fromkeys(ALPHABET)
        for letter in letters:
            first_state_matrix_dict[letter] = 2

        return cls(
            states=[1, 2],
            final_states=[2],
            alphabet=ALPHABET,
            matrix={
                1: first_state_matrix_dict,
                2: dict.fromkeys(ALPHABET)
            }
        )

    def quantify(self, quantifier):
        assert self.states == [1, 2]
        # print(quantifier)
        if quantifier[1] == 'inf':
            self.states = list(range(1, quantifier[0] + 2))
            self.final_states = [self.states[-1]]
            # raise Exception
        else:
            assert quantifier[0] <= quantifier[1]
            self.states = list(range(1, quantifier[1] + 2))
            self.final_states = list(range(quantifier[0] + 1, quantifier[1] + 2))
            assert len(self.final_states) == 1, "Not implemented yet!"

        new_matrix = dict.fromkeys(self.states)
        letters = [k for k, v in self.matrix[1].iteritems() if v]

        for state in self.states:
            new_matrix[state] = dict.fromkeys(ALPHABET)
            if quantifier[1] == 'inf':
                next_state = state if state == self.final_states[0] else state + 1
            else:
                next_state = None if state == self.final_states[0] else state + 1

            for letter in letters:
                new_matrix[state][letter] = next_state

        self.matrix = new_matrix
        return self

    @classmethod
    def join_two(cls, left, right):
        assert left.states[0] == 1
        new_states = list(range(1, len(left.states) + len(right.states)))
        new_final_states = [new_states[-1]]
        new_matrix = dict.fromkeys(new_states)

        for i in range(1, len(left.states) + 1):
            new_matrix[i] = copy.deepcopy(left.matrix[i])

        for i in range(2, len(right.states) + 1):
            j = i + len(left.states) - 1
            new_matrix[j] = dict.fromkeys(ALPHABET)
            for k, v in right.matrix[i].iteritems():
                new_matrix[j][k] = v + len(left.states) - 1 if v is not None else None

        # print(new_matrix)
        if len(right.states) == 1:
            new_states.append(len(left.states) + 1)
            last_state = new_states[-1]
            new_final_states = [last_state]
            new_matrix[last_state] = dict.fromkeys(ALPHABET)
            for k, v in right.matrix[1].iteritems():
                if v is not None:
                    new_matrix[last_state][k] = last_state
                    new_matrix[last_state - 1][k] = last_state

        else:
            for k, v in right.matrix[1].iteritems():
                if v is not None:
                    new_matrix[len(left.states)][k] = v + len(left.states) - 1

        return cls(states=new_states, final_states=new_final_states, matrix=new_matrix, alphabet=ALPHABET)

    def __str__(self):
        return (
            "AUTOMATON:\n" +
            str(self.states) +
            str(self.final_states) + '\n' + str(self.matrix))
