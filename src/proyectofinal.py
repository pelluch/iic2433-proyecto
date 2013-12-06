import numpy as np
from numpy import linalg as LA
from numpy import mean,cov,double,cumsum,dot,linalg,array,rank
from collections import Counter
import matplotlib.pyplot as plt
import Queue
import time

#Grupo de trabajo: Nuno Teles, Pablo Lluch, Tomas Fuentes

#Frecuent_ItemSet_DataSet-: Read all data transactions from Database
Frecuent_ItemSet_DataSet = array(np.genfromtxt('.\..\data\grouptest.dat'), dtype='int')
#Lets the user define de Minimum Threshold to find frequent item-sets
Min_Threshold = 2

def InsertTransaction(TransactionLists,Transaction,Itemlider,Sortedscore):        
#Function InsertTransaction - function that inserts a transaction in the TransactionLists, using el itemLider as index,
#To do that, it is necessary to know the itemindex, that the ItemLider have in list Sortedscore (index,count)

# This receives the structure (TransactionLists) where the transactions will be stored (it can be empty if the structure is created at begining)
#or the the Relimstructure (during the recursion) because after iterate through an TransactionList it necessary to assign 
#the transactions without the item that the list indexes (Itemlider)

# TransactionLists has in each position, an List that as in the first position a Support Counter and in the second position an Queue -
#That stores the rest of each Transaction (Transaction Original without the Itemlider

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
#Function SearchTransactions - function that returns the transactions that are store in the TransactionQueue
#Iteratively retrieves all values until the Queue remains empty
    
    TransactionListProcessed = []
    
    while not TransactionQueue.empty():
         TransactionListProcessed.append(TransactionQueue.get())
    return TransactionListProcessed


def CreateRelimStructureWhithoutTransactions(Sortedscore):
#Function CreateRelimStructureWhithoutTransactions - function that creates the structure (empty) that will support the Algorithm
# To do that, it uses the Sortedscore - list that has in each position (index,counter). Its important to refer that this list 
# already doesnt have the support with respect to Infrequent Items - These items were removed in the Preprocessing Step RemoveInFrecuentItems function  
# Output: the Lists of Transactions (Data structure) that will be used to store the transactions    
    TransactionLists = []
    TransactionList = []
    
    for item_score in Sortedscore: #(item_score : (item,counter))
        QueueTransaction = Queue.Queue(0) #Inicializes each Queue 
        TransactionList.insert(0,0) # inserts the inicial support 0 because we dont insert any transaction yet
        TransactionList.insert(1,QueueTransaction) #Queue will be store in the second position of each List 
        
        itemindex=np.where(Sortedscore==item_score) 
        
        TransactionLists.insert(itemindex[0][0],TransactionList) #insert the TransactionList in the index, obtained from the position of the item_score in the Sortedscore List
        TransactionList = []
    
    return TransactionLists

def ConstructRelimStructureWithTransactionLists(Transactions,Sorted_score):
#Function ConstructRelimStructureWithTransactionLists - function that initially Creates the Empty Structure using the function -
# CreateRelimStructureWhithoutTransactions. For each transaction that exists in the list Transactions, we insert the transaction
# in the Empty Structure using the function - InsertTransaction
    Itemlider = []
    TransactionLists = CreateRelimStructureWhithoutTransactions(Sorted_score) 
    
    for transaction in Transactions:
        if not transaction: #if the transaction to insert is empty it does not necessary to insert the transaction
            continue
        else:
            Itemlider = transaction[0] #extracts the item lider
            transactionToInsert = transaction[1:] #extracts the rest of the transaction without the item lider
            TransactionLists = InsertTransaction(TransactionLists,transactionToInsert,Itemlider,Sorted_score) 
    return TransactionLists

def RemoveInFrecuentItems(TransactionsDataBase,Sortedscore):
#Function RemoveInFrecuentItems - function that receives the set of transactions (Database) in order to remove the infrequent items
#To do that, it first calculates de items that are infrequent (thats does not satisfy the minimum threshold)    
# After from doing that removes the infrequent items from the Sortedscore list.
# Finally removes the infrequent items from the original set of transactions (Database) - TransactionsWithoutInFrecuent
# Output: Database Actualized without the inefrequent item and the actualized Sortedscore - List
    InfrecuentItems = []
    TransactionsWithoutInFrecuent = []
    Sorted_scoreWithoutInefrecuents = []
    
    for intem_score in Sortedscore: # for each pair of the form (item,counter)
        if intem_score['count'] < Min_Threshold: #Test if the item is infrequent
            InfrecuentItems.append(intem_score['item'])
     
    #removes the inefrequentes items form the the Sortedscore List, thats the pairs (item,counter)    
    Sorted_scoreWithoutInefrecuents = [intem_score for intem_score in Sortedscore if intem_score['item'] not in InfrecuentItems]
        
    for transaction in TransactionsDataBase: #for each transaction in the original database

        #we remove the infrequente items
        TupleWhithoutInFrecuent = [item for j, item in enumerate(transaction) if item not in InfrecuentItems]
        TransactionsWithoutInFrecuent.append(TupleWhithoutInFrecuent)

    return TransactionsWithoutInFrecuent,Sorted_scoreWithoutInefrecuents

