import copy, sys
import PySimpleGUIQt as sg
import utils.helper_utils as h_utils
import utils.print_utils as p_utils
import utils.struct_utils as s_utils
import itertools

identificator = ''
grammarList = []
index = 0 #pozice prave nacitaneho znaku
counter = 0 #citac nactenych gramatik

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
    global endOfLine, index
    counter = 0
    while(nextToken(file) == s_utils.TokenKind.IDENT and identificator.isupper() and identificator.isalpha()): #kontrola identifikatoru, velkych pismen a textovych znaku v identifikatoru
        #print("\n",counter,"\n")
        #PRIDAT KONTROLU, ZE LEVA STRANA PRAVIDLA JE EXISTUJICI NETERMINAL
        leftSide = identificator
        if(nextToken(file) != s_utils.TokenKind.ARROW):
            #PRIDAT OSETRENI SITUACE, ZE V PRAVIDLE NENI SIPKA ALE NECO JINEHO
            return s_utils.TokenKind.ERROR
        rightSide = []
        while (nextToken(file) == s_utils.TokenKind.IDENT):
            rightSide.append(identificator)
            next = nextToken(file)  # nacteni dalsiho tokenu
            if(next == s_utils.TokenKind.PIPE):  # nactena pajpa, pokracujeme v nacitani
                continue
            if(endOfLine):
                rule = s_utils.Rule(counter, leftSide, rightSide)
                g.addRuleToGrammar(rule)
                index -= len(identificator) #vraceni se zpatky ve cteni o delku identifikatoru
                #file.seek(file.tell() - len(identificator), 0)
                counter += 1
                break
    index -= len(identificator) #vraceni se zpatky ve cteni o delku identifikatoru
    #file.seek(file.tell() - len(identificator), 0)  # vraceni ukazatele cteni v souboru o 1 zpet

#funkce nacitajici dalsi token z predaneho souboru
def nextToken(file):
    global index
    #c = h_utils.readCharacter(file)
    try:
        c = file[index]
    except:
        return s_utils.TokenKind.EOF  # konec souboru
    #if c == '': #kontrola konce souboru
    #    return s_utils.TokenKind.EOF #konec souboru

    while (c.isspace()): #remove space characters
        index += 1
        try:
            c = file[index]
            continue
        except:
            return s_utils.TokenKind.EOF
    if("=" in c): #= character
        index += 1
        return s_utils.TokenKind.EQUALS
    elif("{" in c):#{ character
        index += 1
        return s_utils.TokenKind.OpenCurlyBrace
    elif("}" in c): #} character
        index += 1
        return s_utils.TokenKind.CloseCurlyBrace
    elif("|" in c): #pipe character
        index += 1
        return s_utils.TokenKind.PIPE
    elif("," in c): #comma character
        index += 1
        return s_utils.TokenKind.COMMA
    elif("-" in c): #arrow character
        temp = h_utils.readNextChar(file,index) #kontrola nasledujiciho znaku >
        if(">" in temp):
            index += 2 #pousunuti se o dva znaky ->
            #h_utils.readCharacter(file) #precteni znaku >
            #print("NASEL JSEM SIPKU\n")
            return s_utils.TokenKind.ARROW #-> character
        else:
            return s_utils.TokenKind.ERROR
    elif(c.isalnum() or c in s_utils.specialChars): # identifikator a-z
        temp = h_utils.readNextChar(file, index)
        if temp != s_utils.TokenKind.EOF:
            while(temp.isalnum() or temp in s_utils.specialChars):
                index += 1
                c = c + file[index]
                temp = h_utils.readNextChar(file,index)
                if temp == s_utils.TokenKind.EOF:
                    break
        if(temp == "\n"):
            global endOfLine
            endOfLine = True
            #print("MAM KONEC RADKU")
        global identificator
        identificator = c
        #print("identifikator v nextToken fci: "+ identificator)
        index += 1
        return s_utils.TokenKind.IDENT
    elif(c in s_utils.specialChars):
        #print("jiny znak... je ", c)
        return s_utils.TokenKind.OtherChar
    else:
        return s_utils.TokenKind.ERROR

