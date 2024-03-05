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
import re

# codebase imports 
from src.Glicko2.glicko2 import Player
from src.util.squash.score_sigmoid import score_sigmoid
# from src.util.squash.date_parser import date_parser

from src.util.arparse import parseArguments
from plotter import PlotEngine


def time_parser(dt:str):
    dttime = [int(i) for i in re.split('[ _ \- : ]',dt)]
    timestamp = dttime[0]*100000000 + int(100*dttime[1]/12)*1000000 + int(100*dttime[2]/(30 + dttime[1]%12))*10000 + int(100*dttime[3]/24)*100 + int(100*dttime[4]/60)
    return timestamp



#load files 
def load_data(fname,stdt=0,enddt=99999999):
    matches = pd.read_csv(fname)
    matches["timestamp"] = matches.apply(lambda row: time_parser(row['date_time']),axis=1)
    matches.sort_values(by=["timestamp"])
    # for ind,row in matches.iterrows():
    #     matches.at[ind,'date_time'] = int(date_parser(row['date_time']))
    #sort this dataframe based on column date_time
    #filter matches such that result column is not equal to 'D'
    matches = matches[matches['result']!='D']
    print(matches[matches['usr_id']==4145].to_json())

    return matches


def evaluateData(matches,fname,p_ids):
    # print(matches.shape)
    # #print first few entries in the date_time column of matches
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
        
        timestamp = int(row['timestamp'])
        while timestamp in prat[p1_id].keys() or timestamp in prat[p2_id].keys():
            timestamp += 1
        if p1_id == 4145 or p2_id == 4145:
            print(timestamp)
        p1.update_player([p2_rating],[p2_rd],[oc])
        p2.update_player([p1_rating],[p1_rd],[1-oc])
        player_ratings[p1_id]['Rating'] = p1.getRating()
        prat[p1_id][timestamp] = p1.getRating()
        player_ratings[p1_id]['RD'] = p1.getRd()
        player_ratings[p2_id]['Rating'] = p2.getRating()
        prat[p2_id][timestamp] = p2.getRating()
        player_ratings[p2_id]['RD'] = p2.getRd()
        

    print('Count : ',count)
    masterdict = {
        'rating':prat,
        'error':plerr
    }
    with open(fname,'w') as fp:
        json.dump(masterdict,fp)

    # Concatenate all dataframes in the list


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
    plotter.load_data(arguments.output,'glicko')
    plotter.plot_ratings(subFilter,arguments.percentage)

