import random 
import matplotlib.pyplot as plt 
import datetime
import json 
'''
    plot_type : stores either x-axis will be date-wise or match-wise
    save_path : None or path (save plots here) None-> show the plots
    rating_data : list of data of rating with time 
        ratings_data[0] : dict of type [time]->[rating] (currently in sorted order TODO: make it work even for unsorted order)
    error_data : list of data with error with time (other stuff same as rating data)
    attribute_mapper : (optional) maps other information of each player to their primary key through a dict of dict 
    time_format: 'DD-MM-YYYY' (string)
        
'''


class PlotEngine:
    def __init__(self,_plot_type='matchwise',_save_path=None):
        self.plot_type = _plot_type
        self.save_path = _save_path
        self.rating_data = []
        self.error_data = [] 
        self.rating_name = [] 
        self.attribute_mapper = [] # should be None or dict for each entry in rating-data and error-data 

    def constraints(self):
        assert(len(self.rating_data) == len(self.error_data))
        assert(len(self.rating_data) == len(self.attribute_mapper))

    def load_data(self,filepath,name=''):
        try:
            with open(filepath,'r') as fp:
                data = json.load(fp)
                assert('rating' in data.keys() and type(data['rating']) == type({}))
                assert('error' in data.keys() and type(data['error'] == type({})))
                self.rating_data.append(data['rating']) 
                self.error_data.append(data['error'])
                self.rating_name.append(name)
                if 'attributes' in data.keys():
                    self.attribute_mapper.append(data['attributes'])
                else:
                    self.attribute_mapper.append(None)
        except Exception as e:
            print(f"ERROR:: [function load_data() in class PlotEngine threw {e} for file {filepath}\n",end="")
        self.constraints() # throws errors if there is some issue in state of the object after calling the function 


    def plot_ratings(self,subFilter=None,percent=1,drange=[0,-1]): 
        # errenous input handling 
        if drange[1] < drange[0] or drange[0] < 0 or drange[1] >= len(self.rating_data): # default case... or error in input 
            drange = [0,len(self.rating_data)-1]
        i = drange[0] 
        while i <= drange[1]:
            for akey in self.rating_data[i].keys():
                if subFilter != None and akey not in subFilter:
                    # print('skipping',akey)
                    continue
                if random.random() > percent:
                    continue
                # print('not skipping',akey)
                # to make sure the keys for both error and rating_data is the same.... and if attribute is not none, then each has the key:name placeholder (either correct value or None)
                # currently using plt.plot 
                # @Varul TODO: overload this function with another argument (plot-object) and do work on that object
                self.rating_data[i][akey] = {int(float(k)):v for k,v in self.rating_data[i][akey].items()}
                self.rating_data[i][akey] = dict(sorted(self.rating_data[i][akey].items()))
                # print(self.rating_data[i][akey].keys())
                if self.plot_type == 'datewise':
                    plt.plot(self.rating_data[i][akey].keys(),self.rating_data[i][akey].values(),label=self.rating_name[i] + ( akey if (self.attribute_mapper[i] == None or self.attribute_mapper[i][akey]['name'] == None) else self.attribute_mapper[i][akey]['name']))
                elif self.plot_type == 'matchwise':
                    z = len(list(self.rating_data[i][akey].keys()))
                    plt.plot(range(z),list(self.rating_data[i][akey].values()),label=self.rating_name[i] + akey) # ( key if (self.attribute_mapper[i] == None or self.attribute_mapper[i][key]['name'] == None) else self.attribute_mapper[i][key]['name']))
            i += 1

        plt.title(f'Plot of Rating vs {self.plot_type[:-4]}')
        plt.xlabel(f'{self.plot_type[:-4]}')
        plt.ylabel('Ratings')
        plt.legend() 
        if self.save_path == None:
            plt.show() 
        else:
            plt.savefig(self.save_path+'/'+datetime.datetime.now().strftime("%d%m%Y_%H%M")+'_ratings.png')
        self.constraints() # not required as this is a non-mutable type function but still added for security 

    