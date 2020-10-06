import sys
import csv
import numpy as np

from data_loader import *
from util import *




##########################################
#                                        #
#       HOTKEYCOACH LOADER               #
#                                        #
##########################################
class HotkeyCoach_Loader( Experiment_Loader_Interface ):


    ######################
    def __init__( self ):
        super(Experiment_Loader_Interface, self).__init__()
        self.name = "HotkeyCoach Loader"
        self.annotation = TransitionAnnotation('./data/transition_annotation.csv', 750)
        self.reset()

    
    def trial_info( self, row_str ) :
        keys = self.header
        values = row_str.split()

        return dict( zip(keys, values) )


    ######################
    def reset( self ):
        self.count_pure_hotkey = 0
        self.count_pure_menu = 0
        self.count_hotkey_menu = 0
        self.count_hotkey_learning = 0
        self.count_menu_unknown = 0
        self.count_unknown = 0
        self.header =""


    ######################
    def load( self, path ) :
        if not path:
            raise("The path for", self.name,  " is not valid: ", path)
            return []
        res = []
        try : 
            with open(path, 'r') as csvFile:
                reader = csv.reader(csvFile, delimiter= ',')
                headerFlag = True
                user_id = -1
                user_data = None
                technique_name_vec = ["traditional", "audio", "disable"]

                for row in reader:
                    if not headerFlag:
                        if True :
                            if user_id != int( row[1] ):
                                if user_id > -1:
                                    res.append( user_data )
                                user_data = User_Data()
                            user_id = int(row[1])
                            technique_id = int( row[4] )
                            user_data.set( user_id, technique_id, technique_name_vec[ technique_id] ) #userid, techniqueid, techniquename
                            
                            time = round( float( row[24] ), 3)
                            if time > 0 :
                                user_data.other.block.append( int(row[2]) )
                                user_data.other.block_trial.append( int(row[3]) )
                                cmd_name = row[6]
                                if cmd_name not in user_data.command_info.name:
                                    user_data.command_info.name.append( cmd_name )
                                    user_data.command_info.frequency.append( int( row[30] ) )
                                    trans_range = self.annotation.trial_range(user_id, cmd_name )
                                    user_data.command_info.start_transition.append( trans_range[0] )
                                    user_data.command_info.stop_transition.append( trans_range[1] ) 
                                    user_data.command_info.id.append( len( user_data.command_info.name ) - 1 )
                                
                                cmd = user_data.command_info.name.index( cmd_name )
                                user_data.cmd.append( cmd )
                        
                                user_data.other.encounter.append( int( float(row[31]) ) )

                                method_id = int( row[12] )
                                user_data.other.method_id.append( method_id )
                                user_data.other.method_name.append( "menu" if method_id == 0 else "hotkey" ) 
                            
                                strategy = self.strategy( row ) 

                                user_data.output.action.append( Action(cmd, strategy) )                
                                user_data.output.time.append( time )
                                success = 1 if int(row[26]) == 0 else 0
                                user_data.output.success.append( success )
                                #user_data.user_extra_info.append( row )
                            #else :
                                #print(row)
                                #print("time <0.....", user_id, technique_id)

                    else:
                        headerFlag = False
                        self.header = row
                        #for i in range(0, len(self.header) ) :
                            #print("header ", i, self.header[i] )



                if time != -1:
                    res.append( user_data )

                #print("pure menu: ", self.count_pure_menu, "pure hotkey: ", self.count_pure_hotkey, "unknown: ", self.count_unknown, "hotkey->menu: ", self.count_hotkey_menu, "hotkey->learning: ", self.count_hotkey_learning, "menu->?: ", self.count_menu_unknown)
        except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
            print( "ERROR: path", path, "not found" )
        return res



    ######################
    def strategy( self, row ) :
        success = 1 if int(row[26]) == 0 else 0
        technique_id = int(row[4] )
        menu_opened = float(row[20]) > 0
        time_any_menu_opened = float( row[19] )
        modifier_pressed = float(row[22]) > 0
        letter_pressed = float(row[23] ) > 0
        time_letter_pressed = float( row[23] )
        time_total = float( row[24] ) # I am hesitating between time_item_selected and time_end_trial
        
        method = int( row[12] )
        selections = row[29].split( ' | ' )
        del selections[-1]
        #print(selections)
        count_menu_modifier_pressed = 0

        strategy = -1
        if success :
            if len(selections) > 1 :
                print(row)
                print("success but len selections > 1")
                exit(0)

            if method == 1 :     # hotkey

                if letter_pressed :
                    strategy = Strategy.HOTKEY

                    #if not modifier_pressed :
                    #    print( "method == 1 but no modifier press or user:", row[1] )

                    if menu_opened :
                        return Strategy.LEARNING
                    else :
                        return Strategy.HOTKEY
                    
            
            elif method == 0 :   # menu
                if modifier_pressed :
                    count_menu_modifier_pressed += 1
                    #print(row)
                    #print("method == 0 (menu) and modifier pressed \t ", count_menu_modifier_pressed, row[1])
                    return Strategy.LEARNING
                
                else :
                    return Strategy.MENU
            else :
                return -1 #error in the file
        
        else :   #ERROR

            #parse selections
            first_method = int( selections[0][0] )
            second_method = int(selections[1][0] )
            #print("errror: ", selections, menu_opened, letter_pressed)

            if not menu_opened :
                self.count_pure_hotkey += 1                         #case never open the menu Hotkey -> Hotkey
                return Strategy.HOTKEY

            elif not letter_pressed :
                self.count_pure_menu += 1                           #case never press the hotkey => Menu -> Menu
                return Strategy.MENU
            
            else :
                if time_letter_pressed < time_any_menu_opened :     # case hotkey -> Menu (last hotkey before first menu open)
                    self.count_hotkey_menu +=1
                    return Strategy.HOTKEY
                    #print("vrai hotkey -> menu error")
                
                elif time_total - time_any_menu_opened < 3.5 :        # case hotkey -> Learning 
                    #first menu_open necessary occured on the last selection
                    # as time_letter_pressed > first_menu_opened
                    # => last selection is a LEARNING (menu+hotkey)
                    # => trials before are necessary hotkeys
                    self.count_hotkey_learning += 1
                    return Strategy.HOTKEY
                
                elif first_method == 0 :                            # case menu -> ?
                    self.count_menu_unknown += 1
                    
                    return Strategy.MENU

                #elif time_any_menu_opened
                else :                                              # case learning -> ?
                    #print(selections, row[0], row[4], time_any_menu_opened, time_letter_pressed, row[25])
                    #theoretically, t
                    #print(row)
                    #print(" ")
                    self.count_unknown +=1
                    return Strategy.LEARNING

                #print("error do not know what to do")
                
                #return Strategy.LEARNING



if __name__=="__main__":
    path = './experiment/hotkeys_formatted_dirty.csv'
    loader = HotkeyCoach_Loader()
    print( loader.name )
    experiment = loader.experiment( path )
    print( "load", len( experiment ), "sequences" )


