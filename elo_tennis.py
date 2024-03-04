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
from src.util.tennis.rating import Tennis as Player,get_rating
from src.v1.rating_elo.elo import Elo 
from src.util.ufuncs import date_parser, parse_score




#load files 
def load_data(fname):
    matches = pd.read_csv(fname)
    # filter dataset 
    matches_dropset = ['tourney_name', 'surface', 'draw_size', 'winner_seed', 'winner_entry',
        'winner_hand', 'winner_ht', 'winner_ioc', 'winner_age', 'loser_seed', 'loser_entry', 'loser_hand', 'loser_ht', 
        'loser_ioc', 'loser_age', 'winner_rank_points', 'loser_rank_points', 'round','minutes', 'w_ace', 'w_df', 
        'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_SvGms', 'w_bpSaved', 'w_bpFaced', 'l_ace', 'l_df', 'l_svpt',
        'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_SvGms', 'l_bpSaved', 'l_bpFaced', 'winner_rank', 'loser_rank']
    try:
        matches.drop(matches_dropset,inplace=True,axis=1)
    except Exception as e:
        print("Keys not found")


    md = matches.to_dict()
    data = {}
    for i in md['tourney_id'].keys():
        data[md['tourney_date'][i]*1000 + md['match_num'][i]] = md
    dataset = pd.DataFrame.from_dict(md)
    return dataset

def evaluateData(dataset,filename, begin_date=0,end_date=99999999):
    players = {}
    prat = {}
    plerr = {}
    eloObj = Elo()
    name_id = {} # will store meta information 

    for i in range(dataset.shape[0]):
        pdone = int(100*i/dataset.shape[0])
        print('\r',pdone,end=' ')
        print('\r[',pdone*'=',(100-pdone)*'-',']',pdone,'\%',sep='',end='')
        mtch = dataset.loc[i]
        if mtch['tourney_date'] < begin_date or mtch['tourney_date'] > end_date:
            continue
        name_id[mtch['winner_name']] = mtch['winner_id']
        if mtch['winner_name'] not in players.keys():
            players[mtch['winner_name']] = Player(mtch['winner_id'],mtch['winner_name'])
            prat[mtch['winner_name']] = {}
            plerr[mtch['winner_name']] = {}
        if mtch['loser_name'] not in players.keys():
            players[mtch['loser_name']] = Player(mtch['loser_id'],mtch['loser_name'])
            prat[mtch['loser_name']] = {}
            plerr[mtch['loser_name']] = {}
        
        # difference in timing...
        dscore = date_parser(mtch['tourney_date'])
        yr = (mtch['tourney_date'])/10000
        mth = int(((mtch['tourney_date']%10000)/100)*100/12)
        day = int(((mtch['tourney_date']%100))*100/(30 + (mth%2)))
        time_st = str(yr*10000 + mth*100 + day)

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
            match_ratings = get_rating(parse_score(mtch['score']))
        except Exception as e:
            # print("Skipped ",mtch)
            continue
        winner_stat = max(match_ratings[0],match_ratings[1])/(float(match_ratings[0]) + match_ratings[1])
        loser_stat = 1 - winner_stat

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
    with open(filename,'w') as fp:
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
    dataset = load_data(arguments.dataset)
    evaluateData(dataset,arguments.output,stdt,endt)
    plotter.load_data(arguments.output)
    plotter.plot_ratings(subFilter)
