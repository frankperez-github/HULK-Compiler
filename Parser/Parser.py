from cmp.automata import State
from cmp.pycompiler import Item
from cmp.utils import ContainerSet

# errores detectados en el proceso del parser
class ParserError(Exception):
    def __init__(self, text, token_index):
        super().__init__(text)
        self.token_index = token_index

# Computes First(alpha)
def compute_local_first(firsts, alpha):
    first_alpha = ContainerSet()
    for symbol in alpha:
        if symbol.IsEpsilon:
            continue
        if symbol.IsTerminal:
            first_alpha.update(ContainerSet((symbol)))
            return first_alpha
        else:
            first_alpha.update(firsts[symbol])

            if not firsts[symbol].contains_epsilon:
                return first_alpha
    first_alpha.set_epsilon(True)
    return first_alpha

def compute_firsts(G):
    firsts = {}
    change = True

    for terminal in G.terminals:
        firsts[terminal] = ContainerSet(terminal)
        
    for nonterminal in G.nonTerminals:
        firsts[nonterminal] = ContainerSet()
    
    while change:
        change = False
        
        for production in G.Productions:
            X = production.Left
            alpha = production.Right
            
            first_X = firsts[X]
            try:
                first_alpha = firsts[alpha]
            except KeyError:
                first_alpha = firsts[alpha] = ContainerSet()
            
            local_first = compute_local_first(firsts, alpha)
           

            change |= first_alpha.hard_update(local_first)
            change |= first_X.hard_update(local_first)
                    
    return firsts

def expand(G, item, firsts):
    next_symbol = item.NextSymbol
    if next_symbol is None or not next_symbol.IsNonTerminal:
        return []
    lookaheads = ContainerSet()
    for prev in item.Preview():
        lookaheads.update(compute_local_first(firsts, prev))

    assert not lookaheads.contains_epsilon
    ans = []
    for p in next_symbol.productions:
        ans.append(Item(p,0,lookaheads))
    return ans

def compress(items):
    centers = {}

    for item in items:
        center = item.Center()
        try:
            lookaheads = centers[center]
        except KeyError:
            centers[center] = lookaheads = set()
        lookaheads.update(item.lookaheads)
    
    return { Item(x.production, x.pos, set(lookahead)) for x, lookahead in centers.items() }

def closure_lr1(G, items, firsts):
    closure = ContainerSet(*items)
    
    changed = True
    while changed:
        changed = False
        
        new_items = ContainerSet()
        for item in closure:
            new_items.extend(expand(G, item, firsts))
        changed = closure.update(new_items)
        
    return compress(closure)

def goto_lr1(G, items, symbol, firsts=None, just_kernel=False):
    assert just_kernel or firsts is not None, '`firsts` must be provided if `just_kernel=False`'
    items = frozenset(item.NextItem() for item in items if item.NextSymbol == symbol)
    return items if just_kernel else closure_lr1(G, items, firsts)


class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'
    
    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()
    
    
    def _build_parsing_table(self):
        raise NotImplementedError()


    def __call__(self, w):
        stack = [ 0 ]
        cursor = 0
        output = []
        operations = []
        while cursor < len(w):
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose: print(stack, '<---||--->', w[cursor:])
            if (state, lookahead) in self.action.keys():
                action, tag = self.action[state, lookahead]
                if action != self.OK: operations.append(action) 

                match action: 
                    #OK case
                    case self.OK:
                        return output, operations
                    
                    #Shift case
                    case self.SHIFT:
                        stack.append(tag)
                        cursor += 1
                    #Reduce case
                    case self.REDUCE: 
                        left, right = tag
                        for ele in right:
                            if not ele.IsEpsilon:
                                    stack.pop()
                        l = stack[-1]              
                        stack.append(self.goto[(l, left)])
                        output.append(tag)
                    #Invalid case
                    case _: 
                        
                        raise ParserError('Chain cannot be parsed', cursor)
            else:
                raise ParserError('Chain cannot be parsed', cursor)
        
        raise ParserError('Chain cannot be parsed', cursor)


def build_LR1_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'
    
    firsts = compute_firsts(G)
    firsts[G.EOF] = ContainerSet(G.EOF)
    
    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=[G.EOF])
    start = frozenset([start_item])
    closure = closure_lr1(G, start, firsts)
    automaton = State(frozenset(closure), True)
    
    pending = [ start ]
    visited = { start: automaton }
    
    while pending:
        current = pending.pop()
        current_state = visited[current]
        
        for symbol in G.terminals + G.nonTerminals:
            goto = frozenset(goto_lr1(G, current_state.state, symbol, firsts))
            if len(goto):
                if not goto in visited: 
                    next_state = State(goto, True)
                    pending.append(goto)
                    visited[goto] = next_state
                    current_state.add_transition(symbol.Name, next_state)
                else:
                    trans = visited[goto]
                    current_state.add_transition(symbol.Name, trans)
    
    return automaton


class LR1Parser(ShiftReduceParser):
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        
        automaton = build_LR1_automaton(G)
        for i, node in enumerate(automaton):
            if self.verbose: print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for item in node.state:
                left, _ = item.production
                next_ = item.NextSymbol

                if next_ is not None:
                    transition = node.transitions[next_.Name]
                    if next_.IsTerminal:
                        self._register(self.action, (idx, next_), (ShiftReduceParser.SHIFT, transition[0].idx))
                    else:
                        self._register(self.goto, (idx,next_), transition[0].idx)
                else:
                    if left == G.startSymbol:
                        self._register(self.action, (idx, G.EOF), (ShiftReduceParser.OK, None))
                    else:
                        for lookahead in item.lookaheads:
                            self._register(self.action, (idx, lookahead), (ShiftReduceParser.REDUCE, item.production))

    @staticmethod
    def _register(table, key, value): 
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value