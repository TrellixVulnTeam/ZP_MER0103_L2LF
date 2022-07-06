import sys
from tabulate import tabulate

helpMessage = '. Check the readme.txt file for more details.'
outputFileCreated = 'Program úspěšně vypsal hodnoty do zadaného výstupního souboru.'

#funkce vypisujici mnozinu FIRST do Multiline elementu
def printFirstToMultiline(first, epsilon, grammar):
    data = '### FIRST set ###\n'
    for key, value in first.items():
        if (key in epsilon):  # pokud je neterminal i v mnozine epsilon, je epsilon v mnozine first daneho neterminalu
            value.add('eps')
        temp = [] #setrizeni terminalu ve vypisu podle poradi na vstupu
        for i in grammar.terminals:
            if i.value in value:
                temp.append(i.value)
        if 'eps' in value:
            temp.append('eps') #konec setrizeni terminalu
        values = ', '.join(temp)
        data += key +' : { ' + values + ' }\n'
    return data

#funkce vypisujici mnozinu FOLLOW do Multiline elementu
def printFollowToMultiline(follow, grammar):
    data = '### FOLLOW set ###\n'
    for key, value in follow.items():
        if (' ' in value):  # nahrazeni mezery za epsilon pro vypis
            value.remove(' ')
            value.add('eps')
        temp = [] #setrizeni terminalu ve vypisu podle poradi na vstupu
        for i in grammar.terminals:
            if i.value in value:
                temp.append(i.value)
        if 'eps' in value:
            temp.append('eps') #konec setrizeni
        values = ', '.join(temp)
        data += key +' : { ' + values + ' }\n'
    return data

#funkce vypisujici informaci o zredukovatelnosti gramatiky do Multiline elementu
def printReductionInfoToMultiline(isReduced):
    data = '### Reduction ###\n'
    if isReduced:
        data += 'CFG is already reduced\n'
    else:
        data += 'CFG has been reduced\n'
    return data

#funkce vypisujici jednotlive pravidla gramatiky
def printGrammarRules(grammar):
    print('Rules: ')
    previousNonterminal = '' #pomocna promenna pro zjisteni predchoziho neterminalniho symbolu
    for rule in grammar:
        if previousNonterminal != rule[0]:
            if previousNonterminal != '':
                print('\n',end='')
            if rule[1] == '': #prazdna prava strana znamena eps
                print(rule[0], '-> eps', end='')
            else:
                print(rule[0],'->',rule[1],end='')
        else:
            if rule[1] == '': #prazdna prava strana znamena eps
                print(' | eps',end='')
            else:
                print(' |',rule[1],end='')
        previousNonterminal = rule[0]
    print('')
    return

#funkce vypisujici jednotlive pravidla gramatiky do Multiline elementu
def printReductionGrammarRulesToMultiline(rules, grammar, originRules):
    sortedRules = 'Rules: \n'
    temp = [] #pomocna promenna pro serazeni pravidel na vypisu
    temp2 = [] #pomocna promenna pro serazeni pravidel na vypisu
    for i in grammar.nonterminals: #iterace pres vsechny neterminaly
        for key, value in rules: #iterace pres set pravidel
            if key == i.value: #pri nalezeni pravidla, u nehoz se shoduje neterminal, pridam pravou stranu pravidla do pomocne promenne
                temp.append(value)
        for key2, value2 in originRules: #projdu seznam pravych stran puvodnich pravidel a jestlize se vyskytuji v me pomocne promenne
            if value2 in temp:
                if value2 == '':
                    value2 = 'eps'
                if key2 == i.value:
                    temp2.append(value2) #pridam pravou stranu do druhe pomocne promenne
        for key3, value3 in rules: #iteruji pres set pravidel a vytvorim pravidla na zaklade druhe pomocne promenne
            if key3 == i.value:
                sortedRules += i.value + ' -> ' + ' | '.join(temp2) + '\n'
                break
        temp = []
        temp2 = []
    return sortedRules

#funkce vypisujici jednotlive pravidla gramatiky do Multiline elementu
def printRemovalGrammarRulesToMultiline(rules, grammar):
    sortedRules = 'Rules: \n'
    temp = []
    nonterminals = []
    for nonterminal in grammar.nonterminals:
        nonterminals.append(nonterminal.value)
    for nt, expression in rules:
        if nt not in nonterminals:
            nonterminals.append(nt)
    nonterminalsWithoutDuplicates = []
    [nonterminalsWithoutDuplicates.append(x) for x in nonterminals if x not in nonterminalsWithoutDuplicates] #odstraneni duplicitnich pravidel
    for i in nonterminalsWithoutDuplicates: #iterace pres vsechny neterminaly
        for key, value in rules: #iterace pres set pravidel
            if key == i: #pri nalezeni pravidla, u nehoz se shoduje neterminal, pridam pravou stranu pravidla do pomocne promenne
                temp.append(value)
        if len(temp) != 0:
            sortedRules += i + ' -> ' + ' | '.join(temp) + '\n'
        temp = []
    return sortedRules