def loadAndParseData(inputString):
    global counter
    grammarList= []
    try:
        while True:
            token = nextToken(inputString)
            if(token == s_utils.TokenKind.EOF):
                #print("konec souboru!")
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
                if(identificator.lower() == "cfg"): #nacteni jmena a inicializace gramatiky
                    grammarName = loadGrammarName(inputString)
                    if(grammarName == s_utils.TokenKind.ERROR):
                        return s_utils.TokenKind.ERROR
                    else:
                        g = s_utils.Grammar(grammarName)
                        counter += 1
                elif(identificator == "N" and nextToken(inputString) == s_utils.TokenKind.EQUALS):
                    if g.nonterminals: #osetreni vymazani predchozich polozek
                        g.nonterminals = []
                    loadNonterminals(inputString,g)
                    #print("neterminaly nacteny!")
                elif(identificator == "T" and nextToken(inputString) == s_utils.TokenKind.EQUALS):
                    if g.terminals: #osetreni vymazani predchozich polozek
                        g.terminals = []
                    loadTerminals(inputString,g)
                    #print("terminaly nacteny!")
                elif(identificator == "S" and nextToken(inputString) == s_utils.TokenKind.EQUALS):
                    if g.symbol: #osetreni vymazani predchozich polozek
                        g.symbol = ''
                    loadStartingSymbol(inputString,g)
                    #print("symbol nacteny!")
                elif(identificator == "P" and nextToken(inputString) == s_utils.TokenKind.EQUALS):
                    if g.rules: #osetreni vymazani predchozich polozek
                        g.rules = []
                    loadRules(inputString,g)
                    grammarList = copy.deepcopy(g)
                    if(grammarList.nonterminals != [] and grammarList.terminals != [] and grammarList.symbol != '' and grammarList.rules != []):
                        #print("Gramatika byla kompletne nactena")
                        return grammarList
            elif(token == s_utils.TokenKind.ERROR):
                print("INCORRECT SYNTAX - only a single CFG can be loaded!")
                return
    except FileNotFoundError:
        p_utils.printError("Input file was not found")

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
        if not updated: #pokud v poslednim cyklu nebyly pridany zadne nove symboly do mnozin, funkce konci vypocet a navraci vypoctene mnoziny
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
            if(flag == True or expression == '' or expression == 'eps'):
                T_validNonterminals.add(nt)
    #print('mnozina T = ',T_validNonterminals)
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
    #print('mnozina D = ',D_reachableNonterminals)
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
        return rules, isReduced, rules
    #gramatika byla zredukovana
    else:
        isReduced = False
        grammarList.setNewRulesFromTupleList(finalListOfRules)
        return set(finalListOfRules), isReduced, rules

#funkce pro odstraneni epsilon pravidel z gramatiky
def epsRulesRemoval(grammar):
    setE = set() #mnozina E obsahuje vsechny neterminaly, ktere lze v gramatice prepsat na epsilon
    finalRules = []
    nonterminals = set()
    for nonterminal in grammar.nonterminals:
        nonterminals.add(nonterminal.value)
    terminals = set()
    for terminal in grammar.terminals:
        terminals.add(terminal.value)
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
    #print('mnozina E = ',setE)
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
                occurrences += (occurrence,)
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
        #listOfCombinations = list(value)
        #print(type(listOfCombinations))
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
                    #print('nalezeno')
                    counter += 1
            if ((len(combination) - counter) < minLength):
                finalCombs.remove(combination)
        for combi in finalCombs:
            temp = ''.join(combi)
            setOfRuleCombinations.add(temp)
        for i in setOfRuleCombinations:
            finalRule = (key, i)
            finalRules += (finalRule,)
    return finalRules

