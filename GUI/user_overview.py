import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import QCoreApplication

from matplotlib_view import EpisodeView

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

   