def Relim(RelimStructure,Sortedscore):
#Function Relim - Recursive Function that iterates throught all transactionlists individually that are stored in the RelimStructure
# Tests for each Transaction List if the support Counter stored in the first position respects the Min_Threshold, if respects,
# stores the itemprefix of that transaction List, thats this prefix (item), that is given by the position of the transactionList in
# the Sortedscore
# In case of the item satisfies the Min_Threshold, it is necessary to create an NewRelimStructure with the transactions that the item
#points, thats is the Queue of transactions present in the transaction List. The NewRelimStructure is iterated recursively and his Frecuent-Items
#are returned
# After processing one transaction List, the algorithm asigns the transactions pointed in the Queue to the others TransactionLists in order to
# discover new frecuent-item sets that not have the respective item-lider 
    
    TransactionsListToProcess = []
    NewRelimStructure = [] 
    FrecuentItemsInRecursion = []
    FrecuentItems = []
    Aux = []

    for TransactionList in RelimStructure:
        #Search for the transactions that are associated to the ItemLider, thats his Queue
        TransactionsListToProcess = SearchTransactions(TransactionList[1])
        
        if TransactionList[0] >= Min_Threshold: #Test the SupportCounter against the Min_Treshold
            
            index = RelimStructure.index(TransactionList) #obtain the index of the transactionlist with the objective of knowing                                                        
            itemprefix = Sortedscore[index]['item']       # which item is associated to that position
            FrecuentItems.append(itemprefix)              # Asign the frequent item to the List of FrequentItems
            
            #Creates the new RelimStructure with the transactions stored in the Queue of that Item
            NewRelimStructure = ConstructRelimStructureWithTransactionLists(TransactionsListToProcess,Sortedscore) 
            
            #Calls the algorithm recursively with the new RelimStructure
            FrecuentItemsInRecursion = Relim(NewRelimStructure,Sortedscore)

            for item in FrecuentItemsInRecursion: # Asign each frecuent-item found in recursion with the actual item that                                              #
                Aux.append(itemprefix)            # we are considering
                Aux.append(item)
                FrecuentItems.append(Aux)
                Aux = []
            FrecuentItemsInRecursion = []

       
        for Transaction in TransactionsListToProcess: #Inserts each of the Transactions stored in the Queue of this Item
            if not Transaction:                       #in the other transactionsList using the InsertTransaction Fuction
                continue                              #this step actualizes the RelimStructure that we are considering
            else :
                Itemlider = Transaction[0]
                TransactionToInsert = Transaction[1:]
                RelimStructure = InsertTransaction(RelimStructure,TransactionToInsert,Itemlider,Sortedscore)
        
        NewRelimStructure = []
        TransactionList[0] = 0
    
    return FrecuentItems

def DataPreprocessing(DatabaseTransactions):
#Function DataPreprocessing - that preprocesses the data from the database in order to constructs the 
#the initial that structure that the algorithm will use
#To do that, first calculates the score of each item individually, second removes the infrequent items from the original database
#and actualizes the list of scores of each item, if at least one infrequent item is found - uses the RemoveInFrecuentItems function.
#After this step, reorder each item in each transaction independently using the counter of support of each item present in the Score List
# The next step consists of creating the DataStructure that will support the RELIM algorithm using the 
# function - ConstructRelimStructureWithTransactionLists
# Finally calls the RELIM function
    
    ItemsCounts = []
    
    #Step1: Count the frecuencies of each item (find support)
    for transaction  in DatabaseTransactions:
        #counts the frequencies of each item individually for each transaction in the database, limiting 
        # the Counting using the maximum value of one item present in all database 
        ItemsCounts.append(np.bincount(np.array(transaction),minlength=np.amax(np.amax(DatabaseTransactions ,axis=1)) + 1))

    ItemsCounts = np.array(ItemsCounts)
    Support = ItemsCounts.sum(axis=0)[1::] #Sum the frecuencies of each row to obtain the final score for each item
    ##########################################################################################
    
    #Step2: Order Support of each item 
    Tuples = []
    dtype = [('item', int), ('count', int)]
    
    for item, counter in enumerate(Support):
        Tuples.append((item+1,counter))

    TuplesWithSupport = np.array(Tuples, dtype=dtype)
    Sorted_Support = np.sort(TuplesWithSupport, kind='quicksort', order='count') #order the pairs (item,counter) using the attribute count (support)
    #########################################################################################

    #Step3: Remove Infrecuent Items from the initial DataBase of Transactions and from the Sorted Support 
    [DatabaseTransactions,sorted_score_whithoutIne] = RemoveInFrecuentItems(DatabaseTransactions,Sorted_Support)
    #########################################################################################

    #Step4: Order each transaction using the Support Order
    OrderedTransactions = []
    
    for transaction in DatabaseTransactions:
        TuplesToOrder = []
        
        for item in transaction:
            TuplesToOrder.append((item, Support[item - 1]))
        
        TransactionToOrder = np.array(TuplesToOrder, dtype=dtype)
        
        OrderedTransaction = np.sort(TransactionToOrder, kind='quicksort', order='count') #order the pairs (item,counter) using the attribute count (support)

        OrderedTransaction = [ item['item'] for item in OrderedTransaction] #remains with the attribute item to obtain the ordered transaction
        
        OrderedTransactions.append(OrderedTransaction)
    ##################################################
    
    #Step5: Creates Initial Relim Structure with the OrderedTransactions and the actualized sorted_score. Sorted_score is necessary because 
    # we have to map the transactions in the RelimStructure using the SupportOrder.
    InitialRelimStructure = ConstructRelimStructureWithTransactionLists(OrderedTransactions,sorted_score_whithoutIne) 
    ################################

    #Calls RelimAlgorithm, obtaing the FrecuentItems
    FrecuentItemsFinal = Relim(InitialRelimStructure,sorted_score_whithoutIne)
    print(FrecuentItemsFinal)

start_time = time.clock() #Time Primitives - used to estimate the Computation Time (uses the internal Clock Time)
DataPreprocessing(Frecuent_ItemSet_DataSet)
print time.clock() - start_time, "seconds" #The results obtained for each database (we evaluated) are described in the experimental Results 


