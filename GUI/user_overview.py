

import sys
sys.path.append("./GUI/")
sys.path.append("./lib/")
sys.path.append("./plugins/")
sys.path.append("./plugins/loader/")
sys.path.append("./plugins/export/")
sys.path.append("./plugins/model/")

import os
import numpy as np
from datetime import datetime
import argparse
import itertools
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication

from gui_util import *
from data_loader import *
from user_data_loader import *
from matplotlib_view import *
from filter import *
######################################
#                                    #
#          TRIAL INFO                #
#                                    #
######################################
class User_Overview(QScrollArea) :

    ##################################
    def __init__(self ):
        super( QScrollArea, self ).__init__()
        
        #self.setBackgroundRole(QPalette.Shadow);
        self.setWidgetResizable( True )
        self.resize( 800, 400 )
        self.setMinimumWidth(250)
        

    ##################################
    def set_users_df(self, _users_df) :
        self.container = QWidget()
        self.l = QVBoxLayout()
        self.container.setLayout( self.l )
        self.setWidget( self.container )
        self.container.show()
        users_df = _users_df.copy()
        users_df[ 'bounded_time' ] = np.where( users_df['time'] > 10, 10, users_df['time'] )
        user_vec = users_df.user_id.unique()

        for i, user_id in enumerate( user_vec ) :
            if i==0:        #Used because there is a bug with the first seaborn plot
                view = EpisodeView()
                df = users_df[ users_df.user_id == user_id ]
                technique_name = df.technique_name.unique()[0]
                view.set_user_df( df, user_id, technique_name )
                view.canvas.show()
                view.canvas.hide()
                
            view = EpisodeView()
            df = users_df[ users_df.user_id == user_id ]
            technique_name = df.technique_name.unique()[0]
            view.set_user_df( df, user_id, technique_name )
            self.l.addWidget( view.canvas )
            QCoreApplication.processEvents()
        self.hide()
        self.show()

   
    
if __name__=="__main__":
    path = './data/user_data.csv'
    loader = User_Data_Loader()
    users_data = loader.load( path )
    print( "data of ", len( users_data ), "participants loaded" )

    my_filter = Filter(user_min= 1, user_max = 5, techniques=["traditional", "audio"] )
    filtered_users_data = my_filter.filter( users_data )
    users_df = user_data_vec_to_data_frame( filtered_users_data )
    app = QApplication(sys.argv)
    
    overview = User_Overview()
    overview.set_users_df( users_df )
    overview.show()

    sys.exit(app.exec_())

