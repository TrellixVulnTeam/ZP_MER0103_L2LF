import copy, sys
import PySimpleGUIQt as sg
import utils.helper_utils as h_utils
import utils.print_utils as p_utils
import utils.struct_utils as s_utils
import utils.function_utils as f_utils

identificator = ''
grammarList = []
index = 0 #pozice prave nacitaneho znaku
counter = 0 #citac nactenych gramatik
cfg_name = False
cfg_n = False
cfg_t = False
cfg_s = False
cfg_p = False
cfg_p_n = False
cfg_p_t = False
cfg_syntax = True
def loadGrammarName(file):
    if(nextToken(file) == s_utils.TokenKind.EQUALS and nextToken(file) == s_utils.TokenKind.IDENT): #kontrola, ze je po "cfg" znak rovna se a identifikator
        return identificator
    else: #nespravna syntaxe
        return s_utils.TokenKind.ERROR

def loadNonterminals(file,g): #funkce pro nacitani neterminalu
    if(nextToken(file) == s_utils.TokenKind.OpenCurlyBrace): #kontrola, ze je po "N" rovna se a zacinajici chlupate zavorka
        counter = 0
        while(nextToken(file) == s_utils.TokenKind.IDENT): #cyklus pro nacitani neterminalu
            if(identificator.isupper() and identificator.isalnum()): #kontrola velkych pismen a textovych znaku v identifikatoru
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
        listOfLoadedNonterminals = []
        for item in g.nonterminals:
            listOfLoadedNonterminals.append(item.value)
        if startingSymbol.value not in listOfLoadedNonterminals:
            return 'unknown nonterminal'
        g.addSymbol(startingSymbol) #pridani pocatecniho symbolu do gramatiky
        return
    else:
        return s_utils.TokenKind.ERROR

def loadRules(file,g):
    global endOfLine, index, cfg_p
    counter = 0
    while(nextToken(file) == s_utils.TokenKind.IDENT and identificator.isupper() and identificator.isalnum()): #kontrola identifikatoru, velkych pismen a textovych znaku v identifikatoru
        leftSide = identificator
        listOfLoadedNonterminals = []
        for item in g.nonterminals:
            listOfLoadedNonterminals.append(item.value)
        if leftSide not in listOfLoadedNonterminals:
            return 'unknown nonterminal'
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
    cfg_p = True

#funkce nacitajici dalsi token z predaneho souboru
def nextToken(file):
    global index
    global identificator
    global endOfLine

    try:
        c = file[index]
    except:
        return s_utils.TokenKind.EOF  # konec souboru
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
    elif(c.isalnum() or c in s_utils.specialChars): # identifikator a-z nebo specialni znak
        temp = h_utils.readNextChar(file, index)
        identificator = c
        if temp != s_utils.TokenKind.EOF:
            if (c in '-' and temp in '>'):
                index += 2
                return s_utils.TokenKind.ARROW #-> character
            while(temp.isalnum() or temp in s_utils.specialChars):
                if (temp in '-'):
                    nextIndex = index+1
                    temp2 = h_utils.readNextChar(file, nextIndex) # zjisti jestli neni >
                    if (temp == temp2): # kdyz se index nejak posune, je treba se na tu sipku podivat znovu
                        temp2 = h_utils.readNextChar(file, nextIndex+1)
                    if(">" in temp2):
                        identificator = c
                        index += 1
                        return s_utils.TokenKind.IDENT #-> character
                index += 1
                c = c + file[index]
                temp = h_utils.readNextChar(file,index)
                if temp == s_utils.TokenKind.EOF:
                    break
        if(temp == "\n"):
            endOfLine = True
        identificator = c
        index += 1
        return s_utils.TokenKind.IDENT
    elif(c in s_utils.specialChars):
        return s_utils.TokenKind.OtherChar
    else:
        return s_utils.TokenKind.ERROR

