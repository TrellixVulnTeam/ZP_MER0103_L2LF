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
        self.first = []
        self.follow = []

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
        self.pointer = 0
        self.goto = ''

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
    def addTerminal(self,terminal):
        self.terminals.append(terminal)
    def addNonterminal(self,nonterminal):
        self.nonterminals.append(nonterminal)
    def addSymbol(self,symbol):
        self.symbol = symbol
    def addRuleToGrammar(self,rule):
        self.rules.append(rule)
    def hasRule(self, rule):
        for gr in self.rules:
            if gr.leftSide == rule.leftSide:
                for rs in gr.rightSide:
                    if rule.rightSide[0] == rs:
                        return True
        return False

    def setNewRulesFromTupleList(self, ruleList):
        newRules = []
        for ruleTuple in ruleList:
            leftSide, rightSide = ruleTuple
            newRules.append(Rule(leftSide, leftSide, [rightSide]))
        self.rules = newRules



class Closure: #trida Closure
    def __init__(self):
        self.rules = []
        self.isFinal = False
    def createClosureRule(self, leftSide: str, rightSide:str, pointer: int, goto:str): #vytvoreni Closure pravidla
        rule = Rule(leftSide, leftSide, [rightSide])
        rule.pointer = pointer
        rule.goto = goto

        return rule

    def appendRule(self, leftSide: str, rightSide: str, pointer: int, goto: str):
        self.rules.append(self.createClosureRule(leftSide, rightSide, pointer, goto))
    def hasRule(self, rule: Rule):
        for r in self.rules:
            if r.leftSide.strip() == rule.leftSide.strip():
                for rv in rule.rightSide:
                    if r.rightSide[0] == rv and r.pointer == rule.pointer:
                        return True
        return False


class LRParser: #trida LR parseru
    def __init__(self, grammar : Grammar):
        self.grammar = grammar
        self.closures = {}
        self.parsingTable = {}
    def getGotoString(self, pointer, rightSide):
        if pointer < len(rightSide):
            return "%s%s" % (rightSide[0:pointer + 1], pointer + 1)
        return ''

    def extendChain(self, leftSide:str, rightSide: str, pointer: int, closureKey: str):
        if closureKey == '': #nic k rozvoji
            return
        if not closureKey in self.closures: # LR item jeste neexistuje
            self.closures[closureKey] = Closure()
        if pointer <= len(rightSide):
            if pointer < len(rightSide):
                if rightSide[pointer].isupper: #musi se do LR itemu rozvest pravidlo
                    for rule in self.grammar.rules:
                        if rule.leftSide == rightSide[pointer]:
                            for rs in rule.rightSide:
                                if not self.closures[closureKey].hasRule(self.closures[closureKey].createClosureRule(rule.leftSide, rs, 0, '')): #pridej pouze pokud tam jeste neni
                                    self.closures[closureKey].appendRule(rule.leftSide, rs, 0, self.getGotoString(0, rs))
                                    self.extendChain(rule.leftSide, rs, 0, closureKey) #closure se musi dale rozvest
                                else: #pravidlo je jiz tam
                                    return

            if self.closures[closureKey].hasRule(self.closures[closureKey].createClosureRule(leftSide, rightSide, pointer, '')): #pridej pouze pokud tam jeste neni
                return
            self.closures[closureKey].appendRule(leftSide, rightSide, pointer, self.getGotoString(pointer, rightSide))
            for rule in self.closures[closureKey].rules:
                self.extendChain(rule.leftSide, rule.rightSide[0], rule.pointer + 1, self.getGotoString(rule.pointer, rule.rightSide[0]))

    def buildClosures(self):
        augmentedRule = Rule('augmented', 'S\'', [self.grammar.symbol.value])
        for rv in augmentedRule.rightSide:
            self.extendChain(augmentedRule.leftSide, rv, 0, "%s%s" % (self.grammar.symbol.value, 0))
        cnt = 0
        keyMap = {}
        remappedClosures = {}
        for key in self.closures:
            newKey = "%s" % cnt
            keyMap[key] = newKey
            remappedClosures[newKey] = self.closures[key]
            cnt+= 1
        for key in remappedClosures:
            for rule in remappedClosures[key].rules:
                if rule.goto != '':
                    rule.goto = keyMap[rule.goto]

        self.closures = remappedClosures
        return self.closures

    def buildParsingTable(self):
        for key in self.closures:
            self.parsingTable[key] = {}
            for rule in self.closures[key].rules:
                if rule.goto == '' and rule.rightSide[0] == self.grammar.symbol.value:
                    self.parsingTable[key]['$'] = "acp"
                    continue
                if rule.goto == '': #finalni polozky
                    for terminal in self.grammar.terminals:
                        self.parsingTable[key][terminal.value] = "r%s-%s" % (rule.leftSide, len(rule.rightSide[0]))
                    self.parsingTable[key]['$'] = "r%s-%s" % (rule.leftSide, len(rule.rightSide[0]))
                    continue;
                expandChar = rule.rightSide[0][rule.pointer]
                if expandChar.isupper(): #nasleduje se neterminal, akce je GOTO
                    self.parsingTable[key][expandChar] = rule.goto
                    continue
                else:
                    self.parsingTable[key][expandChar] = "s%s" % rule.goto
        return self.parsingTable

    def parseLR0Input(self, inputText):
        if inputText == "": return "EMPTY"
        pointer = 0
        currentState = list(self.parsingTable.keys())[0]
        stack = [currentState] #zacatak prvnim stavem tabulky
        character = inputText[pointer]
        while(True):
            if character not in self.parsingTable[stack[-1]]:
                return 'INVALID'

            actionString = self.parsingTable[stack[-1]][character]

            if actionString == 'acp':
                return "VALID"

            actionType = actionString[:1]
            action = actionString[1:]

            if actionType == 's': #shift
                stack.append(character)
                stack.append(action)
                currentState = action
                pointer += 1
                character = inputText[pointer]
            if actionType == 'r':
                reduceDef = action.split("-")
                for i in range(int(reduceDef[1]) * 2):
                    stack.pop()
                lastState = stack[-1] #ziskej posledni element
                stack.append(reduceDef[0])
                stack.append(self.parsingTable[lastState][reduceDef[0]])

