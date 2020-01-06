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
    def __init__(self, path, _filter=""):
        self.data = self.load(path, _filter)
        self.header =""

    def filtering(self, _filter):
        res = _filter.split('=')

        return res # [key, value]

    #######################
    def load(self, path, _filter=""):
        if not path:
            raise("The path is not valid: ", path)
            return
        res = []
        
        all_filter = (_filter =="")
        index_filter = -1
        value_filter = -1
        

        with open(path, 'r') as csvFile:
            reader = csv.reader(csvFile, delimiter= ',')
            headerFlag = True
            user_id = -1
            history = None
            for row in reader:
                if not headerFlag:


                    if all_filter or (value_filter == row[index_filter] ):

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
                        cmd = history.command_name.index(row[7])
                        history.cmd.append( cmd )
                    
                        history.encounter = int( float(row[8]) )

                        method_id = int( row[11] )
                        history.method_name[ method_id ] = row[10]
                        history.method_id.append( method_id )
                    
                        ub_id = int( row[13] )
                        history.ub_name[ ub_id ] = row[12]
                        history.ub_id.append( ub_id )
                        

                        s = Strategy.LEARNING
                        if ub_id == 3:
                            s = Strategy.HOTKEY
                        elif ub_id == 0:
                            s = Strategy.MENU


                        history.user_action.append( Action(cmd, s) )
                        history.user_time.append( round( float( row[14] ), 3) )
                        success = 1 if int(row[15]) == 0 else 0
                        history.user_success.append( success )
                    
                else:
                    headerFlag = False
                    print("header: ", row)
                    self.header = row

                    if not all_filter:
                        filtering = self.filtering(_filter)
                        index_filter = self.header.index(filtering[0]) # index key
                        value_filter = filtering[1]


            res.append( history )

        return res


