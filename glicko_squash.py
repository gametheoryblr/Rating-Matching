# system imports 
import sys

# library imports 
import os
import pandas as pd 
import matplotlib.pyplot as plt
import json
from datetime import datetime
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import json
from tqdm import tqdm

# codebase imports 
from src.Glicko2.glicko2 import Player
from src.util.squash.score_sigmoid import score_sigmoid
from src.util.squash.date_parser import date_parser

#load files 
def load_data(fname):
    matches = pd.read_csv(fname)
    for ind,row in matches.iterrows():
        matches.at[ind,'date_time'] = int(date_parser(row['date_time']))
        
    #sort this dataframe based on column date_time
    matches = matches.sort_values(by='date_time')
    #filter matches such that result column is not equal to 'D'
    matches = matches[matches['result']!='D']

    return matches

def evaluateData(matches,p_ids):
    # print(matches.shape)
    # #print first few entries in the date_time column of matches
    dfs_to_concat = []
    df = pd.DataFrame()
    player_ratings = {}
    for ind,row in tqdm(matches.iterrows(), total=len(matches), desc="Processing matches"):
        p1_id = row["usr_id"]
        p2_id = row["oppnt_id"]
        scoreline = row['score']    
        for player_id in [p1_id, p2_id]:
            if player_id not in player_ratings:
                player_ratings[player_id] = {"Rating": 1500, "RD": 200}
        
        p1_rating = player_ratings[p1_id]['Rating']
        p1_rd = player_ratings[p1_id]['RD']
        p2_rating = player_ratings[p2_id]['Rating']
        p2_rd = player_ratings[p2_id]['RD']
        
        #setting up p1
        p1 = Player()
        p1.setRating(player_ratings[p1_id]['Rating'])
        p1.setRd(    player_ratings[p1_id]['RD'])
        
        #Setting up p2
        p2 = Player()
        p2.setRating(player_ratings[p2_id]['Rating'])
        p2.setRd(player_ratings[p2_id]['RD'])
        
        oc1,oc2 = score_sigmoid(scoreline) 
        if row['result']=='W':
            oc = max(oc1,oc2)
        elif row['result']=='L':
            oc = min(oc1,oc2)
        else:
            oc = 0.5

        p1.update_player([p2_rating],[p2_rd],[oc])
        p2.update_player([p1_rating],[p1_rd],[1-oc])
        
        player_ratings[p1_id]['Rating'] = p1.getRating()
        player_ratings[p1_id]['RD'] = p1.getRd()
        player_ratings[p2_id]['Rating'] = p2.getRating()
        player_ratings[p2_id]['RD'] = p2.getRd()


        if row['usr_id'] in p_ids:
            # Create a dataframe with the required data
            player_df = pd.DataFrame({'player_id': [row['usr_id']], 'player_rating': [player_ratings[row['usr_id']]['Rating']], 'tourney_date': [row['date_time']]})
            # Append the dataframe to the list
            dfs_to_concat.append(player_df)

        if row['oppnt_id'] in p_ids:
            # Create a dataframe with the required data
            player_df = pd.DataFrame({'player_id': [row['oppnt_id']], 'player_rating': [player_ratings[row['oppnt_id']]['Rating']], 'tourney_date': [row['date_time']]})
            # Append the dataframe to the list
            dfs_to_concat.append(player_df)

    # Concatenate all dataframes in the list
    if dfs_to_concat:
        df = pd.concat(dfs_to_concat, ignore_index=True)
        return df

def display_results(dataset):
    df = dataset
    grouped = df.groupby('player_id')

    for player_name, group_df in grouped:
        plt.plot( group_df['tourney_date'],group_df['player_rating'], label=f'Player {player_name}')

    # Add labels and title
    plt.xlabel('Ranking with date')
    plt.ylabel('Player Rating')
    plt.title('Player Rating Over Time')
    plt.legend()  # Add legend to distinguish between player IDs

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=90)
    
    output_dir = 'outputs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    curr_time = datetime.now().strftime('%Y_%b_%d_%H_%M_%S')
    plt.savefig(os.path.join(output_dir, f'player_ratings_over_time_squash{curr_time}.png'))

    # Show the plot
    plt.tight_layout()  # Adjust layout to prevent overlapping labels
    plt.show()

if __name__ == '__main__':
    # fname = input('Enter Dataset Filename')
    fname = sys.argv[1]
    dformat = sys.argv[2]
    assert(dformat in ['datewise','matchwise'])
    dataset = load_data(fname)
    if len(sys.argv) == 4: # input file 
        try:
            input_set = json.load(open(sys.argv[3],'r'))['input']
        except Exception as e:
            print('Error: Invalid file or input format. Please input list through a json file.')
            print(e)
            exit(1)   
    else:
        print("Glicko needs input file. Please input list through a json file.")
        exit(1)

    preds = evaluateData(dataset,input_set)
    display_results(preds)
