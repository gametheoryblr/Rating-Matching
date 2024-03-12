import argparse
def parseArguments(args:list):
    
    print(args)
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '--dataset',help='Enter Dataset to use for the script',type=str,default=None)
    parser.add_argument(
        '--display',help='Display datewise/matchwise',type=str,default=None)
    parser.add_argument(
        '--mapper',help='Mapper (maps id to name)',type=str,default=None)
    parser.add_argument(
        '--debug',help='Debug mode? (with print statements)',type=bool,default=False)
    parser.add_argument(
        '--output',help='Output folder destination',type=str,default=None)
    parser.add_argument(
        '--input',help='Input file path',type=str,default=None)
    parser.add_argument(
        '--startTime',help='start-time (format = yyyymmdd) for plotting data',type=int,default=0)
    parser.add_argument(
        '--endTime',help='end-time (format = yyyymmdd) for plotting data', type=int, default=99999999)
    parser.add_argument(
        '--plot_path',help='Folder where plots are stoed (don\'t put \\ in the end)',type=str,default=None)
    parser.add_argument(
        '--train',help='true/false (train or use a pre-loaded file)',type=int, default=0)
    parser.add_argument(
        '--percentage',help='percentage of players to randomly sample',type=float,default=1.0)
    parser.add_argument(
        '--winner_bonus',help='winner bonus point (faction of total points) [0,1]',type=float,default=1.0)
    return  parser.parse_args()
