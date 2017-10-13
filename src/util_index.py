# ------------------------------------------------------------------
# Import

from os import listdir
from os.path import isfile, join
from ipywidgets import FloatProgress
from IPython.display import display
from bs4 import BeautifulSoup as bs
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import *
import nltk
import string
import operator
import shutil,os
import re
# ------------------------------------------------------------------
# constant

# Represent the constraint of memory
NB_DOCUMENT = 1000
DATA_PATH = "../data/latimes/"
NAME_POSTING_LIST = "postingList_"
SEPARATOR = " "

# link the tags with the importance in the text.
TAGS_IMPORTANCE = {  'headline': 3,
                     'text': 1,
                     'section':1,
                     'graphic':2
                  }
STOP_WORDS = stopwords.words('english') + list(string.punctuation)
STEMMER = PorterStemmer()
TAG_NUMBER = "NUMBER"
# ------------------------------------------------------------------

##
# clean repository of the giver path: "folder"
###
def cleanRepository(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
            
            
##
# Tokenize a sentense.
##
def tokenizeWord(paragraphContent):  
    # We tokenize and remove the stop word
    words = [word for word in word_tokenize(paragraphContent.lower()) if word not in STOP_WORDS]
    
    # nlkt does not decompose the hyphen.
    splitHiphen = []
    for word in words:
        if '-' in word:
            for decomposedWord in word.split('-'):
                splitHiphen.append(decomposedWord)
        else:
            splitHiphen.append(word)  
            
    return splitHiphen


##
# Format the text in the right form.
# Tokenize and stem the text
# Update the voc list passed in parameter.
##
def handleFormatText(paragraphContent, vocList, docLenght, docId):  
    # We tokenize and remove the stop word
    words = tokenizeWord(paragraphContent) 
    
    stemWords = []
    # We loop on each word.
    for word in words:
        stemWord = STEMMER.stem(word)
        
        # Selection on a part of string.
        stemWord = re.sub("[*\'\.+:,\`:/]", '', stemWord)
        if stemWord.isdigit() or len(stemWord) < 2:
            continue
            
        stemWords.append(stemWord)
        # Update the listVoc
        if stemWord in vocList:
            vocList[stemWord] = vocList[stemWord] + 1
        else:
            vocList[stemWord] = 1
        
        docLenght[docId] += 1
    return stemWords

##
# The function add the entry in the correct posting list
##
def buildPostingList(stemWords, currentDict, idDoc):
    # We update the stemWords.
    for word in stemWords:
        # The word have already been seen, we update thedict
        if word in currentDict :
            # We update the dict reprensenting the posting list.
            if idDoc in currentDict[word]:
                currentDict[word][idDoc] = currentDict[word][idDoc] + 1

            else:
                currentDict[word][idDoc] = 1

        # We don't have word for now
        else:
            currentDict[word] = {idDoc : 1};
            
    return

##
# Write file.
##
def writingInFile(currentDict, index, path, name, separator):  
    # sort word for the posting list.
    sorted_word = sorted(currentDict.keys())
    
    # write the posting list.
    with open(path+name+str(index),"a+") as f:
        for word in sorted_word:
            portingEntry = word + separator
            for docID, value in currentDict[word].items():
                portingEntry = portingEntry + str(docID) + separator + str(value) + separator
            f.write(portingEntry + '\n')
            
##
# Write voc file
##
def writingDictInFile(currentDict, path, name, separator): 
    # write the posting list.
    with open(path+name ,"a+") as f:
        for docID, value in currentDict.items():
            portingEntry = ""
            portingEntry = portingEntry + str(docID) + separator + str(value)
            f.write(portingEntry + '\n')
            
            
##
# The function build the index file composed by the voc and the associated posting list.
##
def buildIndexFile(vocList, docLenght, WRITING_PATH_POSTING_LIST = "../data/saveFile/") :
    print("Building index File")
    
    # We get the list of file containing the articles.
    articles = [DATA_PATH + file for file in listdir(DATA_PATH) if (isfile(join(DATA_PATH, file)) and ".txt" not in file and ".DS_Store" not in file )]
    progress_bar = FloatProgress(min=0, max=len(articles))
    display(progress_bar)
    
    # List containing the term and the number of time it appear.
    currentPostingList = {}
    counter = 0
    docIDCounter = 0 
    
    
    #We loop on each document composing the corpus.
    for article in articles:
        with open(article) as curArticle:
            file = curArticle.read()
            fileXML = bs(file,"lxml")
            
            # We loop on each doc tag
            for document in fileXML.findAll('doc'):
                docIDCounter = docIDCounter + 1
                docID = document.find("docid").string
                docLenght[docID] = 0
                
                # get the text containing in the current article
                curParagraph = document.find_all('p')
                for paragraph in curParagraph:
                   
                    # We balance with the importance of the parent tag
                    if paragraph.parent.name in TAGS_IMPORTANCE:
                        for index in range(TAGS_IMPORTANCE[paragraph.parent.name]):
                            stemWords = handleFormatText(paragraph.string,vocList, docLenght, docID)
                            buildPostingList(stemWords, currentPostingList, int(docID))
                             
                if docIDCounter % NB_DOCUMENT == 0 :
                    counter = counter + 1
                    writingInFile(currentPostingList, counter, WRITING_PATH_POSTING_LIST, NAME_POSTING_LIST, SEPARATOR)
                    # clear the ram memory.
                    currentPostingList.clear()
             
        curArticle.closed
        progress_bar.value += 1