def loadAndParseData(inputString):
    global counter, cfg_name, cfg_n, cfg_t, cfg_s, cfg_p, cfg_p_n, cfg_p_t, cfg_syntax
    grammarList= []
    try:
        while True:
            token = nextToken(inputString)
            if(token == s_utils.TokenKind.EOF):
                if (grammarList.nonterminals != [] and grammarList.terminals != [] and grammarList.symbol != '' and grammarList.rules != []):
                    cfg_syntax = True
                    return grammarList
                else:
                    cfg_syntax = False
                    return s_utils.TokenKind.ERROR
            elif(token == s_utils.TokenKind.IDENT):
                if(identificator.lower() == "cfg"): #nacteni jmena a inicializace gramatiky
                    grammarName = loadGrammarName(inputString)
                    if(grammarName == s_utils.TokenKind.ERROR):
                        cfg_name = False
                        return s_utils.TokenKind.ERROR
                    else:
                        g = s_utils.Grammar(grammarName)
                        cfg_name = True
                        counter += 1
                elif(identificator == "N" and nextToken(inputString) == s_utils.TokenKind.EQUALS):
                    if g.nonterminals: #osetreni vymazani predchozich polozek
                        g.nonterminals = []
                    grammarNonterminals = loadNonterminals(inputString,g)
                    if grammarNonterminals == s_utils.TokenKind.ERROR:
                        cfg_n = False
                        return s_utils.TokenKind.ERROR
                    else:
                        cfg_n = True
                elif(identificator == "T" and nextToken(inputString) == s_utils.TokenKind.EQUALS):
                    if g.terminals: #osetreni vymazani predchozich polozek
                        g.terminals = []
                    grammarTerminals = loadTerminals(inputString,g)
                    if grammarTerminals == s_utils.TokenKind.ERROR:
                        cfg_t = False
                        return s_utils.TokenKind.ERROR
                    else:
                        cfg_t = True
                elif(identificator == "S" and nextToken(inputString) == s_utils.TokenKind.EQUALS):
                    if g.symbol: #osetreni vymazani predchozich polozek
                        g.symbol = ''
                    grammarStartingSymbol = loadStartingSymbol(inputString,g)
                    if grammarStartingSymbol == 'unknown nonterminal':
                        cfg_p_n = False
                        return s_utils.TokenKind.ERROR
                    elif grammarStartingSymbol == s_utils.TokenKind.ERROR:
                        cfg_s = False
                        return s_utils.TokenKind.ERROR
                    else:
                        cfg_s = True
                elif(identificator == "P" and nextToken(inputString) == s_utils.TokenKind.EQUALS):
                    if g.rules: #osetreni vymazani predchozich polozek
                        g.rules = []
                    grammarRules = loadRules(inputString,g)

                    grammarList = copy.deepcopy(g)
                    if(grammarList.nonterminals != [] and grammarList.terminals != [] and grammarList.symbol != '' and grammarList.rules != []):
                        cfg_syntax = True
                        return grammarList
            elif(token == s_utils.TokenKind.ERROR):
                cfg_syntax = False
                return s_utils.TokenKind.ERROR
    except:
        cfg_syntax = False
        return s_utils.TokenKind.ERROR

