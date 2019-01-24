# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 07:59:24 2019
Simulation of the market based on Ising model. Each step agents place buy or sell order.
Agents are placed on a chosen type of network and their relationships evolve during the simulation.
The results are presented in the form of the price, return and log return plots.
Every 6000 steps network and its weights are saved to a file.
@author: Evangelista
"""


import random 
import numpy
from math import exp, log
import csv
import matplotlib.pyplot as plt
import datetime
import pathlib
import network_generation as ng

def simulate_Simple(numberOfAgents, numberOfSteps, iteracja, time, networkType):
    #tworzenie listy agentow
    agentList = [Agent(numberOfAgents, x) for x in range(numberOfAgents)]
    #tworzenie rynku
    market = Market(numberOfAgents, numberOfAgents)
    #tworzenie newsow
    news = News()
    #tworzymy siec społeczną i nadajemy układowi te znajomosci
    network = ng.generate_graph(numberOfAgents, networkType)
    for i in range(0, len(agentList)):
        agentList[i].sentiments = network[i]
        
    ###symulacja
    for step in range(0, numberOfSteps):
        if step == 0 or step % 6000 == 0 or step == numberOfSteps-1:
            create_graph(agentList, time, step, iteracja, networkType) #tworzy i zrzuca aktualny graf co 100 krokow
        ##pojedynczy krok
        #zbieramy oczekiwania
        expectationsTot = []
        for i in range(0, numberOfAgents):
            expectationsTot.append(agentList[i].successHist[-1]) #działa
        #i dajemy oczekiwania agentom
        for i in range(0, numberOfAgents):
            agentList[i].expectations = expectationsTot
        #nowy news opinion
        if step<2000000:
            news.determine_Market_Opinion(market.returnHist[-1])
        else:
            news.determine_Market_Opinion2(market.priceHist)
        #liczyymy nowe sentymenty
        for i in range(0, numberOfAgents):
            agentList[i].calculate_New_Sentimets(market.returnHist[-1], news.marketLastScore)
        #ustalamy decyzje
        for i in range(0, numberOfAgents):
            agentList[i].make_Decision(news.marketLastScore)
        #zbieramy decyzje
        decisionsTot = []
        for i in range(0, numberOfAgents):
            decisionsTot.append(agentList[i].decisionHist[-1])
        #obliczamy zwrot
        market.calculate_Return(decisionsTot)
        #sprawdzamy czy news miał rację
        news.determine_Score(market.returnHist[-1])
        #obliczamy nową wartosc portfela dla agentow
        for i in range(0, numberOfAgents):
            agentList[i].update_Value(market.returnHist[-1])
    #zapisuje wykresy 
    write_plot(market.returnHist, 'returns', iteracja, time, networkType)
    write_plot(market.priceHist, 'prices', iteracja, time, networkType)
    write_plot(market.logReturns, 'logreturns', iteracja, time, networkType)
    write_values(agentList, iteracja, time, networkType)
    return market.priceHist, market.returnHist, market.logReturns

def write_values(agentList, iteracja, time, networkType):
    pathlib.Path('wyniki/' + str(time) + "-" + str(networkType) + '/PortfolioSymulacjaNr' + str(iteracja)).mkdir(parents=True, exist_ok=True)
    for i in range(0, len(agentList)):
        filename = 'wyniki/' + str(time) + "-" + str(networkType) + '/PortfolioSymulacjaNr' + str(iteracja) + '/AgentNr' + str(agentList[i].index) + 'PortfolioValue.csv'
        with open(filename, 'w') as csvfile:
            fieldnames = ['Iter', 'Value']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            data = agentList[i].portfolioValue
            for i in range(0, len(data)):
                writer.writerow({'Iter': i, 'Value': data[i]})
    
def create_graph(agentList, time, curentStep, iteracja, networkType):
    nodes = []
    edges = []
    pathlib.Path('wyniki/' + str(time) + "-" + str(networkType) + '/GrafySymulacjaNr' + str(iteracja)).mkdir(parents=True, exist_ok=True)
    #wypisujemy wszystkie węzły
    for i in range(0, len(agentList)):
        nodes.append({"nazwa_agenta":agentList[i].name })
        #wypisujemy krawędzie dla danego agenta
        for j in range(0, len(agentList[i].sentiments)):
            edges.append({"From" : agentList[i].name, "To": agentList[j].name, "Value": agentList[i].sentiments[j]})
    #zapisuje węzły
    if curentStep == 0:
        filename = 'wyniki/' + str(time) + "-" + str(networkType) + '/GrafySymulacjaNr' + str(iteracja) + '/krok' + str(curentStep) + 'Wezly.csv'
        with open(filename, 'w') as csvfile:
            fieldnames = ['nazwa_agenta']        
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(0, len(nodes)):
                writer.writerow(nodes[i])
    #zapisuje krawędzie
    filename = 'wyniki/' + str(time) + "-" + str(networkType) + '/GrafySymulacjaNr' + str(iteracja) + '/krok' + str(curentStep) + 'Krawedzie.csv'
    with open(filename, 'w') as csvfile:
        fieldnames = ['From', 'To', 'Value']        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(0, len(edges)):
            if edges[i]["Value"]!=0:
                writer.writerow(edges[i])
            
def write_plot(data, title, iteracja, time, networkType):
    filename = 'wyniki/' + str(time) + "-" + str(networkType) + "/" + str(title) + str(iteracja) + '.csv'
    with open(filename, 'w') as csvfile:
        fieldnames = ['Iter', title]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(0, len(data)):
            writer.writerow({'Iter': i, title: data[i]})


def make_Histogram(returnsDict):
    histogram = [{"x" : 100 * list(returnsDict.keys())[i], "y": list(returnsDict.values())[i]} for i in range(len(returnsDict))]
    return histogram
    
class Agent:
    def __init__(self, numberOfAgents, index):
        '''poczatkowe wartosci dla agentow - tutaj mozna zmieniac parametry, mozna tez przekazywac wartosci jakich chcemy uzyc
        do funkcji glownej i przesylac je do tej klasy - da sie to szybko zrobic
        aktualne parametry są inne niz w moich ostatecznych symulacjach, bo zmienialem je bardzo duzo razy
        '''
        self.index = index
        self.name = "agent_" + str(index)
        self.portfolioValue = [1000000.0]
        self.successHist = [random.choice([-1,1])] #success history with first previous success
        self.sentiments = []
        self.prevSentiments = [random.random() for x in range(numberOfAgents)]
        self.decisionHist = [random.choice([-1,1])]
        self.expectations = []
        #parametry dla agenta
        self.sigma = random.uniform(0.02, 0.06)
        self.b_i = random.uniform(0.01, 0.045)
        self.beta = 0.35
        self.alpha = 0.10
    #new K   
    def calculate_New_Sentimets(self, lastReturn, lastImpact):
        '''zakomentowane jest tutaj wrzucanie do pliku sentymentow i inna wersja generacji b_i'''
        temp = self.sentiments
        for i in range(0, len(self.sentiments)):
            self.b_i = random.uniform(0.01, 0.045)
            if self.sentiments[i] != 0:
                self.sentiments[i] = self.b_i + self.alpha * self.prevSentiments[i] + self.beta * lastReturn * lastImpact
            else:
                self.sentiments[i]  = 0
        self.prevSentiments = temp

    #make decision
    def make_Decision(self, newsPrediction):
        factor = 0
        self.sigma = self.sigma * random.choice([0.95, 1.05])
        self.epsilon = self.sigma * random.choice([0.8, 1.2])
        for i in range(0, len(self.sentiments)):
            if i != self.index:
                factor = factor + (self.sentiments[i] * self.expectations[i])        
        factor = factor + self.sigma * newsPrediction + self.epsilon
        self.decisionHist.append(numpy.sign(factor))
        
    def update_Value(self, lastReturn):
        newVal = lastReturn*self.portfolioValue[-1]
        self.portfolioValue.append(newVal)
        
        
class Market:
    '''klasa market '''
    def __init__(self, numberOfAgents, liquidity):
        self.liquidity = liquidity
        self.numberOfAgents = numberOfAgents
        self.returnHist = [random.uniform(-0.2, 0.2)]
        self.priceHist = [100000.0]
        self.logReturns = []
    def calculate_Return(self, decisions):
        self.returnHist.append(sum(decisions)/(self.liquidity * self.numberOfAgents))
        self.priceHist.append(self.priceHist[-1] * exp(self.returnHist[-1]))
        self.logReturns.append(log(self.priceHist[-1]/self.priceHist[-2]))
        
class News:
    def __init__(self):
        self.marketLastScore = random.choice([-1,1])
        self.marketOpinion = random.choice([-1,1])
    def determine_Market_Opinion (self, lastReturn):
        '''Bierze pod uwagę kierunek ostatniego zwrotu'''
        self.marketOpinion = numpy.sign(lastReturn)
    def determine_Market_Opinion2(self, priceHist):
        '''bierze pod uwagę srednie dlugo i krotkoterminowe'''
        MovMean = numpy.mean(priceHist[(len(priceHist)-50):len(priceHist)])
        MovMeanShort =  numpy.mean(priceHist[(len(priceHist)-10):len(priceHist)])   
        if MovMean>MovMeanShort:
            self.marketOpinion = numpy.sign(-1)
        else:
            self.marketOpinion = numpy.sign(1)
    def determine_Score(self, lastReturn):
        if numpy.sign(lastReturn) == self.marketOpinion:
            self.marketLastScore = 1
        else:
            self.marketLastScore = -1
            
if __name__ == "__main__":
    nets = ["FullNet", "SmallWorldAsymetric", "ScaleFree", "CentralDomination", "Ring"]
    #pętla po sieciach
    for j in range(0, len(nets)):
        time = datetime.datetime.now()
        time = time.strftime("%Y-%m-%d %H-%M")
        for i in range(0, 3):
            #pętla zawierająca kolejne symulacje
            print("==========================================")
            print("NASTEPNA SYMULACJA: " + str(i))
            net = nets[j]
            priceHist = simulate_Simple(10,30, i, time, net)
            plt.figure(i)
            plt.xlabel('step')
            plt.ylabel('price')
            plt.plot(priceHist[0])
            plt.show()
            plt.close()
            try:
                plt.figure(1000+i)
                plt.xlabel('return')
                plt.ylabel('occurrences')
                plt.hist(priceHist[1])
                plt.show()
                plt.close()
                
                plt.figure(2000+i)
                plt.xlabel('log return')
                plt.ylabel('occurrences')
                plt.hist(priceHist[2])
                plt.show()
                plt.close()
            except:
                print("Wartosci za wysokie, zeby wyswietlic")