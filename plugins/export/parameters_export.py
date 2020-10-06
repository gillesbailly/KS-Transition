import os
import csv
from util import *

class Parameters_Export( object ) :

    ###############################
    def __init__( self ) :
        self.name = "Parameters"
    
    ###############################
    def write_all( paramaters_vec, path ) :
        for parameters in parameters_vec:
            filename = parameters.name + "_model.csv"
            Paramaters_Export.write( parameters, path, filename)

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