def simpleRulesRemoval(rules, grammar):
    finalRules = []
    for i in grammar.nonterminals:
        setN = set()
        setN.add(i.value) #vlozeni sebe sama do mnoziny
        updated = True
        previousNonterminal = i.value
        while updated:
            changed = len(setN)
            for nt, expression in rules:
                if nt == previousNonterminal and len(expression) == 1: #hledam pouze neterminalni symboly a pravidlo musi byt jednoduche
                    for j in grammar.nonterminals: #kontrola, ze mam neterminal a ne terminal
                        if j.value == expression:
                            setN.update(expression)
                            #print('mam te: ', nt, '<>', expression)
                            previousNonterminal = expression
            if changed == len(setN):
                updated = False
        for nt, expression in rules:
            if nt in setN and expression not in setN:
                finalRule = (i.value, expression)
                finalRules += (finalRule,)
    return finalRules

def convertToCNF(grammar):
    rules = h_utils.getRulesSet(grammar.rules)
    index = 0
    augmentedRules = []
    for nt, expression in rules: #v prvnim kroku prevedu pravidla o delce vic nez 2 na ekvivalentni pravidla delky max 2 pridanim novych neterminalnich symbolu

        length = len(expression)
        if length <= 2: #pravidla o delce 2 a mensi neni treba upravovat
            newRule = (nt, expression)
            augmentedRules.append(newRule)
        while length > 2:
            newNonterminal = expression[0] + str(index)
            newRule = (nt, newNonterminal)
            newRule2 = (newNonterminal, expression[1])
            length -= 2
            augmentedRules.append(newRule)
            augmentedRules.append(newRule2)
