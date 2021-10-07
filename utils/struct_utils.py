from enum import Enum
from collections import namedtuple
specialChars = ['+','*','/','(',')','$']

Arguments = namedtuple('Arguments',['inputFile','outputFile','first','follow','reduction','epsRemoval'])

class TokenKind(Enum):
    EOF = 0 #konec souboru ''
    IDENT = 1 #identifikator
    NUM = 2 #cislo
    EQUALS = 3 #rovna se =
    OpenCurlyBrace = 4 #pocatecni chlupata zavorka {
    CloseCurlyBrace = 5 #koncova chlupata zavorka }
    PIPE = 6 #pajpa |
    COMMA = 7 #carka ,
    ARROW = 8 #sipka ->
    EOL = 9 #konec radku \n
    OtherChar = 10 #jiny znak
    ERROR = 11

#trida definujici terminalni symbol
class Terminal:
    def __init__(self,name,value):
        self.name = name
        self.value = value
        self.length = len(value)
    def __str__(self):
        return "TERMINALY JSOU name: % s, value is % s" % (self.name, self.value)

#trida definujici neterminalni symbol
class Nonterminal:
    def __init__(self,name,value):
        self.name = name
        self.value = value
        self.length = len(value)

#trida definujici pocatecni symbol
class StartingSymbol:
    def __init__(self,value):
        self.value = value
        self.length = len(value) #zbytecne asi

#trida definujici pravidlo gramatiky
class Rule:
    def __init__(self,name,leftSide,rightSide = []):
        self.name = name
        self.leftSide = leftSide
        self.rightSide = rightSide
        self.count = len(rightSide)

#trida definujici bezkontextovou gramatiku
class Grammar:
    count = 0
    terminals = []
    nonterminals = []
    symbol = ''
    rules = []
    def __init__(self,name):#,value):
        self.__class__.count += 1
        self.name = name
            #self.value = value
    def __str__(self):
        return "From str method of Grammar: nonterminaly jsou % s, terminaly jsou % s" % (self.nonterminals, self.terminals)
        #return '{g.nonterminals}: {g.terminals}'.format(g=Grammar)
    def addTerminal(self,terminal):
        self.terminals.append(terminal)
    def addNonterminal(self,nonterminal):
        self.nonterminals.append(nonterminal)
    def addSymbol(self,symbol):
        self.symbol = symbol
    def addRuleToGrammar(self,rule):
        self.rules.append(rule)