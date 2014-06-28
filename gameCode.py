#How to go to a certain byte in file:
#f.seek(byteNum)
#This moves the file cursor to that location.
#How to find current byte location of cursor: f.tell()
''' 
Master plan:
---The game will load all of the codeword sets into a dictionary for the word sets.
---Then, it will select an uncoded word at random (from network), and call that startWord.
---It will find all of the words that appear after one change of startWord.
---Then, it will take these words, and remember them so that nothing will change into something alredy covered.
---It will find all of the words that appear when it finds the changes of all of the words it previously found. Note that, if it comes across a previously found word, it will erase it from the new list.
---It will do this over and over again, until it reaches x changes away from startWord (to correspond to the difficulty level)
---For each generated word, it will keep track of its relationship to startWord.
---Finally, it will pick a word at random from the xth layer, then use its relationship path to make the solution to the problem in the game!
the game will randomly select a starting word.
First, the program will find the basic set of codewords within network
that have the number of characters of the selected starting word.
'''
import random
import time
nwks={}
def parent(nw):
    lnw=list(nw)
    i=len(lnw)/2
    nwWord=[]
    while i<len(lnw):
        focusLetter=lnw[i]
        nwWord=nwWord+[focusLetter]
        i=i+1
    word="".join(nwWord)
    return word
def child(nw):
    lnw=list(nw)
    i=0
    nwWord=[]
    while i<(len(lnw)/2):
        focusLetter=lnw[i]
        nwWord=nwWord+[focusLetter]
        i=i+1
    word="".join(nwWord)
    return word
def twoChars(string):
    charList=list(string)
    newCharList=[charList[0],charList[1]]
    result="".join(newCharList)
    return result
def removeListFromList(valsToRemove,originalList):
    for val in valsToRemove:
        if val in originalList:
            originalList.remove(val)
    return originalList

def allWordsUnderListOfKeys(dct,keys,alreadyDone):
    words=[]
    for key in keys:
        if key in dct:
            words = set(dct[key]) - alreadyDone
            # for val in dct[key]:
            #     if val not in alreadyDone:
            #         words+=[val]
    return words
#works
def decodeIndNumbers(numberStringList):
    cs=[]
    location=[]
    passedSpace=False
    #numberStringList would be something like ["1","2","3"," ", "3"]
    for val in numberStringList:
        if val != " " and not passedSpace:
            cs+=[val]
        if val == " ":
            passedSpace=True
        if val != " " and passedSpace:
            location+=[val]
    cs=int("".join(cs))
    location=int("".join(location))
    return cs,location
#AWESOMENESS!! THIS WORKS!
def getIndex():
    #hopefully, this will return something like
    # [{charSet:[start,end]},{charSet:[start,end]}, and so on]
    with open("index","ab+") as index:
        locations={}
        for line in index:
            if twoChars(line)=="CS":
                listLine=list(line)
                listLine.remove("C")
                listLine.remove("S")
                listLine.remove(" ")
                indNumList=decodeIndNumbers(listLine)
                locations[indNumList[0]]=[indNumList[1]]
            if twoChars(line)=="EN":
                listLine=list(line)
                listLine.remove("E")
                listLine.remove("N")
                listLine.remove("D")
                listLine.remove("C")
                listLine.remove("S")
                listLine.remove(" ")
                indNumList=decodeIndNumbers(listLine)
                locations[indNumList[0]] += [indNumList[1]]
    return locations

def getIndexAppa():
    # {charSet1:[start,end],charSet2:[start,end]},...}
    locations = {}
    with open('index','ab+') as index:
        for line in index:
            if line.startswith("CS"):
                vals = line.rstrip().split(' ')
                start = int(vals[2])
            elif line.startswith("ENDCS"):
                vals = line.rstrip().split(' ')
                locations[int(vals[1])]=[start,int(vals[2])]
            else:
                raise Exception("Unexpected line: "+line)
    return locations
def getNetwork(charsInWord):
    # {parent:[children],parent:[children],...}
    index=getIndex()
    print index
    netwk={}
    with open('network','ab+') as network:
        network.seek(index[charsInWord][0])
        print "startseek location is %d"%index[charsInWord][0]
        prevParent=None
        for line in network:
            line=line.rstrip()
            #if network.tell()>=index[charsInWord][1]:
            if line.startswith("EndCS"):
                break
            #if the current line has the same parent as the previous line...
            elif parent(line)==prevParent:
                #add to existing dict entry
                netwk[parent(line)].add(child(line))
            elif parent(line)!=prevParent:
                #create new dict entry
                netwk[parent(line)]={child(line)}
            else:
                raise Exception("error in loadNetwork")
            prevParent=parent(line)
    return netwk
def addListToDict(lst,dct):
    for val in dct:
        dct[val]=True
    return dct
def updateFrontier(nwk,farthestAwayWords,coveredWords,networkPiece):
    possibles=set([])
    for word in farthestAwayWords:
        if word in nwk:
            possibles |= nwk[word]
            networkPiece[word] = nwk[word] - coveredWords
    possibles -= coveredWords
    coveredWords |= possibles
    return possibles
