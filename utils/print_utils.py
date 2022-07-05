import sys

helpMessage = '. Check the readme.txt file for more details.'
outputFileCreated = 'Program úspěšně vypsal hodnoty do zadaného výstupního souboru.'

#funkce vypisujici mnozinu FIRST
def printFirst(first, epsilon):
    print('### FIRST set ###')
    for key, value in first.items():
        if (key in epsilon):  # pokud je neterminal i v mnozine epsilon, je epsilon v mnozine first daneho neterminalu
            value.add('eps')
        print(key, ':', value)

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

#funkce vypisujici mnozinu FOLLOW
def printFollow(follow):
    print('### FOLLOW set ###')
    for key, value in follow.items():
        if (' ' in value):  # nahrazeni mezery za epsilon pro vypis
            value.remove(' ')
            value.add('eps')
        print(key, ':', value)

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

#funkce vypisujici informaci o zredukovatelnosti gramatiky
def printReductionInfo(isReduced):
    print('### Reduction ###')
    if isReduced:
        print('CFG is already reduced')
    else:
        print('CFG has been reduced')

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
    #print('cago belo rules', rules )
    for nonterminal in grammar.nonterminals:
        nonterminals.append(nonterminal.value)
    for nt, expression in rules:
        if nt not in nonterminals:
            #print("novy nt:", nt)
            nonterminals.append(nt)
    #print('moje neterminaly:', nonterminals)
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

def printCFGPattern():
    return 'cfg=\nN={,}\nT={,}\nS=\nP=S->'

def printError(message):
    sys.stderr.write(message + helpMessage)
    #sys.exit(1)

def printMessage(message):
    print(message)

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
    maxStepLength = 0 # output spacing formatting
    for key in parsingTable:
        keyLength = len(key)
        maxStepLength = keyLength if keyLength > maxStepLength else maxStepLength

    data = ''.join("   " for i in range(maxStepLength))
    data += " | "
    for terminal in grammar.terminals:
        data += "%s  " % terminal.value
        data += ''.join("  " for i in range(maxStepLength - len(terminal.value) + 1))
    data += ';  | '
    for nonterminal in grammar.nonterminals:
        data += "%s  " % nonterminal.value
        data += ''.join("  " for i in range(maxStepLength - len(nonterminal.value) + 1))
    data += "\n"
    for key in parsingTable:
        data += '%s' % key
        data += "".join(" " for i in range(maxStepLength))
        data += " | "
        for terminal in grammar.terminals:
            if terminal.value in parsingTable[key]:
                data += parsingTable[key][terminal.value]
                data += "".join("  " for i in range(maxStepLength))
            else:
                data += "".join("     " for i in range(maxStepLength))
        if ';' in parsingTable[key]:
            data += parsingTable[key][';']
            data += " "
        else:
            data += "".join("     " for i in range(maxStepLength))
        data += "| "
        for nonterminal in grammar.nonterminals:
            if nonterminal.value in parsingTable[key]:
                data += parsingTable[key][nonterminal.value]
                data += "".join("    " for i in range(maxStepLength))
            else:
                data += "".join("     " for i in range(maxStepLength))
        data += "\n"
    return data

def printLLParsingTableToMultiline(grammar, parsingTable):
    data = ''
    for rule in parsingTable['ruleList']:
        data += '%s. %s->%s \n' % (rule.pointer, rule.leftSide, rule.rightSide[0])
    data += '\n'
    data += '  '
    data += "  | "
    for terminal in grammar.terminals:
        data += "  %s " % terminal.value
    data += '  ; | \n'
    for key in parsingTable:
        if key == 'ruleList':
            continue

        data += '%s' % key
        data += " "
        data += " | "
        for terminal in grammar.terminals:
            if terminal.value in parsingTable[key]:
                rule = parsingTable[key][terminal.value]
                data += "  %s " % rule.pointer
            else:
                data += "    "
        if ';' in parsingTable[key]:
            rule = parsingTable[key][';']
            data += "  %s " % rule.pointer
        else:
            data += "     "
        data += "| "
        data += "\n"
    return data

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
