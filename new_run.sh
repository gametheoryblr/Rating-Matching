python3 elo_tennis.py --dataset ./dataset/atp_matches_till_2022.csv --output elo_tennis_1.json --display datewise --plot_path outdir --input ./inputs/in1.json --train 1 --winner_bonus 0.75
sleep 60 
python3 elo_tennis.py --dataset ./dataset/atp_matches_till_2022.csv --output elo_tennis_1.json --display matchwise --plot_path outdir --input ./inputs/in1.json --train 1 --winner_bonus 0.75
sleep 60 
python3 glicko_tennis.py --dataset ./dataset/atp_matches_till_2022.csv --output glicko_tennis_1.json --display datewise --plot_path outdir --input ./inputs/in1.json --train 1 --winner_bonus 0.75
sleep 60 
python3 glicko_tennis.py --dataset ./dataset/atp_matches_till_2022.csv --output glicko_tennis_1.json --display matchwise --plot_path outdir --input ./inputs/in1.json --train 1 --winner_bonus 0.75
mkdir outputs/tennis
mv outputs/*.png outputs/tennis/
sleep 60 
python3 elo_squash.py --dataset ./dataset/squash_dataset_exco.csv --output elo_squash_1.json --display datewise --plot_path outdir --input ./inputs/in_squash.json --train 1 --winner_bonus 0.75
sleep 60 
python3 elo_squash.py --dataset ./dataset/squash_dataset_exco.csv --output elo_squash_1.json --display matchwise --plot_path outdir --input ./inputs/in_squash.json --train 1 --winner_bonus 0.75
sleep 60 
python3 glicko_squash.py --dataset ./dataset/squash_dataset_exco.csv --output glicko_squash_1.json --display datewise --plot_path outdir --input ./inputs/in_squash.json --train 1 --winner_bonus 0.75
sleep 60 
python3 glicko_squash.py --dataset ./dataset/squash_dataset_exco.csv --output glicko_squash_1.json --display matchwise --plot_path outdir --input ./inputs/in_squash.json --train 1 --winner_bonus 0.75
mkdir outputs/squash
mv outputs/*.png outputs/squash/
sleep 60 
python3 glicko_badminton.py --dataset ./dataset/player_predictions.csv --output glicko_badminton_1.json --display datewise --plot_path outdir --input ./inputs/in_badminton.json --train 1 --winner_bonus 0.75
sleep 60 
python3 glicko_badminton.py --dataset ./dataset/player_predictions.csv --output glicko_badminton_1.json --display matchwise --plot_path outdir --input ./inputs/in_badminton.json --train 1 --winner_bonus 0.75
sleep 60 
python3 elo_badminton.py --dataset ./dataset/player_predictions.csv --output elo_badminton_1.json --display datewise --plot_path outdir --input ./inputs/in_badminton.json --train 1 --winner_bonus 0.75
sleep 60 
python3 elo_badminton.py --dataset ./dataset/player_predictions.csv --output elo_badminton_1.json --display matchwise --plot_path outdir --input ./inputs/in_badminton.json --train 1 --winner_bonus 0.75
mkdir outputs/badminton
mv outputs/*.png outputs/badminton/
mkdir outputs/experiment5 
mv outputs/tennis outputs/badminton outputs/squash outputs/experiment5 
python3 elo_tennis.py --dataset ./dataset/atp_matches_till_2022.csv --output elo_tennis_1.json --display datewise --plot_path outdir --percentage 0.1 --train 0 --winner_bonus 0.75
sleep 60 
python3 elo_tennis.py --dataset ./dataset/atp_matches_till_2022.csv --output elo_tennis_1.json --display matchwise --plot_path outdir --percentage 0.1 --train 0 --winner_bonus 0.75
sleep 60 
python3 glicko_tennis.py --dataset ./dataset/atp_matches_till_2022.csv --output glicko_tennis_1.json --display datewise --plot_path outdir --percentage 0.1 --train 0 --winner_bonus 0.75
sleep 60 
python3 glicko_tennis.py --dataset ./dataset/atp_matches_till_2022.csv --output glicko_tennis_1.json --display matchwise --plot_path outdir --percentage 0.1 --train 0 --winner_bonus 0.75
mkdir outputs/tennis
mv outputs/*.png outputs/tennis/
sleep 60 
python3 elo_squash.py --dataset ./dataset/squash_dataset_exco.csv --output elo_squash_1.json --display datewise --plot_path outdir --percentage 0.1 --train 0 --winner_bonus 0.75
sleep 60 
python3 elo_squash.py --dataset ./dataset/squash_dataset_exco.csv --output elo_squash_1.json --display matchwise --plot_path outdir --percentage 0.1 --train 0 --winner_bonus 0.75
sleep 60 
python3 glicko_squash.py --dataset ./dataset/squash_dataset_exco.csv --output glicko_squash_1.json --display datewise --plot_path outdir --percentage 0.1 --train 0 --winner_bonus 0.75
sleep 60 
python3 glicko_squash.py --dataset ./dataset/squash_dataset_exco.csv --output glicko_squash_1.json --display matchwise --plot_path outdir --percentage 0.1 --train 0 --winner_bonus 0.75
mkdir outputs/squash
mv outputs/*.png outputs/squash/
sleep 60 
python3 glicko_badminton.py --dataset ./dataset/player_predictions.csv --output glicko_badminton_1.json --display datewise --plot_path outdir --percentage 0.1 --train 0 --winner_bonus 0.75
sleep 60 
python3 glicko_badminton.py --dataset ./dataset/player_predictions.csv --output glicko_badminton_1.json --display matchwise --plot_path outdir --percentage 0.1 --train 0 --winner_bonus 0.75
sleep 60 
python3 elo_badminton.py --dataset ./dataset/player_predictions.csv --output elo_badminton_1.json --display datewise --plot_path outdir --percentage 0.1 --train 0 --winner_bonus 0.75
sleep 60 
python3 elo_badminton.py --dataset ./dataset/player_predictions.csv --output elo_badminton_1.json --display matchwise --plot_path outdir --percentage 0.1 --train 0 --winner_bonus 0.75
mkdir outputs/badminton
mv outputs/*.png outputs/badminton/
mkdir outputs/experiment6 
mv outputs/tennis outputs/badminton outputs/squash outputs/experiment6



