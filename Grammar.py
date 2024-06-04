from cmp.pycompiler import Symbol
from cmp.pycompiler import NonTerminal
from cmp.pycompiler import Terminal
from cmp.pycompiler import EOF
from cmp.pycompiler import Sentence, SentenceList
from cmp.pycompiler import Epsilon
from cmp.pycompiler import Production
from cmp.pycompiler import Grammar

from cmp.utils import pprint, inspect

G = Grammar()
E = G.NonTerminal('E', True)
T,F,X,Y = G.NonTerminals('T F X Y')
plus, minus, star, div, opar, cpar, num = G.Terminals('+ - * / ( ) num')

E %= T + X
X %= plus + T + X | minus + T + X | G.Epsilon
T %= F + Y
Y %= star + F + Y | div + F + Y | G.Epsilon
F %= num | opar + E + cpar

