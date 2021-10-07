import sys, argparse, copy
import utils.helper_utils as h_utils
import utils.print_utils as p_utils
import utils.struct_utils as s_utils
from collections import namedtuple

identificator = ''
grammarList = []

def parseArguments():
    parser = argparse.ArgumentParser(description='Program je nutne spustit s argumentem -i INPUTFILE, pricemz INPUTFILE je nazev vstupniho souboru. Napovedu lze zobrazit argumentem -h.')
    parser.add_argument('-i', '--inputFile', required=True, help='Input file must be specified', default='gramatika.txt')
    parser.add_argument('-o', '--outputFile', required=False, help='Zadejte nazev vystupniho souboru')
    parser.add_argument('-f', '--first', help='Vypocet mnoziny FIRST', action='store_true')
    parser.add_argument('-g', '--follow', help='Vypocet mnoziny FOLLOW', action='store_true')
    parser.add_argument('-r', '--reduction', help='Redukce gramatiky', action='store_true')
    parser.add_argument('-e', '--epsRemoval', help='Odstraneni epsilon pravidel', action='store_true')
    parser.add_argument('-a', '--all', help='Vypocet vsech funkci programu', action='store_true')

    args = parser.parse_args()
    #nastaveni outputFile. Pokud je zadany jiny soubor nez s koncovkou .txt, je pouzita vychozi hodnota outputFile.txt
    if args.outputFile != None:
        if args.outputFile.endswith('.txt'):
            outputFile = args.outputFile
        else:
            outputFile = 'outputFile.txt'
        sys.stdout = open(outputFile, 'w')
    else: #outputFile nebyl zadan, vystup souboru je do prikazove radky
        outputFile = False
    if args.all:
        arguments = s_utils.Arguments(args.inputFile, outputFile, True, True, True, False)
    else:
        arguments = s_utils.Arguments(args.inputFile, outputFile, args.first, args.follow, args.reduction, args.epsRemoval)
    return arguments

def loadGrammarName(file):
    if(nextToken(file) == s_utils.TokenKind.EQUALS and nextToken(file) == s_utils.TokenKind.IDENT): #kontrola, ze je po "cfg" znak rovna se a identifikator
        return identificator
    else: #nespravna syntaxe
        s_utils.TokenKind.ERROR

def loadNonterminals(file,g): #funkce pro nacitani neterminalu
    if(nextToken(file) == s_utils.TokenKind.OpenCurlyBrace): #kontrola, ze je po "N" rovna se a zacinajici chlupate zavorka
        counter = 0
        while(nextToken(file) == s_utils.TokenKind.IDENT): #cyklus pro nacitani neterminalu
            if(identificator.isupper() and identificator.isalpha()): #kontrola velkych pismen a textovych znaku v identifikatoru
###staci kontrolovat alfanumericke znaky v neterminalech pomoci isalnum() funkce?
                nonterminal = s_utils.Nonterminal(counter, identificator) #vytvoreni objektu Nonterminal
                g.addNonterminal(nonterminal) #pridani objektu do gramatiky
                counter += 1
                t = nextToken(file) #nacteni dalsiho tokenu
                if(t == s_utils.TokenKind.COMMA): #nactena carka, pokracujeme v nacitani
                    continue
                elif(t == s_utils.TokenKind.CloseCurlyBrace): #nactena ukoncovani chlupata zavorka, konec nacitani
                    return
        return s_utils.TokenKind.ERROR
    else: #nespravna syntaxe
        return s_utils.TokenKind.ERROR

def loadTerminals(file,g):
    if(nextToken(file) == s_utils.TokenKind.OpenCurlyBrace): #kontrola zacinajici chlupate zavorky
        counter = 0
        while(nextToken(file) == s_utils.TokenKind.IDENT): #cyklus pro nacitani neterminalu
            if(identificator.islower() and identificator.isalpha() or identificator in s_utils.specialChars): #kontrola velkych pismen a alfanumerickych znaku v identifikatoru ci specialnich znaku
                terminal = s_utils.Terminal(counter, identificator) #vytvoreni objektu Nonterminal
                g.addTerminal(terminal) #pridani objektu do gramatiky
                counter += 1
                t = nextToken(file) #nacteni dalsiho tokenu
                if(t == s_utils.TokenKind.COMMA): #nactena carka, pokracujeme v nacitani
                    continue
                elif(t == s_utils.TokenKind.CloseCurlyBrace): #nactena ukoncovani chlupata zavorka, konec nacitani
                    return
        return s_utils.TokenKind.ERROR
    else: #nespravna syntaxe
        return s_utils.TokenKind.ERROR

