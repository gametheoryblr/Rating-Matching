# system imports 
import sys
# library imports 
import os
import pandas as pd 
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
from datetime import datetime
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import json
from tqdm import tqdm

from src.util.arparse import parseArguments
from plotter import PlotEngine


# codebase imports 
from src.Glicko2.glicko2 import Player

def time_parser(dt):
    dt = int(dt)
    dttime = [dt/10000,(dt%10000)/100,dt%100,0,0]
    timestamp = dttime[0]*100000000 + int(100*dttime[1]/12)*1000000 + int(100*dttime[2]/31)*10000 + int(100*dttime[3]/24)*100 + int(100*dttime[4]/60)
    return timestamp

#load files 
def load_data(fname,stdt=0,enddt=99999999):
    matches = pd.read_csv(fname)
    # filter dataset 
    matches = matches[matches["tourney_date"]>=stdt]
    matches = matches[matches["tourney_date"]<=enddt]
    matches["timestamp"] = matches.apply(lambda row: time_parser(row['tourney_date']),axis=1)
    matches.sort_values(by=["timestamp"],inplace=True)
    return matches 

def evaluateData(matches,opFname,p_ids):

    df = pd.DataFrame()
    player_ratings = {}
    plerr = {}
    prat = {}
    for ind,row in matches.iterrows():# tqdm(matches.iterrows(), total=len(matches), desc="Processing matches"):
        winner_id = row["winner_name"]
        loser_id = row["loser_name"]
            
        for player_id in [winner_id, loser_id]:
            if player_id not in player_ratings:
                player_ratings[player_id] = {"Rating": 1500, "RD": 200}
            if player_id not in prat.keys():
                prat[player_id] = {}
                plerr[player_id] = {} 
        
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
        
        # convert time to desired format here 
        timestamp = row['timestamp']
        while timestamp in prat[loser_id].keys() or timestamp in prat[winner_id].keys():
            timestamp += 1
        
        player_ratings[winner_id]['Rating'] = winner.getRating()
        prat[winner_id][timestamp] = winner.getRating()
        player_ratings[winner_id]['RD'] = winner.getRd()
        player_ratings[loser_id]['Rating'] = loser.getRating()
        prat[loser_id][timestamp] = loser.getRating()
        player_ratings[loser_id]['RD'] = loser.getRd()

        if w_rating> l_rating:
            err = 0
        else:
            err = 1

        if row['winner_name'] in p_ids:
            #append to df with columns: player updated rating, prediction, player_id,tourney_date 
            df = pd.concat([df,pd.DataFrame([{'player_name':row['winner_name'], 'player_rating': player_ratings[winner_id]['Rating'], 'prediction': err, 'tourney_date': row['tourney_date']}])],ignore_index=True)
            # df = df.append({'player_name':row['winner_name'], 'player_rating': player_ratings[winner_id]['Rating'], 'prediction': err, 'tourney_date': row['tourney_date']}, ignore_index=True)

        if row['loser_name'] in p_ids:
            #append to df with columns: player updated rating, prediction, player_id,tourney_date 
            df = pd.concat([df,pd.DataFrame([{'player_name':row['loser_name'],  'player_rating': player_ratings[loser_id]['Rating'], 'prediction': err, 'tourney_date': row['tourney_date']}])],ignore_index=True)
            # df = df.append({'player_name':row['loser_name'],  'player_rating': player_ratings[loser_id]['Rating'], 'prediction': err, 'tourney_date': row['tourney_date']}, ignore_index=True)

    masterdict = {
        'rating':prat,
        'error':plerr
    } 
    print('Prat',prat)
    print('Master dict',masterdict)
    with open(opFname,'w') as fp:
        json.dump(masterdict,fp)

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
    
    arguments = parseArguments(sys.argv)
    plotter = PlotEngine(arguments.display,arguments.plot_path)

    stdt = arguments.startTime
    endt = arguments.endTime 
    subFilter = None 
    if arguments.input != None:
        with open(arguments.input,'r') as fp:
            subFilter = json.load(fp)['inputs']

    if arguments.train == 1:
        dataset = load_data(arguments.dataset,stdt,endt)
        preds = evaluateData(dataset,arguments.output,subFilter)
    plotter.load_data(arguments.output)
    plotter.plot_ratings(subFilter,arguments.percentage)
