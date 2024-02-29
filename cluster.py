import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import csv
import json

df = pd.read_csv("dataset/squash_dataset.csv")
filtered_df = df.drop_duplicates(subset=['match_id'])
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
for key, value in dict.items():
    dataset.append((value["min"], value["max"], {'weight': value["weight"]}))

G = nx.Graph()
G.add_edges_from(dataset)

pos = nx.spring_layout(G, weight='weight')
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=3, edge_color='black', linewidths=0.2, font_size=1)
plt.savefig('filename.png', dpi=3000)
plt.show()

