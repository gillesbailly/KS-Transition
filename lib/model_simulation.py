import sys
import os
import numpy as np
import cProfile
import argparse
import itertools
import time as TIME
from datetime import datetime
from scipy.optimize import *

sys.path.append("./GUI/")
sys.path.append("./lib/")
sys.path.append("./plugins/")
sys.path.append("./plugins/loader/")
sys.path.append("./plugins/export/")
sys.path.append("./plugins/model/")


from filter import *
from parameters_export import *
from data_loader import *
from user_data_loader import *
from util import *
from alpha_beta_model import *



        
##########################################
#                                        #
#           MODEL SIMILUATION            #
#                                        #
##########################################
class Simulation( object ):

    ######################################
    def __init__( self  ):
        self.user_input = []            # sequence of commands
        self.model = None


    ######################################
    # Output: [ User_Output, Model_Output, time(int) ]
    # User_Output = { time (vector<int>), success (vector<boolean>), action (vector<Action>) }
    # Model_Output = {menu, hotkey, learning (vectors <float> : probability to select the strategy menu, hotkey, learning) } 
    ######################################
    def run( self ):
        agent_output = User_Output( len( self.user_input ) )         # Multi sequence : Time, Success, Action
        model_output = Model_Output( len( self.user_input ) )
        start = TIME.time()

        for i, cmd in enumerate( self.user_input ) :
            strategy, prob_vec = self.model.select_strategy( cmd )
            a_vec = self.model.get_actions_from( cmd )
            probs = values_long_format(a_vec, prob_vec)
            step = self.model.generate_step(cmd, Action( cmd, strategy) )
            agent_output.time[ i ]    = step.time
            agent_output.success[ i ] = step.success
            agent_output.action[ i ]  = step.action

            model_output.menu [ i ]     = probs[ Strategy.MENU ]
            model_output.hotkey [ i ]   = probs[ Strategy.HOTKEY ]
            model_output.learning [ i ] = probs[ Strategy.LEARNING ]
            
            self.model.update_model( step )

        t = TIME.time() - start
        return agent_output, model_output, t


    ######################################
    def run_debug( self ):
        start = TIME.time()
        res = Fit_Output_Debug( len( self.user_input ) )
        i = 0
        for cmd, action, time, success in zip( self.user_input, self.user_output.action, self.user_output.time, self.user_output.success ) :                
            res.prob[ i ] = self.model.prob_from_action( action )
            prob_vec = self.model.action_probs( cmd )
            a_vec = self.model.get_actions_from( cmd )
            probs = values_long_format(a_vec, prob_vec)
            res.output.menu[ i ]     = probs[ Strategy.MENU ]
            res.output.hotkey[ i ]   = probs[ Strategy.HOTKEY ]
            res.output.learning[ i ] = probs[ Strategy.LEARNING ]
            res.output.meta_info_1[ i ] = self.model.meta_info_1( cmd )
            res.output.meta_info_2[ i ] = self.model.meta_info_2( cmd )

            user_step = StepResult( cmd, Action( cmd, action.strategy ),  time, success )
            self.model.update_model( user_step )
            i = i + 1
        res.time = TIME.time() - start
        return res



##########################################
#                                        #
#             MODEL SIMULATION           #
#                                        #
##########################################
class Model_Simulation( object ):

    ######################################
    def __init__( self, debug = False ):
        self.command_ids = []                       # Type int
        self.model_vec    = []                      # Type Model_Interface
        self.user_data_vec = []                     # Type User_Data
        self.method = Simulation()
        self.debug = debug
        self.debug_var = 0
        

    ######################################
    def backup_parameters( self, parameters, timestamp ):
        path = "./backup/" + timestamp + "/"
        filename = parameters.name + "_model.csv"
        Parameters_Export.write( parameters, path, filename )


    ######################################
    #
    # Output: vector< Simulation_Result >
    # Simulation_Result {name (string), user_id (int), input (list<int>  of command ids), output ( list<Output> ), prob ( list<Model_Output> ), time (float) }
    #
    ######################################
    def run( self ):
        result = []                               # Type Model_Result
        for model in self.model_vec:

            self.method.model    = model
            start = TIME.time()
            
            for i , user_data in enumerate( self.user_data_vec ):
                simulation_result    = Simulation_Result( model.name )
                simulation_result.user_id = user_data.id
                simulation_result.technique_name = user_data.technique_name
                simulation_result.input = user_data.cmd

                model.reset( self.command_ids, strategies_from_technique( user_data.technique_name ) )
                self.method.model = model
                self.method.user_input  = user_data.cmd
                agent_output = None
                model_ouput  = None
                time = 0
                if self.debug :
                    agent_output, model_output, time = self.method.run_debug()
                else :
                    agent_output, model_output, time = self.method.run()
                simulation_result.output = agent_output
                simulation_result.prob   = model_output
                simulation_result.time   = time

                result.append( simulation_result )
                    
        return result 





if __name__=="__main__":
    # available_strategies = [ Strategy.MENU , Strategy.HOTKEY , Strategy.LEARNING ] 
    # cmd_id = 1
    # start = TIME.time()
    # #res = [None] * len( available_strategies )
    # #for i, s in enumerate( available_strategies ):
    # #    res[i] = Action( cmd_id , s )
    # res = [ Action(cmd_id, s) for s in available_strategies ]     
    # stop = TIME.time()
    # print( "time:", stop - start, "res : " , res )
    # exit(0)
    
    print("run Simulation")

    path = './data/user_data.csv'
    loader = User_Data_Loader()
    users_data = loader.load( path )
    print( "number of users: ", len(users_data) )
    my_filter = Filter( user_min = 1, user_max = 1 )
    filtered_users_data = my_filter.filter( users_data )
    print( len( filtered_users_data ), "users data once filtered" )

    
    simulation = Model_Simulation( debug = False)
    simulation.command_ids = [ i for i in range(0, 14) ]
    simulation.model_vec = [ Alpha_Beta_Model( 'RW' ) ]
    simulation.user_data_vec = filtered_users_data

    simulated_data = simulation.run()
    for data in simulated_data :
        print( data.user_id, data.technique_name, round( data.time, 2 ) )









