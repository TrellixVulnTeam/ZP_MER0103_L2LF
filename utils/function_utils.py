import utils.helper_utils as h_utils
import copy
import itertools

#funkce pro vypocet mnoziny FIRST a FOLLOW
def firstAndFollow(grammarList, computeFirst, computeFollow):
    first = {}
    follow = {}
    epsilon = set()
    #priprava neterminalnich symbolu do struktury dictionary pro FIRST a FOLLOW
    for i in grammarList.nonterminals:
        # reset first/follow mnozin v jiz nactene gramatice
        i.first = []
        i.follow = []
        first.update({i.value: set()})
        if(grammarList.symbol.value in i.value):
            follow.update({i.value: set(' ')})
        else:
            follow.update({i.value: set()})
    #priprava terminalnich symbolu do struktury dictionary pro FIRST
    for i in grammarList.terminals:
        first.update({i.value: {i.value}})
    #nacteni vsech pravidel do n-tice (struktura tuple)
    rules = h_utils.getRulesSet(grammarList.rules)
    nonTerminals = list(map(lambda x: x.value, grammarList.nonterminals))
    while True: #cyklus se opakuje, dokud jsou do mnozin pridavany nove symboly
        updated = False
        for nt, expression in rules:
            if computeFirst or computeFollow: #vypocet mnoziny FIRST
                r = expression.split(' ')
                if (len(r) == 1 and expression not in nonTerminals):
                    if expression == 'eps':
                        expression = ''
                    for symbol in expression:
                        updated |= h_utils.union(first[nt], first[symbol])
                        if symbol not in epsilon:
                            break
                    else:
                        updated |= h_utils.union(epsilon, {nt})
                else:
                    for symbol in r:
                        updated |= h_utils.union(first[nt], first[symbol])
                        if symbol not in epsilon:
                            break
                    else:
                        updated |= h_utils.union(epsilon, {nt})
        for nt, expression in rules:
            if computeFollow: #vypocet mnoziny FOLLOW
                aux = follow[nt]
                r = expression.split(' ')
                if (len(r) == 1 and expression not in nonTerminals):
                    if expression == 'eps':
                        expression = ''
                    for symbol in reversed(expression):
                        if symbol in follow:
                            updated |= h_utils.union(follow[symbol], aux)
                        if symbol in epsilon:
                            aux = aux.union(first[symbol])
                        else:
                            aux = first[symbol]
                else:
                    for symbol in reversed(r):
                        if symbol in follow:
                            updated |= h_utils.union(follow[symbol], aux)
                        if symbol in epsilon:
                            aux = aux.union(first[symbol])
                        else:
                            aux = first[symbol]
        if not updated: #pokud v poslednim cyklu nebyly pridany zadne nove symboly do mnozin, funkce konci vypocet a navraci vypoctene mnoziny
            return first, follow, epsilon

