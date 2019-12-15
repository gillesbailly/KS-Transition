import sys
import csv
import numpy as np
from util import *



##########################################
#                                        #
#             Experiment                 #
#                                        #
##########################################
class Experiment(object):

    ####################
    def __init__(self, path):
        self.data = self.load(path)


    #######################
    def load(self, path):
        if not path:
            raise("The path is not valid: ", path)
            return
        res = []
        with open(path, 'r') as csvFile:
            reader = csv.reader(csvFile, delimiter= ',')
            header = True
            user_id = -1
            history = None
            for row in reader:
                if not header:
                    if user_id != int( row[1] ):
                        if user_id > -1:
                            res.append(history)
                        history = User_History()

                    user_id = int( row[1])
                    history.user_id = int( row[1])
                    history.block.append( int(row[2]) )
                    history.block_trial.append( int(row[3]) )
                    history.trial.append( int(row[4]) )
                    
                    history.technique_name  = row[5]
                    history.technique_id = int( row[6] )
                    
                    if row[7] not in history.cmd_name:
                        history.cmd_name.append( row[7] )
                        history.cmd_frequency.append( int( row[9] ) ) 
                        history.commands.append( len(history.cmd_name) - 1 )
                    history.cmd.append( history.cmd_name.index(row[7]) )
                    
                    history.encounter = int( float(row[8]) )

                    method_id = int( row[11] )
                    history.method_name[ method_id ] = row[10]
                    history.method_id.append( method_id )
                    
                    ub_id = int( row[13] )
                    history.ub_name[ ub_id ] = row[12]
                    history.ub_id.append( ub_id )
                    action = ub_id
                    if action > 2:
                        action = 2
                    history.action.append( action )
                    history.time.append( float( row[14] ) )
                    history.errors.append( int( row[15] ) )
                    
                else:
                    header = False
                    print("header: ", row)
            res.append( history )

        return res


