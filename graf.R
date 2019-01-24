#miejsce umieszczenia skryptu R
setwd("C://Users//Evangelista//Desktop//pytong//magisterka//v1")

#wymagane biblioteki
require(visNetwork)
require(dplyr)
require(shiny)
require(magrittr)

#ladowanie krawedzi i wezlow
graf.info = read.csv("krok0Wezly.csv")
id <- rownames(graf.info)
graf.info <- (cbind(id=id, graf.info))
graf.powiazania = read.csv("krok0Krawedzie.csv")

#tworzenie wezlow
visNetworkNodes <- data.frame(graf.info) %>%
  mutate(id=graf.info$nazwa_agenta,
         label = graf.info$nazwa_agenta,
         title = graf.info$nazwa_agenta,
         font.size = 50)

#tworzenie krawedzi
visNetworkLinks <- data.frame(from = graf.powiazania$From,
                              to = graf.powiazania$To,
                              width = 5,
                              arrows = list(to = list(enabled = TRUE, scaleFactor = 1)))

#tworzenie sieci
net <- visNetwork(nodes = visNetworkNodes,
                  edges = visNetworkLinks,
                  height = "600px",
                  width = "800px") %>%
  visOptions(highlightNearest = TRUE) %>%
  visEvents(stabilizationIterationsDone = "function() {this.setOptions({physics : true});}") %>%
  visPhysics(solver = 'forceAtlas2Based', forceAtlas2Based = list(gravitationalConstant = -500, avoidOverlap = 1, damping = 1), minVelocity = 20) %>%
  visLayout(randomSeed = 2)

#wyswietlanie sieci w podgladzie
net 

#zapisywanie sieci jako htmla
visSave(net, file = "network.html")