#funkce pro redukci gramatiky
def reduction(grammarList):
    setOfTerminals = set() #struktura set pro nactene terminalni symboly
    setOfNonterminals = set() #struktura set pro nactene neterminalni symboly
    for i in grammarList.terminals:
        setOfTerminals.add(i.value)
    for i in grammarList.nonterminals:
        setOfNonterminals.add(i.value)
    T_validNonterminals = set() #struktura set pro nalezene validni neterminalni symboly
    D_reachableNonterminals = set() #struktura set pro nalezene dosazitelne neterminalni symboly
    rules = h_utils.getRulesSet(grammarList.rules) #nacteni vsech pravidel do n-tice (struktura tuple)
    updated = len(T_validNonterminals) - 1
    while updated != len(T_validNonterminals): #cyklus pro naplneni mnoziny validnich neterminalnich symbolu
        updated = len(T_validNonterminals)
        for nt, expression in rules:
            flag = True #pomocna promenna pro kontrolu, jestli je znak v mnozine terminalnich symbolu nebo v mnozine validnich neterminalnich symbolu
            r = expression.split(' ')
            if (len(r) == 1 and expression not in setOfNonterminals):
                for elem in expression:
                    #pokud dany znak neni v mnozine terminalnich symbolu
                    if (elem not in setOfTerminals and elem not in T_validNonterminals):
                        flag = False
            else:
                for elem in r:
                    if elem == '':
                        continue
                    # pokud dany znak neni v mnozine terminalnich symbolu
                    if (elem not in setOfTerminals and elem not in T_validNonterminals):
                        flag = False
            if(flag == True or expression == '' or expression == 'eps'):
                T_validNonterminals.add(nt)
    nonterminalsToRemove = set() #struktura set pro neterminalni symboly k odstraneni
    for i in setOfNonterminals:
        if(i not in T_validNonterminals):
            nonterminalsToRemove.update(i)
    rules = list(rules) #prevod n-tice na seznam
    listOfRules = copy.deepcopy(rules) #zkopirovani pravidel
    for rule in rules: #cyklus prochazejici jednotlive pravidla
        for elem in nonterminalsToRemove: #cyklus prochazejici jednotlive neterminalni symboly nalezene k odstraneni
            if elem in rule[0] or elem in rule[1]: #pokud je neterminalni symbol na leve nebo prave strane pravidla, odstranime jej
                if rule in listOfRules: #pravidlo lze odstranit, pouze pokud se v seznamu pravidel vyskytuje (napr. u pravidla A -> BC a nutnosti odstraneni B i C by se program pokusil odstranit totez pravidlo 2x)
                    listOfRules.remove(rule) #odstraneni pravidla ze seznamu
    D_reachableNonterminals.add(grammarList.symbol.value) #v mnozine dosazitelnych symbolu je na zacatky vzdy pocatecni symbol
    for i in listOfRules: #cyklus prochazi doposud zpracovane pravidla
        #vypocet dosazitelnych neterminalnich symbolu
        tempReachableNonterminals = D_reachableNonterminals.copy()
        for j in tempReachableNonterminals:
            if(j in i[0]):
                r = i[1].split(' ')
                if (len(r) == 1):
                    for elem in i[1]:
                        if(elem in setOfNonterminals and elem not in D_reachableNonterminals):
                            D_reachableNonterminals.add(elem)
                else:
                    for elem in r:
                        if elem == '':
                            continue
                        if(elem in setOfNonterminals and elem not in D_reachableNonterminals):
                            D_reachableNonterminals.add(elem)
    finalListOfRules = copy.deepcopy(listOfRules) #zkopirovani pravidel do finalni promenne
    for rule in listOfRules:
        for elem in T_validNonterminals:
            #odstraneni pravidel, ktere obsahuji nedosazitelne neterminalni symboly
            if((elem in rule[0] and elem not in D_reachableNonterminals) or (elem in rule[1] and elem not in D_reachableNonterminals)):
                if rule in finalListOfRules:
                    finalListOfRules.remove(rule)
    #pokud je pocet puvodnich pravidel stejny jako pocet pravidel po algoritmu redukce -> gramatika je jiz v redukovanem tvaru
    if(len(finalListOfRules) == len(rules)):
        isReduced = True
        return rules, isReduced, rules, T_validNonterminals, D_reachableNonterminals
    #gramatika byla zredukovana
    else:
        isReduced = False
        grammarList.setNewRulesFromTupleList(finalListOfRules)
        return set(finalListOfRules), isReduced, rules, T_validNonterminals, D_reachableNonterminals

