import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from PyQt5.QtCore import QCoreApplication
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import seaborn as sns
from gui_util import *



######################################
#                                    #
#          Parameter View            #
#                                    #
######################################
class Parameter_Matrix_View( Serie2DGallery ):
    
    ################################
    def __init__( self ):
        super().__init__()
        self.setMinimumWidth( 250 )
        self.l.setHorizontalSpacing( 1 )
        self.l.setVerticalSpacing( 1 )     
        self.setWidgetResizable( True )
        self.resize( 1400, 1400 )
        self.figure = plt.figure( tight_layout=True )
        self.canvas = FigureCanvas( self.figure )
        self.canvas.setMinimumHeight( 1400 )
        # self.toolbar = NavigationToolbar(self.canvas, self )
        # self.l.addWidget( self.toolbar )
        # self.l.addWidget( self.canvas )

        self.figure = plt.figure( tight_layout=True )
        self.canvas = FigureCanvas( self.figure )
        self.canvas.setMinimumHeight( 1400 )
        self.toolbar = NavigationToolbar(self.canvas, self )
        self.l.addWidget( self.toolbar )
        self.l.addWidget( self.canvas )

        
    ##################################
    def set_data( self, param_df, variant_name ):
        
        self.figure.clear()
        print( sns.__version__ )
        parameters_df = param_df.copy()
        parameters_df = parameters_df[ ( parameters_df.variant == variant_name ) & ( parameters_df.freedom == 1 ) ]
        parameters_df['r_value'] = parameters_df['value'] * parameters_df['freedom'] + parameters_df['default_value'] * (1 - parameters_df['freedom']) 
        df = parameters_df.pivot_table( index = ["user_id", "technique"] , values = "r_value", columns="parameter")
        parameter_vec = list(df.columns)
        if 'ALPHA_IMPLICIT' in parameter_vec and 'ALPHA_EXPLICIT_DIFF' in parameter_vec :
            df[ 'ALPHA_EXPLICIT' ] = df[ 'ALPHA_IMPLICIT' ] + df[ 'ALPHA_EXPLICIT_DIFF' ] 
            parameter_vec = list(df.columns)
            parameter_vec.remove( 'ALPHA_EXPLICIT_DIFF' )
        n = len(parameter_vec )
        df.reset_index(drop=False, inplace=True) 
        df = df.drop( columns= ['user_id'] )
        

        #sns.pairplot( hue = 'technique', palette = technique_hue, markers = technique_marker, data = df ) #failed
        
        
        for i, h_param in enumerate( parameter_vec ) :
            for j, v_param in enumerate( parameter_vec ) :
                ax = self.figure.add_subplot( n, n, j * n + i + 1 )
                if i == j :
                    sns.histplot( x = h_param, hue = 'technique', kde=True, data = df )
                    #print( "i == j.................")
                else:
                    
                    sns.scatterplot( x = h_param, y = v_param, hue = 'technique', style = 'technique', markers = technique_marker, palette = technique_hue, data = df )
                    sns.kdeplot( x = h_param, y = v_param, levels = 1, thresh = 0.25, hue = 'technique', palette = technique_hue, data = df )
                    #sns.distplot( a = df[ h_param ] , rug=True, hist=False )
                    #sns.distplot( a = df[ v_param ] , vertical = True, rug=True, hist=False )
                
                ax.legend().remove()

        # for i, h_param in enumerate( parameter_vec ) :
        #     ax = self.figure.add_subplot( n, n, i * n + i + 1 )
        #     sns.histplot( x = df[ h_param ] )

        #self.hide()
        self.show()




