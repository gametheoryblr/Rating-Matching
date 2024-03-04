import pandas as pd
import json

df = pd.read_csv("cluster.csv")

for ind,row in df.iterrows():
    for node in row["nodes"]:
        strr = row["nodes"].strip('{').strip('}')
        strr = strr.strip("'")
        lst = strr.split(',')
        for i in range(0,len(lst)):
            lst[i]=lst[i].strip(" ").strip("'")
            lst[i] = int(lst[i])
    df.at[ind,"nodes"]=lst

with open('player_matches.json') as f:
    match_counts = json.load(f)

# Function to calculate percentage of players with match counts exceeding a threshold
def calculate_percentage(df_slice, threshold):
    percent_players_played_above_threshold_matches=0
    for ind, row in df_slice.iterrows():
        total_matches = row['total_matches']
        total_players = row["total_nodes"]
        players_above_threshold = 0
        
        for node in row["nodes"]:
            if int(match_counts[str(node)]) >= threshold * total_matches:
                players_above_threshold += 1
                #print(threshold * total_matches,match_counts[str(node)])
        percent_players_played_above_threshold_matches+=100 * players_above_threshold/ total_players
    return percent_players_played_above_threshold_matches/len(df_slice)

cluster_size = 3
#run the below code for cluster size : [2,4],[5,7],[8,10],[11,inf)

thresholds = [0,0.02,0.06,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]
mean_percentages = {}
for threshold in thresholds:
    percentages = []
    percentages.append(calculate_percentage(df[df["total_nodes"]==cluster_size], threshold))  # change for cluster_size
    mean_percentages[threshold] = sum(percentages) / len(percentages)

for threshold, percentage in mean_percentages.items():
    print(f"Percentage of players with more than {threshold*100}% matches: {percentage:.2f}%")
