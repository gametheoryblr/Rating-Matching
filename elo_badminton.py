import ast 
import sys
import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from plotter import PlotEngine
import json 
import re 

from src.util.squash.rating import Squash
from src.v1.rating_elo.elo import Elo
from src.util.arparse import parseArguments

def parse_score(score:str):
    return json.loads(score)

def time_parser(dt:str):
    # print('Date is',dt)
    dttime = [int(i) for i in re.split('[ _ \- : ]',dt)]
    timestamp = dttime[0]*100000000 + int(100*dttime[1]/12)*1000000 + int(100*dttime[2]/31)*10000 + int(100*dttime[3]/24)*100 + int(100*dttime[4]/60)
    return timestamp

def clean_data(filename:str,stdt=0,enddt=99999999):
    matches = pd.read_csv(filename)
    matches = matches.dropna()
    matches = matches[matches['result']!='D']
    matches["timestamp"] = matches.apply(lambda row: time_parser(row['date_time']),axis=1)
    matches.sort_values(by=["timestamp"],inplace=True)
    stdt *= 10000
    enddt *= 10000
    matches = matches[matches["timestamp"]<=enddt]
    matches.sort_values(by=["timestamp"],inplace=True)
    # print(matches[matches['usr_id']==4145].to_json())
    # Cleaning the data.... 
    '''
        Required Params:
                - usr_id
                - date_time (for temporal k)
                - result 
                - score 
                - sets-won
                - cntr_id (for clustering)
                - oppnt_id
                - user_id
                - opponent 
                - centre_id
    '''
    # matches_dropset = ['match_id',
    #     'centre_user_verified', 'centre_verified', 'created', 'match_type', 'sport', 'status', 'team',
    #     'user_opponent_verified', 'user_verified', 'verified', 'booking_id']
    # try:
    #     matches.drop(matches_dropset,inplace=True,axis=1)
    # except Exception as e:
    #     print("Keys not found")

    # check if identifier is unique (can be used as primary key)
    # primary_keys = []
    # for k in matches.keys():
    #     if matches[k].is_unique:
    #             primary_keys.append(k)
    # print('All keys', matches.keys())
    # print('Primary keys',primary_keys)
    return matches
    
def get_rating(score:list,result='W'):
    score = [score] # just for badminton dataset because data is from one set and of the form [] not [[]] 
    score_p0 = 0
    score_p1 = 0
    w0 = 0 
    w1 = 0
    winning_bonus = 0.5
    multiplication_factor = (1 - winning_bonus)/len(score)
    for st in score:
        if st[0] > st[1]:
            w0 += 1
            score_p0 += multiplication_factor*st[0]/(st[0] + st[1])
            score_p1 += multiplication_factor*st[1]/(st[0] + st[1])
        else:
            score_p1 = multiplication_factor*st[1]/(st[0] + st[1])
            score_p0 = multiplication_factor*st[0]/(st[0] + st[1])
    if w0 > w1:
        score_p0 += winning_bonus
    else:
        score_p1 += winning_bonus
    sscore = score_p0 + score_p1
    score_p0 = score_p0 /sscore
    score_p1 = score_p1/sscore
    return (score_p0,score_p1)