#funkce pro odstraneni epsilon pravidel z gramatiky
def epsRulesRemoval(grammar, rules):
    setE = set() #mnozina E obsahuje vsechny neterminaly, ktere lze v gramatice prepsat na epsilon
    finalRules = []
    nonterminals = set()
    for nonterminal in grammar.nonterminals:
        nonterminals.add(nonterminal.value)
    terminals = set()
    for terminal in grammar.terminals:
        terminals.add(terminal.value)
    if rules: #pridani novych terminalu pri volani z funkce ChomskehoNF
        for nt, expression in rules:
            if nt not in nonterminals:
                nonterminals.add(nt)
        if expression == '': #pridam do mnoziny E neterminal, ktery lze prepsat na epsilon
            setE.update(nt)
    else: #volani pouze Epsilon removal nebo Simple rules removal
        for rule in grammar.rules:
            if ('Îµ' in rule.rightSide or 'epsilon' in rule.rightSide or 'eps' in rule.rightSide):  # ε
                setE.update(rule.leftSide)
        rules = h_utils.getRulesSet(grammar.rules)

    updated = True
    temp = '' #pomocna promenna pro viceznakove neterminaly
    while updated:
        changed = len(setE)
        for nt, expression in rules:
            flag = True
            temp = ''
            for i in expression:
                temp += i
                temp = temp.strip()
                if temp in nonterminals or temp in terminals:
                    if temp not in setE:
                        flag = False
                    temp = ''
            if flag:
                setE.add(nt)
        if changed == len(setE):
            updated = False
    idxCount = 0
    if grammar.symbol.value in setE: #jestlize se pocatecni symbol nachazi v mnozine E, pridavam novy neterminalni symbol umoznujici prepis na epsilon a prepis na pocatecni symbol CFG
        newNonterminal = grammar.symbol.value + str(idxCount)
        while newNonterminal in nonterminals: #pokud se neterminal Y1 nebo vyssi cislo jiz nachazi v mnozine neterminalu, inkrementiji citac a pokracuji az kdyz naleznu novy mozny neterminal
            idxCount += 1
            newNonterminal = grammar.symbol.value + str(idxCount)
            continue
        newRule = (newNonterminal, 'eps')
        newRule2 = (newNonterminal, grammar.symbol.value)
        finalRules.append(newRule)
        finalRules.append(newRule2)
        finalRules

    rulesWithoutEps = list(rules)
    for item in rulesWithoutEps:
        if item[1] == '' or item[1] == 'eps':
            rulesWithoutEps.remove(item)

    rules = tuple(rulesWithoutEps)
    for key, value in rules:
        occurrences = []
        sum = 0
        for i in setE:
            count = value.count(i)
            if count > 0: #zajimaji me pouze pravidla, v nichz je nalezen neterminal z mnoziny E
                sum += count
                indexes = list(h_utils.find_all(value, i)) #zjisteni indexu, kde se nachazeji
                occurrence = (i,count, indexes)
                occurrences.append(occurrence,)
        setOfRuleCombinations = set()
        #setOfRuleCombinations.add(value)
        temp = ''
        listOfCombinations = [] #naplneni kombinaci do promenne, osetreni viceznakovych neterminalu
        for i in value:
            temp += i
            temp = temp.strip()
            if temp in nonterminals or temp in terminals:
                listOfCombinations.append(temp)
                temp = ''
        combs = []
        for j in range(1, len(listOfCombinations) + 1):
            variant = [list(x) for x in itertools.combinations(listOfCombinations, j)]
            combs.extend(variant)
        finalCombs = combs
        lenValue = 0
        temp = ''
        for i in value:
            temp += i
            temp = temp.strip()
            if temp in nonterminals or temp in terminals:
                lenValue += 1
                temp = ''
        minLength = lenValue - sum
        for combination in combs[:]:
            counter = 0
            for item in combination:
                if item in setE:
                    counter += 1
            if ((len(combination) - counter) < minLength):
                finalCombs.remove(combination)
        for combi in finalCombs:
            temp = ' '.join(combi)
            setOfRuleCombinations.add(temp)
        for i in setOfRuleCombinations:
            finalRule = (key, i)
            finalRules.append(finalRule,)
    finalRulesWithoutDuplicates = []
    [finalRulesWithoutDuplicates.append(x) for x in finalRules if x not in finalRulesWithoutDuplicates] #odstraneni duplicitnich pravidel
    return finalRulesWithoutDuplicates, setE

