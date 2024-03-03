import argparse
def parseArguments(args:list):
    
    print(args)
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '--dataset',help='Enter Dataset to use for the script',type=str)
    parser.add_argument(
        '--display',help='Display datewise/matchwise',type=str,default='matchwise')
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
    return  parser.parse_args()