def evaluateData(dataset,filename,begin_date=0,end_date=99999999):
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
    i = 0
    for idx, mtch in dataset.iterrows():
        pdone = int(100*i/dataset.shape[0])
        print('\r[',pdone*'=',(100-pdone)*'-',']',pdone,'\%',sep='',end='')
        i += 1
        # mtch = dataset.loc[i]
        player1 = mtch['user_id']
        player2 = mtch['partner']
        opponent1 = ast.literal_eval(mtch['opponent'])[0]
        opponent2 = ast.literal_eval(mtch['opponent'])[1]
        # print(player1,player2,opponent1,opponent2)
        if player1 not in players.keys():
            players[player1] = Squash(player1,player1)
            prat[str(player1)] = {}
            plerr[str(player1)] = {}
        if player2 not in players.keys():
            players[player2] = Squash(player2,player2)
            prat[str(player2)] = {}
            plerr[str(player2)] = {}
        if opponent1 not in players.keys():
            players[opponent1] = Squash(opponent1,opponent1)
            prat[str(opponent1)] = {}
            plerr[str(opponent1)] = {}
        if opponent2 not in players.keys():
            players[opponent2] = Squash(opponent2,opponent2)
            prat[str(opponent2)] = {}
            plerr[str(opponent2)] = {}
        
        # difference in timing...
        timestamp = int(mtch['timestamp'])
        while timestamp in prat[str(opponent1)].keys() or timestamp in prat[str(opponent2)].keys() or timestamp in prat[str(player1)].keys() or timestamp in prat[str(player2)].keys():
            timestamp += 1
        
        #TODO:@Varul add date parser here (for datewise stuff)
        if players[player1].last_match == -1:
            players[player1].last_match = timestamp
        if players[player2].last_match == -1:
            players[player2].last_match = timestamp
        if players[opponent1].last_match == -1:
            players[opponent1].last_match = timestamp
        if players[opponent2].last_match == -1:
            players[opponent2].last_match = timestamp

        # This difference in time from last match will be passed as the argument to update the score...
        # 1 is added to keep the value of k_loser/k_winner >= 0
        k_winner = abs(timestamp - (players[player1].last_match + players[player2].last_match)/2 + 1)
        k_loser = abs(timestamp - (players[opponent1].last_match + players[opponent2].last_match)/2 + 1)
        
        players[opponent1].updateTime(timestamp)
        players[opponent2].updateTime(timestamp)
        players[player1].updateTime(timestamp)
        players[player2].updateTime(timestamp)
        delta = ((players[player1].rating + players[player2].rating) - (players[opponent1].rating + players[opponent2].rating))/2
        # predict result of the match 
        pred = eloObj.predict(delta) 
        match_ratings = get_rating(parse_score(mtch['score']))
        
        winner_stat = max(match_ratings[0],match_ratings[1]) #max(match_ratings[0],match_ratings[1])/(float(match_ratings[0]) + match_ratings[1])
        loser_stat = min(match_ratings[0],match_ratings[1]) # 1 - winner_stat
        
        #UPDATE SCORES HERE 
        # if mtch['result'] == 'W':
        #     plerr[str(mtch['oppnt_id'])][timestamp] = (abs(pred - match_ratings[1]))        # loss for opponent
        #     plerr[str(mtch['usr_id'])][timestamp] = (abs(1 - pred - match_ratings[0]))  # loss for winner 
        # else: 
        #     plerr[str(mtch['oppnt_id'])][timestamp] = (abs(pred - match_ratings[1]))        # loss for opponent
        #     plerr[str(mtch['usr_id'])][timestamp] = (abs(1 - pred - match_ratings[0]))  # loss for winner 
        # prev_rating = players[mtch['usr_id']].rating 
        if match_ratings[0] > match_ratings[1]: # mtch['result'] == 'W':
            players[player1].rating = eloObj.elo_rate(players[player1].rating,-1*delta,winner_stat,k_winner)
            players[player1].wins +=1 
            players[player2].rating = eloObj.elo_rate(players[player2].rating,-1*delta,winner_stat,k_winner)
            players[player2].wins +=1 
            
            players[opponent1].rating = eloObj.elo_rate(players[opponent1].rating,delta,loser_stat,k_loser)
            players[opponent1].lose += 1
            players[opponent2].rating = eloObj.elo_rate(players[opponent2].rating,delta,loser_stat,k_loser)
            players[opponent2].lose += 1
        else:
            players[opponent1].rating = eloObj.elo_rate(players[opponent1].rating,delta,winner_stat,k_winner)
            players[opponent1].wins +=1 
            players[opponent2].rating = eloObj.elo_rate(players[opponent2].rating,delta,winner_stat,k_winner)
            players[opponent2].wins +=1 
            
            players[player1].rating = eloObj.elo_rate(players[player1].rating,-1*delta,loser_stat,k_loser)
            players[player1].lose += 1
            players[player2].rating = eloObj.elo_rate(players[player2].rating,-1*delta,loser_stat,k_loser)
            players[player2].lose += 1

        
        prat[str(opponent1)][timestamp]  = players[opponent1].rating
        prat[str(opponent2)][timestamp]  = players[opponent2].rating
        prat[str(player1)][timestamp]  = players[player1].rating
        prat[str(player2)][timestamp]  = players[player2].rating
        
    print()
    print('Done training on data')    
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
        evaluateData(dataset,arguments.output,stdt,endt)
    if arguments.display != None:
        plotter.load_data(arguments.output,'elo')
        plotter.plot_ratings(subFilter,arguments.percentage)