def simpleRulesRemoval(rules, grammar):
    finalRules = []
    nonterminals = []
    for nonterminal in grammar.nonterminals:
        nonterminals.append(nonterminal.value)
    for nt, expression in rules:
        if nt not in nonterminals:
            nonterminals.append(nt)
    nonterminalsWithoutDuplicates = []
    [nonterminalsWithoutDuplicates.append(x) for x in nonterminals if x not in nonterminalsWithoutDuplicates] #odstraneni duplicitnich pravidel
    setsN = ''
    for i in nonterminalsWithoutDuplicates:
        setN = set()
        setN.add(i) #vlozeni sebe sama do mnoziny
        updated = True
        while updated:
            changed = len(setN)
            for nt, expression in rules:
                expression = expression.strip()
                if nt in setN:
                    if len(expression) == 1 or len(expression) > 1 and expression in nonterminals: # or if len(expression) > 1 and expression is in nonterminals
                        if expression in nonterminals:
                            setN.add(expression)
            if changed == len(setN):
                updated = False
        setsN += 'set N ' + str(i) + ' ' + str(setN) + '\n'
        for nt, expression in rules:
            if nt in setN and expression not in setN:
                finalRule = (i, expression)
                finalRules.append(finalRule,)
    finalRulesWithoutDuplicates = []
    [finalRulesWithoutDuplicates.append(x) for x in finalRules if x not in finalRulesWithoutDuplicates] #odstraneni duplicitnich pravidel
    setsN = setsN.strip()
    return finalRulesWithoutDuplicates, setsN

def convertToCNF(grammar):
    rules = h_utils.getRulesSet(grammar.rules)
    counter = 1
    augmentedRules = []
    nonterminals = set()
    for nonterminal in grammar.nonterminals:
        nonterminals.add(nonterminal.value)
    for nt, expression in rules: #v prvnim kroku prevedu pravidla o delce vic nez 2 na ekvivalentni pravidla delky max 2 pridanim novych neterminalnich symbolu
        index = 0
        r = expression.split(' ')
        if (len(r) == 1):
            if len(expression) <= 2:
                newRule = (nt, expression)
                augmentedRules.append(newRule)
            else:
                length = len(expression)
                newNt = nt
                while length > 2:
                    newNonterminal = 'Z' + str(counter)
                    if newNonterminal in nonterminals:
                        counter += 1
                        continue
                    if (length - 1) > 2:
                        newRule = (newNt, expression[index] + ' ' + newNonterminal)
                        newNt = newNonterminal
                        newNonterminal2 = 'Z' + str(counter + 1)
                        newRule2 = (newNonterminal, expression[index + 1] + ' ' + newNonterminal2)
                    else:
                        newRule = (newNt, expression[index] + ' ' + newNonterminal)
                        newRule2 = (newNonterminal, expression[index + 1] + ' ' + expression[index + 2])
                    length -= 1
                    counter += 1
                    index += 1
                    augmentedRules.append(newRule)
                    augmentedRules.append(newRule2)
        else:
            if len(r) <= 2:
                newRule = (nt, expression)
                augmentedRules.append(newRule)
            else:
                length = len(r)
                newNt = nt
                while length > 2:
                    newNonterminal = 'Z' + str(counter)
                    if newNonterminal in nonterminals:
                        counter += 1
                        continue
                    if (length - 1) > 2:
                        newRule = (newNt, r[index] + ' ' + newNonterminal)
                        newNt = newNonterminal
                        newNonterminal2 = 'Z' + str(counter + 1)
                        newRule2 = (newNonterminal, r[index + 1] + ' ' + newNonterminal2)
                    else:
                        newRule = (newNt, r[index] + ' ' + newNonterminal)
                        newRule2 = (newNonterminal, r[index + 1] + ' ' + r[index + 2])
                    length -= 1
                    counter += 1
                    index += 1
                    augmentedRules.append(newRule)
                    augmentedRules.append(newRule2)
    augmentedRulesWithoutDuplicates = []
    [augmentedRulesWithoutDuplicates.append(x) for x in augmentedRules if x not in augmentedRulesWithoutDuplicates] #odstraneni duplicitnich pravidel
    return augmentedRulesWithoutDuplicates

