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
                    user_id = int(row[1])
                    history.set_info( int(row[1]), int(row[6]), row[5] ) #userid, techniqueid, techniquename
                    history.block.append( int(row[2]) )
                    history.block_trial.append( int(row[3]) )
                    
                    if row[7] not in history.command_name:
                        history.command_name.append( row[7] )
                        history.command_frequency.append( int( row[9] ) ) 
                        history.commands.append( len(history.command_name) - 1 )
                    history.cmd.append( history.command_name.index(row[7]) )
                    
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
                    history.user_action.append( action )
                    history.user_time.append( round( float( row[14] ), 3) )
                    history.user_errors.append( int( row[15] ) )
                    
                else:
                    header = False
                    print("header: ", row)
            res.append( history )

        return res


