# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 07:49:47 2019

@author: Evangelista
"""

import random
import math 
import networkx as nx

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
        
def generate_graph(numberOfAgents, graphType, strMin = 0.0, strMax = 0.035):
    '''
    funkcja zwraca tablice polaczen w n listach z siłą przyjazni miedzy strMin i strMax, 0 oznacza brak polaczenia miedzy wezlami
    for example:
        array0 = [0,1,1,0,0,0]
        array1 = [0,1,0,1,0,1]
        array2 = [0,0,0,1,1,1]
        array3 = [1,1,0,1,1,1]
        array4 = [0,1,0,0,1,1]
    etc...
    '''
    #pełna lista połączeń o wartosci od strMin do strMax i jednoczesnie siec zupełna
    allArrays = [[random.uniform(strMin, strMax) for i in range(0, numberOfAgents)] for x in range(numberOfAgents)]
    for i in range(0, numberOfAgents):
        for j in range(0, numberOfAgents):
            if i==j:
                allArrays[i][j]=0
    #sieć zupełna        
    if graphType == "FullNet":
        return allArrays
    #sieć małego swiata oparta na pierscieniu z przyjazniami symetrycznymi
    elif graphType == "SmallWorldSymetric": 
        
        for i in range(0, numberOfAgents):
            if i!= numberOfAgents-1 and i!=1:
                if random.uniform(-0.9, 0.1) < 0:
                    allArrays[0][i] = 0
                             
        for i in range(0, numberOfAgents):
            if i!= numberOfAgents-2 and i!=0:
                if random.uniform(-0.9, 0.1) < 0:
                    allArrays[numberOfAgents-1][i] = 0
                             
        for i in range(1, numberOfAgents-1):
            for j in range(0, numberOfAgents):
                if random.uniform(-0.9, 0.1) < 0:
                    if i != j+1 and i != j-1:
                        allArrays[i][j] = 0 
        return allArrays
    #sieć małego swiata z przyjaźniami niekoniecznie symetrycznymi
    elif graphType == "SmallWorldAsymetric":
                
        for i in range(0, numberOfAgents):
            if i!= numberOfAgents-1 and i!=1:
                if random.uniform(-0.7, 0.2) < 0:
                    allArrays[0][i] = 0
                             
        for i in range(0, numberOfAgents):
            if i!= numberOfAgents-2 and i!=0:
                if random.uniform(-0.7, 0.2) < 0:
                    allArrays[numberOfAgents-1][i] = 0
                             
        for i in range(1, numberOfAgents-1):
            for j in range(0, numberOfAgents):
                if random.uniform(-0.7, 0.2) < 0:
                    if i != j+1:
                        allArrays[i][j] = 0 
        return allArrays
    #siec pierscieniowa w ktorej przyjaźnimy się tylko z sasiadami na okręgu
    elif graphType == "Ring":
        for i in range(0, numberOfAgents):
            if i!= numberOfAgents-1 and i!=1:
                allArrays[0][i] = 0
        for i in range(0, numberOfAgents):
            if i!= numberOfAgents-2 and i!=0:
                allArrays[numberOfAgents-1][i] = 0
        for i in range(1, numberOfAgents-1):
            for j in range(0, numberOfAgents):
                    if j!=i-1 and j!=i+1:
                        allArrays[i][j] = 0
        return allArrays
    #siec z jednym dominujacym agentem ktory przyjaźni się ze wszystkimi a reszta przyjaźni jest losowa
    elif graphType == "CentralDomination":
        #losujemy ktory nr agenta bedzie dominowal
        dominantAgent = random.randint(1, numberOfAgents-1)
        for i in range(0, numberOfAgents):
            if i!= dominantAgent:
                for j in range(0, numberOfAgents):
                    if j !=dominantAgent:
                        if random.uniform(-0.8, 0.2) < 0:
                            allArrays[i][j] = 0 
        return allArrays
    #sieć z zadaną liczbą klastrow
    elif graphType == "Clusters":
        numberOfClusters = 2
        dominantAgents = list(random.sample(range(1, numberOfAgents-1), numberOfClusters))
        for i in range(0, numberOfAgents):
            if i in dominantAgents:
                for j in range(0, numberOfAgents):
                    if random.uniform(-0.1, 0.9) < 0:
                        allArrays[i][j] = 0   
            else:
                for j in range(0, numberOfAgents):
                    if j not in dominantAgents:
                        if random.uniform(-0.95, 0.05) < 0:
                            allArrays[i][j] = 0 
        return allArrays
    #siec z podklastrami polaczonymi z jednym agentem
    elif graphType == "ConnectedClusters":
        dominantAgent = 0
        numberOfSubclusters = 3
        remainingAgents = numberOfAgents - 1
        clusters = list(chunks(range(1, numberOfAgents), math.ceil(remainingAgents/numberOfSubclusters)))
        clusters = [list(clusters[x]) for x in range(len(clusters))]
        #pierwszy agent z każdego klastra będzie przekazywał informacje głownemu agentowi
        informators = [clusters[x][0] for x in range(len(clusters))]
        print(clusters)
        print(informators)
        #tworzymy sieć zupełną w obrębie klastra
        for i in range(0, len(clusters)):
            sizeOfCluster = len(clusters[i])
            for j in range(0, sizeOfCluster):
                curentNum = clusters[i][j]
                for z in range(0, numberOfAgents):
                    if z not in clusters[i]:
                        allArrays[curentNum][z] = 0
        #tworzymy połączenia od informatora do głownego agenta
        for i in range(0, numberOfAgents):
            if i in informators:
                allArrays[i][0] = random.uniform(0, strMax/2)                
        #tworzymy połączenia dla głownego agenta                        
        for i in range(0, numberOfAgents):
            if i not in informators:
                allArrays[0][i] = 0
        return allArrays
    #linia prosta z oddziaływaniem miedzy sąsiadami
    elif graphType == "Line":
        for i in range(0, numberOfAgents):
            for j in range(0, numberOfAgents):
                if j!=i+1 and j!=i-1:
                    allArrays[i][j] = 0
        return allArrays
    #siec bezskalowa
    elif graphType == "ScaleFree":
        #najpierw zerujemy siec, bo ta siec lepiej generowac z pustej
        allArrays = [[0 for i in range(0, numberOfAgents)] for x in range(numberOfAgents)]
        G = nx.scale_free_graph(numberOfAgents)
        edges = list(G.edges())
        for i in range(0, len(edges)):
            allArrays[edges[i][0]][edges[i][1]] = random.uniform(strMin, strMax)
        return allArrays
    
if __name__ == "__main__":
    
    network = generate_graph(5, "FullNet")
    print("FullNet: " + chr(10) + str(network))
    print("=======================================")
    
    network = generate_graph(5, "SmallWorldSymetric")
    print("SmallWorldSymetric: " + chr(10) + str(network))
    print("=======================================")
    
    network = generate_graph(5, "SmallWorldAsymetric")
    print("SmallWorldAsymetric: " + chr(10) + str(network))
    print("=======================================")
    
    network = generate_graph(5, "Ring")
    print("Ring: " + chr(10) + str(network))
    print("=======================================")
        
    network = generate_graph(5, "CentralDomination")
    print("CentralDomination: " + chr(10) + str(network))
    print("=======================================")
    
    network = generate_graph(10, "Clusters")
    print("Clusters: " + chr(10) + str(network))
    print("=======================================")
    
    network = generate_graph(10, "ConnectedClusters")
    print("ConnectedClusters: " + chr(10) + str(network))
    print("=======================================")
    
    network = generate_graph(10, "Line")
    print("Line: " + chr(10) + str(network))
    print("=======================================")

    
    network = generate_graph(10, "ScaleFree")
    print("ScaleFree: " + chr(10) + str(network))
    print("=======================================")