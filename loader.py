import sys 
import json 
from src.util.arparse import parseArguments
from plotter import PlotEngine



if __name__ == '__main__':
    
    arguments = parseArguments(sys.argv)
    plotter = PlotEngine(arguments.display,arguments.plot_path)

    subFilter = None 
    if arguments.input != None:
        with open(arguments.input,'r') as fp:
            subFilter = json.load(fp)['inputs']
    while True:
        fn = input('Enter Filename (dataset json path) [press X to exit]:> ')
        if fn in ['X','x']:
            break
        name = input('Enter label of this dataset (elo/glicko)')
        plotter.load_data(fn,name)
    plotter.plot_ratings(subFilter,arguments.percentage)



