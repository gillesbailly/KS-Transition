import os
import csv
from dataframe_util import *

class Parameters_Export() :
    name = "Parameters"
    
    ##############################################
    # Type of model_result_vec                   #
    # is a list of Model_Result                  #
    #                                            #
    ##############################################
    def write( model_result_vec, path ):
        parameters_df = model_res_vec_to_data_frame( model_result_vec )
        Parameters_Export.write_from_df( parameters_df, path )


    ##############################################
    # df should contains at least the columns:   #
    #   - Model                                  #
    #   - Parameter                              #
    #   - Value                                  #
    #                                            #
    ##############################################
    def write_from_df( df, path ) :
        if not os.path.exists( path ):
            os.mkdir( path )
        if not set( ['model','parameter', 'value'] ).issubset(df.columns):
            raise ValueError(" the dataframe does not contain the columns model, parameter and value: ", df.columns )
        model_name_vec = df.model.unique()
        user_id_vec    = df.user_id.unique()
        #print( "write all ", df )
        for name in model_name_vec:
            for user_id in user_id_vec:
                sub_df = df[ (df.model == name ) & (df.user_id == user_id ) ]
                if not sub_df.empty : 
                    sub_df.to_csv( path + name + '_model_' + str( user_id ) + '.csv', index=False, mode = 'w' )

    ###############################
    def write_all( paramaters_vec, path ) :
        for parameters in parameters_vec:
            filename = parameters.name + "_model.csv"
            Paramaters_Export.write( parameters, path, filename)

    