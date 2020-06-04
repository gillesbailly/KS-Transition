import sys
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

# if __name__=="__main__":
#     annotation = TransitionAnnotation('./experiment/transition_annotation.csv', 750)
#     print(annotation.trial_range(1, 'Strawberry'), annotation.occurence_range(1, 'Strawberry') )




##########################################
#                                        #
#             Experiment                 #
#                                        #
##########################################
class Experiment(object):

    ####################
    def __init__(self, path, n_strategy, raw_data = True, _filter=""):
        self.annotation = TransitionAnnotation('./experiment/transition_annotation.csv', 750)

        self.count_pure_hotkey = 0
        self.count_pure_menu = 0
        self.count_hotkey_menu = 0
        self.count_hotkey_learning = 0
        self.count_menu_unknown = 0
        self.count_unknown = 0
        if raw_data : 
            self.data = self.load_raw_data(path, _filter) #best one
        else :
            self.data = self.load(path, n_strategy, _filter)
        
        self.header =""


    def filtering(self, _filter):
        res = _filter.split('=')

        return res # [key, value]




    def strategy(self, row ) :
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






                    

    def add_and_save(self, file_in, file_out ) :


        with open(file_out, mode= 'w' ) as out:
            writer = csv.writer(out, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            with open(file_in, 'r') as csvFile:
                reader = csv.reader(csvFile, delimiter= ',')
                technique_name_vec = ["traditional", "audio", "disable"]
                strategy_name_vec = ["menu", "hotkey", "learning", "none"]
                header_flag = True

                for row in reader:
                    if header_flag :
                        header_flag = False
                        row.append("strategy")
                        row.append("strategy_name")
                        row.append("technique_name")
                        writer.writerow(row)

                    else :
                        technique_name = technique_name_vec[ int( row[4] ) ]
                        strategy = self.strategy( row )
                        #print(strategy)

                        strategy_name = strategy_name_vec[ strategy ]
                        row.append( strategy )
                        row.append( strategy_name ) 
                        row.append( technique_name )
                        writer.writerow(row)



    def load_raw_data(self, path, _filter="") :
        if not path:
            raise("The path is not valid: ", path)
            return

        all_filter = (_filter =="")
        index_filter = -1
        value_filter = -1

        with open(path, 'r') as csvFile:
            reader = csv.reader(csvFile, delimiter= ',')
            headerFlag = True
            user_id = -1
            history = None
            technique_name_vec = ["traditional", "audio", "disable"]
            res = []
            for row in reader:
                if not headerFlag:
                    if all_filter or (value_filter == row[index_filter] ):
                        if user_id != int( row[1] ):
                            if user_id > -1:
                                res.append(history)
                            history = User_History()
                        user_id = int(row[1])
                        technique_id = int( row[4] )
                        history.set_info( user_id, technique_id, technique_name_vec[ technique_id] ) #userid, techniqueid, techniquename
                        
                        time = round( float( row[24] ), 3)
                        if time > 0 :
                            history.block.append( int(row[2]) )
                            history.block_trial.append( int(row[3]) )
                            cmd_name = row[6]
                            if row[6] not in history.command_name:
                                history.command_name.append( cmd_name )
                                history.command_frequency.append( int( row[30] ) )
                                trans_range = self.annotation.trial_range(user_id, cmd_name )
                                history.start_transition.append( trans_range[0] )
                                history.stop_transition.append( trans_range[1] ) 
                                history.commands.append( len(history.command_name) - 1 )
                            cmd = history.command_name.index(row[6])

                           

                            history.cmd.append( cmd )
                    
                            history.encounter = int( float(row[31]) )

                            method_id = int( row[12] )
                            history.method_name[ method_id ] = "menu" if method_id == 0 else "hotkey" 
                            history.method_id.append( method_id )
                        
                            strategy = self.strategy( row )

                            history.user_action.append( Action(cmd, strategy) )                
                            history.user_time.append( time )
                            success = 1 if int(row[26]) == 0 else 0
                            history.user_success.append( success )
                            history.user_extra_info.append( row )
                        #else :
                            #print(row)
                            #print("time <0.....", user_id, technique_id)

                else:
                    headerFlag = False
                    self.header = row
                    #for i in range(0, len(self.header) ) :
                        #print("header ", i, self.header[i] )

                    if not all_filter:
                        filtering = self.filtering(_filter)
                        index_filter = self.header.index(filtering[0]) # index key
                        value_filter = filtering[1]

            if time != -1:
                res.append( history )

            #print("pure menu: ", self.count_pure_menu, "pure hotkey: ", self.count_pure_hotkey, "unknown: ", self.count_unknown, "hotkey->menu: ", self.count_hotkey_menu, "hotkey->learning: ", self.count_hotkey_learning, "menu->?: ", self.count_menu_unknown)

        return res

    #######################
    def load(self, path, n_strategy, _filter=""):
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
                        
                        time = round( float( row[14] ), 3)
                        if time > 0 :
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
                        
                            s = Strategy.HOTKEY if ub_id == 3 else Strategy.MENU

                           # if include the learning strategy
                            if ub_id == 2  :
                                s = Strategy.LEARNING

                            history.user_action.append( Action(cmd, s) )                
                            history.user_time.append( time )
                            success = 1 if int(row[15]) == 0 else 0
                            history.user_success.append( success )
                            if s == Strategy.LEARNING and success == 0 :
                                self.count_unknown += 1
                            if s == Strategy.MENU and success == 0 :
                                self.count_pure_menu += 1
                            if s == Strategy.HOTKEY and success == 0 :
                                self.count_pure_hotkey += 1
                            


                else:
                    headerFlag = False
                    self.header = row

                    if not all_filter:
                        filtering = self.filtering(_filter)
                        index_filter = self.header.index(filtering[0]) # index key
                        value_filter = filtering[1]
            print("menu:", self.count_pure_menu, "hotkey:", self.count_pure_hotkey, "learning: ", self.count_unknown, )

            if time != -1:
                res.append( history )

        return res