def substituteTerminals(rules, grammar):
    counter = 1
    foundTerminals = set()
    finalRules = copy.deepcopy(rules) #zkopirovani pravidel
    terminals = []
    for i in grammar.terminals:
        terminals.append(i.value)
    nonterminals = set()
    for i in grammar.nonterminals:
        nonterminals.add(i.value)
    for nt, expression in rules: #v tomto cyklu prochazim pravidla a hledam vsechny mozne terminaly v pravidlech o 2 symbolech
        r = expression.split(' ')
        if len(r) == 2 and (r[0] in terminals or r[1] in terminals):
            if r[0] in terminals and r[1] in terminals: #v pripade nalezeni dvou terminalu soucasne vytvorim pro oba nove pravidlo a nahradim je novymi neterminaly
                if r[0] == r[1]: #nalezeny dva shodne terminaly
                    foundTerminals.add(r[0].strip())
                else: #nalezeny dva odlisne terminaly
                    foundTerminals.add(r[0].strip())
                    foundTerminals.add(r[1].strip())
            elif r[0] in terminals: #nalezen terminal vlevo
                foundTerminals.add(r[0].strip())
            else: #nalezen terminal vpravo
                foundTerminals.add(r[1].strip())
    replacedTerminals = set()
    for elem in foundTerminals:
        newNonterminal = 'Y' + str(counter)
        while newNonterminal in nonterminals: #pokud se neterminal Y1 nebo vyssi cislo jiz nachazi v mnozine neterminalu, inkrementiji citac a pokracuji az kdyz naleznu novy mozny neterminal
            counter += 1
            newNonterminal = 'Y' + str(counter)
            continue
        for nt, expression in rules:
            r = expression.split(' ')
            if len(r) == 2:
                if elem in r:
                    for i in range(len(r)):
                        if r[i] == elem:
                            r[i] = newNonterminal
                            flag = True
                    newRule = (nt, r[0] + ' ' + r[1])
                    newRule2 = (newNonterminal, elem)
                    finalRules.append(newRule)
                    finalRules.append(newRule2)
                    nonterminals.add(newNonterminal)
                    ruleToRemove = (nt.strip(), expression.strip())
                    if ruleToRemove in finalRules:
                        finalRules.remove(ruleToRemove)
        if flag:
            counter+=1
    finalRulesWithoutDuplicates = []
    [finalRulesWithoutDuplicates.append(x) for x in finalRules if x not in finalRulesWithoutDuplicates] #odstraneni duplicitnich pravidel
    return finalRulesWithoutDuplicates

