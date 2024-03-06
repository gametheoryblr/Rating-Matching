import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import csv
import json
import ast
from constants import THRESHOLD_MATCHES_BETWEEN_TWO_PLAYERS

df = pd.read_csv("../../../data/badminton_dataset_doubles.csv")
dict = {}

#print(ast.literal_eval(df['opponent'][0])[0])
for _, row in df.iterrows():
    id1_1 = row['user_id']
    id1_2 = row['partner']
    id2_1 = ast.literal_eval(row['opponent'])[0]
    id2_2 = ast.literal_eval(row['opponent'])[1]
    ID_string_1 = str(min(id1_1, id1_2)) + "," + str(max(id1_1, id1_2))
    ID_string_2 = str(min(id2_1, id2_2)) + "," + str(max(id2_1, id2_2))
    ID_string_3 = str(min(id1_1, id2_1)) + "," + str(max(id1_1, id2_1))
    ID_string_4 = str(min(id1_1, id2_2)) + "," + str(max(id1_1, id2_2))
    ID_string_5 = str(min(id1_2, id2_1)) + "," + str(max(id1_2, id2_1))
    ID_string_6 = str(min(id1_2, id2_2)) + "," + str(max(id1_2, id2_2))
    ID_strings = [ID_string_1, ID_string_2, ID_string_3, ID_string_4, ID_string_5, ID_string_6]
    for ID_string in ID_strings:
        if ID_string not in dict:
            dict[ID_string] = {"min": ID_string.split(",")[0], "max": ID_string.split(",")[1], "weight": 1}
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
    
df.to_csv("cluster_doubles.csv")
# save player_ratings in a json

with open('player_matches_doubles.json', 'w') as fp:
    json.dump(player_matches, fp)

# nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=3, edge_color='black', linewidths=0.2, font_size=1)
#plt.savefig('filename.png', dpi=3000)
#plt.show()

