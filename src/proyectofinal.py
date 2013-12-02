import numpy as np
from numpy import linalg as LA
from numpy import mean,cov,double,cumsum,dot,linalg,array,rank
from collections import Counter
import matplotlib.pyplot as plt

Frecuent_ItemSet_DataSet = array(np.genfromtxt('./../data/chess.dat'), dtype='int')
Min_Threshold = 2

    
def remove_values_from_list(the_list, val):
    A = list(the_list)
    for ii in range(list(the_list).count(val)):
        A.remove(val)
        return A



def DataPreprocessing(M):
    NumberCounts = []
    for i  in M:
        NumberCounts.append(np.bincount(np.array(i),minlength=np.amax(np.amax(M ,axis=1)) + 1))
    
    NumberCounts = np.array(NumberCounts)
    Score = NumberCounts.sum(axis=0)[1::]
    print(Score)
    tuples = []
    dtype = [('item', int), ('count', int)]
    for idx, count in enumerate(Score):
        tuples.append((idx+1,count))

    #print(tuples)
    print(tuples)

    npTuples = np.array(tuples, dtype=dtype)
    sorted_score = np.sort(npTuples, kind='quicksort', order='count')
    print(sorted_score)

    #for i in range(0,np.amax(np.amax(M ,axis=1)) + 1):
    #    if Score[i] < Min_Threshold:
    #        for x in M:
    #            if i in x:
    #                x = remove_values_from_list(x,i)
    #                #print(x)

        
DataPreprocessing(Frecuent_ItemSet_DataSet)



