import csv
from util import *

class User_Data_Export( object ) :

    ###############################
    def __init__( self ) :
        self.name = "User Data"
        

    ###############################
    def write( user_data_vec, folder, filename ):
        with open( folder + filename, mode='w' ) as log_file:
            writer = csv.writer( log_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL )
            header_flag = True
            for user_data in user_data_vec :
                for trial_id in range( 0, len( user_data.cmd ) ) :
                    trial_info = user_data.trial_info( trial_id )
                    if header_flag :
                        header_flag = False
                        header = [ key.replace( ' ' , '_' ) for key in trial_info.keys() ]
                        writer.writerow( header )
                    row = list( trial_info.values() )
                    print(row)
                    writer.writerow( row )

