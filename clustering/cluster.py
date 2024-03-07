import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import csv
import json
from constants import THRESHOLD_MATCHES_BETWEEN_TWO_PLAYERS

df = pd.read_csv("../dataset/squash_dataset_expanded.csv")
dict = {}

for _, row in df.iterrows():
    id1 = row['usr_id']
    id2 = row['oppnt_id']
    minID = min(id1, id2)
    maxID = max(id1, id2)
    ID_string = str(minID) + "," + str(maxID)
    if ID_string not in dict:
        dict[ID_string] = {"min": str(minID), "max": str(maxID), "weight": 1}
    else:
        dict[ID_string]["weight"] += 1


dataset=[]
player_matches={}
for key, value in dict.items():
    if(value["weight"] < THRESHOLD_MATCHES_BETWEEN_TWO_PLAYERS):
        continue
    dataset.append((value["min"], value["max"], {'weight': value["weight"]}))
    if value["min"] not in player_matches:
        player_matches[value["min"]] = 0
    if value["max"] not in player_matches:
        player_matches[value["max"]] = 0
    player_matches[value["min"]] += value["weight"]
    player_matches[value["max"]] += value["weight"]

G = nx.Graph()
G.add_edges_from(dataset)
print("Total number of clusters: ",nx.number_connected_components(G))
# print(list(nx.connected_components(G)))
pos = nx.spring_layout(G, weight='weight')

#make a dataframe where each row depicts a cluster:
df = pd.DataFrame( columns=["total_nodes","total_matches","nodes"])
clusters = list(nx.connected_components(G))

for cluster in clusters:
    matches = 0
    for player in cluster:
        matches+=player_matches[player]

    df.loc[len(df)] = {"total_nodes":len(cluster),"total_matches":matches/2,"nodes":cluster}
    
df.to_csv("cluster.csv")
# save player_ratings in a json

with open('player_matches.json', 'w') as fp:
    json.dump(player_matches, fp)

nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=3, edge_color='black', linewidths=0.2, font_size=1)
#plt.savefig('filename.png', dpi=3000)
plt.show()

