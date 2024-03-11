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

# codebase imports 
from src.Glicko2.glicko2 import Player
from src.util.squash.score_sigmoid import score_sigmoid
from src.util.squash.date_parser import date_parser

from src.util.arparse import parseArguments
from plotter import PlotEngine


#load files 
def load_data(fname,stdt=0,enddt=99999999):
    matches = pd.read_csv(fname)
    for ind,row in matches.iterrows():
        matches.at[ind,'date_time'] = int(date_parser(row['date_time']))
        
    #sort this dataframe based on column date_time
    matches = matches.sort_values(by='date_time')
    #filter matches such that result column is not equal to 'D'
    matches = matches[matches['result']!='D']

    return matches

def date_to_timestamp(date:str): 
    date = date.split('_')[0].split('-')
    yr = int(date[0])
    month = int(date[1])
    day = int(date[0])
    time_score = (yr - 1950)*365 + (month-1)*30 + day
    timestamp = yr*10000 + int(month/12*100)*100 + int(day/(30 + month%2)*100)
    return time_score, timestamp



def evaluateData(matches,fname,p_ids):
    # print(matches.shape)
    # #print first few entries in the date_time column of matches
    dfs_to_concat = []
    df = pd.DataFrame()
    prat = {} 
    plerr = {} 
    player_ratings = {}
    count = 0
    print('Dataset size',len(matches))
    for ind,row in tqdm(matches.iterrows(), total=len(matches), desc="Processing matches"):
        p1_id = row["usr_id"]
        p2_id = row["oppnt_id"]
        if 3300 in [p1_id,p2_id]:
            count += 1
        scoreline = row['score']    
        for player_id in [p1_id, p2_id]:
            if player_id not in player_ratings:
                player_ratings[player_id] = {"Rating": 1500, "RD": 200}
            if player_id not in prat.keys():
                prat[player_id] = {} 
                plerr[player_id] = {} 
        
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
        tst = row['date_time']/10000
        # print(row['date_time'],type(row['date_time']))
        yr = int(tst/10000)
        mth = int((tst%10000)/100)
        day = int(tst%100)
        ttime = row['date_time']%10000
        timestamp = yr*100000000 + int(100*(mth/12))*1000000 + int(100*(day/(30+mth%2)))*10000 + ttime
        print(timestamp)
        
        p1.update_player([p2_rating],[p2_rd],[oc])
        p2.update_player([p1_rating],[p1_rd],[1-oc])
        
        player_ratings[p1_id]['Rating'] = p1.getRating()
        prat[p1_id][timestamp] = p1.getRating()
        player_ratings[p1_id]['RD'] = p1.getRd()
        player_ratings[p2_id]['Rating'] = p2.getRating()
        prat[p2_id][timestamp] = p2.getRating()
        player_ratings[p2_id]['RD'] = p2.getRd()
        
        if True: # don't need filtration here..
            # Create a dataframe with the required data
            player_df = pd.DataFrame({'player_id': [row['usr_id']], 'player_rating': [player_ratings[row['usr_id']]['Rating']], 'tourney_date': [row['date_time']]})
            # Append the dataframe to the list
            dfs_to_concat.append(player_df)

        if True: # don't need filtration here...
            # Create a dataframe with the required data
            player_df = pd.DataFrame({'player_id': [row['oppnt_id']], 'player_rating': [player_ratings[row['oppnt_id']]['Rating']], 'tourney_date': [row['date_time']]})
            # Append the dataframe to the list
            dfs_to_concat.append(player_df)

    print('Count : ',count)
    masterdict = {
        'rating':prat,
        'error':plerr
    }
    with open(fname,'w') as fp:
        json.dump(masterdict,fp)

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

