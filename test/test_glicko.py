import glicko2
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import math
import json
import csv
from tqdm import tqdm

matches = pd.read_csv("../Data/Tennis/atp_matches_till_2022.csv")
matches = matches[['tourney_id', 'tourney_name', 'surface', 'draw_size', 'tourney_level', 'tourney_date', 'match_num', 'winner_id', 'winner_name','loser_id', 'loser_name', 'score', 'best_of', 'round']]
matches = matches[matches["tourney_level"]=='A']

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
    winner = glicko2.Player()
    winner.setRating(player_ratings[winner_id]['Rating'])
    winner.setRd(player_ratings[winner_id]['RD'])
    
    #Setting up Loser
    loser = glicko2.Player()
    loser.setRating(player_ratings[loser_id]['Rating'])
    loser.setRd(player_ratings[loser_id]['RD'])
    
    winner.update_player([l_rating],[l_rd],[1])
    loser.update_player([w_rating],[w_rd],[0])
    
    player_ratings[winner_id]['Rating'] = winner.getRating()
    player_ratings[winner_id]['RD'] = winner.getRd()
    player_ratings[loser_id]['Rating'] = loser.getRating()
    player_ratings[loser_id]['RD'] = loser.getRd()


#store player ratings in a csv file with columnns ID, rating, RD
with open('player_ratings.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Rating', 'RD'])
    for key, value in player_ratings.items():
        writer.writerow([key, value['Rating'], value['RD']])
