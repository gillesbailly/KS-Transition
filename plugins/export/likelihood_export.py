import os
import csv
from util import *
import pandas as pd

class Likelihood_Export( object ) :

    ###############################
    def __init__( self ) :
        self.name = "Likelihood"
    

############################
    # def __init__( self, name = "" ):
    #     self.name           = name
    #     self.user_id        = np.array([], dtype=int)
    #     self.log_likelihood = np.array([])
    #     self.prob           = []    # proability to peform the user action
    #     self.output         = []    # output: {menu, hotkey, learning } vector<float>, probability to perform the conrresponding strategy
    #     self.time           = []    #time of the simulation
    #     self.parameters     = []
    #     self.whole_time     = 0
    #     self.n_observations = np.array([], dtype=int)
    #     self.n_parameters       = 0 

    ###############################
    def write_all( df, path ) :
        model_name_vec = df.model.unique()
        user_id_vec    = df.user_id.unique()
        print( "write all ", df )
        for name in model_name_vec:
            for user_id in user_id_vec:
                sub_df = df[ (df.model == name ) & (df.user_id == user_id ) ]
                print("sub_df ", sub_df) 
                if not sub_df.empty : 
                    sub_df.to_csv( path + name + '_model_' + str( user_id ) + '.csv', index=False )


        # columns = np.array( ['model', 'user_id', 'parameter', 'value', 'freedom', 'log_likelihood', 'n_observations', 'n_parameters', 'bic'] )
        
        # row = dict()
        # for model_result in model_result_vec :
        #     for i, user_id in enumerate( model_result.user_id ) :
        #         df = pd.DataFrame( columns = columns )
        #         row[ 'model' ]          = model_result.name
        #         row[ 'n_parameters']    = model_result.n_parameters
        #         row[ 'user_id' ]        = user_id
        #         row[ 'log_likelihood' ] = round( model_result.log_likelihood[ i ], 2)
        #         row[ 'n_observations' ] = model_result.n_observations[ i ]
        #         row [ 'bic' ]           = row[ 'n_parameters'] * row[ 'n_observations' ] - 2 * row[ 'log_likelihood' ]
        #         for parameter in model_result.parameters[ i ].values() :
        #             row[ 'parameter' ] = parameter.name
        #             row[ 'value'     ] = round( parameter.value, 5)
        #             row[ 'freedom'   ] = parameter.freedom
        #             df = df.append( row, ignore_index = True )
        #         print("write all debug:", path, model_result.name, user_id)
        #         print( df )
        #         df.to_csv( path + model_result.name + '_model_' + str( user_id ) + '.csv', index=False )









        

    ###############################
    def write( parameters, path, filename ):
        if not os.path.exists( path ):
            os.mkdir( path )

        with open( path + filename, mode='w' ) as log_file:
            writer = csv.writer( log_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL )
            header_flag = True
            for param in parameters.values() :
                if header_flag :
                    header_flag = False
                    header = ["name", "value", "min", "max", "step", "freedom", "comment"]
                    writer.writerow( header )
                
                row = [ param.name, str( round( param.value, 3 ) ), str( param.min ), str( param.max ), str( param.step ), str( param.freedom ), param.comment ]
                writer.writerow( row )

