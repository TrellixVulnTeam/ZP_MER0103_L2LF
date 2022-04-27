import sys

helpMessage = '. Pro napovedu spustte program s parametrem -help.'
outputFileCreated = 'Program úspěšně vypsal hodnoty do zadaného výstupního souboru.'

#funkce vypisujici mnozinu FIRST
def printFirst(first, epsilon):
    print('### FIRST set ###')
    for key, value in first.items():
        if (key in epsilon):  # pokud je neterminal i v mnozine epsilon, je epsilon v mnozine first daneho neterminalu
            value.add('eps')
        print(key, ':', value)

#funkce vypisujici mnozinu FIRST do Multiline elementu
def printFirstToMultiline(first, epsilon):
    data = '### FIRST set ###\n'
    for key, value in first.items():
        if (key in epsilon):  # pokud je neterminal i v mnozine epsilon, je epsilon v mnozine first daneho neterminalu
            value.add('eps')
        print(key, ':', value)
        values = ', '.join(value)
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
def printFollowToMultiline(follow):
    data = '### FOLLOW set ###\n'
    for key, value in follow.items():
        if (' ' in value):  # nahrazeni mezery za epsilon pro vypis
            value.remove(' ')
            value.add('eps')
        values = ', '.join(value)
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

#funkce vypisujici jednotlive pravidla gramatiky do Multiline elementu
def printGrammarRulesToMultiline(rules):
    print(rules)
    data = 'Rules: \n'
    previousNonterminal = '' #pomocna promenna pro zjisteni predchoziho neterminalniho symbolu
    for rule in rules:
        if previousNonterminal != rule[0]:
            if previousNonterminal != '':
                data += '\n'
            if rule[1] == '': #prazdna prava strana znamena eps
                data += rule[0] + ' -> eps'
            else:
                data += rule[0] + ' -> ' + rule[1]
        else:
            if rule[1] == '': #prazdna prava strana znamena eps
                data += ' | eps'
            else:
                data += ' | ' + rule[1]
        previousNonterminal = rule[0]
    data += '\n'
    return data

def printCFGPattern():
    return 'cfg=\nN={,}\nT={,}\nS=\nP=S->'

def printError(message):
    sys.stderr.write(message + helpMessage)
    sys.exit(1)

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
    data += '$  | '
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
        if '$' in parsingTable[key]:
            data += parsingTable[key]['$']
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
    data += '  $ | \n'

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
        if '$' in parsingTable[key]:
            rule = parsingTable[key]['$']
            data += "  %s " % rule.pointer
        else:
            data += "     "
        data += "| "
        data += "\n"
    return data

def printStackAutomaton(grammar):
    data = ''
    stateCnt = 0

    data += 'M = (Q,Σ,Γ,δ,q0,Z0)\n'
    data += 'Q = {'
    stateList = ['q0']
    for i in range(len(grammar.terminals)):
        stateList.append('q%s' % (i+1))
    data += ','.join(stateList)
    data += '}\n'
    data += 'Σ = %s\n' % ','.join(map(lambda nt: nt.value, grammar.terminals))
    data += 'Γ = %s\n' % ','.join(map(lambda nt: nt.value, grammar.nonterminals + grammar.terminals))
    data += 'δ = {\n'
    data += '  q0ε --[ε]-> q0 ε\n'
    for rule in grammar.rules:
        for rs in rule.rightSide:
            data += '  q0%s --[ε]-> q0 %s\n' % (rule.leftSide, rs)
    for terminal in grammar.terminals:
        data += '  q%s%s --[ε]-> q%s %s\n' % (stateCnt, terminal.value, stateCnt+1, terminal.value)
        stateCnt +=1
    data += '}\n'
    data += 'q0 = q0\n'
    data += 'Z0 = %s\n' % grammar.symbol.value

    return data