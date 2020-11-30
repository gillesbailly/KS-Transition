import numpy as np
import time as TIME
import pandas as pd
from scipy.optimize import *
import cProfile

from parameters_export import *
from util import *


        
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
        action_prob = np.zeros( len( self.user_input ) )
        for i, (cmd, action, time, success) in enumerate( zip( self.user_input, self.user_output.action, self.user_output.time, self.user_output.success ) ) :                
            action_prob[ i ] = self.model.action_prob( cmd, action )
            #print(cmd, action.strategy, action_prob[i] )
            self.model.update_model( StepResult( cmd, Action( cmd, action.strategy ),  time, success ) )
        return action_prob

    ######################################
    def run_debug( self ):
        n = len( self.user_input )
        action_prob  = np.zeros( n )    #
        actions_prob = np.zeros( ( n, 3 ) ) #n trials x 3 strategies
        meta_info = np.zeros( n )
        for i, (cmd, action, time, success) in enumerate( zip( self.user_input, self.user_output.action, self.user_output.time, self.user_output.success ) ) :                

            actions_prob[ i ] = self.model.action_probs( cmd )
            action_prob[ i ]  = actions_prob[ i ][ action.strategy ]
            meta_info[ i ] = self.model.meta_info_1( cmd )
            # res.output.meta_info_2[ i ] = self.model.meta_info_2( cmd )

            user_step = StepResult( cmd, Action( cmd, action.strategy ),  time, success )
            self.model.update_model( user_step )
        #res.time = TIME.time() - start
        return action_prob, actions_prob, meta_info



