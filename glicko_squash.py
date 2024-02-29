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

#load files 
def load_data(fname):
    matches = pd.read_csv(fname)
    #sort this dataframe based on column date_time
    matches = matches.sort_values(by=['date_time'])

    #filter


    return matches

def evaluateData(matches,p_ids):

    df = pd.DataFrame()
    player_ratings = {}
    for ind,row in tqdm(matches.iterrows(), total=len(matches), desc="Processing matches"):
        p1_id = row["usr_id"]
        p2_id = row["oppnt_id"]
            
        for player_id in [p1_id, p2_id]:
            if player_id not in player_ratings:
                player_ratings[player_id] = {"Rating": 1500, "RD": 200}
        
        p1_rating = player_ratings[p1_id]['Rating']
        p1_rd = player_ratings[p1_id]['RD']
        p2_rating = player_ratings[p2_id]['Rating']
        p2_rd = player_ratings[p2_id]['RD']
        
        #setting up Winner
        p1 = Player()
        p1.setRating(player_ratings[p1_id]['Rating'])
        p1.setRd(    player_ratings[p1_id]['RD'])
        
        #Setting up Loser
        p2 = Player()
        p2.setRating(player_ratings[p2_id]['Rating'])
        p2.setRd(player_ratings[p2_id]['RD'])
        
        if row['result']=='W':
            oc = 1
        elif row['result']=='L':
            oc = 0
        else:
            oc = 0.5

        p1.update_player([p2_rating],[p2_rd],[oc])
        p2.update_player([p1_rating],[p1_rd],[1-oc])
        
        player_ratings[p1_id]['Rating'] = p1.getRating()
        player_ratings[p1_id]['RD'] = p1.getRd()
        player_ratings[p2_id]['Rating'] = p2.getRating()
        player_ratings[p2_id]['RD'] = p2.getRd()


        if row['usr_id'] in p_ids:
            #append to df with columns: player updated rating, prediction, player_id,tourney_date 
            df = df.append({'player_id':row['usr_id'], 'player_rating': player_ratings[p1_id]['Rating'], 'tourney_date': row['date_time']}, ignore_index=True)

        if row['oppnt_id'] in p_ids:
            #append to df with columns: player updated rating, prediction, player_id,tourney_date 
            df = df.append({'player_id':row['oppnt_id'],  'player_rating': player_ratings[p2_id]['Rating'], 'tourney_date': row['date_time']}, ignore_index=True)

    return df

def display_results(dataset):
    df = dataset
    grouped = df.groupby('player_id')

    for player_name, group_df in grouped:
        plt.plot( group_df['player_rating'], label=f'Player {player_name}')

    # Add labels and title
    plt.xlabel('Ranking with matches')
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
        print("Glicko needs input. Please input list through a json file.")
        exit(1)

    preds = evaluateData(dataset,input_set)
    display_results(preds)
