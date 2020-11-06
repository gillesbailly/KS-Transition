import os
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
        if not os.path.exists( path ):
            print("The path for", self.name,  " is not valid: ", path)
            return np.empty(0)
        res = np.empty(0)
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
                                    res = np.append( res, user_data )
                                user_data = User_Data()
                            user_id        = int( row[ 0 ] )
                            user_data.set( int( row[ 0 ] ) , technique_name_vec.index( row[1 ] ) , row[ 1 ] ) #userid, techniqueid, techniquename
                            
                            cmd = int( row[2] )
                            if cmd not in user_data.command_info.id:
                                user_data.command_info.name             = np.append( user_data.command_info.name, row[ 4 ] )
                                user_data.command_info.frequency        = np.append( user_data.command_info.frequency, int( row[ 3 ] ) )
                                user_data.command_info.start_transition = np.append( user_data.command_info.start_transition, int( row[ 5 ] ) )
                                user_data.command_info.stop_transition  = np.append( user_data.command_info.stop_transition, int( row[ 6 ] ) )
                                user_data.command_info.id               = np.append( user_data.command_info.id, int( row[ 2 ] ) )
                                
                            user_data.cmd               = np.append( user_data.cmd, cmd )
                            user_data.output.time       = np.append( user_data.output.time, float( row[ 7 ] ) )
                            user_data.output.success    = np.append( user_data.output.success, int( row[ 8 ] ) )
                            user_data.output.action     = np.append( user_data.output.action, Action( cmd, int( row[ 9 ] ) ) )
                            user_data.other.block       = np.append( user_data.other.block, int( row[11] ) )
                            user_data.other.block_trial = np.append( user_data.other.block_trial, int( row[12] ) )
                            user_data.other.encounter   = np.append( user_data.other.encounter, int( row[13] ) )
                            user_data.other.method_id   = np.append( user_data.other.method_id, int( row[14] ) )
                            user_data.other.method_name = np.append( user_data.other.method_name, row[15] ) 
                            
                                
                    else:
                        headerFlag = False
                        self.header = row
                        #for i in range(0, len(self.header) ) :
                            #print("header ", i, self.header[i] )

                res = np.append( res, user_data )

                #print("pure menu: ", self.count_pure_menu, "pure hotkey: ", self.count_pure_hotkey, "unknown: ", self.count_unknown, "hotkey->menu: ", self.count_hotkey_menu, "hotkey->learning: ", self.count_hotkey_learning, "menu->?: ", self.count_menu_unknown)
        except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
            print( "ERROR: path", path, "not found" )
        return res



    
