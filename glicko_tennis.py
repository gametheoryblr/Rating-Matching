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
    # filter dataset 
    matches = matches[['tourney_id', 'tourney_name', 'surface', 'draw_size', 'tourney_level', 'tourney_date', 'match_num', 'winner_id', 'winner_name','loser_id', 'loser_name', 'score', 'best_of', 'round']]
    # filter dataframe where tourney_date is between 2014 and 2016
    matches = matches[matches["tourney_date"]>=20150000]
    matches = matches[matches["tourney_date"]<=20160000]
    return matches

def evaluateData(matches,p_ids):

    df = pd.DataFrame()
    player_ratings = {}
    for ind,row in tqdm(matches.iterrows(), total=len(matches), desc="Processing matches"):
        winner_id = row["winner_id"]
        loser_id = row["loser_id"]
            
        for player_id in [winner_id, loser_id]:
            if player_id not in player_ratings:
                player_ratings[player_id] = {"Rating": 1500, "RD": 200}
        
        w_rating = player_ratings[winner_id]['Rating']
        w_rd = player_ratings[winner_id]['RD']
        l_rating = player_ratings[loser_id]['Rating']
        l_rd = player_ratings[loser_id]['RD']
        
        #setting up Winner
        winner = Player()
        winner.setRating(player_ratings[winner_id]['Rating'])
        winner.setRd(player_ratings[winner_id]['RD'])
        
        #Setting up Loser
        loser = Player()
        loser.setRating(player_ratings[loser_id]['Rating'])
        loser.setRd(player_ratings[loser_id]['RD'])
        
        winner.update_player([l_rating],[l_rd],[1])
        loser.update_player([w_rating],[w_rd],[0])
        
        player_ratings[winner_id]['Rating'] = winner.getRating()
        player_ratings[winner_id]['RD'] = winner.getRd()
        player_ratings[loser_id]['Rating'] = loser.getRating()
        player_ratings[loser_id]['RD'] = loser.getRd()

        if w_rating> l_rating:
            err = 0
        else:
            err = 1

        if row['winner_name'] in p_ids:
            #append to df with columns: player updated rating, prediction, player_id,tourney_date 
            df = df.append({'player_name':row['winner_name'], 'player_rating': player_ratings[winner_id]['Rating'], 'prediction': err, 'tourney_date': row['tourney_date']}, ignore_index=True)

        if row['loser_name'] in p_ids:
            #append to df with columns: player updated rating, prediction, player_id,tourney_date 
            df = df.append({'player_name':row['loser_name'],  'player_rating': player_ratings[loser_id]['Rating'], 'prediction': err, 'tourney_date': row['tourney_date']}, ignore_index=True)

    return df

def display_results(dataset):
    df = dataset
    grouped = df.groupby('player_name')

    for player_name, group_df in grouped:
        plt.plot(group_df['tourney_date'], group_df['player_rating'], label=f'Player {player_name}')

    # Add labels and title
    plt.xlabel('Ranking Date')
    plt.ylabel('Player Rating')
    plt.title('Player Rating Over Time')
    plt.legend()  # Add legend to distinguish between player IDs

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=90)
    
    output_dir = 'outputs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    curr_time = datetime.now().strftime('%Y_%b_%d_%H_%M_%S')
    plt.savefig(os.path.join(output_dir, f'player_ratings_over_time_{curr_time}.png'))

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