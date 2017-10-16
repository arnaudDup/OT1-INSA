# -----------------------------------------------------------------------------------------
# import
import matplotlib.pyplot as plt
import util_index
import util_posting
import math
import os
import time
# -----------------------------------------------------------------------------------------
# constant


##
# Compute the mean size in byte of files in 'folder'
# return int = mean size of document
##
def computeMeanSizeFilesInRepo(folder):
    nbFile = 0
    sizeFile = 0 
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                sizeFile += os.path.getsize(file_path)
                nbFile += 1
                
        except Exception as e:
            print(e)
    
    return int(float(sizeFile)/float(nbFile))


##
# loop on nbCuts and build the processing list for different document size.
# return a dict of form {nbcut : (meanSize, time elapsed)}
##
def computeDictRelationWithSizeTime(nbCuts, writingPath, docFile):
    result = {}
    for nbCut in nbCuts:
    
        print('WORKING FOR: ' + str (nbCut))
        vocList = {}
        docLenght = {}
        # We clean the repo containing all partial posting list
        util_index.cleanRepository(writingPath)
        
        # build partial index file
        util_index.buildIndexFile(vocList, docLenght, writingPath, nbCut)
        util_index.writingDictInFile(docLenght, writingPath, docFile, " ")

        # We compute the mean size of document needed for the posting list.
        meanSizebytes =  computeMeanSizeFilesInRepo(writingPath)

        # Compute the time needed to build the posting list
        start = time.time()
        util_posting.createPostingList()
        end = time.time()
        elapsed_time = end - start
        result[nbCut] = (meanSizebytes, elapsed_time) 
        
    return result


##
# display trade-off between time and space
##
def displayResult(result, titleString, xlabel, ylabel):
    axisX = []
    axisY = []
    for key, value in result.items():
        if value[0] !=  1781108.0:
            axisX.append(math.log(int(value[0])))
            axisY.append(int(value[1]))
        
    plt.plot(axisX, axisY)
    plt.title(titleString)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()