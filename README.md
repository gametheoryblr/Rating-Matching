# Rating-Matching
Implementation of Rating and Player matching algorithm 

## Testing 

We make available ATP dataset of matches from `1968-2022`. This can be used for training the rating system and viewing the results (cumulative loss, windowed error and ratings with matches) for different players in `A-level` tournaments by using the following command in the root directory of the repo. 

### Tennis

#### Elo
```sh
$ python3 (elo_tennis/elo_squash).py --dataset [DATASET-PATH] --output [JSON-OUTPUT-FILEPATH] --display [datewise/matchwise] --plot_path [OUTPUT-DIRECTORY for PLOTTING (dont write the last '/') (optional)] --input [INPUTS (json file if any)] --train [0/1 train or use pretrained data] --percentage [if --input is not provided then randomly sample with probability percentage (0,1)]
```

> Example: `$ python3 elo_tennis.py --dataset ./dataset/atp_matches_till_2022.csv --output temp.json --display datewise --plot_path outputs --input ./inputs/in1.json --train 1 ` 

> Example: `$ python3 elo_tennis.py --dataset ./dataset/atp_matches_till_2022.csv --output temp.json --display datewise --plot_path outputs --input ./inputs/in1.json --train 0` 

> Example: `$ python3 elo_tennis.py --dataset ./dataset/atp_matches_till_2022.csv --output temp.json --display datewise --plot_path outputs --train 0 --percentage=0.1` 


> Example: `$ python3 elo_squash.py --dataset ./dataset/squash_dataset.csv --output temp_squash.json --display datewise --plot_path ./outputs --train 1 --input ./inputs/in_squash.json`

> Example: `$ python3 elo_squash.py --dataset ./dataset/squash_dataset.csv --output temp_squash.json --display datewise --plot_path ./outputs --train 0 --input ./inputs/in_squash.json`

> Example: `$ python3 elo_squash.py --dataset ./dataset/squash_dataset.csv --output temp_squash.json --display datewise --plot_path ./outputs --train 0 --percentage 0.1`


DO input the input otherwise code tries to print all logs and it is not possible/very heavy in matplotlib 
#### Glicko
```sh
$ python3 (glicko_tennis/glicko_squash).py --dataset [DATASET-PATH] --output [JSON-OUTPUT-FILEPATH] --display [datewise/matchwise] --plot_path [OUTPUT-DIRECTORY for PLOTTING (dont write the last '/') (optional)] --input [INPUTS (json file if any)] --train [0/1 train or use pretrained data] --percentage [if --input is not provided then randomly sample with probability percentage (0,1)]
```
> Example: `$ python3 glicko_squash.py --dataset ./dataset/squash_dataset.csv --display datewise --input ./inputs/in_squash.json --output op_squash.json --plot_path ./outputs --train 1`
> Example `$ python3 glicko_squash.py --dataset ./dataset/squash_dataset.csv --display datewise --input ./inputs/in_squash.json --output op_squash.json --plot_path ./outputs --train 0 `
> Example `$ python3 glicko_squash.py --dataset ./dataset/squash_dataset.csv --display datewise --percentage 0.1 --output op_squash.json --plot_path ./outputs --train 1 `

### Squash

#### Glicko
```sh
$ python3 glicko_squash.py ./dataset/squash_dataset.py [datewise] [input_file]
```
> Example: `$ python3 glicko_squash.py dataset/squash_dataset.csv datewise inputs/squash_in1.json`

***
# Glicko Testing
1. Make a new Player object.
2. Assign it Rating and RD using the respective class-methods from the stored values.
3. Update the player's Rating and RD.
4. Store the updated values.

