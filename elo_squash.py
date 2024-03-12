import sys
import pandas as pd
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
from plotter import PlotEngine
import json 
import re 

from src.util.ufuncs import get_rating
from src.util.squash.rating import Squash
from src.v1.rating_elo.elo import Elo
from src.util.arparse import parseArguments

def parse_score(score:str):
    return json.loads(score)

def time_parser(dt:str):
    dttime = [int(i) for i in re.split('[ _ \- : ]',dt)]
    timestamp = dttime[0]*100000000 + int(100*dttime[1]/12)*1000000 + int(100*dttime[2]/31)*10000 + int(100*dttime[3]/24)*100 + int(100*dttime[4]/60)
    return timestamp

def clean_data(filename:str,stdt=0,enddt=99999999):
    matches = pd.read_csv(filename)
    matches = matches[matches['result']!='D']
    matches["timestamp"] = matches.apply(lambda row: time_parser(row['date_time']),axis=1)
    matches.sort_values(by=["timestamp"],inplace=True)
    stdt *= 10000
    enddt *= 10000
    matches = matches[matches["timestamp"]<=enddt]
    matches = matches[matches["timestamp"]>=stdt]
    matches.sort_values(by=["timestamp"],inplace=True)
    return matches
    

def evaluateData(dataset,filename,winner_bonus):
    # Initialize variables 
    players = {}
    prat = {}
    plerr = {}
    eloObj = Elo()
    name_id = {}
    count = 0
    dataset.sort_values(by=["timestamp"],inplace=True)
    
    if arguments.debug:
        print('Dataset Shape',dataset.shape[0])
    for idx, mtch in dataset.iterrows():
        # pdone = int(100*i/dataset.shape[0])
        # print('\r[',pdone*'=',(100-pdone)*'-',']',pdone,'\%',sep='',end='')
        # mtch = dataset.loc[i]
        if mtch['usr_id'] == 72 or mtch['oppnt_id'] == 72:
            print(mtch['timestamp'])
        name_id[mtch['usr_id']] = mtch['usr_id'] # TODO: change this line @Varul 
        if mtch['usr_id'] not in players.keys():
            # graph[int(mtch['usr_id'])] = []
            players[mtch['usr_id']] = Squash(mtch['usr_id'],mtch['usr_id'])
            prat[str(mtch['usr_id'])] = {}
            plerr[str(mtch['usr_id'])] = {}
        if mtch['oppnt_id'] not in players.keys():
            # graph[int(mtch['oppnt_id'])] = []
            players[mtch['oppnt_id']] = Squash(mtch['oppnt_id'],mtch['oppnt_id'])
            prat[str(mtch['oppnt_id'])] = {}
            plerr[str(mtch['oppnt_id'])] = {}

        # difference in timing...
        timestamp = int(mtch['timestamp'])
        while timestamp in prat[str(mtch['oppnt_id'])].keys() or timestamp in prat[str(mtch['usr_id'])].keys():
            timestamp += 1
        
        #TODO:@Varul add date parser here (for datewise stuff)

        if players[mtch['oppnt_id']].last_match == -1:
            players[mtch['oppnt_id']].last_match = timestamp
        if players[mtch['usr_id']].last_match == -1:
            players[mtch['usr_id']].last_match = timestamp

        # This difference in time from last match will be passed as the argument to update the score...
        # 1 is added to keep the value of k_loser/k_winner >= 0
        k_winner = abs(timestamp - players[mtch['usr_id']].last_match + 1)
        k_loser = abs(timestamp - players[mtch['oppnt_id']].last_match + 1)
        
        players[mtch['oppnt_id']].updateTime(timestamp)
        players[mtch['usr_id']].updateTime(timestamp)
        delta = players[mtch['usr_id']].rating - players[mtch['oppnt_id']].rating
        # predict result of the match 
        pred = eloObj.predict(delta) 
        match_ratings = get_rating(parse_score(mtch['score']),winner_bonus)
        
        winner_stat = max(match_ratings[0],match_ratings[1]) #max(match_ratings[0],match_ratings[1])/(float(match_ratings[0]) + match_ratings[1])
        loser_stat = min(match_ratings[0],match_ratings[1]) # 1 - winner_stat
        
        #UPDATE SCORES HERE 
        # if mtch['result'] == 'W':
        #     plerr[str(mtch['oppnt_id'])][timestamp] = (abs(pred - match_ratings[1]))        # loss for opponent
        #     plerr[str(mtch['usr_id'])][timestamp] = (abs(1 - pred - match_ratings[0]))  # loss for winner 
        # else: 
        #     plerr[str(mtch['oppnt_id'])][timestamp] = (abs(pred - match_ratings[1]))        # loss for opponent
        #     plerr[str(mtch['usr_id'])][timestamp] = (abs(1 - pred - match_ratings[0]))  # loss for winner 
        if match_ratings[0] > match_ratings[1]: # mtch['result'] == 'W':
            players[mtch['usr_id']].rating = eloObj.elo_rate(players[mtch['usr_id']].rating,-1*delta,winner_stat,k_winner)
            players[mtch['usr_id']].wins +=1 
            
            players[mtch['oppnt_id']].rating = eloObj.elo_rate(players[mtch['oppnt_id']].rating,delta,loser_stat,k_loser)
            players[mtch['oppnt_id']].lose += 1
        else:
            players[mtch['oppnt_id']].rating = eloObj.elo_rate(players[mtch['oppnt_id']].rating,delta,winner_stat,k_winner)
            players[mtch['oppnt_id']].wins +=1 
            
            players[mtch['usr_id']].rating = eloObj.elo_rate(players[mtch['usr_id']].rating,-1*delta,loser_stat,k_loser)
            players[mtch['usr_id']].lose += 1

        prat[str(mtch['oppnt_id'])][timestamp]  = players[mtch['oppnt_id']].rating
        prat[str(mtch['usr_id'])][timestamp]  = players[mtch['usr_id']].rating
        if mtch['usr_id'] == 3300 or mtch['oppnt_id'] == 3300:
            count += 1
        
        #TODO:Add time-based updates here...
    print()
    print('Done training on data')    
    print('Count : ',count)
    final_dict = {
        'rating':prat,
        'error':plerr
    }
    with open(filename,'w+') as fp:
        json.dump(final_dict,fp)

if __name__ == '__main__':
    arguments = parseArguments(sys.argv)
    plotter = PlotEngine(arguments.display,arguments.plot_path)

    stdt = arguments.startTime
    endt = arguments.endTime
    subFilter = None 
    if arguments.input != None:
        with open(arguments.input,'r') as fp:
            subFilter = json.load(fp)['inputs']
    print(subFilter)
    if arguments.train:
        dataset = clean_data(arguments.dataset)
        evaluateData(dataset,arguments.output,arguments.winner_bonus)
    plotter.load_data(arguments.output,'elo')
    plotter.plot_ratings(subFilter,arguments.percentage)
