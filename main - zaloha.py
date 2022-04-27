import sys, argparse, copy
import PySimpleGUIQt as sg
import utils.helper_utils as h_utils
import utils.print_utils as p_utils
import utils.struct_utils as s_utils
from collections import namedtuple

identificator = ''
grammarList = []

def parseArguments():
    parser = argparse.ArgumentParser(description='Program je nutne spustit s argumentem -i INPUTFILE, pricemz INPUTFILE je nazev vstupniho souboru. Napovedu lze zobrazit argumentem -h.')
    parser.add_argument('-i', '--inputFile', required=True, help='Input file must be specified', default='grammar.txt')
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
        arguments = s_utils.Arguments(args.inputFile, outputFile, True, True, True, True)
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
                    print("konec souboru!")
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
        for nt, expression in rules:
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
    # print('mnozina T = ',T_validNonterminals)
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
    # print('mnozina D = ',D_reachableNonterminals)
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
        grammarList.setNewRulesFromTupleList(finalListOfRules)
        return finalListOfRules, isReduced

#funkce pro odstraneni epsilon pravidel z gramatiky
def epsRulesRemoval(grammarList):
    setE = set() #mnozina E obsahuje vsechny neterminaly, ktere lze v gramatice prepsat na epsilon
    for rule in grammarList.rules:
        if ('Îµ' in rule.rightSide or 'epsilon' in rule.rightSide or 'eps' in rule.rightSide):  # ε
            setE.update(rule.leftSide)
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
    print('mnozina E = ',setE)
    newRules = copy.deepcopy(rules)
    for rule in rules: #cyklus prochazi vsechny pravidla
        for i in setE: #cyklus prochazi vsechny symboly z mnoziny E
            for j in rule[1]: #cyklus prochazi vsechny znaky z prave strany daneho pravidla
                if i == j: #pokud se symbol z mnoziny E shoduje se znakem z prave strany daneho pravidla, budu generovat nove pravidla namisto epsilon
                    for x in range(rule[1].count(j)): #iteruji tolikrat, kolikrat byl dany neterminalni symbol nalezen na prav estrane pravidla
                        if rule[1].count(j) == 1: #reseni pro pravidla s jednim vyskytem neterminalu
                            temp = rule[1]
                            temp = temp.replace(j,'')
                            newRule = (rule[0],temp)
                            newRules += (newRule,)
                        if (rule[1].count(j) == len(rule[1])) and len(rule[1]) > 1: #reseni pro pavidla se dvema a vice vyskyty stejneho neterminalniho symbolu v pravidlu
                            temp = rule[1]
                            for i in range(len(rule[1])-1):
                                temp = rule[1][i+1:]
                                newRule = (rule[0], temp)
                                newRules += (newRule,)
                            #print('tak co:',rule[0],'->',rule[1],'odstranuji:',j)
    return set(newRules)
    '''vypsani vsech moznych podretezcu zadaneho retezce
    test = "ABCA"
    n = len(test)
    for i in range(n):
        temp = ""
        for j in range(i, n):
            temp += test[j]
            print(temp)'''