def loadStartingSymbol(file,g): #funkce nacitajici pocatecni symbol
    if(nextToken(file) == s_utils.TokenKind.IDENT): #kontrola, ze se jedna o identifikator
        startingSymbol = s_utils.StartingSymbol(identificator)
        g.addSymbol(startingSymbol) #pridani pocatecniho symbolu do gramatiky
        return
    else:
        return s_utils.TokenKind.ERROR

def loadRules(file,g):
    counter = 0
    while(nextToken(file) == s_utils.TokenKind.IDENT and identificator.isupper() and identificator.isalpha()): #kontrola identifikatoru, velkych pismen a textovych znaku v identifikatoru
        #print("\n",counter,"\n")
        leftSide = identificator
        if(nextToken(file) != s_utils.TokenKind.ARROW):
            return s_utils.TokenKind.ERROR
        rightSide = []
        while (nextToken(file) == s_utils.TokenKind.IDENT ):
            rightSide.append(identificator)
            next = nextToken(file)  # nacteni dalsiho tokenu
            if(next == s_utils.TokenKind.PIPE):  # nactena pajpa, pokracujeme v nacitani
                continue
            if(endOfLine):
                rule = s_utils.Rule(counter, leftSide, rightSide)
                g.addRuleToGrammar(rule)
                file.seek(file.tell() - len(identificator), 0)
                counter += 1
                break
    file.seek(file.tell() - len(identificator), 0)  # vraceni ukazatele cteni v souboru o 1 zpet

#funkce nacitajici dalsi token z predaneho souboru
def nextToken(file):
    c = h_utils.readCharacter(file)
    if c == '': #kontrola konce souboru
        return s_utils.TokenKind.EOF #konec souboru

    while (c.isspace()): #remove space characters
        c = h_utils.readCharacter(file)
        continue
    if("=" in c): #= character
        return s_utils.TokenKind.EQUALS
    elif("{" in c):#{ character
        return s_utils.TokenKind.OpenCurlyBrace
    elif("}" in c): #} character
        return s_utils.TokenKind.CloseCurlyBrace
    elif("|" in c): #pipe character
        return s_utils.TokenKind.PIPE
    elif("," in c): #comma character
        return s_utils.TokenKind.COMMA
    elif("-" in c): #arrow character
        temp = h_utils.readNextChar(file) #kontrola nasledujiciho znaku >
        if(">" in temp):
            h_utils.readCharacter(file) #precteni znaku >
            #print("NASEL JSEM SIPKU\n")
            return s_utils.TokenKind.ARROW #-> character
        else:
            return s_utils.TokenKind.ERROR
    elif(c.isalnum() or c in s_utils.specialChars): # identifikator a-z
        #print("hahahahaha")
        temp = h_utils.readNextChar(file)
        while(temp.isalnum() or temp in s_utils.specialChars):
            c = c + h_utils.readCharacter(file)
            temp = h_utils.readNextChar(file)
        if(temp == "\n"):
            global endOfLine
            endOfLine = True
            #print("MAM KONEC RADKU")
        global identificator
        identificator = c
        #print("identifikator v nextToken fci: "+ identificator)
        return s_utils.TokenKind.IDENT
    elif(c in s_utils.specialChars):
        #print("jiny znak... je ", c)
        return s_utils.TokenKind.OtherChar
    else:
        return s_utils.TokenKind.ERROR