def trackTree(nwkPiece,nwk,start,end):
    #Finish. Make sure that it does not slow the prog down
    possibleParents=nwk[end]
    path=[end]
    currentWord=end
    #Must make this loop and loop and loop until it finds start
    #while currentWord != start:
    for i in range(10):
        for parent in possibleParents:
            if parent not in path and parent in nwkPiece and currentWord in nwkPiece[parent]:
                path.insert(0,parent)
                break
        if parent == start:
            break
        currentWord=parent
        possibleParents=nwk[parent]
    return path
def makePuzzle(numChars, numOfRounds):
    global nwks
    again=True
    if numChars not in nwks:
        nwks[numChars]=getNetwork(numChars)
    nwk=nwks[numChars]
    print 'got network'
    nkeys=set(nwk.keys())
    newNkeys=nkeys
    badStart=None
    tries=1
    networkPiece={}
    while again:
        print "starting try %d"%tries
        startTime=time.time()
        if badStart in newNkeys:
            newNkeys.remove(badStart)
        again=False
        startWord = random.choice(list(newNkeys))
        farthestAwayWords={startWord}
        coveredWords={startWord}
        print 'coveredWord is '+str(coveredWords)
        '''
        This will go numOfRounds levels outwards.
        At each level, it will remove all words it has seen before 
            using removeListFromList.
        Each level will then be recorded to farthestAwayWords, replacing the previous
        After numOfRounds levels, it will pick a random word from farthestAwayWords
        to be the destination!
        '''
        for i in range(numOfRounds):
#            farthestAwayWords=allWordsUnderListOfKeys(nwk,farthestAwayWords,coveredWords)
            farthestAwayWords = updateFrontier(nwk,farthestAwayWords,coveredWords,networkPiece)
            if farthestAwayWords==set([]):
                again = True
                tries+=1
                badStart = startWord
                break
            # if farthestAwayWords!=[]:
            #     print '.'
            #     coveredWords=addListToDict(farthestAwayWords,coveredWords)
            # else:
            #     print 'failed try %d; took %d seconds'%(tries,time.time()-startTime)
            #     again=True
            #     tries+=1
            #     badStart=startWord
            #     break
            print '.'
    print 'finished try %d; took %d seconds'%(tries,time.time()-startTime)
    destination=random.choice(list(farthestAwayWords))
    path=trackTree(networkPiece,nwk,startWord,destination)
    return path
def pathBetween(start,end):
    global nwks
    nwk=nwks[len(start)]
    print 'got network'
    nkeys=set(nwk.keys())
    newNkeys=nkeys
    networkPiece={}
    print "starting try"
    startTime=time.time()
    startWord = start
    farthestAwayWords={startWord}
    coveredWords={startWord}
    print 'coveredWord is '+str(coveredWords)
    while end not in farthestAwayWords:
        #            farthestAwayWords=allWordsUnderListOfKeys(nwk,farthestAwayWords,coveredWords)
        farthestAwayWords = updateFrontier(nwk,farthestAwayWords,coveredWords,networkPiece)
        print '.'
    print 'finished try; took seconds'
    path=trackTree(networkPiece,nwk,startWord,end)
    return path
def makePuzzleSlow(numChars, numOfRounds):
    again=True
    nwk=getNetwork(numChars)
    print 'got network'
    nkeys=nwk.keys()
    newNkeys=nkeys
    badStart=None
    tries=1
    while again:
        print "starting try %d"%tries
        startTime=time.time()
        if badStart in newNkeys:
            newNkeys.remove(badStart)
        again=False
        farthestAwayWords=[random.choice(newNkeys)]
        #farthestAwayWords=[startWord]
        startWord=farthestAwayWords[0]
        coveredWords=farthestAwayWords
        print 'coveredWord is '+str(coveredWords)
        '''
        This will go numOfRounds levels outwards.
        At each level, it will remove all words it has seen before 
            using removeListFromList.
        Each level will then be recorded to farthestAwayWords, replacing the previous
        After numOfRounds levels, it will pick a random word from farthestAwayWords
        to be the destination!
        '''
        for i in range(numOfRounds):
            farthestAwayWords=allWordsUnderListOfKeys(nwk,farthestAwayWords,coveredWords)
            if farthestAwayWords!=[]:
                print '.'
                coveredWords+=farthestAwayWords
            else:
                print 'failed try %d; took %d seconds'%(tries,time.time()-startTime)
                again=True
                tries+=1
                badStart=startWord
                break
    print 'finished try %d; took %d seconds'%(tries,time.time()-startTime)
    destination=random.choice(farthestAwayWords)
    return startWord,destination
#FIX GETNETWORK SO THAT IT ONLY GETS THE WORDS OF A CERTAIN CHARSET!!!!!!!
#NEWEST NOTE: GETNETWORK FIXED, MAKE allWordsUnderListOfKeys MORE EFFICIENT! 
print "loaded"
