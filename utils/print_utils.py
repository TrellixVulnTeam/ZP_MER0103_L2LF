import sys

helpMessage = '. Pro napovedu spustte program s parametrem -help.'
outputFileCreated = 'Program úspěšně vypsal hodnoty do zadaného výstupního souboru.'

#funkce vypisujici mnozinu FIRST
def printFirst(first, epsilon):
    print('### mnozina FIRST ###')
    for key, value in first.items():
        if (key in epsilon):  # pokud je neterminal i v mnozine epsilon, je epsilon v mnozine first daneho neterminalu
            value.add('eps')
        print(key, ':', value)

#funkce vypisujici mnozinu FIRST do Multiline elementu
def printFirstToMultiline(first, epsilon):
    data = '### mnozina FIRST ###\n'
    for key, value in first.items():
        if (key in epsilon):  # pokud je neterminal i v mnozine epsilon, je epsilon v mnozine first daneho neterminalu
            value.add('eps')
        print(key, ':', value)
        values = ', '.join(value)
        data += key +' : { ' + values + ' }\n'
    return data

#funkce vypisujici mnozinu FOLLOW
def printFollow(follow):
    print('### mnozina FOLLOW ###')
    for key, value in follow.items():
        if (' ' in value):  # nahrazeni mezery za epsilon pro vypis
            value.remove(' ')
            value.add('eps')
        print(key, ':', value)

#funkce vypisujici mnozinu FOLLOW do Multiline elementu
def printFollowToMultiline(follow):
    data = '### mnozina FOLLOW ###\n'
    for key, value in follow.items():
        if (' ' in value):  # nahrazeni mezery za epsilon pro vypis
            value.remove(' ')
            value.add('eps')
        values = ', '.join(value)
        data += key +' : { ' + values + ' }\n'
    return data

#funkce vypisujici informaci o zredukovatelnosti gramatiky
def printReductionInfo(isReduced):
    print('### redukce gramatiky ###')
    if isReduced:
        print('Gramatika je jiz ve zredukovanem tvaru')
    else:
        print('Gramatiku bylo mozne zredukovat')

#funkce vypisujici informaci o zredukovatelnosti gramatiky do Multiline elementu
def printReductionInfoToMultiline(isReduced):
    data = '### redukce gramatiky ###\n'
    if isReduced:
        data += 'Gramatika je jiz ve zredukovanem tvaru\n'
    else:
        data += 'Gramatiku bylo mozne zredukovat\n'
    return data

#funkce vypisujici jednotlive pravidla gramatiky
def printGrammarRules(grammar):
    print('Pravidla gramatiky: ')
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
def printGrammarRulesToMultiline(grammar):
    data = 'Pravidla gramatiky: \n'
    previousNonterminal = '' #pomocna promenna pro zjisteni predchoziho neterminalniho symbolu
    for rule in grammar:
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