def run():
    global index, grammarList, window, shouldClose

    event, values = window.read() #naslouchani udalostem
    if event == '-IN-': #byl vybran soubor s CFG, aktualizuj okna
        inputString = h_utils.readWholeFile(values['-IN-'])
        index = 0
        grammarList = []
        grammarList = loadAndParseData(inputString)
        try:
            if (grammarList.nonterminals != [] and grammarList.terminals != [] and grammarList.symbol != '' and grammarList.rules != []):
                loadedCFG = p_utils.printCFG(grammarList)
                window['input'].update(loadedCFG)
                window['ll_parsing_table'].update(loadedCFG)
                window['parsing_table'].update(loadedCFG)
        except:
            grammarList = []

    elif event == sg.WIN_CLOSED or event == 'Close program': #ukonceni programu
        shouldClose = True
        return
    elif event == 'insertSampleCFG':
        window['input'].update(s_utils.sampleCFG)
        window['parsing_table'].update(s_utils.sampleCFG)
        window['ll_parsing_table'].update(s_utils.sampleCFG)
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
        if values['first'] or values['follow'] or values['reduction'] or values ['eps'] or values['srr'] or values['cnf'] or values['gnf'] or values['constructPDA']:
            try:
                grammarList = loadAndParseData(actualGrammar)
                if (grammarList.nonterminals != [] and grammarList.terminals != [] and grammarList.symbol != '' and grammarList.rules != []):
                    loadedCFG = p_utils.printCFG(grammarList)
                    window['input'].update(loadedCFG)
            except:
                grammarList = []
        data = ''
        if values['first'] or values['follow']: #byl vybran FIRST nebo FOLLOW prepinac
            first, follow, epsilon = f_utils.firstAndFollow(grammarList, values['first'], values['follow'])  # algoritmus pro pocitani FIRST a FOLLOW
            if values['first']:
                data = p_utils.printFirstToMultiline(first, epsilon, grammarList)
            if values['follow']:
                data += p_utils.printFollowToMultiline(follow, grammarList)
        if values['reduction']: #byl vybran prepinac redukce
            reducedGrammar, isReduced, originRules, setT, setD = f_utils.reduction(grammarList)  # algoritmus pro redukci gramatiky
            data += p_utils.printReductionInfoToMultiline(isReduced)
            data += p_utils.printReductionGrammarRulesToMultiline(reducedGrammar, grammarList, originRules)
            if values['interimResults']:
                data += 'set T = ' + str(setT) + '\nset D = ' + str(setD) + '\n'
        if values['eps']: #byl vybran prepinac odstraneni epsilon pravidel
            data += '### Epsilon rules removal ###\n'
            epsRemovedGrammar, setE = f_utils.epsRulesRemoval(grammarList, False)  # algoritmus pro odstraneni epsilon pravidel
            data += p_utils.printRemovalGrammarRulesToMultiline(epsRemovedGrammar, grammarList)  # vypsani pravidel gramatiky
            if values['interimResults']:
                data += 'set E = ' + str(setE) + '\n'
        if values['srr']: #byl vybran prepinac odstraneni jednoduchych pravidel
            data += '### Simple rules removal ###\n'
            removedEpsRules, setE = f_utils.epsRulesRemoval(grammarList, False) #na vstupu musi byt CFG bez epsilon pravidel, proto je odstranime
            removedSimpleRules, setN = f_utils.simpleRulesRemoval(removedEpsRules, grammarList) #funkce odstranujici jednoduche pravidla
            data += p_utils.printRemovalGrammarRulesToMultiline(removedSimpleRules, grammarList)
            if values['interimResults']:
                data += setN + '\n'
        if values['cnf']: #byl vybran prepinac prevodu do Chomskeho normalni formy
            data += '### Chomsky Normal Form ###\n'
            shortenedRules = f_utils.convertToCNF(grammarList)
            removedEpsShortenedRules, setE = f_utils.epsRulesRemoval(grammarList, shortenedRules)
            removedEpsSimpleShortenedRules, setN = f_utils.simpleRulesRemoval(removedEpsShortenedRules, grammarList)
            rulesInCNF = f_utils.substituteTerminals(removedEpsSimpleShortenedRules, grammarList)
            data += p_utils.printRemovalGrammarRulesToMultiline(rulesInCNF,grammarList)
            if values['interimResults']:
                data += 'set E = ' + str(setE) + '\n'
                data += setN + '\n'
        if values['gnf']:
            data += '### Greibach Normal Form ###\n'
            shortenedRules = f_utils.convertToCNF(grammarList)
            removedEpsShortenedRules, setE = f_utils.epsRulesRemoval(grammarList, shortenedRules)
            removedEpsSimpleShortenedRules, setN = f_utils.simpleRulesRemoval(removedEpsShortenedRules, grammarList)
            rulesInCNF = f_utils.substituteTerminals(removedEpsSimpleShortenedRules, grammarList)
            rulesInGNF = f_utils.convertToGNF(rulesInCNF, grammarList)
            data += p_utils.printRemovalGrammarRulesToMultiline(rulesInGNF,grammarList)
            if values['interimResults']:
                data += 'set E = ' + str(setE) + '\n'
                data += setN + '\n'
        if values['constructPDA']: #byl vybran prepinac konstrukce zasobnikoveho automatu
            data += '### Pushdown automaton: ###\n'
            data += p_utils.printPushdownAutomaton(grammarList)
        window['output'].update(data)  # vypsani vysledku do vystupniho okna
    elif event == 'createParsingTable': #parsing_table, input_validation
        window['input_validation'].update('')
        grammarList = []
        index = 0
        actualGrammar = values['parsing_table']
        try:
            grammarList = loadAndParseData(actualGrammar)
            if (grammarList.nonterminals != [] and grammarList.terminals != [] and grammarList.symbol != '' and grammarList.rules != []):
                loadedCFG = p_utils.printCFG(grammarList)
                window['parsing_table'].update(loadedCFG)
        except:
            window['input_validation'].update('Parsing grammar error. See the readme.txt file for the correct syntax of input file.')
            grammarList = []
        data = ''
        f_utils.reduction(grammarList)  # algoritmus pro redukci gramatiky
        parser = s_utils.LRParser(grammarList)
        closures = parser.buildClosures()
        parsingTable = parser.buildParsingTable()
        conflicts = parser.conflicts
        if bool(conflicts):
            #print("CONFLICTS", conflicts)
            data += "Found conflicts, grammar is not valid LR\n"
            window['input_validation'].update(data)
        else:
            data += '### LR items ###\n'
            data += p_utils.printClosuresToMultiline(closures)
            data += '### LR(0) table ###\n'
            data += p_utils.printParsingTableToMultiline(grammarList, parsingTable)
            window['input_validation'].update(data)

    elif event == 'validateInput':
        window['input_validation'].update('')
        grammarList = []
        index = 0
        actualGrammar = values['parsing_table']
        try:
            grammarList = loadAndParseData(actualGrammar)
            if (grammarList.nonterminals != [] and grammarList.terminals != [] and grammarList.symbol != '' and grammarList.rules != []):
                loadedCFG = p_utils.printCFG(grammarList)
                window['parsing_table'].update(loadedCFG)
        except:
            window['input_validation'].update('Parsing grammar error. See the readme.txt file for the correct syntax of input file.')
            grammarList = []
        data = ''
        f_utils.reduction(grammarList)  # algoritmus pro redukci gramatiky
        parser = s_utils.LRParser(grammarList)
        closures = parser.buildClosures()
        parsingTable = parser.buildParsingTable()
        conflicts = parser.conflicts
        if bool(conflicts):
            #print("CONFLICTS", conflicts)
            data += "Found conflicts, grammar is not valid LR\n"
            window['input_validation'].update(data)
        else:
            dataLR = ''
            dataLR += '### LR items ###\n'
            dataLR += p_utils.printClosuresToMultiline(closures)
            dataLR += '### LR(0) table ###\n'
            dataLR += p_utils.printParsingTableToMultiline(grammarList, parsingTable)
            inputText = values['text_to_parse']
            if len(inputText) == 0:
                data = '### No input provided ###\n\n'
                data += dataLR
                window['input_validation'].update(data)
            else:
                if not inputText[-1] == ';': #input must have ending character
                    inputText += ';'
                output = parser.parseLR0Input(inputText)
                data = '### LR(0) validation ###\n'
                data += "'%s' is %s\n\n" % (values['text_to_parse'], output)
                data += dataLR
                window['input_validation'].update(data)

    elif event == 'createLLParsingTable': #ll_parsing_table, ll_input_validation
        window['ll_input_validation'].update('')
        grammarList = []
        index = 0
        actualGrammar = values['ll_parsing_table']
        try:
            grammarList = loadAndParseData(actualGrammar)
            if (grammarList.nonterminals != [] and grammarList.terminals != [] and grammarList.symbol != '' and grammarList.rules != []):
                loadedCFG = p_utils.printCFG(grammarList)
                window['ll_parsing_table'].update(loadedCFG)
        except:
            window['ll_input_validation'].update('Parsing grammar error. See the readme.txt file for the correct syntax of input file.')
            grammarList = []
        data = ''
        first, follow, epsilon = f_utils.firstAndFollow(grammarList, True, True)
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
        conflictData = '### Grammar has conflicts, is not valid LL(1) grammar\n\n'
        hasConflict = False

        conflictData += '### LL conflicts: ###\n'
        #print('conflict', len(conflicts), conflicts)
        for c in conflicts:
            if len(conflicts[c]) == 0:
                conflictData += "%s - without conflict \n" % c
            else:
                hasConflict = True
                conflictData += "%s - %s\n" % (c, ', '.join(conflicts[c]))
        conflictData += '\n'

        if hasConflict:
            window['ll_input_validation'].update(conflictData)
        else:
            data += '### LL(1) table ###\n'
            data += p_utils.printLLParsingTableToMultiline(grammarList, parsingTable)
            window['ll_input_validation'].update(data)
    elif event == 'validateLLInput':
        window['ll_input_validation'].update('')
        grammarList = []
        index = 0
        actualGrammar = values['ll_parsing_table']
        try:
            grammarList = loadAndParseData(actualGrammar)
            if (grammarList.nonterminals != [] and grammarList.terminals != [] and grammarList.symbol != '' and grammarList.rules != []):
                loadedCFG = p_utils.printCFG(grammarList)
                window['ll_parsing_table'].update(loadedCFG)
        except:
            window['ll_input_validation'].update('Parsing grammar error. See the readme.txt file for the correct syntax of input file.')
            grammarList = []
        data = ''
        first, follow, epsilon = f_utils.firstAndFollow(grammarList, True, True)
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
        conflictData = '### Grammar has conflicts, is not valid LL(1) grammar\n\n'
        hasConflict = False
        conflictData += '### LL conflicts: ###\n'
        for c in conflicts:
            if len(conflicts[c]) == 0:
                conflictData += "%s - without conflict \n" % c
            else:
                hasConflict = True
                conflictData += "%s - %s\n" % (c, ', '.join(conflicts[c]))
        conflictData += '\n'

        if hasConflict:
            window['ll_input_validation'].update(conflictData)
        else:
            dataLL = ''
            dataLL += '### LL(1) table ###\n'
            dataLL += p_utils.printLLParsingTableToMultiline(grammarList, parsingTable)
            inputText = values['ll_text_to_parse']
            if len(inputText) == 0:
                data = '### No input provided ###\n\n'
                data += dataLL
                window['ll_input_validation'].update(data)
            else:
                if not inputText[-1] == ';': #input must have ending character
                    inputText += ';'
                output = parser.parseInput(inputText)
                data = '### LL(1) validation ###\n'
                data += "'%s' is %s\n\n" % (values['ll_text_to_parse'], output)
                data += dataLL
                window['ll_input_validation'].update(data)
    elif event == 'saveData1stTab':
        if (values['saveData1stTab'] != ''):
            dataToSave = ''
            if values['includeInput1stTab'] and values['includeOutput1stTab']:
                dataToSave += '=== INPUT ===\n' + values['input'] + '\n\n'
                dataToSave += '=== OUTPUT ===\n' + values['output']
            elif values['includeInput1stTab'] and not values['includeOutput1stTab']:
                dataToSave += '=== INPUT ===\n' + values['input']
            elif values['includeOutput1stTab'] and not values['includeInput1stTab']:
                dataToSave += '=== OUTPUT ===\n' + values['output']
            try:
                f = open(values['saveData1stTab'], 'w', encoding="utf-8")
                f.write(dataToSave)
                f.close()
            except:
                values['saveData1stTab'] = ''
    elif event == 'saveData2ndTab':
        if (values['saveData2ndTab'] != ''):
            dataToSave = ''
            if values['includeInput2ndTab'] and values['includeOutput2ndTab']:
                dataToSave += '=== INPUT ===\n' + values['parsing_table'] + '\n\n'
                dataToSave += '=== OUTPUT ===\n' + values['input_validation']
            elif values['includeInput2ndTab'] and not values['includeOutput2ndTab']:
                dataToSave += '=== INPUT ===\n' + values['parsing_table']
            elif values['includeOutput2ndTab'] and not values['includeInput2ndTab']:
                dataToSave += '=== OUTPUT ===\n' + values['input_validation']
            try:
                f = open(values['saveData2ndTab'], 'w', encoding="utf-8")
                f.write(dataToSave)
                f.close()
            except:
                values['saveData2ndTab'] = ''
    elif event == 'saveData3rdTab':
        if (values['saveData3rdTab'] != ''):
            dataToSave = ''
            if values['includeInput3rdTab'] and values['includeOutput3rdTab']:
                dataToSave += '=== INPUT ===\n' + values['ll_parsing_table'] + '\n\n'
                dataToSave += '=== OUTPUT ===\n' + values['ll_input_validation']
            elif values['includeInput3rdTab'] and not values['includeOutput3rdTab']:
                dataToSave += '=== INPUT ===\n' + values['ll_parsing_table']
            elif values['includeOutput3rdTab'] and not values['includeInput3rdTab']:
                dataToSave += '=== OUTPUT ===\n' + values['ll_input_validation']
            try:
                f = open(values['saveData3rdTab'], 'w', encoding="utf-8")
                f.write(dataToSave)
                f.close()
            except:
                values['saveData3rdTab'] = ''

