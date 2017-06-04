import copy
from warnings import warn
from functools import partial


class Automaton:
    def __init__(self, states, final_states, matrix, alphabet):
        """
        TODO: write something here
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

    def minimize(self):
        equality_matrix = [[not (state1 in self.final_states ^ state0 in self.final_states) for state1 in
                            self.states[self.states.index(state0) + 1:]] for state0 in self.states]

        while True:
            prev_equality_matrix = copy.copy(equality_matrix)
            for state0 in self.states:
                for state1 in self.states[self.states.index(state0) + 1:]:
                    if equality_matrix[state0][state1]:
                        equality_matrix[state0][state1] = list(map(partial(self.delta, state=state0), self.alphabet))\
                                                          == list(map(partial(self.delta, state=state1), self.alphabet))

            if prev_equality_matrix == equality_matrix:
                break

        states_to_remove = set()
        for state0 in self.states:
            for state1 in self.states[self.states.index(state0) + 1:]:
                if equality_matrix[state0][state1]:
                    states_to_remove.add(state1)

        map(self.remove_state, states_to_remove)

    def __eq__(self, other):
        if not type(other, Automaton):
            warn("Comparing Automaton to non-automaton")
            return False

        self.minimize()
        other.minimize()

        raise NotImplementedError("Мы честно сделали на бумажке.")

    @classmethod
    def init_from_regex(cls, regex):
        raise NotImplementedError

    def delta(self, state, element):
        if state in self.states and element in self.alphabet:
            return self.matrix[state][element]
        else:
            raise TypeError("You have to pass proper state and/or element")

    def remove_state(self, state):
        self.states.remove(state)
        self.final_states.remove(state)
        del self.matrix[state]
