
import pandas as pd
import numpy as np
from util import *
from parameters import Parameter, Parameters

###########################
def model_res_vec_to_data_frame( model_result_vec ):
    columns = np.array( ['model', 'variant', 'user_id', 'technique', 'parameter', 'value', 'min', 'max', 'default_value', 'freedom', 'comment', 'log_likelihood', 'n_observations', 'n_parameters', 'BIC'] )
    
    df = pd.DataFrame( columns = columns )    
    row = dict()
    for model_result in model_result_vec :
        for i, user_id in enumerate( model_result.user_id ) :
            row[ 'model' ]          = model_result.name
            row[ 'variant' ]        = model_result.variant
            row[ 'n_parameters']    = model_result.n_parameters
            row[ 'user_id' ]        = user_id
            row[ 'technique']       = model_result.technique[i]
            row[ 'log_likelihood' ] = round( model_result.log_likelihood[ i ], 2)
            row[ 'n_observations' ] = float(model_result.n_observations[ i ])
            row [ 'BIC' ]           = bic_score(  row[ 'n_observations' ], row[ 'n_parameters'], row[ 'log_likelihood' ] )
            if model_result.parameters[i]  :
                for parameter in model_result.parameters[ i ].values() :
                    row[ 'parameter' ] = parameter.name
                    row[ 'value' ] = round( parameter.value, 5)
                    row[ 'min'   ] = parameter.min
                    row[ 'max'   ] = parameter.max
                    row[ 'default_value' ] = parameter.default_value                    
                    row[ 'freedom'   ] = parameter.freedom
                    row[ 'comment' ] = parameter.comment
                    df = df.append( row, ignore_index = True )
            else:
                row[ 'parameter' ] = 'none'
                row[ 'value'     ] = 0
                row[ 'min' ] = 0
                row[ 'max' ] = 0
                row[ 'default_value' ] = 0                    
                row[ 'freedom'   ] = 0
                row[ 'comment' ] = ''
                df = df.append( row, ignore_index = True )

    return df



############################
def parameters_from_df( df, model, user_id ):
    print("parameters_from_df for ", model.name, model.variant_name)
    #print(df[df.model == 'RWCK'])

    df = df[ ( df.model == model.name ) & ( df.variant == model.variant_name ) & ( df.user_id == user_id ) ]
    #print( df )
    parameters = Parameters( name = model.long_name() )
    n_row = df.shape[0]
    for i in range( 0, n_row ):
        parameter = Parameter()
        parameter.name    = df.at[i, 'parameter']
        parameter.value   = df.at[i, 'value'] #float( df.at[i, 'value'] ) if '.' in df.at[i, 'value'] else int( df.at[i, 'value'] )
        parameter.min     = df.at[i, 'min']
        parameter.max     = df.at[i, 'max']
        parameter.default_value = df.at[i, 'default_value']
        parameter.freedom = df.at[i, 'freedom']
        parameter.comment = df.at[i, 'comment']
        parameters[ parameter.name ] = parameter
                
    return parameters


############################
def user_data_vec_to_data_frame( user_data_vec ):
    df = pd.DataFrame()
    for user_data in user_data_vec:
        df_user = user_data_to_data_frame( user_data )
        if  df.empty:
            df = df_user
        else:
            df = pd.concat( [df, df_user] )
    return df




############################
def user_data_to_data_frame( user_data ):
    df = pd.DataFrame({    'model'          : 'Observations',
                           'user_id'        : user_data.id,
                           'technique_name' : user_data.technique_name,
                           'block_id'       : user_data.other.block,
                           'trial_id'       : np.arange(0, len( user_data.output.action ) ),
                           'cmd_input'      : user_data.cmd,
                           'time'           : user_data.output.time,
                           'success'        : user_data.output.success,
                           'strategy'       : np.array( [a.strategy for a in user_data.output.action] ),
                           'cmd_output'     : np.array( [a.cmd for a in user_data.output.action] ),
                           'start_transition': 0,
                           'stop_transition'  : 0 })

    cmd_vec = df.cmd_input.unique()
    for cmd in cmd_vec :
        start_transition = user_data.command_info.start_transition[ np.where( user_data.command_info.id == cmd )[ 0 ][ 0 ] ]
        stop_transition   = user_data.command_info.stop_transition  [ np.where( user_data.command_info.id == cmd )[ 0 ][ 0 ] ]
        df.loc[ df.cmd_input == cmd , 'start_transition' ] = start_transition
        df.loc[ df.cmd_input == cmd , 'stop_transition'  ] = stop_transition
        
    return df


############################
def simulation_vec_to_data_frame( model_simulation_vec ):
    df = pd.DataFrame()
    for model_simulation in model_simulation_vec:
        df_model = simulation_to_data_frame( model_simulation )
        if  df.empty:
            df = df_model
        else:
            df = pd.concat( [df, df_model] )
    return df

############################
def simulation_to_data_frame( model_simulation ):
    res_df = pd.DataFrame()
    for k in range(0, model_simulation.n_simulations ):
        prob   = model_simulation.prob[k]
        output = model_simulation.output[k]
        df = pd.DataFrame({'model'          : model_simulation.name,
                           'variant'        : model_simulation.variant,
                           'user_id'        : model_simulation.user_data.id,
                           'simulation'     : k,
                           'technique_name' : model_simulation.user_data.technique_name,
                           'block_id'       : model_simulation.user_data.other.block,
                           'trial_id'       : np.arange(0, len( output.action ) ),
                           'cmd_input'      : model_simulation.user_data.cmd,
                           'menu_prob'      : prob[ :, 0 ],
                           'hotkey_prob'    : prob[ :, 1 ],
                           'learning_prob'  : prob[ :, 2 ],                           
                           'time'           : output.time,
                           'success'        : output.success,
                           'strategy'       : np.array( [a.strategy for a in output.action] ),
                           'cmd_output'     : np.array( [a.cmd for a in output.action] ) })
        if  res_df.empty:
            res_df = df
        else:
            res_df = pd.concat( [res_df, df] )
    return res_df











