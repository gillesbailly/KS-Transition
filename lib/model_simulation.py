#import numpy as np
import pandas as pd
import time as TIME

from util import *
from dataframe_util import *

##########################################
#                                        #
#             MODEL SIMULATION           #
#                                        #
##########################################
class Model_Simulation( object ):

    ######################################
    def __init__( self, debug = False ):
        self.command_ids   = []                     # Type int
        self.model_vec     = []                     # Type Model_Interface
        self.user_data_vec = []                     # Type User_Data
        self.n_simulations = 10                     # Type int
        self.parameters    = pd.DataFrame()         # Type DataFrame
        self.debug  = debug
        self.debug_var = 0
    

    ##########################################################################
    # Given a sequence of commands, the model produces a sequence of actions #
    # INPUT                                                                  #
    #   - model ( Model ) : model (see model_interface.py)                   #
    #   - cmd_sequence ( list< int > ) : sequence of command ids             #
    # OUTPUT                                                                 #
    #   - agent_output ( User_Ouput ) : what the agent produces. See util.py #
    #   - model_output ( Model_Output ): see util.py                         #
    ##########################################################################

    def simulate( self, model, cmd_sequence ):
        agent_output = User_Output(  len( cmd_sequence ) )         # Multi sequence : Time, Success, Action
        #model_output = Model_Output( len( cmd_sequence ) )
        actions_prob = np.zeros( (len(cmd_sequence) , 3) ) 
        
        # TOOD 5.a
        # use the methods selecte_strategy, generate_step and update_model from Model (model_interface.py)
        for i, cmd in enumerate( cmd_sequence ):
            strategy, probs = model.select_strategy( cmd )
            step = model.generate_step( cmd, Action( cmd, strategy) )
            model.update_model( step )
            agent_output.time[ i ]    = step.time
            agent_output.success[ i ] = step.success
            agent_output.action[ i ]  = step.action
            actions_prob[ i ] = probs 
            #model_output.menu [ i ]     = probs[ Strategy.MENU ]
            #model_output.hotkey [ i ]   = probs[ Strategy.HOTKEY ]
            #model_output.learning [ i ] = probs[ Strategy.LEARNING ]

        return agent_output, actions_prob



    ######################################
    #
    # Output: vector< Simulation_Result >
    # Simulation_Result {name (string), user_id (int), input (list<int>  of command ids), output ( list<Output> ), prob ( list<Model_Output> ), time (float) }
    #
    ######################################
    def run( self, parameters = None ):
        result = []                               # Type Model_Result
        for model in self.model_vec:
            print("simulation of the model:", model.long_name())
            start = TIME.time()
            for i , user_data in enumerate( self.user_data_vec ):
                simulation_result           = Simulation_Result( self.n_simulations, model )
                simulation_result.user_data = user_data
                if not self.parameters.empty :
                    params = parameters_from_df( self.parameters, model, user_data.id )
                    model.params = params
                for k in range(0, self.n_simulations ):
                    model.reset( self.command_ids, strategies_from_technique( user_data.technique_name ) )
                    agent_output, actions_prob = self.simulate( model, user_data.cmd )
                    simulation_result.output[ k ] = agent_output
                    simulation_result.prob[ k ]   = actions_prob
                    #simulation_result.whole_time += time

                result.append( simulation_result )
                    
        return result 