#hlavni funkce v niz je inicializovano GUI a spusten beh programu
def main():
    global index, grammarList, window, shouldClose, cfg_name, cfg_n, cfg_t, cfg_s, cfg_p, cfg_p_n, cfg_p_t, cfg_syntax
    sg.theme('LightGrey2')  #barevne schema aplikace
    tab1_layout = [[sg.Checkbox('FIRST', key='first'), sg.Checkbox('FOLLOW', key='follow'), sg.Checkbox('Reduction', key='reduction'),sg.Checkbox('Epsilon removal', key='eps'), sg.Checkbox('Simple rules removal', key='srr'), sg.Checkbox('Chomsky NF', key='cnf'), sg.Checkbox('Greibach NF', key='gnf'), sg.Checkbox('Construct PDA', key='constructPDA')],
                   [sg.Text(' Input'), sg.Text('                             Output'), sg.Checkbox('Show interim results', key='interimResults',size_px=(150,25)), sg.Button('Enter', key='Enter', size_px=(60,25))],
                   [sg.Multiline('', key='input', font='consolas 10'), sg.Multiline('', key='output', font='consolas 10')],
                   [sg.Text('Include:'),sg.Checkbox('Input', key='includeInput1stTab', pad=((0,3),3)), sg.Checkbox('Output', key='includeOutput1stTab'), sg.FileSaveAs('Save data', key='saveDataToTXT1stTab',target='saveData1stTab',file_types=(("Text Files", "*.txt"),), change_submits=True), sg.Input('', key='saveData1stTab', enable_events=True, disabled=True)]]
    tab2_layout = [[sg.Button('Build LR items', key='createParsingTable'), sg.Text('Parse string:', pad=((260,3),3)), sg.Input(key='text_to_parse'), sg.Button('Validate input', key='validateInput')],
                   [sg.Text(' Input:'),  sg.Text(' Output:', pad=((312,3),3))],
                   [sg.Multiline('', key='parsing_table', font='consolas 10'), sg.Multiline('' , key='input_validation', font='consolas 10')],
                   [sg.Text('Include:'),sg.Checkbox('Input', key='includeInput2ndTab', pad=((0,3),3)), sg.Checkbox('Output', key='includeOutput2ndTab'), sg.FileSaveAs('Save data', key='saveDataToTXT2ndTab',target='saveData2ndTab',file_types=(("Text Files", "*.txt"),), change_submits=True), sg.Input('', key='saveData2ndTab', enable_events=True, disabled=True)]]
    tab3_layout = [[sg.Button('Build LL(1) table', key='createLLParsingTable'), sg.Text('Parse string:', pad=((260,3),3)), sg.Input(key='ll_text_to_parse'), sg.Button('Validate input', key='validateLLInput')],
                   [sg.Text(' Input:'),  sg.Text(' Output:', pad=((312,3),3))],
                   [sg.Multiline('', key='ll_parsing_table', font='consolas 10'), sg.Multiline('' ,key='ll_input_validation', font='consolas 10')],
                   [sg.Text('Include:'), sg.Checkbox('Input', key='includeInput3rdTab', pad=((0, 3), 3)),
                    sg.Checkbox('Output', key='includeOutput3rdTab'),
                    sg.FileSaveAs('Save data', key='saveDataToTXT3rdTab', target='saveData3rdTab',
                                  file_types=(("Text Files", "*.txt"),), change_submits=True),
                    sg.Input('', key='saveData3rdTab', enable_events=True, disabled=True)]]
    layout = [[sg.Input( key='-IN-', default_text='grammar.txt', enable_events=True, disabled=True),sg.FileBrowse('Load CFG',file_types=(('Text files', '*.txt'),), key="fileBrowse",
                                                                                                                  tooltip='Allows to choose text file containing context-free grammar', change_submits=True), sg.Button('Insert sample CFG', key='insertSampleCFG') , sg.Button('Clear windows', key='clearWindows')],
              [sg.TabGroup([[sg.Tab('CFG operations', tab1_layout), sg.Tab('LR(0) Parser', tab2_layout), sg.Tab('LL(1) Parser', tab3_layout)]])],
              [sg.Button('Close program', pad=((400,400),3))]]

    window = sg.Window('Program pro analýzu bezkontextových gramatik - Daniel Merta, MER0103, ak. rok 2021/2022', layout, default_element_size=(150,50), resizable=True, auto_size_buttons=True)

    shouldClose = False
    while not shouldClose: #nekonecna smycka behu programu
        cfg_syntax = True
        try:
            run()
        except:
            if not cfg_syntax:
                window['output'].update('Input CFG has INVALID SYNTAX\n- You may have entered a symbol that is not alphanumeric or that is not '
                                        'in the list of special characters: +, *, /, (, ), $, -, <, >, ^, &, %, #, @, ?, !, [, ], _.\n- Rules have this syntax:\nP = S -> A | a BB\nA -> b\nwhere \'P =\' specifies'
                                        'the beginning of rules, \'S\' is the initial symbol, \'A, BB\' are nonterminals and \'a, b\' are terminals.\n- Click the \'Insert sample CFG\' button to view a valid input syntax.')
                window['input_validation'].update('Input CFG has INVALID SYNTAX\n- You may have entered a symbol that is not alphanumeric or that is not '
                                        'in the list of special characters: +, *, /, (, ), $, -, <, >, ^, &, %, #, @, ?, !, [, ], _.\n- Rules have this syntax:\nP = S -> A | a BB\nA -> b\nwhere \'P =\' specifies'
                                        'the beginning of rules, \'S\' is the initial symbol, \'A, BB\' are nonterminals and \'a, b\' are terminals.\n- Click the \'Insert sample CFG\' button to view a valid input syntax.')
                window['ll_input_validation'].update('Input CFG has INVALID SYNTAX\n- You may have entered a symbol that is not alphanumeric or that is not '
                                        'in the list of special characters: +, *, /, (, ), $, -, <, >, ^, &, %, #, @, ?, !, [, ], _.\n- Rules have this syntax:\nP = S -> A | a BB\nA -> b\nwhere \'P =\' specifies'
                                        'the beginning of rules, \'S\' is the initial symbol, \'A, BB\' are nonterminals and \'a, b\' are terminals.\n- Click the \'Insert sample CFG\' button to view a valid input syntax.')
            elif not cfg_name:
                window['output'].update('Unable to read GRAMMAR NAME\n- Correct syntax is cfg = <grammarName>,'
                                        ' where <grammarName> is string from alphanumeric characters and characters defined'
                                        ' in the set of special characters: +, *, /, (, ), $, -, <, >, ^, &, %, #, @, ?, !, [, ], _')
                window['input_validation'].update('Unable to read GRAMMAR NAME\n- Correct syntax is cfg = <grammarName>,'
                                        ' where <grammarName> is string from alphanumeric characters and characters defined'
                                        ' in the set of special characters: +, *, /, (, ), $, -, <, >, ^, &, %, #, @, ?, !, [, ], _')
                window['ll_input_validation'].update('Unable to read GRAMMAR NAME\n- Correct syntax is cfg = <grammarName>,'
                                        ' where <grammarName> is string from alphanumeric characters and characters defined'
                                        ' in the set of special characters: +, *, /, (, ), $, -, <, >, ^, &, %, #, @, ?, !, [, ], _')
            elif not cfg_n:
                window['output'].update('Unable to read NONTERMINALS\n- Correct syntax is N = {A, B} where A, B are comma separated nonterminal symbols.'
                                        '\n- Nonterminals must be defined by uppercase alphanumeric characters.\n- First character must be a letter from the alphabet (a-z).'
                                        '\n- Multicharacter nonterminals must be separated by a single space.\n- Indentation with tabs is not supported.')
                window['input_validation'].update('Unable to read NONTERMINALS\n- Correct syntax is N = {A, B} where A, B are comma separated nonterminal symbols.'
                                        '\n- Nonterminals must be defined by uppercase alphanumeric characters.\n- First character must be a letter from the alphabet (a-z).'
                                        '\n- Multicharacter nonterminals must be separated by a single space.\n- Indentation with tabs is not supported.')
                window['ll_input_validation'].update('Unable to read NONTERMINALS\n- Correct syntax is N = {A, B} where A, B are comma separated nonterminal symbols.'
                                        '\n- Nonterminals must be defined by uppercase alphanumeric characters.\n- First character must be a letter from the alphabet (a-z).'
                                        '\n- Multicharacter nonterminals must be separated by a single space.\n- Indentation with tabs is not supported.')
            elif not cfg_t:
                window['output'].update('Unable to read TERMINALS\n- Correct syntax is T = {a, b, +} where a, b and + are comma separated terminal symbols.'
                                        '\n- Terminals must be single character lower case letters from the alphabet (a-z) or symbols from the set'
                                         ' of special characters: +, *, /, (, ), $, -, <, >, ^, &, %, #, @, ?, !, [, ], _')
                window['input_validation'].update('Unable to read TERMINALS\n- Correct syntax is T = {a, b, +} where a, b and + are comma separated terminal symbols.'
                                        '\n- Terminals must be single character lower case letters from the alphabet (a-z) or symbols from the set'
                                         ' of special characters: +, *, /, (, ), $, -, <, >, ^, &, %, #, @, ?, !, [, ], _')
                window['ll_input_validation'].update('Unable to read TERMINALS\n- Correct syntax is T = {a, b, +} where a, b and + are comma separated terminal symbols.'
                                        '\n- Terminals must be single character lower case letters from the alphabet (a-z) or symbols from the set'
                                         ' of special characters: +, *, /, (, ), $, -, <, >, ^, &, %, #, @, ?, !, [, ], _')
            elif not cfg_p_n:
                window['output'].update('Unknown NONTERMINAL\n- All nonterminal symbols must be defined in the set of nonterminal symbols.')
                window['input_validation'].update('Unknown NONTERMINAL\n- All nonterminal symbols must be defined in the set of nonterminal symbols.')
                window['ll_input_validation'].update('Unknown NONTERMINAL\n- All nonterminal symbols must be defined in the set of nonterminal symbols.')
            elif not cfg_s:
                window['output'].update('Unable to read INITIAL SYMBOL\n- Correct syntax is S = <S> where <S> is the initial symbol'
                                        ' that belongs to the set of nonterminal symbols.')
                window['input_validation'].update('Unable to read INITIAL SYMBOL\n- Correct syntax is S = <S> where <S> is the initial symbol'
                                        ' that belongs to the set of nonterminal symbols.')
                window['ll_input_validation'].update('Unable to read INITIAL SYMBOL\n- Correct syntax is S = <S> where <S> is the initial symbol'
                                        ' that belongs to the set of nonterminal symbols.')
            elif not cfg_p_t:
                window['output'].update('Unknown TERMINAL or NONTERMINAL\n- Rules can contain only terminal symbols that are defined in the set of terminal symbols'
                                        ' and nonterminal symbols that are defined in the set of nonterminal symbols.')
                window['input_validation'].update('Unknown TERMINAL or NONTERMINAL\n- Rules can contain only terminal symbols that are defined in the set of terminal symbols'
                                        ' and nonterminal symbols that are defined in the set of nonterminal symbols.')
                window['ll_input_validation'].update('Unknown TERMINAL or NONTERMINAL\n- Rules can contain only terminal symbols that are defined in the set of terminal symbols'
                                        ' and nonterminal symbols that are defined in the set of nonterminal symbols.')
            elif not cfg_p:
                window['output'].update('Unable to read RULES\n- Correct syntax is...')

if __name__ == '__main__':
    main()
    sys.exit(0) #uspesny konec programu