def loadAndParseData(inputFile):
    token = ''
    counter = 0
    grammarList = []
    try:
        with open(inputFile,"r") as file:
            while True:
                token = nextToken(file)
                if(token == s_utils.TokenKind.EOF):
                    print("konec souboru panacku!")
                    return grammarList
                elif(token == s_utils.TokenKind.EQUALS):
                    print("EQUALS TOKEN")
                elif(token == s_utils.TokenKind.OpenCurlyBrace):
                    print ("OpenCurlyBrace TOKEN")
                elif(token == s_utils.TokenKind.CloseCurlyBrace):
                    print ("CloseCurlyBrace TOKEN")
                elif(token == s_utils.TokenKind.PIPE):
                    print ("PIPE TOKEN")
                elif(token == s_utils.TokenKind.COMMA):
                    print ("COMMA TOKEN")
                elif(token == s_utils.TokenKind.IDENT):
                    if(identificator == "cfg"): #nacteni jmena a inicializace gramatiky
                        grammarName = loadGrammarName(file)
                        if(grammarName == s_utils.TokenKind.ERROR):
                            return s_utils.TokenKind.ERROR
                        else:
                            g = s_utils.Grammar(grammarName)
                            counter += 1
                    elif(identificator == "N" and nextToken(file) == s_utils.TokenKind.EQUALS):
                        loadNonterminals(file,g)
                        #print("neterminaly nacteny!")
                    elif(identificator == "T" and nextToken(file) == s_utils.TokenKind.EQUALS):
                        loadTerminals(file,g)
                        #print("terminaly nacteny!")
                    elif(identificator == "S" and nextToken(file) == s_utils.TokenKind.EQUALS):
                        loadStartingSymbol(file,g)
                        #print("symbol nacteny!")
                    elif(identificator == "P" and nextToken(file) == s_utils.TokenKind.EQUALS):
                        loadRules(file,g)
                        #print("pravidla nacteny!")
                        grammarList = copy.deepcopy(g)
                        if(grammarList.nonterminals != [] and grammarList.terminals != [] and grammarList.symbol != '' and grammarList.rules != []):
                            #print("Gramatika byla kompletne nactena")
                            return grammarList
                elif(token == s_utils.TokenKind.ERROR):
                    print("INCORRECT SYNTAX!")
    except FileNotFoundError:
        p_utils.printError("Zadany vstupni soubor nenalezen")

#funkce pro vypocet mnoziny FIRST a FOLLOW
def firstAndFollow(grammarList, computeFirst, computeFollow):
    first = {}
    follow = {}
    epsilon = set()
    #priprava neterminalnich symbolu do struktury dictionary pro FIRST a FOLLOW
    for i in grammarList.nonterminals:
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
    while True: #cyklus se opakuje, dokud jsou do mnozin pridavany nove symboly
        updated = False
        for nt, expression in rules:
            if computeFirst or computeFollow: #vypocet mnoziny FIRST
                for symbol in expression:
                    updated |= h_utils.union(first[nt], first[symbol])
                    if symbol not in epsilon:
                        break
                else:
                    updated |= h_utils.union(epsilon, {nt})
            if computeFollow: #vypocet mnoziny FOLLOW
                aux = follow[nt]
                for symbol in reversed(expression):
                    if symbol in follow:
                        updated |= h_utils.union(follow[symbol], aux)
                    if symbol in epsilon:
                        aux = aux.union(first[symbol])
                    else:
                        aux = first[symbol]
        if not updated: #pokud v poslednim cyklu nebyly pridany zadne nove symboly do mnozin, funkce ukoncuje vypocet a navraci spocitane mnoziny
            return first, follow, epsilon

