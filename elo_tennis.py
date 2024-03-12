#!/usr/bin/python3 

# system imports 
import sys

# library imports 
import pandas as pd 
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
from datetime import datetime
from plotter import PlotEngine

# codebase imports 
from src.util.arparse import parseArguments
from src.util.tennis.rating import Tennis
from src.v1.rating_elo.elo import Elo 
from src.util.ufuncs import get_rating

# time-parser will be different for each dataset 
def time_parser(dt):
    dt = int(dt)
    dttime = [dt/10000,(dt%10000)/100,dt%100,0,0]
    timestamp = dttime[0]*100000000 + int(100*dttime[1]/12)*1000000 + int(100*dttime[2]/31)*10000 + int(100*dttime[3]/24)*100 + int(100*dttime[4]/60)
    return timestamp

def date_parser(date:int):
    yr = date/10000
    month = (date%10000)/100
    day = (date%100)
    time_score = (yr - 1950)*365 + (month-1)*30 + day
    return time_score

def parse_score(score:str):
    sc = []
    for st in score.split(' '):
        sc.append([0,0])
        idx = 0
        for pt in st.split('-'):
            sc[-1][idx] = int(pt)
            idx+=1
    return sc

#load files 
def load_data(fname,stdt=0,enddt=99999999):
    matches = pd.read_csv(fname)
    # filter dataset 
    matches = matches[matches["tourney_date"]>=stdt]
    matches = matches[matches["tourney_date"]<=enddt]
    matches["timestamp"] = matches.apply(lambda row: time_parser(row['tourney_date']),axis=1)
    matches.sort_values(by=["timestamp"],inplace=True)
    return matches 

def evaluateData(dataset,filename,winner_bonus, begin_date=0,end_date=99999999):
    players = {}
    prat = {}
    plerr = {}
    eloObj = Elo()
    name_id = {} # will store meta information 

    # for i in range(dataset.shape[0]):
    for idx,mtch in dataset.iterrows():
        # pdone = int(100*i/dataset.shape[0])
        # print('\r',pdone,end=' ')
        # print('\r[',pdone*'=',(100-pdone)*'-',']',pdone,'\%',sep='',end='')
        # mtch = dataset.loc[i]
        if mtch['tourney_date'] < begin_date or mtch['tourney_date'] > end_date:
            continue
        name_id[mtch['winner_name']] = mtch['winner_id']
        if mtch['winner_name'] not in players.keys():
            players[mtch['winner_name']] = Tennis(mtch['winner_id'],mtch['winner_name'])
            prat[mtch['winner_name']] = {}
            plerr[mtch['winner_name']] = {}
        if mtch['loser_name'] not in players.keys():
            players[mtch['loser_name']] = Tennis(mtch['loser_id'],mtch['loser_name'])
            prat[mtch['loser_name']] = {}
            plerr[mtch['loser_name']] = {}
        
        # difference in timing...
        dscore = date_parser(mtch['tourney_date'])
        # yr = (mtch['tourney_date'])/10000
        # mth = int(((mtch['tourney_date']%10000)/100)*100/12)
        # day = int(((mtch['tourney_date']%100))*100/(30 + (mth%2)))
        # time_st = str(yr*10000 + mth*100 + day)
        time_st = mtch['timestamp']
        if players[mtch['loser_name']].last_match == -1:
            players[mtch['loser_name']].last_match = dscore
        if players[mtch['winner_name']].last_match == -1:
            players[mtch['winner_name']].last_match = dscore
        k_loser = dscore - players[mtch['loser_name']].last_match
        k_winner = dscore - players[mtch['winner_name']].last_match

        players[mtch['loser_name']].updateTime(dscore)
        players[mtch['winner_name']].updateTime(dscore)
        delta = players[mtch['winner_name']].rating - players[mtch['loser_name']].rating
        # predict result of the match 
        pred = eloObj.predict(delta) # probability of a person with rating ``advantage`` DELTA winning?? 
        try:
            # get result of the match (statistically)
            match_ratings = get_rating(parse_score(mtch['score']),winner_bonus)
        except Exception as e:
            # print("Skipped ",mtch)
            continue
        winner_stat = max(match_ratings[0],match_ratings[1])/(float(match_ratings[0]) + match_ratings[1])
        loser_stat = 1 - winner_stat

        while time_st in prat[mtch['loser_name']].keys() or time_st in prat[mtch['winner_name']].keys():
            time_st += 1

        plerr[mtch['loser_name']][time_st] = (abs(pred - loser_stat))        # might need to change this 
        plerr[mtch['winner_name']][time_st] = (abs(1 - pred - winner_stat))  # might need to change this 

        players[mtch['winner_name']].rating = eloObj.elo_rate(players[mtch['winner_name']].rating,-1*delta,winner_stat,k_winner)
        players[mtch['winner_name']].wins +=1 
        players[mtch['loser_name']].rating = eloObj.elo_rate(players[mtch['loser_name']].rating,delta,loser_stat,k_loser)
        players[mtch['loser_name']].lose += 1

        prat[mtch['loser_name']][time_st] = (players[mtch['loser_name']].rating)
        prat[mtch['winner_name']][time_st] = (players[mtch['winner_name']].rating)

    final_dict = {
        'rating':prat,
        'error':plerr
    }
    with open(filename,'w+') as fp:
        json.dump(final_dict,fp)
    


if __name__ == '__main__':
    # fname = input('Enter Dataset Filename')
    arguments = parseArguments(sys.argv)
    plotter = PlotEngine(arguments.display,arguments.plot_path)
    
    stdt = arguments.startTime
    endt = arguments.endTime
    subFilter = None 
    if arguments.input != None:
        with open(arguments.input,'r') as fp:
            subFilter = json.load(fp)['inputs']
    print("skipping",subFilter)
    print(arguments.train,type(arguments.train))
    if arguments.train == 1: 
        dataset = load_data(arguments.dataset)
        evaluateData(dataset,arguments.output,arguments.winner_bonus,stdt,endt)
    plotter.load_data(arguments.output)
    plotter.plot_ratings(subFilter,arguments.percentage)
