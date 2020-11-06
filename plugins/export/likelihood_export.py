import os
import csv
from util import *
import pandas as pd

class Likelihood_Export( object ) :

   name = "Likelihood"
   
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