##########################################
#                                        #
#             MODEL FITTING              #
#                                        #
##########################################
class Model_Fitting( object ):

    ######################################
    def __init__( self, debug = False ):
        self.command_ids   = []                     # Type list < int > : 
        self.model_vec     = []                     # Type list < Model_Interface >
        self.user_data_vec = []                     # Type list < User_Data >
        self.parameters    = pd.DataFrame()                   # Type Dataframe
        self.method = Individual_Model_Fitting()    
        self.debug = debug
        self.debug_var = 0

        #specific if (1)ILPH model (2) with implicit learning
        self.alpha_implicit_index = 0
        self.alpha_explicit_diff_index  = 0
        
    ######################################
    def is_ILHP_model_with_implicit_learning( self, model_name, free_param_name_vec ):
        print(model_name )
        print( free_param_name_vec)
        if model_name == 'ILHP' and 'ALPHA_IMPLICIT' in free_param_name_vec :
            self.alpha_implicit_index      = free_param_name_vec.index( 'ALPHA_IMPLICIT' )
            self.alpha_explicit_diff_index = free_param_name_vec.index( 'ALPHA_EXPLICIT_DIFF' )
            print( " ILHP with implicit learning" )
            return True
        else:
            return False

    ######################################
    def ILPH_constr_f(self, param_vec):
        if param_vec[ self.alpha_implicit_index ] + param_vec[ self.alpha_explicit_diff_index ] > 1.0 :
            print( "constrained.......")
        return param_vec[ self.alpha_implicit_index ] + param_vec[ self.alpha_explicit_diff_index ]

    ######################################
    def optimize( self ):
        self.is_valid()
        timestamp    = TIME.strftime("%Y-%m-%d-%H-%M-%S", TIME.gmtime() )
        result_vec   = []
        user_id_vec  = [ user_data.id for user_data in self.user_data_vec ]
        #p = cProfile.Profile()
        #p.enable()
        for model in self.model_vec:
            model.params = Parameters( model.long_name(), model.default_parameters_path() ) #needed to get the min and the max
            model_result = Model_Result.create( model, np.array( user_id_vec ), self.debug )
            model_result.n_parameters = model.params.n( Freedom.USER_FREE )   
            for i , user_data in enumerate( self.user_data_vec ):
                model_result.n_observations[ i ] = len( user_data.cmd )
                model_result.technique[ i ]      = user_data.technique_name
                start = TIME.time()
                available_strategies = strategies_from_technique( user_data.technique_name )
                
                self.method.model       = model
                self.method.user_input  = user_data.cmd
                self.method.user_output = user_data.output

                #params = model.get_params()
                free_param_name_vec = []                    # name of the parameters to optimize
                free_param_bnds_vec = []                    # Bounds for parameter values list( [min, max] )
                for param in model.params.values(): 
                    if param.freedom == Freedom.USER_FREE :
                        free_param_name_vec.append( param.name )
                        free_param_bnds_vec.append( [ param.min, param.max ] )
                self.debug_var = 1000000000

                res = None
                if self.is_ILHP_model_with_implicit_learning( model.name, free_param_name_vec ):
                    #nlc = NonlinearConstraint(self.ILPH_constr_f, 0.0, 1.0) #implicit + explicit = 1                  
                    linear_mat = np.zeros( len( free_param_name_vec ) )
                    linear_mat[ self.alpha_implicit_index ] = 1
                    linear_mat[ self.alpha_explicit_diff_index ] = 1
                    print( free_param_name_vec, linear_mat )
                    linear_constraint = LinearConstraint( linear_mat, 0, 1 )
                    print("use constrained optimisation")
                    res = differential_evolution(self.to_minimize,
                                                constraints=(linear_constraint), 
                                                bounds = free_param_bnds_vec, 
                                                args = (free_param_name_vec, self.method, available_strategies ) )
            
                else:
                    res = differential_evolution(self.to_minimize, 
                                                bounds = free_param_bnds_vec, 
                                                args = (free_param_name_vec, self.method, available_strategies ) )
            
                end = TIME.time()
                print("optmize the model: ", model.long_name(), "on user: ", user_data.id, "in ",  round(end - start, 2),"s")
                print( res )

                parameters = Parameters( model.name, model.default_parameters_path() )
                for name, value in zip( free_param_name_vec, res.x ):
                    parameters[ name ].value = value
                

                model_result.log_likelihood[ i ] = - res.fun
                model_result.time[ i ]           = end - start
                model_result.parameters[ i ]     = parameters
                self.backup_parameters( model_result, timestamp ) 
            result_vec.append( model_result )
        #p.disable()
        #p.print_stats()
        return result_vec


    ######################################
    def to_minimize( self, param_value, param_name, method, available_strategies ):
        # assign the novel values of the freeparameters
        for name, value in zip( param_name, param_value ):
             method.model.params[ name ].value = value
        method.model.reset( self.command_ids, available_strategies )
        action_prob_vec = method.run()
        #print(action_prob_vec)
        ll = round( log_likelihood( action_prob_vec ), 3 )
        #print(ll)
        if self.debug_var > - ll :
            self.debug_var = - ll
            print( self.debug_var )
        return - ll

    
    
    ######################################
    def run( self ):
        self.is_valid()
        result = []                                 # Type Model_Result
        for model in self.model_vec:

            self.method.model = model
            user_id_vec  = [ user_data.id for user_data in self.user_data_vec ]
            model_result = Model_Result.create( model, np.array( user_id_vec ), self.debug )
            model_result.n_parameters = model.params.n( Freedom.USER_FREE )
            start = TIME.time()
            
            for i , user_data in enumerate( self.user_data_vec ):
                model_result.n_observations[ i ] = len( user_data.cmd )
                model_result.technique[ i ] = user_data.technique_name
                if not self.parameters.empty :
                    params = parameters_from_df( self.parameters, model, user_data.id )
                    model.params = params
                model.reset( self.command_ids, strategies_from_technique( user_data.technique_name ) )
                self.method.model = model
                self.method.user_input  = user_data.cmd
                self.method.user_output = user_data.output
                
                action_prob_vec  = None
                actions_prob_vec = None
                meta_info_vec = None
                if self.debug :
                    action_prob_vec, actions_prob_vec, meta_info_vec = self.method.run_debug()
                    #model_result.output[ i ] =  goodness_of_fit.output
                    #model_result.prob[ i ]   =  goodness_of_fit.prob
                else :
                    action_prob_vec = self.method.run()

                model_result.prob[ i ]   = action_prob_vec
                model_result.output[ i ] = actions_prob_vec 
                model_result.log_likelihood[ i ] = log_likelihood( action_prob_vec )
                model_result.meta_info[ i ] = meta_info_vec
                #model_result.time[ i ] = goodness_of_fit.time
            
            model_result.whole_time = TIME.time() - start
            result.append( model_result )
        
        return result 

    ######################################
    def backup_parameters( self, parameters, timestamp ):
        path = "./backup/" + timestamp + "/"
        #filename = parameters.name + "_model_"+ str( user_id ) + ".csv"
        Parameters_Export.write( [parameters], path )

    ######################################
    def is_valid( self ):
        res = True
        if len( self.command_ids ) == 0 :
            res = False
            raise ValueError(" Model_Fit: command_ids is empty ")

        if len( self.model_vec ) == 0 :
            res = False
            raise ValueError(" Model_Fit: model_vec is empty ")

        if len( self.user_data_vec ) == 0 : 
            res = False
            raise ValueError(" Model_Fit: user_data_vec is empty ")
        if not res:
            exit(0)
        return True  










