from os import listdir
from os.path import isfile, join
import pandas as pd
import numpy as np


##########################################
#                                        #
#         USER DATA LOADER               #
#                                        #
##########################################
class Parameters_Loader():

    def load( path ):
        file_vec = [f for f in listdir(path) if isfile(join(path, f))]
        df = pd.DataFrame()
        for file in file_vec:
            df_model_user = pd.read_csv( path+file )
            df = pd.concat( [df, df_model_user] )
        df = df.replace(np.nan, '', regex=True)
        return df


    