#funkce pro redukci gramatiky
def reduction(grammarList):
    setOfTerminals = set() #struktura set pro nactene terminalni symboly
    setOfNonterminals = set() #struktura set pro nactene neterminalni symboly
    for i in grammarList.terminals:
        setOfTerminals.update(i.value)
    for i in grammarList.nonterminals:
        setOfNonterminals.update(i.value)
    T_validNonterminals = set() #struktura set pro nalezene validni neterminalni symboly
    D_reachableNonterminals = set() #struktura set pro nalezene dosazitelne neterminalni symboly
    rules = h_utils.getRulesSet(grammarList.rules) #nacteni vsech pravidel do n-tice (struktura tuple)
    updated = len(T_validNonterminals) - 1
    while updated != len(T_validNonterminals): #cyklus pro naplneni mnoziny validnich neterminalnich symbolu
        updated = len(T_validNonterminals)
        for nt, expression in rules:
            flag = True #pomocna promenna pro kontrolu, jestli je znak v mnozine terminalnich symbolu nebo v mnozine validnich neterminalnich symbolu
            for elem in expression:
                #pokud dany znak neni v mnozine terminalnich symbolu
                if (elem not in setOfTerminals and elem not in T_validNonterminals):
                    flag = False
            if(flag == True or expression == ''):
                T_validNonterminals.add(nt)
    print('mnozina T = ',T_validNonterminals)
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
                for elem in i[1]:
                    if(elem in setOfNonterminals and elem not in D_reachableNonterminals):
                        D_reachableNonterminals.update(elem)
    print('mnozina D = ',D_reachableNonterminals)
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
        return rules, isReduced
    #gramatika byla zredukovana
    else:
        isReduced = False
        return finalListOfRules, isReduced

#funkce pro odstraneni epsilon pravidel z gramatiky
def epsRulesRemoval(grammarList):
    setE = set() #mnozina E obsahuje vsechny neterminaly, ktere lze v gramatice prepsat na epsilon
    for rule in grammarList.rules:
        if ('Îµ' in rule.rightSide or 'epsilon' in rule.rightSide or 'eps' in rule.rightSide):  # ε
            setE.update(rule.leftSide)
    print('najite ciste epsilony: ',setE)
    rules = h_utils.getRulesSet(grammarList.rules)
    updated = True
    while updated:
        changed = len(setE)
        for nt, expression in rules:
            flag = True
            for i in expression:
                if i not in setE:
                    flag = False
            if flag:
                setE.update(nt)
        if changed == len(setE):
            updated = False
    print('setE: ',setE)
    print(list(rules))
    newRules = copy.deepcopy(rules)
    print(newRules)
    for rule in rules:
        for i in setE:
            for j in rule[1]:
                if i == j:
                    print('uprava: ', rule[1])
                    print(type(rule[1]))


                    n = len(rule[1])
                    string = str(rule[1])
                    for k in range(n):
                        temp = ""
                        for l in range(k, n):
                            temp += string[l]
                            print(temp)

    '''test = "ABCA"
    n = len(test)

    for i in range(n):
        temp = ""
        for j in range(i, n):
            temp += test[j]
            print(temp)
    '''

#hlavni funkce, skrze kterou jsou volany prislusne funkce na zaklade zadanych argumentu
def main():
    arguments = parseArguments() #parsovani argumentu ze vstupu, funkce fraci strukturu namedTuple Arguments
    grammarList = loadAndParseData(arguments.inputFile)
    if arguments.first or arguments.follow: #vypocet mnoziny FIRST a FOLLOW
        first, follow, epsilon = firstAndFollow(grammarList, arguments.first, arguments.follow) #algoritmus pro pocitani FIRST a FOLLOW
        if arguments.first:
            p_utils.printFirst(first, epsilon) #vypsani mnoziny FIRST
        if arguments.follow:
            p_utils.printFollow(follow) #vypsani mnoziny FOLLOW
    if arguments.reduction: #pocitani redukovane gramatiky
        p_utils.print('### redukce gramatiky ###')
        reducedGrammar, isReduced = reduction(grammarList) #algoritmus pro redukci gramatiky
        p_utils.printReductionInfo(isReduced) #vypsani informaci o redukci gramatiky
        p_utils.printGrammarRules(reducedGrammar) #vypsani pravidel gramatiky
    if arguments.epsRemoval: #odstraneni epsilon pravidel z gramatiky
        p_utils.printMessage('### odstraneni Epsilon pravidel ###')
        epsRemovedGrammar = epsRulesRemoval(grammarList) #algoritmus pro odstraneni epsilon pravidel
        #p_utils.printGrammarRules(epsRemovedGrammar) #vypsani pravidel gramatiky
    if not arguments.outputFile: #uzavreni vystupniho souboru, pokud byl zadan v argumentu
        sys.stdout.close()

if __name__ == '__main__':
    main()
    sys.exit(0) #uspesny konec programu