def convertToGNF(rules, grammar):
    terminals = []
    for i in grammar.terminals:
        terminals.append(i.value)
    nonterminalsToRename = []
    for nt, expression in rules:
        if nt not in nonterminalsToRename:
            nonterminalsToRename.append(nt)
        r = expression.split(' ')
        if len(r) == 1:
            for symbol in expression: #jednoznake neterminaly bez mezery na prave strane pravidla
                if symbol not in nonterminalsToRename and symbol not in terminals:
                    nonterminalsToRename.append(symbol)
        else:
            for symbol in r:
                if symbol not in nonterminalsToRename and symbol not in terminals: #viceznake neterminaly s mezerou na prave strane pravidla
                    nonterminalsToRename.append(symbol)
    pattern = []
    for i, value in enumerate(nonterminalsToRename):
        newValue = (i + 1, value)
        pattern.append(newValue)
    renamedRules = [] #copy.deepcopy(rules) #zkopirovani pravidel
    for nt, expression in rules:
        newLeftside = nt
        if nt in nonterminalsToRename:
            for elem in pattern:
                if nt == elem[1]:
                    newLeftside = 'X' + str(elem[0]) #X a cislo podle indexu z patternu
        newRightside = expression
        r = expression.split(' ')
        if len(r) == 2:
            for elem in pattern:
                if elem[1] in r: #prepsani neterminalu na prave strane pravidla
                    for i in range(len(r)):
                        if  r[i] == elem[1]:
                            r[i] = 'X' + str(elem[0])
                            newRightside = (r[0] + ' ' + r[1])
        newRule = (newLeftside, newRightside)
        renamedRules.append(newRule)
    counter = 1
    changed = True
    leftRecursions = []
    while changed:
        sortedRules = []
        changed = False
        for nt, expression in renamedRules:
            compareLeft = nt[1:]
            r = expression.split(' ')
            if r[0] not in terminals: #pokud zacina prava strana terminalem, je jiz pravidlo v GNF
                if len(r) >= 2:
                    compareNt = r[0]
                    compareRight = r[0][1:]
                    r.pop(0)
                    if int(compareLeft) > int(compareRight):
                        for nt2, expression2 in renamedRules:
                            if nt2 == compareNt:
                                newRightside = ''
                                newRightside = expression2 + ' ' + ' '.join(r)
                                newRule = (nt,newRightside)
                                sortedRules.append(newRule)
                                changed = True
                    elif int(compareLeft) == int(compareRight): #odstranuji levou rekurzi
                        newNonterminal = 'W' + str(counter)
                        newRule = (newNonterminal, ' '.join(r) + ' ' + newNonterminal)
                        newRule2 = (newNonterminal, ' '.join(r))
                        sortedRules.append(newRule)
                        sortedRules.append(newRule2)
                        leftRecursion = (nt, newNonterminal)
                        leftRecursions.append(leftRecursion)
                    else:
                        newRule = (nt, expression)
                        sortedRules.append(newRule)
                else:
                    newRule = (nt, expression)
                    sortedRules.append(newRule)
            else:
                newRule = (nt,expression)
                sortedRules.append(newRule)
        renamedRules = sortedRules
    sortedRulesWithoutLeftRecursion =  copy.deepcopy(sortedRules)
    if len(leftRecursions) != 0: #pokud byly nalezeny leve rekurze, odstranim je
        for recursion in leftRecursions:
            for nt, expression in sortedRules:
                if nt == recursion[0]:
                    newRule = (nt, expression + ' ' +recursion[1])
                    sortedRulesWithoutLeftRecursion.append(newRule)
    changed = True
    while changed:
        updatedList = []
        changed = False
        for nt, expression in sortedRulesWithoutLeftRecursion:
            r = expression.split(' ')
            if r[0] not in terminals: #pokud zacina prava strana terminalem, je jiz pravidlo v GNF
                if len(r) >= 2:
                    r = expression.split(' ')
                    temp = r
                    for nt2, expression2 in sortedRulesWithoutLeftRecursion:
                        if nt2 == r[0]:
                            newRule = (nt, expression2 + ' ' + ' '.join(temp))
                            updatedList.append(newRule)
                            ruleToRemove = (nt, expression)
                            if ruleToRemove in updatedList:
                                updatedList.remove(ruleToRemove)
                            changed = True
            else:
                newRule = (nt, expression)
                updatedList.append(newRule)
        sortedRulesWithoutLeftRecursion = updatedList
    updatedListWithoutDuplicates = []
    [updatedListWithoutDuplicates.append(x) for x in updatedList if x not in updatedListWithoutDuplicates] #odstraneni duplicitnich pravidel
    return updatedListWithoutDuplicates