import sys
import os
import numpy as np
import cProfile
import argparse
import itertools
import time as TIME
from datetime import datetime
from scipy.optimize import *

from parameters_export import *
from data_loader import *
from util import *
from alpha_beta_model import *





##########################################
#                                        #
#               FIT OUTPUT               #
#                                        #
##########################################
class Fit_Output( object ):
    
    ######################################
    def __init__( self, sequence_length) :
        self.prob = np.zeros( sequence_length )
        self.time = 0


#log_likelyhood += log2(user_action_prob)

##########################################
#                                        #
#           FIT OUTPUT DEBUG             #
#                                        #
##########################################
class Fit_Output_Debug( Fit_Output ):
    
    ######################################
    def __init__( self, sequence_length) :
        super().__init__( sequence_length )
        self.output = Model_Output_Debug( sequence_length )

        
##########################################
#                                        #
#      INDIVIDUAL MODEL FITTING          #
#                                        #
##########################################
class Individual_Model_Fitting( object ):

    ######################################
    def __init__( self  ):
        self.user_input = []            # sequence of commands
        self.user_output = None         # Multi sequence : Time, Success, Action
        self.model = None


    ######################################
    def run( self ):
        start = TIME.time()
        res = Fit_Output( len( self.user_input ) )
        i = 0
        for cmd, action, time, success in zip( self.user_input, self.user_output.action, self.user_output.time, self.user_output.success ) :                
            res.prob[ i ] = self.model.prob_from_action( action )
            user_step = StepResult( cmd, Action( cmd, action.strategy ),  time, success )
            self.model.update_model( user_step )
            i = i + 1
        res.time = TIME.time() - start
        return res


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
#             MODEL FITTING              #
#                                        #
##########################################
class Model_Fitting( object ):

    ######################################
    def __init__( self, debug = False ):
        self.command_ids = []                       # Type int
        self.model_vec    = []                      # Type Model_Interface
        self.user_data_vec = []                     # Type User_Data
        self.method = Individual_Model_Fitting()    #
        self.debug = debug
        self.debug_var = 0
        
        
    ######################################
    def optimize( self ):
        timestamp = TIME.strftime("%Y-%m-%d-%H-%M-%S", TIME.gmtime() )
        cp = cProfile.Profile()
        cp.enable()
    
        result_vec = []
        for model in self.model_vec:
            

            for i , user_data in enumerate( self.user_data_vec ):
                model_result = Model_Result.create( model, self.user_data_vec, self.debug )
                start = TIME.time()
                available_strategies = strategies_from_technique( user_data.technique_name )
                
                self.method.model       = model
                self.method.user_input  = user_data.cmd
                self.method.user_output = user_data.output

                params = model.get_params()
                free_param_name_vec = []
                free_param_bnds_vec = []
                for param in params.values(): 
                    if param.freedom == Freedom.USER_FREE :
                        free_param_name_vec.append( param.name )
                        free_param_bnds_vec.append( [ param.min, param.max ] )
                self.debug_var = 1000000000
                res = differential_evolution(self.to_minimize, bounds = free_param_bnds_vec, args = (free_param_name_vec, self.method, available_strategies ) )
            
                end = TIME.time()
                print("optmize the model: ", model.name, "on user: ", user_data.id, "in ",  end - start,"s")
                print( res )

                parameters = Parameters( model.name, model.default_parameters_path() )
                for name, value in zip( free_param_name_vec, res.x ):
                    parameters[ name ].value = value
                self.backup_parameters( parameters, timestamp )

                model_result.log_likelihood[ i ] = - res.fun
                model_result.time[ i ]           = end - start
                model_result.parameters[ i ]     = parameters 
                result_vec.append( model_result )
        
        cp.disable()
        cp.print_stats()
        return result_vec


    ######################################
    def backup_parameters( self, parameters, timestamp ):
        path = "./backup/" + timestamp + "/"
        filename = parameters.name + "_model.csv"
        Parameters_Export.write( parameters, path, filename )


    ######################################
    def to_minimize( self, param_value, param_name, method, available_strategies ):
        # assign the novel values of the freeparameters
        for name, value in zip( param_name, param_value ):
             method.model.params[ name ].value = value
        method.model.reset( self.command_ids, available_strategies )
        goodness_of_fit = method.run()
        if self.debug_var > - log_likelihood( goodness_of_fit.prob ) :
            self.debug_var = - log_likelihood( goodness_of_fit.prob )
            print( self.debug_var )
        return - log_likelihood( goodness_of_fit.prob )


    ######################################
    def run( self ):
        result = []                                 # Type Model_Result
        for model in self.model_vec:

            self.method.model    = model
            model_result = Model_Result.create( model.name, [ user_data.id for user_data in self.user_data_vec ], self.debug )

            start = TIME.time()
            
            for i , user_data in enumerate( self.user_data_vec ):

                model.reset( self.command_ids, strategies_from_technique( user_data.technique_name ) )
                self.method.model = model
                self.method.user_input  = user_data.cmd
                self.method.user_output = user_data.output
                
                goodness_of_fit = None
                if self.debug :
                    goodness_of_fit = self.method.run_debug()
                    model_result.output[ i ] =  goodness_of_fit.output
                    model_result.prob[ i ]   =  goodness_of_fit.prob
                else :
                    goodness_of_fit = self.method.run()

                model_result.log_likelihood[ i ] = log_likelihood( goodness_of_fit.prob )
                model_result.time[ i ] = goodness_of_fit.time
            
            model_result.whole_time = TIME.time() - start
            result.append( model_result )
        
        return result 


    # ###################################
    # def init_model_result( self, model, user_data_vec, debug ) :
    #     model_result         = Model_Result( model.name )
    #     model_result.user_id = [ user_data.id for user_data in user_data_vec ]
    #     model_result.time    = [ 0 ] * len( user_data_vec )
    #     model_result.output  = [ None ] * len( user_data_vec) if debug else []
    #     model_result.parameters  = [ None ] * len( user_data_vec) 
    #     model_result.log_likelihood = [ 0 ] * len( user_data_vec )

        return model_result




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
    
    print("run Individual Fitting")

    path = './experiment/hotkeys_formatted_dirty.csv'
    parser = argparse.ArgumentParser()
    parser.add_argument( "-p", "--path", help="path of the empirical data" )
    
    args = parser.parse_args()
    if args.path != None :
        path = args.path
    print("sequences path: ", path)
    loader = HotkeyCoach_Loader()
    users_data = loader.experiment( path )
    print( len( users_data ), "users data loaded" )


    my_filter = Filter()
    filtered_users_data = my_filter.filter( users_data )
    print( len( filtered_users_data ), "users data once filtered" )

    env = Environment( './parameters/env_M2_H0.9_L1.8_P3.csv' )
    #env.commands = user_0.command_info.id
    
    fit = Model_Fitting( debug = True)
    fit.command_ids = [ i for i in range(0, 14) ]
    fit.model_vec = [ Alpha_Beta_Model( env, 'RW' ), Alpha_Beta_Model( env, 'RW_CK' ) ]
    fit.user_data_vec = filtered_users_data

    goodness_of_fit_vec = fit.run()
    for goodness_of_fit in goodness_of_fit_vec :
        print( goodness_of_fit.name, goodness_of_fit.time,  goodness_of_fit.log_likelihood )