class LLParser:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.parsingTable = {}
        self.conflicts = {}
        for nt in self.grammar.nonterminals:
            self.conflicts[nt.value] = []

    def detectConflicts(self):
        for nt in self.grammar.nonterminals:
            for first in nt.first:
                if first in nt.follow: #kontrola FIRST/FOLLOW konfliktu
                    self.conflicts[nt.value].append('FIRST/FOLLOW')
                    break
        return self.conflicts

    def buildParsingTable(self):
        parsingTableRules = []
        ruleNum = 1
        for rule in self.grammar.rules:
            self.parsingTable[rule.leftSide] = {}
            for rs in rule.rightSide:
                term = rs[0] #nacteni polozky z prave strany
                parsingRule = None
                for r in parsingTableRules:
                    if r.leftSide == rule.leftSide and r.rightSide[0] == rs:
                        parsingRule = r
                        break
                if not parsingRule:
                    parsingRule = Rule(rule.leftSide, rule.leftSide, [rs])
                    parsingRule.pointer = ruleNum
                    ruleNum += 1
                    parsingTableRules.append(parsingRule)
                if rs == 'eps': #kontrola nasledujiciho
                    for nt in self.grammar.nonterminals:

                        if nt.value == parsingRule.leftSide:
                            for follow in nt.follow:
                                key = follow
                                if follow == 'eps' or follow == ' ':
                                    key = '$'
                                self.parsingTable[parsingRule.leftSide][key] = parsingRule
                            continue
                if len(list(filter (lambda x : x.value == term, self.grammar.terminals))) > 0:
                    self.parsingTable[parsingRule.leftSide][term] = parsingRule # "%s->%s" % (parsingRule.leftSide, parsingRule.rightSide[0])
                else:
                    for nt in self.grammar.nonterminals:
                        if nt.value == term:
                            for first in nt.first:
                                if first in self.parsingTable[parsingRule.leftSide]: #kontrola FIRST/FIRST konfliktu
                                    self.conflicts[nt.value].append('FIRST/FIRST')
                                self.parsingTable[parsingRule.leftSide][first] = parsingRule
                            continue
        self.parsingTable['ruleList'] = parsingTableRules
        return self.parsingTable

    def parseInput(self, inputText):
        if inputText == "": return "EMPTY"
        pointer = 0
        stack = [self.grammar.symbol.value] #prvni na zasobniku je pocatecni symbol
        while(len(stack) > 0):
            print(stack)
            top = stack[-1] #nacteni vrcholu zasobniku
            inputSymbol = inputText[pointer] #ukazatel aktualni pozice
            if top == inputSymbol: #byl najit terminal
                stack.pop()
                pointer += 1
            else:
                if top in self.parsingTable and inputSymbol in self.parsingTable[top]:
                    rule = self.parsingTable[top][inputSymbol]
                    stack.pop()
                    rs = rule.rightSide[0]
                    if rs == 'eps': #nalezen epsilon, nic dalsiho nedelam
                        continue
                    for c in reversed(rs):
                        stack.append(c)
                else:
                    return 'INVALID'
        return 'VALID'