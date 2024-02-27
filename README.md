# Rating-Matching
Implementation of Rating and Player matching algorithm 

## Testing 

We make available ATP dataset of matches from `1968-2022`. This can be used for training the rating system and viewing the results (cumulative loss, windowed error and ratings with matches) for different players in `A-level` tournaments by using the following command in the root directory of the repo. 

```sh
$ python3 test_tennis.py ./dataset/atp_matches_till_2022.csv
```

Following which, the system will train on the dataset and prompt the name of the player to display the corresponding plots. To exit, press `X`.

***


# Glicko Testing
1. Make a new Player object.
2. Assign it Rating and RD using the respective class-methods from the stored values.
3. Update the player's Rating and RD.
4. Store the updated values.

# Glicko Testing
1. Make a new Player object.
2. Assign it Rating and RD using the respective class-methods from the stored values.
3. Update the player's Rating and RD.
4. Store the updated values.