#bool funkce kontrolujici, jestli je znak alfanumericky
def isChar(char):
    return char.isalpha()

#bool funkce kontroluljici, jestli je znak cislo
def isNum(char):
    return char.isnumeric()

#funkce cte a vraci 1 znak ze souboru predaneho v argumentu funkce
def readCharacter(file):
    return file.read(1)

#funkce cte nasledujici znak ze souboru predaneho v argumentu funkce a posunuje ukazatel o 1 zpet
def readNextChar(inputFile):
    nextChar = inputFile.read(1)
    if nextChar == '': #kontrola konce souboru
        return ''#konec souboru
    inputFile.seek(inputFile.tell() - 1,0) #vraceni ukazatele cteni v souboru o 1 zpet
    return nextChar

#funkce pro inplace update (union) mezi dvema strukturami set
def union(first, begins):
    n = len(first)
    first |= begins
    return len(first) != n

#funkce konvertujici polozky seznamu na n-tici
def convert(list):
    return tuple(i for i in list)

#funkce vraci nactene pravidla gramatiky ve strukture tuple (n-tice)
def getRulesSet(grammarRules):
    rules = () #n-tice, do niz budou pridany zpracovane pravidla
    for i in grammarRules: #prochazeni vsech nactenych pravidel
        if (len(i.rightSide) == 1): #pouze jedno pravidlo na prave strane ve tvaru A -> a
            listToString = ' '.join([str(elem) for elem in i.rightSide]) #prevedeni jednotlivych znaku na retezec
            if ('Îµ' in listToString): #epsilon je nahrazeno prazdnym retezcem
                rule = (i.leftSide, '')
            else:
                rule = (i.leftSide, listToString)
            rules += (rule,) #vlozeni konkretniho pravidla typu tuple (n-tice)
        else:
            for element in i.rightSide:
                if ('Îµ' in element or 'epsilon' in element or 'eps' in element):  #jestlize bylo nalezeno epsilon ε
                    rule = (i.leftSide, '') #epsilon je nahrazeno prazdnym retezcem
                else:
                    rule = (i.leftSide, element)
                rules += (rule,) #vlozeni konkretniho pravidla typu tuple (n-tice)
    return rules