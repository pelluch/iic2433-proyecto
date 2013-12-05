import numpy as np
from numpy import linalg as LA
from numpy import mean,cov,double,cumsum,dot,linalg,array,rank
from collections import Counter
import matplotlib.pyplot as plt
import Queue
import fnmatch
import csv

Frecuent_ItemSet_DataSet = array(np.genfromtxt('.\..\data\chesstest.dat'), dtype='int')
Min_Threshold = 2

def InsertTransaction(TransactionLists,Transaction,Itemlider,Sortedscore):        
    
    TransactionList = []
    
    for intem_score in Sortedscore:
        if intem_score['item'] == Itemlider:
            itemindex=np.where(Sortedscore==intem_score)          
            TransactionList = TransactionLists[itemindex[0][0]]
            TransactionList[0] = TransactionList[0] + 1
            QueueTransaction = TransactionList[1]
            QueueTransaction.put(Transaction)
    
    return TransactionLists

def SearchTransactions(TransactionQueue):
    
    TransactionListProcessed = []
    
    while not TransactionQueue.empty():
         TransactionListProcessed.append(TransactionQueue.get())
    return TransactionListProcessed


def CreateRelimStructureWhithoutTransactions(Sortedscore):
    
    TransactionLists = []
    TransactionList = []
    
    for item_score in Sortedscore:
        QueueTransaction = Queue.Queue(0)
        TransactionList.insert(0,0)
        TransactionList.insert(1,QueueTransaction)
        
        itemindex=np.where(Sortedscore==item_score) 
        
        TransactionLists.insert(itemindex[0][0],TransactionList)
        TransactionList = []
    
    return TransactionLists

def ConstructRelimStructureWithTransactionLists(Transactions,Sorted_score):
    
    Itemlider = []
    TransactionLists = CreateRelimStructureWhithoutTransactions(Sorted_score) 
    
    for transaction in Transactions:
        if not transaction:
            continue
        else:
            Itemlider = transaction[0]
            transactionToInsert = transaction[1:]
            TransactionLists = InsertTransaction(TransactionLists,transactionToInsert,Itemlider,Sorted_score)
    return TransactionLists

def RemoveInFrecuentItems(TransactionsDataBase,Sortedscore):
    
    InfrecuentItems = []
    TransactionsWithoutInFrecuent = []
    Sorted_scoreWithoutInefrecuents = []
    
    for intem_score in Sortedscore:
        if intem_score['count'] < Min_Threshold:
            InfrecuentItems.append(intem_score['item'])
            itemindex=np.where(Sortedscore==intem_score)
        
    Sorted_scoreWithoutInefrecuents = [intem_score for intem_score in Sortedscore if intem_score['item'] not in InfrecuentItems]
        
    for transaction in TransactionsDataBase:

        TupleWhithoutInFrecuent = [transaction for j, transaction in enumerate(transaction) if transaction not in InfrecuentItems]
        TransactionsWithoutInFrecuent.append(TupleWhithoutInFrecuent)

    return TransactionsWithoutInFrecuent,Sorted_scoreWithoutInefrecuents

def DataPreprocessing(DatabaseTransactions):
   
    ItemsCounts = []
    
    #Count the frecuencies of each item
    for transaction  in DatabaseTransactions:
        ItemsCounts.append(np.bincount(np.array(transaction),minlength=np.amax(np.amax(DatabaseTransactions ,axis=1)) + 1))

    ItemsCounts = np.array(ItemsCounts)
    Support = ItemsCounts.sum(axis=0)[1::]
    ##########################################################################################
    
    #Order Support of each item
    Tuples = []
    dtype = [('item', int), ('count', int)]
    
    for item, counter in enumerate(Support):
        Tuples.append((item+1,counter))

    TuplesWithSupport = np.array(Tuples, dtype=dtype)
    Sorted_Support = np.sort(TuplesWithSupport, kind='quicksort', order='count')
    #########################################################################################

    #Remove InFrecuent Items from Transactions DataBase and Sorted Support
    [DatabaseTransactions,sorted_score_whithoutIne] = RemoveInFrecuentItems(DatabaseTransactions,Sorted_Support)
    #########################################################################################
    
    #Order each transaction using the Support Order
    OrderedTransactions = []
    
    for transaction in DatabaseTransactions:
        TuplesToOrder = []
        
        for item in transaction:
            TuplesToOrder.append((item, Support[item - 1]))
        
        TransactionToOrder = np.array(TuplesToOrder, dtype=dtype)
        
        OrderedTransaction = np.sort(TransactionToOrder, kind='quicksort', order='count')
        OrderedTransaction = [ item['item'] for item in OrderedTransaction]
        
        OrderedTransactions.append(OrderedTransaction)
    ##########################################
    
    #Creates Initial Relim Structure   
    InitialRelimStructure = ConstructRelimStructureWithTransactionLists(OrderedTransactions,sorted_score_whithoutIne) 
    print(InitialRelimStructure) 
    ##########################################

    #Calls RelimAlgorithm
    FrecuentItemsFinal = Relim(InitialRelimStructure,sorted_score_whithoutIne)
    print(FrecuentItemsFinal)

def Relim(RelimStructure,Sortedscore):
    
    TransactionsListToProcess = []
    NewRelimStructure = [] 
    FrecuentItemsInRecursion = []
    FrecuentItems = []
    Aux = []

    for TransactionList in RelimStructure:
        #Busca las transacciones que estan asociadas al itemlider
        TransactionsListToProcess = SearchTransactions(TransactionList[1])
        #print(ListaTransactionsProcessedByRelim)
        if TransactionList[0] >= Min_Threshold: 
            
            index = RelimStructure.index(TransactionList)
            itemprefix = Sortedscore[index]['item']
            FrecuentItems.append(itemprefix)
            
            NewRelimStructure = ConstructRelimStructureWithTransactionLists(TransactionsListToProcess,Sortedscore)
            
            FrecuentItemsInRecursion = Relim(NewRelimStructure,Sortedscore)
            for item in FrecuentItemsInRecursion:
                Aux.append(itemprefix)
                Aux.append(item)
                FrecuentItems.append(Aux)
                Aux = []
            FrecuentItemsInRecursion = []

        #inserta las de la lista de transacciones que esta a ser procesada en la estrutura procesada originalmente
        for Transaction in TransactionsListToProcess:
            if not Transaction:
                continue
            else :
                Itemlider = Transaction[0]
                TransactionToInsert = Transaction[1:]
                RelimStructure = InsertTransaction(RelimStructure,TransactionToInsert,Itemlider,Sortedscore)
        
        NewRelimStructure = []
        TransactionList[0] = 0
    
    return FrecuentItems

DataPreprocessing(Frecuent_ItemSet_DataSet)



