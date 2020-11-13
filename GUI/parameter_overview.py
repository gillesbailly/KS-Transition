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
#          TRIAL INFO                #
#                                    #
######################################
class Parameter_Overview( Serie2DGallery ):
    
    ################################
    def __init__( self ):
        super().__init__()
        self.setMinimumWidth( 250 )
        self.l.setHorizontalSpacing( 1 )
        self.l.setVerticalSpacing( 1 )     
        self.setWidgetResizable( True )
        self.resize( 1000, 800 )
        self.setMinimumWidth(250)
        self.max_params = 6
        self.figure = None
        

    ##################################
    def set_df(self, parameters_df) :
        self.figure = plt.figure( tight_layout=True )
        self.figure.patch.set_facecolor( [53./255, 53./255, 53./255] )
        COLOR = 'white'
        plt.rcParams[ 'text.color'      ] = COLOR
        plt.rcParams[ 'axes.labelcolor' ] = COLOR
        plt.rcParams[ 'xtick.color'     ] = COLOR
        plt.rcParams[ 'ytick.color'     ] = COLOR
        plt.rcParams[ 'font.size'       ] = 8
        plt.rcParams[ 'figure.facecolor'] = 'dimgray'
        plt.rcParams[ 'axes.facecolor'  ] = 'dimgray'
        
        self.canvas = FigureCanvas( self.figure )
        self.canvas.setMinimumHeight( 1500 )
#        self.canvas.setSizePolicy( QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding ) )
        self.toolbar = NavigationToolbar(self.canvas, self )
        self.l.addWidget( self.toolbar )
        self.l.addWidget( self.canvas )
        self.figure.clear()
        parameters_df = parameters_df[ parameters_df.freedom == 1] 
        model_vec = parameters_df['model'].unique()
        n_rows = len( model_vec )
        n_cols = 6 # max number of parameters

        for i, model in enumerate( model_vec ) :
            model_df = parameters_df[ parameters_df.model == model ]
            model_df = model_df.copy()

            parameter_vec = model_df.parameter.unique()
            parameter_vec = parameter_vec[0: np.min([len(parameter_vec ), 6]) ]
            #print(parameter_vec)
            for j, parameter in enumerate( parameter_vec ):
                parameter_df = model_df[ model_df.parameter == parameter ]
                #print( "parameter freedom", parameter_df['freedom'] )
                ax = self.figure.add_subplot( n_rows, n_cols, i*n_cols + j + 1 )
            #print(parameter_df)
                technique = np.array( ['traditional', 'audio'] )
                sns.boxplot( x= 'technique', order= technique, y="value", data=parameter_df, whis=[0, 100], palette="vlag")
                sns.stripplot( x= 'technique', order=technique, y="value", data=parameter_df, size=4, color=".3", linewidth=0)
                ax.set_ylabel( model + ' - ' + parameter )
                #ax.set_title( model +' - ' + parameter)

        self.hide()
        self.show()