#hlavni funkce, skrze kterou jsou volany prislusne funkce na zaklade zadanych argumentu
def main():
    arguments = parseArguments() #parsovani argumentu ze vstupu, funkce fraci strukturu namedTuple Arguments
    grammarList = loadAndParseData(arguments.inputFile)

    sg.theme('LightGrey2')  # Add a touch of color
    tab1_layout = [[sg.Input( key='-IN-', default_text='grammar.txt'),sg.FileBrowse('Load CFG',file_types=(('Text files', '*.txt'),), key="fileBrowse",
        tooltip='Allows to choose text file containing context-free grammar', change_submits=True), sg.Button('Load CFG pattern', key='loadCFGPattern'),
        sg.Button('Clear windows', key='clearWindows')],
        [sg.Checkbox('FIRST', key='first'), sg.Checkbox('FOLLOW', key='follow'), sg.Checkbox('Reduction', key='reduction'),sg.Checkbox('Eps', key='eps')],
        [sg.Text('Input'),sg.Text('Output', pad=((342,3),3))],
        [sg.Multiline('Enter content-free grammar', key='input'), sg.Multiline('output', key='output')],
        [sg.Button('Enter'), sg.Button('Close'), sg.Checkbox('Print results to file', key='printToFile', pad=((500,3),3))]]
    tab2_layout = [
        [sg.Button('Build LR items', key='createParsingTable'), sg.Text('Parse:', pad=((260,3),3)), sg.InputText(key='text_to_parse',size=(25, 1)), sg.Button('Validate input', key='validateInput')],
        [sg.Text('LR Items:'),  sg.Text('Input validation:', pad=((312,3),3))],
        [sg.Multiline('', key='parsing_table'), sg.Multiline('' ,key='input_validation')]
    ]
    tab3_layout = [
        [sg.Button('Build LL(1) table', key='createLLParsingTable'), sg.Text('Parse:', pad=((260,3),3)), sg.InputText(key='ll_text_to_parse',size=(25, 1)), sg.Button('Validate input', key='validateLLInput')],
        [sg.Text('LL Table:'),  sg.Text('Input validation:', pad=((312,3),3))],
        [sg.Multiline('', key='ll_parsing_table'), sg.Multiline('' ,key='ll_input_validation')]
    ]
    layout = [[sg.TabGroup([[sg.Tab('CFG operations', tab1_layout), sg.Tab('LR Parser', tab2_layout), sg.Tab('LL Parser', tab3_layout)]])],
              [sg.Input( key='-IN-', default_text='grammar.txt'),sg.FileBrowse('Load CFG',file_types=(('Text files', '*.txt'),), key="fileBrowse",
        tooltip='Allows to choose text file containing context-free grammar', change_submits=True), sg.Button('Load CFG pattern', key='loadCFGPattern'),
        sg.Button('Clear windows', key='clearWindows')]
              ]

    window = sg.Window('Program pro analýzu bezkontextových gramatik - Daniel Merta, MER0103, ak. rok 2021/2022', layout, default_element_size=(50,15), resizable=True, auto_size_buttons=True)
    while True:
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED or event == 'Close':
            exit()
        elif event == 'loadCFGPattern':
            window['input'].update(p_utils.printCFGPattern())
        elif event == 'clearWindows':
            window['input'].update('')
            window['output'].update('')
        elif event == 'Enter':
            print(values['-IN-'])

            window['input'].update(h_utils.readWholeFile(values['-IN-']))
            data = ''
            if values['first'] or values['follow']:
                first, follow, epsilon = firstAndFollow(grammarList, values['first'], values['follow'])  # algoritmus pro pocitani FIRST a FOLLOW
                if values['first']:
                    data = p_utils.printFirstToMultiline(first, epsilon)
                if values['follow']:
                    data += p_utils.printFollowToMultiline(follow)
            if values['reduction']:
                reducedGrammar, isReduced = reduction(grammarList)  # algoritmus pro redukci gramatiky
                data += p_utils.printReductionInfoToMultiline(isReduced)
                data += p_utils.printGrammarRulesToMultiline(reducedGrammar)
            if values['eps']:
                data += '### odstraneni Epsilon pravidel ###\n'
                epsRemovedGrammar = epsRulesRemoval(grammarList)  # algoritmus pro odstraneni epsilon pravidel
                data += p_utils.printGrammarRulesToMultiline(epsRemovedGrammar)  # vypsani pravidel gramatiky
            window['output'].update(data)  # vypsani vysledku do vystupniho okna
            if values['printToFile']:
                f = open('outputFile.txt', 'w')
                f.write(data)
                f.close()
        elif event == 'createParsingTable':
            reduction(grammarList)  # algoritmus pro redukci gramatiky

            parser = s_utils.LRParser(grammarList)
            closures = parser.buildClosures()
            parsingTable = parser.buildParsingTable()

            data = ''
            data += '### LR polozky ###\n\n'
            data += p_utils.printClosuresToMultiline(closures)

            data += '\n\n'
            data += '### LR(0) tabulka ###\n\n'
            data += p_utils.printParsingTableToMultiline(grammarList, parsingTable)

            window['parsing_table'].update(data)

        elif event == 'validateInput':
            reduction(grammarList)  # algoritmus pro redukci gramatiky

            parser = s_utils.LRParser(grammarList)
            closures = parser.buildClosures()
            parsingTable = parser.buildParsingTable()

            dataLR = ''
            dataLR += '### LR polozky ###\n\n'
            dataLR += p_utils.printClosuresToMultiline(closures)

            dataLR += '\n\n'
            dataLR += '### LR(0) tabulka ###\n\n'
            dataLR += p_utils.printParsingTableToMultiline(grammarList, parsingTable)

            window['parsing_table'].update(dataLR)

            inputText = values['text_to_parse']
            if not inputText[-1] == '$': #input must have ending character
                inputText += '$'

            output = parser.parseLR0Input(inputText)

            data = '### LR(0) validation ###\n'
            data += "'%s' is %s" % (values['text_to_parse'], output)

            window['input_validation'].update(data)

        elif event == 'createLLParsingTable':
            first, follow, epsilon = firstAndFollow(grammarList, True, True)

            for nt in grammarList.nonterminals:
                for key in first:
                    if key == nt.value:
                        nt.first = first[key]
                for key in follow:
                    if key == nt.value:
                        nt.follow = follow[key]

            parser = s_utils.LLParser(grammarList)

            parsingTable = parser.buildParsingTable()

            data = ''
            data += '\n\n'
            data += '### LL(1) tabulka ###\n\n'
            data += p_utils.printLLParsingTableToMultiline(grammarList, parsingTable)

            window['ll_parsing_table'].update(data)

        elif event == 'validateLLInput':
            first, follow, epsilon = firstAndFollow(grammarList, True, True)

            for nt in grammarList.nonterminals:
                for key in first:
                    if key == nt.value:
                        nt.first = first[key]
                for key in follow:
                    if key == nt.value:
                        nt.follow = follow[key]

            parser = s_utils.LLParser(grammarList)

            parsingTable = parser.buildParsingTable()

            data = ''
            data += '\n\n'
            data += '### LL(1) tabulka ###\n\n'
            data += p_utils.printLLParsingTableToMultiline(grammarList, parsingTable)

            window['ll_parsing_table'].update(data)

            inputText = values['ll_text_to_parse']
            if len(inputText) == 0:
                data = '### No input provided ###\n'
                window['ll_input_validation'].update(data)
            else:
                if not inputText[-1] == '$': #input must have ending character
                    inputText += '$'

                output = parser.parseInput(inputText)

                data = '### LL(1) validation ###\n'
                data += "'%s' is %s" % (values['ll_text_to_parse'], output)

                window['ll_input_validation'].update(data)




    '''if arguments.first or arguments.follow: #vypocet mnoziny FIRST a FOLLOW
        first, follow, epsilon = firstAndFollow(grammarList, arguments.first, arguments.follow) #algoritmus pro pocitani FIRST a FOLLOW
        if arguments.first:
            p_utils.printFirst(first, epsilon) #vypsani mnoziny FIRST
        if arguments.follow:
            p_utils.printFollow(follow) #vypsani mnoziny FOLLOW
    if arguments.reduction: #pocitani redukovane gramatiky
        reducedGrammar, isReduced = reduction(grammarList) #algoritmus pro redukci gramatiky
        p_utils.printReductionInfo(isReduced) #vypsani informaci o redukci gramatiky
        p_utils.printGrammarRules(reducedGrammar) #vypsani pravidel gramatiky
    if arguments.epsRemoval: #odstraneni epsilon pravidel z gramatiky
        p_utils.printMessage('### odstraneni Epsilon pravidel ###')
        epsRemovedGrammar = epsRulesRemoval(grammarList) #algoritmus pro odstraneni epsilon pravidel
        p_utils.printGrammarRules(epsRemovedGrammar) #vypsani pravidel gramatiky
    if not arguments.outputFile: #uzavreni vystupniho souboru, pokud byl zadan v argumentu
        sys.stdout.close()'''

if __name__ == '__main__':
    main()
    #sys.exit(0) #uspesny konec programu