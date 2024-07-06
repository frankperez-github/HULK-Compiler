from cmp.utils import ContainerSet, DisjointSet


class NDFA:
    def __init__(self, states: int, finals: list[int], transitions: dict[(int,str),list[int]], start: int = 0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = { state: {} for state in range(states) }
        
        for (origin, symbol), destinations in transitions.items():
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)
            
        self.vocabulary.discard('')
        

    def to_DFA(self):
        transitions = {}
    
        start = self.epsilon_closure([self.start])
        start.id = 0
        start.is_final = any(s in self.finals for s in start)
        states = [ start ]

        pending = [ start ]
        while pending:
            state = pending.pop()
        
            for symbol in self.vocabulary:

                next_state = self.epsilon_closure(self.evaluate(state,symbol))

                if not next_state:
                    continue

                for item in states:
                    if item == next_state:
                        next_state = item
                        break
                else:
                    next_state.id = len(states)
                    next_state.is_final = any(state in self.finals for state in next_state)
                    states.append(next_state)
                    pending.append(next_state)


                try:
                    transitions[state.id, symbol]
                except KeyError:
                    transitions[state.id,symbol] = next_state.id          
      
        finals = [ state.id for state in states if state.is_final ]
        dfa = DFA(len(states), finals, transitions)
        return dfa
        

    def evaluate(self, states, symbol):
        moves = set()
        for state in states:
            try:
                moves.update(self.transitions[state][symbol]) 
            except:
                pass
        return moves

    def epsilon_closure(self, states):
        pending = [ s for s in states ] 
        closure = { s for s in states }    

        while pending:
            state = pending.pop()

            try:
                next_states = self.transitions[state]['']
            except:
                next_states = ()    

            for item in next_states:
                if item not in pending:
                    pending.append(item)
            closure.update(next_states)
                
        return ContainerSet(*closure)
    

    def union(a1, a2):
        transitions = {}
    
        start = 0
        d_1 = 1
        d_2 = a1.states + d_1
        final = a2.states + d_2
    
        for (origin, symbol), destinations in a1.map.items():
            ## Relocate a1 transitions ...
            transitions[d_1 + origin, symbol] = [d_1 + d for d in destinations]

        for (origin, symbol), destinations in a2.map.items():
            ## Relocate a2 transitions ...
            transitions[d_2 + origin, symbol] = [d_2 + d for d in destinations]
    
        ## Add transitions from start state ...
        transitions[start, ''] = [a1.start + d_1, a2.start + d_2]
    
        ## Add transitions to final state ...
        for i in a1.finals:
            try:
                transitions[i + d_1, ''].add(final)
            except KeyError:
                transitions[i + d_1, ''] = [final]
        for i in a2.finals:
            try:
                transitions[i + d_2, ''].add(final)
            except KeyError:
                transitions[i + d_2, ''] = [final]
            
        states = a1.states + a2.states + 2
        finals = { final }
    
        return NDFA(states, finals, transitions, start)
    
    def concatenation(a1, a2):
        transitions = {}
        
        start = 0
        d_1 = 0
        d_2 = a1.states + d_1
        final = a2.states + d_2
        
        for (origin, symbol), destinations in a1.map.items():
            transitions[origin, symbol] = destinations

        for (origin, symbol), destinations in a2.map.items():
            transitions[d_2 + origin, symbol] = [d_2 + d for d in destinations]
        
        for i in a1.finals:
            try:
                transitions[i + d_1, ''].add(a2.start + d_2)
            except KeyError:
                transitions[i + d_1, ''] = [a2.start + d_2]
                
        for i in a2.finals:
            try:
                transitions[i + d_2, ''].add(final)
            except KeyError:
                transitions[i + d_2, ''] = [final]
                
        states = a1.states + a2.states + 1
        finals = { final }
        
        return NDFA(states, finals, transitions, start)
    

    def closure(a1):
        transitions = {}
        
        start = 0
        d_1 = 1
        final = a1.states + d_1
        
        for (origin, symbol), destinations in a1.map.items():
            transitions[d_1 + origin, symbol] = [d_1 + d for d in destinations] 
        transitions[start, ''] = [a1.start + d_1 , final]
        
        for i in a1.finals:
            try:
                transitions[i + d_1, ''].add(final)
                transitions[i + d_1, ''].add(a1.start + d_1)
            except KeyError:
                transitions[i + d_1, ''] = [final, a1.start + d_1]
                
        states = a1.states +  2
        finals = { final }
        
        return NDFA(states, finals, transitions, start)
    

class DFA(NDFA):    
    def __init__(self, states: int, finals: list[int], transitions: dict[(int,str):int], start: int = 0):
        transitions = { key: [value] for key, value in transitions.items() }
        NDFA.__init__(self, states, finals, transitions, start)
        self.current = start