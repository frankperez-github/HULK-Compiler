class State:
    def __init__(self, name, token=None):
        self.name = name
        self.transitions = {}
        self.token = token

    def set_transition(self, char, next_state):
        if char not in self.transitions:
            self.transitions[char] = [next_state]
        else:
            self.transitions[char].append(next_state)

class DFA:
    def __init__(self, start_state: State, final_states):
        self.start_state = start_state
        self.final_states = final_states
        self.current_state = start_state

    def getDFA(token):
        """
        params:
            token_string --> string with the token name
        return:
            DFA with the token as the final state
        """
        dfa = DFA(State("start"), [])
        for char in token.lex:
            new_state = State(char)
            dfa.current_state.set_transition(char, new_state)
            dfa.current_state = new_state  
        dfa.current_state.token = token
        dfa.final_states = [dfa.current_state]
        dfa.current_state = dfa.start_state
        return dfa

    def evaluate(self, w: str) -> bool:
        """
        params: 
            w --> word to evaluate in the language
        return:
            True if w is in language,
            False in other case
        """
        while len(w) > 0:
            try:
                self.current_state = self.current_state.transitions[w[0]][0]
            except:
                # If there is not a transition to make, there is not current state any more
                self.current_state = None
                break

            # Consume first character in word
            w = w[1:]
        if self.current_state in self.final_states:
            return (True, self.current_state.token)
        return (False, None)

    def to_mermaid(self) -> str:
        mermaid_str = "stateDiagram-v2\n"
        for state in self._all_states():
            state_name = f"**{state.name}**" if state in self.final_states else state.name
            for char, next_states in state.transitions.items():
                for next_state in next_states:
                    next_state_name = f"**{next_state.name}**" if next_state in self.final_states else next_state.name
                    mermaid_str += f'    {state_name} --> {next_state_name} : {char}\n'
        return mermaid_str

    def _all_states(self):
        visited = set()
        to_visit = [self.start_state]
        while to_visit:
            state = to_visit.pop()
            if state not in visited:
                visited.add(state)
                to_visit.extend(
                    next_state for next_states in state.transitions.values() for next_state in next_states
                )
        return visited