#hlavni funkce, skrze kterou jsou volany prislusne funkce na zaklade zadanych argumentu
def main():
    global index, grammarList
    sg.theme('LightGrey2')  #barevne schema aplikace
    tab1_layout = [[sg.Checkbox('FIRST', key='first'), sg.Checkbox('FOLLOW', key='follow'), sg.Checkbox('Reduction', key='reduction'),sg.Checkbox('Epsilon removal', key='eps'), sg.Checkbox('Simple rules removal', key='srr'), sg.Checkbox('Chomsky NF', key='cnf'), sg.Checkbox('Construct PDA', key='constructPDA'), sg.Checkbox('Greibach NF', key='greibachNF'), sg.Button('Enter', key='Enter')],
                   [sg.Text(' Input'),sg.Text(' Output', pad=((342,3),3))],
                   [sg.Multiline('Load grammar via the Load CFG button', key='input'), sg.Multiline('', key='output')]]
    tab2_layout = [[sg.Button('Build LR items', key='createParsingTable'), sg.Text('Parse string:', pad=((260,3),3)), sg.Input(key='text_to_parse'), sg.Button('Validate input', key='validateInput')],
                   [sg.Text(' LR Items and Table:'),  sg.Text(' Output:', pad=((312,3),3))],
                   [sg.Multiline('Load grammar via the Load CFG button', key='parsing_table'), sg.Multiline('' , key='input_validation')]]
    tab3_layout = [[sg.Button('Build LL(1) table', key='createLLParsingTable'), sg.Text('Parse string:', pad=((260,3),3)), sg.Input(key='ll_text_to_parse'), sg.Button('Validate input', key='validateLLInput')],
                   [sg.Checkbox('Detect conflicts', key='ll_conflicts')],
                   [sg.Text(' LL Table:'),  sg.Text(' Output:', pad=((312,3),3))],
                   [sg.Multiline('Load grammar via the Load CFG button', key='ll_parsing_table'), sg.Multiline('' ,key='ll_input_validation')]]
    layout = [[sg.Input( key='-IN-', default_text='grammar.txt', enable_events=True, disabled=True),sg.FileBrowse('Load CFG',file_types=(('Text files', '*.txt'),), key="fileBrowse",
                                                                                                                  tooltip='Allows to choose text file containing context-free grammar', change_submits=True), sg.Button('Insert sample', key='insertSample') , sg.Button('Clear windows', key='clearWindows')],
              [sg.TabGroup([[sg.Tab('CFG operations', tab1_layout), sg.Tab('LR(0) Parser', tab2_layout), sg.Tab('LL(1) Parser', tab3_layout)]])],
              [sg.Checkbox('Print results to file', key='printToFile', pad=((0,3),3)), sg.Button('Close', pad=((160,3),3))]]

    window = sg.Window('Program pro analýzu bezkontextových gramatik - Daniel Merta, MER0103, ak. rok 2021/2022', layout, default_element_size=(50,15), resizable=True, auto_size_buttons=True)
    while True: #nekonecna smycka behu programu
        event, values = window.read() #naslouchani udalostem
        #print(event, values)
        if event == '-IN-': #byl vybran soubor s CFG, aktualizuj okna
            inputString = h_utils.readWholeFile(values['-IN-'])
            index = 0
            grammarList = [] #mozno vymazat!
            grammarList = loadAndParseData(inputString)
            try:
                if (grammarList.nonterminals != [] and grammarList.terminals != [] and grammarList.symbol != '' and grammarList.rules != []):
                    loadedCFG = p_utils.printCFG(grammarList)
                    window['input'].update(loadedCFG)
            except:
                window['input'].update('Parsing grammar error. See the readme.txt file for the correct syntax of input file.')

        elif event == sg.WIN_CLOSED or event == 'Close': #ukonceni programu
            return
            #exit()
        elif event == 'insertSample':
            window['input'].update(s_utils.sampleCFG)
        elif event == 'clearWindows': #stisknuti tlacitka vymazani obsahu oken
            window['input'].update('')
            window['output'].update('')
            window['parsing_table'].update('')
            window['input_validation'].update('')
            window['ll_parsing_table'].update('')
            window['ll_input_validation'].update('')
        elif event == 'Enter': #stisknuti tlacitka pro vypocet danych funkci
            window['output'].update('')
            grammarList = []
            index = 0
            actualGrammar = values['input']
            if values['first'] or values['follow'] or values['reduction'] or values ['eps'] or values['srr'] or values['cnf'] or values['constructPDA']:
                try:
                    grammarList = loadAndParseData(actualGrammar)
                    if (grammarList.nonterminals != [] and grammarList.terminals != [] and grammarList.symbol != '' and grammarList.rules != []):
                        loadedCFG = p_utils.printCFG(grammarList)
                        window['input'].update(loadedCFG)
                except:
                    window['input'].update('Parsing grammar error. See the readme.txt file for the correct syntax of input file.')
            data = ''
            if values['first'] or values['follow']: #byl vybran FIRST nebo FOLLOW prepinac
                first, follow, epsilon = firstAndFollow(grammarList, values['first'], values['follow'])  # algoritmus pro pocitani FIRST a FOLLOW
                if values['first']:
                    data = p_utils.printFirstToMultiline(first, epsilon, grammarList)
                if values['follow']:
                    data += p_utils.printFollowToMultiline(follow, grammarList)
            if values['reduction']: #byl vybran prepinac redukce
                reducedGrammar, isReduced, originRules = reduction(grammarList)  # algoritmus pro redukci gramatiky
                data += p_utils.printReductionInfoToMultiline(isReduced)
                data += p_utils.printReductionGrammarRulesToMultiline(reducedGrammar, grammarList, originRules)
            if values['eps']: #byl vybran prepinac odstraneni epsilon pravidel
                data += '### Epsilon rules removal ###\n'
                epsRemovedGrammar = epsRulesRemoval(grammarList)  # algoritmus pro odstraneni epsilon pravidel
                data += p_utils.printRemovalGrammarRulesToMultiline(epsRemovedGrammar, grammarList)  # vypsani pravidel gramatiky
            if values['srr']: #byl vybran prepinac odstraneni jednoduchych pravidel
                data += '### Simple rules removal ###\n'
                removedEpsRules = epsRulesRemoval(grammarList) #na vstupu musi byt CFG bez epsilon pravidel, proto je odstranime
                removedSimpleRules = simpleRulesRemoval(removedEpsRules, grammarList) #funkce odstranujici jednoduche pravidla
                data += p_utils.printRemovalGrammarRulesToMultiline(removedSimpleRules, grammarList)
            if values['cnf']: #byl vybran prepinac prevodu do Chomskeho normalni formy
                data += '### Chomsky Normal Form ###\n'
                rulesInCNF = convertToCNF(grammarList)
            if values['constructPDA']: #byl vybran prepinac konstrukce zasobnikoveho automatu
                data += '### Pushdown automaton: ###\n'
                data += p_utils.printPushdownAutomaton(grammarList)
            window['output'].update(data)  # vypsani vysledku do vystupniho okna
            if values['printToFile']: #vypis vysledku do souboru
                f = open('outputFile.txt', 'w', encoding="utf-8")
                f.write(data)
                f.close()

        elif event == 'createParsingTable':
            reduction(grammarList)  #algoritmus pro redukci gramatiky
            parser = s_utils.LRParser(grammarList)
            closures = parser.buildClosures()
            parsingTable = parser.buildParsingTable()
            data = ''
            data += '### LR items ###\n'
            data += p_utils.printClosuresToMultiline(closures)
            data += '### LR(0) table ###\n'
            data += p_utils.printParsingTableToMultiline(grammarList, parsingTable)
            window['parsing_table'].update(data)
            if values['printToFile']: #vypis vysledku do souboru
                f = open('outputFile.txt', 'w')
                f.write(data)
                f.close()

        elif event == 'validateInput':
            reduction(grammarList)  # algoritmus pro redukci gramatiky
            parser = s_utils.LRParser(grammarList)
            closures = parser.buildClosures()
            parsingTable = parser.buildParsingTable()
            dataLR = ''
            dataLR += '### LR items ###\n'
            dataLR += p_utils.printClosuresToMultiline(closures)
            dataLR += '### LR(0) table ###\n'
            dataLR += p_utils.printParsingTableToMultiline(grammarList, parsingTable)
            window['parsing_table'].update(dataLR)
            inputText = values['text_to_parse']
            if len(inputText) == 0:
                data = '### No input provided ###\n'
                window['input_validation'].update(data)
            else:
                if not inputText[-1] == '$': #input must have ending character
                    inputText += '$'
                output = parser.parseLR0Input(inputText)
                data = '### LR(0) validation ###\n'
                data += "'%s' is %s" % (values['text_to_parse'], output)
                window['input_validation'].update(data)
                if values['printToFile']: #vypis vysledku do souboru
                    f = open('outputFile.txt', 'w')
                    f.write(data)
                    f.close()

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
            conflicts = parser.detectConflicts()
            data = ''
            if values['ll_conflicts']:
                data += '### LL conflicts: ###\n'
                for c in conflicts:
                    if len(conflicts[c]) == 0:
                        data += "%s - without conflict \n" % c
                    else:
                        data += "%s - %s\n" % (c, ''.join(conflicts[c]))
                data += '\n'

            data += '### LL(1) table ###\n'
            data += p_utils.printLLParsingTableToMultiline(grammarList, parsingTable)
            window['ll_parsing_table'].update(data)
            if values['printToFile']: #vypis vysledku do souboru
                f = open('outputFile.txt', 'w')
                f.write(data)
                f.close()

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
            #data += '\n\n'
            data += '### LL(1) table ###\n'
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
                if values['printToFile']: #vypis vysledku do souboru
                    f = open('outputFile.txt', 'w')
                    f.write(data)
                    f.close()
if __name__ == '__main__':
    main()
    sys.exit(0) #uspesny konec programu