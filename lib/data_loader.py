import csv
import numpy as np
import pandas as pd

from util import *



##########################################
#                                        #
#             Experiment                 #
#                                        #
##########################################
class TransitionAnnotation(object):
    def __init__(self, path, max_trial_id = 750) :
        self.max_trial = max_trial_id
        self.df = pd.read_csv( path, sep=',')


    def get_range( self, user_id, cmd_name, column_names) :
        res = self.df.loc[  (self.df['subject'] == user_id)  & (self.df['item'] == cmd_name), column_names ]
        return res.to_numpy()[0]
        

    def trial_range(self, user_id, cmd_name) :
        res = self.get_range( user_id, cmd_name, ['transition_start_trial', 'transition_end_trial'] )
        res = np.where(res==-1, self.max_trial, res) 
        return res
        

    def occurence_range(self, user_id, cmd_name) :
        return self.get_range( user_id, cmd_name, ['transition_start', 'transition_end'] )


#############################################
#                                           #
#       EXPERIMENT LOADER INTERFACE         #
#                                           #
#############################################
class Experiment_Loader_Interface( object ) :
    
    ####################
    def __init__( self ):
        self.name = "Experiment Loader Interface"

    ####################
    def reset( self ) :
        pass 

    ####################
    def experiment( self, _path ):
        return [] #return an empty vector of User Data