class NDFA:
    def __init__(self, start_state: State, final_states):
        self.start_state = start_state
        self.final_states = final_states
        self.current_states = self.epsilon_closure([self.start_state])

    def evaluate(self, w: str) -> bool:
        """
        params: 
            w --> word to evaluate in the language
        return:
            True if w is in language,
            False in other case
        """
        while len(w) > 0:
            for curr_state in self.current_states.copy():
                self.current_states.remove(curr_state)
                for transition in curr_state.transitions:
                    if transition == w[0]:
                        self.current_states += curr_state.transitions[transition]

            # In case the automata stops and word is not empty, then fail
            if len(self.current_states) == 0 and len(w) > 0:
                return False

            # Consume first character in word
            w = w[1:]

        for curr_state in self.current_states:
            if curr_state in self.final_states:
                return True
        return False

    def epsilon_closure(self, states):
        resulting_states = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            if 'ε' in state.transitions:
                for next_state in state.transitions['ε']:
                    if next_state not in resulting_states:
                        resulting_states.add(next_state)
                        stack.append(next_state)
        return list(resulting_states)

    def go_to(self, states: list[State], char: str):
        resulting_states = []
        for state in states:
            resulting_states += [
                state.transitions[transition][0]
                for transition in state.transitions
                if transition == char and state.transitions[transition][0] not in resulting_states
            ]
        return resulting_states

    def to_DFA(self) -> DFA:
        """
        return: deterministic version of the NDFA received
        """
        dfa = DFA(None, [])
        new_states = {}
        stack = [self.start_state]

        # Generate new states
        while len(stack) > 0:
            current_state = stack.pop()
            eps_clos = self.epsilon_closure([current_state])
            for state in eps_clos:
                if state not in stack:
                    stack.append(state)
            eps_clos = eps_clos.union(set([current_state]))
            state_name = ",".join(sorted([state.name for state in eps_clos]))
            if state_name not in new_states:
                new_states[state_name] = eps_clos

        state_objects = {name: State(name) for name in new_states}

        for state_name, states in new_states.items():
            new_state = state_objects[state_name]

            # Check if new state is the start state
            if self.start_state in states:
                dfa = DFA(new_state, [])

            # Check if new state is a final state
            if any(final in states for final in self.final_states):
                dfa.final_states.append(new_state)

            for sub_state in states:
                for transition in sub_state.transitions:
                    if transition != "ε":
                        target_states = set()
                        for target_state in sub_state.transitions[transition]:
                            target_states.update(self.epsilon_closure([target_state]))
                            target_states.add(target_state)
                        target_state_name = ",".join(sorted([state.name for state in target_states]))
                        if target_state_name not in state_objects:
                            state_objects[target_state_name] = State(target_state_name)
                        # Check if the transition already exists before adding
                        if transition not in new_state.transitions or state_objects[target_state_name] not in new_state.transitions[transition]:
                            new_state.set_transition(transition, state_objects[target_state_name])

        return dfa

    @classmethod
    def union(cls, a1, a2):
        # Create new states
        start = State('start')
        final = State('final')

        state_mapping = {a1.start_state: State(f'a1_{a1.start_state.name}'),
                         a2.start_state: State(f'a2_{a2.start_state.name}')}

        for state in a1._all_states():
            if state not in state_mapping:
                state_mapping[state] = State(f'a1_{state.name}')

        for state in a2._all_states():
            if state not in state_mapping:
                state_mapping[state] = State(f'a2_{state.name}')

        # Relocate a1 transitions
        for state in a1._all_states():
            new_state = state_mapping[state]
            for char, next_states in state.transitions.items():
                for next_state in next_states:
                    new_state.set_transition(char, state_mapping[next_state])

        # Relocate a2 transitions
        for state in a2._all_states():
            new_state = state_mapping[state]
            for char, next_states in state.transitions.items():
                for next_state in next_states:
                    new_state.set_transition(char, state_mapping[next_state])

        # Add transitions from start state
        start.set_transition('ε', state_mapping[a1.start_state])
        start.set_transition('ε', state_mapping[a2.start_state])

        # Add transitions to final state
        for final_state in a1.final_states:
            state_mapping[final_state].set_transition('ε', final)
        for final_state in a2.final_states:
            state_mapping[final_state].set_transition('ε', final)

        return cls(start, [final])

    @classmethod
    def concatenation(cls, a1, a2):
        start = State('start')
        final = State('final')

        state_mapping = {a1.start_state: State(f'a1_{a1.start_state.name}'),
                         a2.start_state: State(f'a2_{a2.start_state.name}')}

        for state in a1._all_states():
            if state not in state_mapping:
                state_mapping[state] = State(f'a1_{state.name}')

        for state in a2._all_states():
            if state not in state_mapping:
                state_mapping[state] = State(f'a2_{state.name}')

        for state in a1._all_states():
            new_state = state_mapping[state]
            for char, next_states in state.transitions.items():
                for next_state in next_states:
                    new_state.set_transition(char, state_mapping[next_state])

        for state in a2._all_states():
            new_state = state_mapping[state]
            for char, next_states in state.transitions.items():
                for next_state in next_states:
                    new_state.set_transition(char, state_mapping[next_state])

        for final_state in a1.final_states:
            state_mapping[final_state].set_transition('ε', state_mapping[a2.start_state])

        return cls(state_mapping[a1.start_state], [state_mapping[final_state] for final_state in a2.final_states])

    def closure(a1):
        start = State('start')
        final = State('final')
        
        state_mapping = {a1.start_state: State(f'a1_{a1.start_state.name}')}

        for state in a1._all_states():
            if state not in state_mapping:
                state_mapping[state] = State(f'a1_{state.name}')

        # Relocate automaton transitions
        for state in a1._all_states():
            new_state = state_mapping[state]
            for symbol, destinations in state.transitions.items():
                for destination in destinations:
                    if destination not in state_mapping:
                        state_mapping[destination] = State(f'a1_{destination.name}')
                    new_state.set_transition(symbol, state_mapping[destination])

        # Add epsilon transitions from new start state to original start state and final state
        start.set_transition('ε', state_mapping[a1.start_state])
        start.set_transition('ε', final)

        # Add epsilon transitions from original final states to final state and back to original start state
        for final_state in a1.final_states:
            state_mapping[final_state].set_transition('ε', final)
            state_mapping[final_state].set_transition('ε', state_mapping[a1.start_state])

        states = list(state_mapping.values()) + [start, final]
        final_states = [final]

        return NDFA(start, final_states)

    def to_mermaid(self) -> str:
        mermaid_str = "stateDiagram-v2\n"
        for state in self._all_states():
            state_name = f"**{state.name}**" if state in self.final_states else state.name
            for char, next_states in state.transitions.items():
                for next_state in next_states:
                    next_state_name = f"**{next_state.name}**" if next_state in self.final_states else next_state.name
                    mermaid_str += f'    {state_name} --> {next_state_name} : {char}\n'
        return mermaid_str

    def _all_states(self):
        visited = set()
        to_visit = [self.start_state]
        while to_visit:
            state = to_visit.pop()
            if state not in visited:
                visited.add(state)
                to_visit.extend(
                    next_state for next_states in state.transitions.values() for next_state in next_states
                )
        return visited


def export_to_md(automaton, filename):
    mermaid_str = automaton.to_mermaid()
    md_content = f"```mermaid\n{mermaid_str}\n```"
    with open(filename, 'w') as f:
        f.write(md_content)



# Example usage:
# a1_start = State('q0')
# a1_final = State('q1')
# a1_start.set_transition('a', a1_final)
# a1 = NDFA(a1_start, [a1_final])

# a2_start = State('p0')
# a2_final = State('p1')
# a2_start.set_transition('b', a2_final)
# a2 = NDFA(a2_start, [a2_final])

# ndfa_union = NDFA.union(a1, a2)
# export_to_md(a1, "a1.md")
# export_to_md(a2, "a2.md")
# export_to_md(ndfa_union, "union.md")

# ndfa_concatenation = NDFA.concatenation(a1, a2)
# export_to_md(a1, "a1.md")
# export_to_md(a2, "a2.md")
# export_to_md(ndfa_concatenation, "concatenation.md")

a1_start = State('q0')
a1_final = State('q1')
a1_start.set_transition('a', a1_final)
a1 = NDFA(a1_start, [a1_final])

ndfa_closure = a1.closure()
export_to_md(ndfa_closure, "closure.md")