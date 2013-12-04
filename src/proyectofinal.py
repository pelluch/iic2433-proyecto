import numpy as np
from numpy import linalg as LA
from numpy import mean,cov,double,cumsum,dot,linalg,array,rank
from collections import Counter
import matplotlib.pyplot as plt
import Queue

Frecuent_ItemSet_DataSet = array(np.genfromtxt('.\..\data\chesstest.dat'), dtype='int')
Min_Threshold = 2



#def remove_values_from_list(the_list, val):
    #A = list(the_list)
    #for ii in range(list(the_list).count(val)):
        #A.remove(val)
        #return A

def InsertTransaction(M,T,itemlider):
    ListTransaction = []
    ListTransaction = M[itemlider - 1]
    ListTransaction[0] = ListTransaction[0] + 1
    Queue1 = ListTransaction[1]
    Queue1.put(T)
    
    return M

def BuscaTransactions(QueueTransac):
    ListaTransactionsProcessedByRelim = []
    while not QueueTransac.empty():
         ListaTransactionsProcessedByRelim.append(QueueTransac.get())
    return ListaTransactionsProcessedByRelim


def CreaEstrutraWhithoutTransactions(Score):
    transactionList = []
    ListTransaction = []
    
    for i in range(1,Score.size + 1):
        Queue1 = Queue.Queue(0)
        ListTransaction.insert(0,0)
        ListTransaction.insert(1,Queue1)
        transactionList.insert(i,ListTransaction)
        ListTransaction = []
    return transactionList

def ConstructTransactionList(M,Score):
    itemlider = []
    transactionList = CreaEstrutraWhithoutTransactions(Score) 
    for i in M:
        itemlider = i[0]
        transaction = i[1:]
        transactionList = InsertTransaction(transactionList,transaction,itemlider)
    return transactionList



def Relim(ProcessedStructure,Score):
    ListaTransactionsProcessedByRelim = []
    NuevaStructure = []
    
    for transactionlist in ProcessedStructure:
        #Busca las transacciones que estan asociadas al itemlider
        ListaTransactionsProcessedByRelim = BuscaTransactions(transactionlist[1])

        if transactionlist[0] >= Min_Threshold: 
            
            #crear una strutura de datos vacio
            NuevaStructure = CreaEstrutraWhithoutTransactions(Score)
            
            #constroye nueva Data Structure insertando apenas las transacciones del itemlider
            for i in ListaTransactionsProcessedByRelim:
                if not i:
                    continue
                else: 
                    itemlider = i[0]
                    transaction = i[1:]
                    NuevaStructure = InsertTransaction(NuevaStructure,transaction,itemlider)
            
            #llama el algoritmo Relim con la nueva estrutura
            Relim(NuevaStructure,Score)
        
        #inserta las de la lista de transacciones que esta a ser procesada en la estrutura procesada originalmente
        for transaction1 in ListaTransactionsProcessedByRelim:
            if not transaction1:
                continue
            else :
                itemlider = transaction1[0]
                transaction = transaction1[1:]
                ProcessedStructure = InsertTransaction(ProcessedStructure,transaction,itemlider)
        NuevaStructure = []

def DataPreprocessing(M):
    NumberCounts = []
    for i  in M:
        NumberCounts.append(np.bincount(np.array(i),minlength=np.amax(np.amax(M ,axis=1)) + 1))
    
    #Contabiliza las frecuencias de cada item
    NumberCounts = np.array(NumberCounts)
    Score = NumberCounts.sum(axis=0)[1::]
    #########################################
    
    #Ordena los items en cada transaccion por el Score
    tuples = []
    dtype = [('item', int), ('count', int)]
    ordered = []
    for itemset in M:
        tmp = []
        for item in itemset:
            tmp.append((item, Score[item - 1]))
        npItemset = np.array(tmp, dtype=dtype)
        npItemset = np.sort(npItemset, kind='quicksort', order='count')
        npItemset = [ t['item'] for t in npItemset]
        ordered.append(npItemset)
    ##########################################

    #Crea la estrutura inicial que va a ser usada en el algoritmo   
    InitialRelimStructure = ConstructTransactionList(ordered,Score)  
    ##########################################

    Relim(InitialRelimStructure,Score)
    
DataPreprocessing(Frecuent_ItemSet_DataSet)



