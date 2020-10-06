import sys
import csv
import numpy as np

from data_loader import *
from util import *




##########################################
#                                        #
#         USER DATA LOADER               #
#                                        #
##########################################
class User_Data_Loader( Experiment_Loader_Interface ):


    ######################
    def __init__( self ):
        super(Experiment_Loader_Interface, self).__init__()
        self.name = "User Data Loader"


    ######################
    def load( self, path ) :
        if not path:
            raise("The path for", self.name,  " is not valid: ", path)
            return []
        res = []
        try : 
            with open(path, 'r') as csvFile:
                reader = csv.reader(csvFile, delimiter= ';')
                headerFlag = True
                user_id = -1
                user_data = None
                technique_name_vec = ["traditional", "audio", "disable"]

                for row in reader:
                    if not headerFlag:
                        if True :
                            if user_id != int( row[ 0 ] ):
                                if user_id > -1:
                                    res.append( user_data )
                                user_data = User_Data()
                            user_id        = int( row[ 0 ] )
                            user_data.set( int( row[ 0 ] ) , technique_name_vec.index( row[1 ] ) , row[ 1 ] ) #userid, techniqueid, techniquename
                            
                            cmd = int( row[2] )
                            if cmd not in user_data.command_info.id:
                                user_data.command_info.name.append( row[ 4 ] )
                                user_data.command_info.frequency.append( int( row[ 3 ] ) )
                                user_data.command_info.start_transition.append( int( row[ 5 ] ) )
                                user_data.command_info.stop_transition.append( int( row[ 6 ] ) )
                                user_data.command_info.id.append( int( row[ 2 ] ) )
                                
                            user_data.cmd.append( cmd )
                            user_data.output.time.append( float( row[ 7 ] ) )
                            user_data.output.success.append( int( row[ 8 ] ) )
                            user_data.output.action.append( Action( cmd, int( row[ 9 ] ) ) )
                            user_data.other.block.append( int( row[10] ) )
                            user_data.other.block_trial.append( int( row[11] ) )
                            user_data.other.encounter.append( int( row[12] ) )
                            user_data.other.method_id.append( int( row[13] ) )
                            user_data.other.method_name.append( row[14] ) 
                            
                                
                    else:
                        headerFlag = False
                        self.header = row
                        #for i in range(0, len(self.header) ) :
                            #print("header ", i, self.header[i] )

                res.append( user_data )

                #print("pure menu: ", self.count_pure_menu, "pure hotkey: ", self.count_pure_hotkey, "unknown: ", self.count_unknown, "hotkey->menu: ", self.count_hotkey_menu, "hotkey->learning: ", self.count_hotkey_learning, "menu->?: ", self.count_menu_unknown)
        except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
            print( "ERROR: path", path, "not found" )
        return res



    
