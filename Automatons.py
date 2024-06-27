from TokenTypes import plus
from cmp.utils import Token

class State:
    def __init__(self, name, token=None):
        self.name = name
        self.transitions = {}
        self.token = token

    def set_transition(self, char, next_state):
        if not char in self.transitions:
            self.transitions[char] = [next_state]
        else:
            self.transitions[char].append(next_state)

class DFA:
    def __init__(self, start_state:State, final_states):
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

    def evaluate(self, w:str) -> bool:
        """
        params: 
            w --> word to evaluate in the language
        return:
            True if w is in language,
            False in other case
        """

        while(len(w) > 0):
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
    def __init__(self, start_state:State, final_states):
        self.start_state = start_state
        self.final_states = final_states
        self.current_states = [self.start_state]

        # At start, start_state is in current states and 
        # every state reacheable using an epsilon transition from start, is current
        self.current_states = [start_state]
        for state in start_state.transitions["ε"]:
            self.current_states.append(state)

    def evaluate(self, w:str) -> bool:
        """
        params: 
            w --> word to evaluate in the language
        return:
            True if w is in language,
            False in other case
        """

        while(len(w) > 0):
            for curr_state in self.current_states.copy():
                self.current_states.remove(curr_state)
                for transition in curr_state.transitions:
                    if transition == w[0]:
                        self.current_states += curr_state.transitions[transition]

            # In case the automata stops and word is not empty, then fail
            if(len(self.current_states) == 0 and len(w) > 0): return False
            
            # Consume first character in word
            w = w[1:]
        
        for curr_state in self.current_states:
            if curr_state in self.final_states:
                return True
        return False
    
    def epsilon_closure(self, states:list[State]) -> list[State]:
        resulting_states = set()
        if len(states) == 1: 
            return resulting_states.union(set(states[0].transitions["ε"]) if "ε" in states[0].transitions else [])
        for state in states:
            resulting_states.union(set(NDFA.epsilon_closure([state])))
        return list(resulting_states)

    def go_to(self, states:list[State], char:str):
        resulting_states = []
        for state in states:
            resulting_states += [
                                    state.transitions[transition][0] 
                                        for transition in state.transitions 
                                            if transition == char and not state.transitions[transition][0] in resulting_states
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

# ---------------------------------------------------

# Testing DFA
# start_state = State("start", plus)
# final_state = State("final", plus)

# start_state.set_transition("0",start_state)
# start_state.set_transition("1",final_state)

# final_state.set_transition("0",start_state)
# final_state.set_transition("1",final_state)


# final_states = [final_state, start_state]

# dfa = DFA(start_state, final_states)

# print(dfa.evaluate("0101011110")) #should return True
# print(dfa.evaluate("01021011110")) #should return False
# export_to_md(dfa, 'dfa.md')


# -----------------------------------------------------

# Testing NDFA
# start_state = State("start")
# q_0 = State("q_0")
# q_1 = State("q_1")

# start_state.set_transition("ε", q_0)
# start_state.set_transition("ε", q_1)

# q_0.set_transition("0", q_0)
# q_0.set_transition("1", q_1)

# q_1.set_transition("1", q_1)
# q_1.set_transition("0", q_0)

# final_states = [q_0, q_1]

# ndfa = NDFA(start_state, final_states)
# print(ndfa.evaluate("01011011")) # should return True
# print(ndfa.evaluate("010110112")) # should return False
# export_to_md(ndfa, "ndfa.md")

# -----------------------------------------------------



# NDFA to DFA
# ndfa_to_dfa = ndfa.to_DFA()
# print(ndfa_to_dfa.evaluate("01011011")) # should return True
# print(ndfa_to_dfa.evaluate("010110112")) # should return False

# export_to_md(ndfa_to_dfa, "ndfa_to_dfa.md")