def printCFG(grammar):
    data = 'CFG = ' + grammar.name + '\n' #vypsani nazvu CFG
    data += 'N = {' #vypsani neterminalnich symbolu
    numOfNonterminals = len(grammar.nonterminals) #pocet neterminalu, at muzu overit, ze za poslednim nepisu carku
    for i in grammar.nonterminals:
        data += i.value
        if i.name != (numOfNonterminals - 1): #pridani carky mezi polozky krome posledni
            data += ', '
    data += '}\n'

    data += 'T = {' #vypsani terminalnich symbolu
    numOfTerminals = len(grammar.terminals)  #pocet terminalu, at muzu overit, ze za poslednim nepisu carku
    for j in grammar.terminals:
        data += j.value
        if j.name != (numOfTerminals - 1): #pridani carky mezi polozky krome posledni
            data += ', '
    data += '}\n'

    data += 'S = ' + grammar.symbol.value + '\n' #vypsani pocatecniho symbolu

    data += 'P = ' #vypsani pravidel gramatiky
    for rule in grammar.rules:
        data += rule.leftSide + ' -> '
        numOfElements = len(rule.rightSide)
        for elem in rule.rightSide:
            #data += elem
            if numOfElements > 1:
                data += elem + ' | '
            else:
                data += elem + '\n'
            numOfElements -= 1
    return data

def printError(message):
    sys.stderr.write(message + helpMessage)

def insert_pointer(string, index):
    return string[:index] + '.' + string[index:]

def printClosuresToMultiline(closures):
    data = ''
    for key in closures:
        data += 'KEY %s\n' % (key)
        for rule in closures[key].rules:
            data += '%s->%s goto %s\n' % (rule.leftSide, insert_pointer(rule.rightSide[0], rule.pointer), rule.goto)
        data += '\n'
    return data

def printParsingTableToMultiline(grammar, parsingTable):
    indexes = list(parsingTable.keys())
    columns = []
    for terminal in grammar.terminals:
        columns.append("%s" % terminal.value)
    columns.append(';')
    for nonterminal in grammar.nonterminals:
        columns.append("%s" % nonterminal.value)

    table = []

    for i in indexes:
        row = []
        row.append(i)
        for j in columns:
            if j.strip() in parsingTable[i]:
                row.append(parsingTable[i][j.strip()])
            else:
                row.append('')
        table.append(row)

    headers = [''] + columns
    return tabulate(table, headers = headers, tablefmt='pretty')

def printLLParsingTableToMultiline(grammar, parsingTable):
    data = ''
    for rule in parsingTable['ruleList']:
        data += '%s. %s->%s \n' % (rule.pointer, rule.leftSide, rule.rightSide[0])
    data += '\n'

    headers = ['']
    columns = []
    for terminal in grammar.terminals:
        columns.append(terminal.value)
    columns.append(';')

    table = []
    for key in parsingTable:

        if key == 'ruleList':
            continue
        row = [key]
        for terminal in columns:
            if terminal in parsingTable[key]:
                rule = parsingTable[key][terminal]
                row.append(rule.pointer)
            elif ';' in parsingTable[key]:
                rule = parsingTable[key][';']
                row.append(rule.pointer)
            else:
                row.append('')
        table.append(row)
    return data + tabulate(table, headers = headers + columns, tablefmt='pretty')

def printPushdownAutomaton(grammar):
    data = ''
    stateCnt = 0
    data += 'M = (Q, \u03A3, Γ, δ, q0, Z0)\n'
    data += 'Q = {'
    stateList = ['q0']
    data += ','.join(stateList)
    data += '}\n'
    data += '\u03A3 = {%s}\n' % ', '.join(map(lambda nt: nt.value, grammar.terminals))
    data += 'Γ = {%s}\n' % ', '.join(map(lambda nt: nt.value, grammar.nonterminals + grammar.terminals))
    data += 'δ = {\n'
    for rule in grammar.rules:
        for rs in rule.rightSide:
            data += '  q0 %s --[ε]-> q0 %s\n' % (rule.leftSide, rs)
    for terminal in grammar.terminals:
        data += '  q0 %s --[%s]-> q0\n' % (terminal.value, terminal.value)
    data += '}\n'
    data += 'q0 = q0\n'
    data += 'Z0 = %s\n' % grammar.symbol.value
    return data
