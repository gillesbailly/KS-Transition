import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import seaborn as sns

from gui_util import *
from dataframe_util import *


######################################
#                                    #
#    MODEL FITTING VISUALISATION     #
#                                    #
######################################
class Model_Simulation_Visualisation( Serie2DGallery ):
    
    ################################
    def __init__( self ):
        super().__init__()
        self.setMinimumWidth( 250 )
        self.l.setHorizontalSpacing( 1 )
        self.l.setVerticalSpacing( 1 )
        self.resize( 700, 800)
        
        #self.table = Fitting_Table()
        #self.l.addWidget( self.table, 0, 0 )

        

    ############################
    def update_figure( self, model_simulation_df, user_df ):
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
        self.canvas.setSizePolicy( QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding ) )
        # self.dialog = QDialog()
        # self.dialog.setWindowTitle( "Model Simulation Results" )
        self.toolbar = NavigationToolbar(self.canvas, self )
        # dialog_layout = QVBoxLayout()
        # self.dialog.setLayout( dialog_layout )
        # dialog_layout.addWidget( self.toolbar )
        # dialog_layout.addWidget( self.canvas  )
        self.l.addWidget( self.toolbar )
        self.l.addWidget( self.canvas )


        bar_width = 0.2
        opacity   = 0.8
        ci = None
        self.figure.clear()
        n_rows = 4
        n_cols = 1
        
        model_df = pd.concat( [ user_df, model_simulation_df ] )

        model_df['success_plot'] = model_df['success'] * 100
        model_df['hotkey'] = 0
        model_df.loc[ model_df.strategy == Strategy.HOTKEY, 'hotkey' ] = 100
        model_df['hotkey_success'] = 0
        model_df.loc[ (model_df.strategy == Strategy.HOTKEY) & (model_df.success == 1), 'hotkey_success' ] = 100
        
        model_vec = list( model_df.model.unique() )
        model_vec.remove( 'Observations')
        n_cols = len( model_vec )
        #dependent variables: time, hotkey, success_plot, hotkey_success,
        #independent variables: model, user_id, technique_name, block_id
        #model_df = model_df.groupby([]) 
        
        for i, model_name in enumerate( model_vec ) :
            
            style_order = [model_name, 'Observations']
            df = model_df[ (model_df['model'] == model_name) | (model_df['model'] == 'Observations') ]
            
            ax = self.figure.add_subplot( n_rows, n_cols, 1 + i )
            sns.lineplot( x='block_id', y="time", hue="technique_name", ci = ci, style = 'model', style_order = style_order, data=df )
            
            plt.title( model_name )
            plt.ylabel( 'Time' )
            plt.xlabel( '' )
            plt.ylim( 0, 6 )
            if i == n_cols -1 :
                #ax.legend().texts[5].set_text("Predictions")
                pass
            else:
                ax.legend().remove()

            ax = self.figure.add_subplot( n_rows, n_cols, n_cols + i + 1 )
            sns.lineplot( x='block_id', y='success_plot', hue="technique_name", ci = ci, style = 'model', style_order = style_order, data=df )
            plt.ylabel( 'Correct Execution (%)' )
            plt.xlabel( '' )
            plt.ylim( 80, 100 )
            ax.legend().remove()

            ax = self.figure.add_subplot( n_rows, n_cols, 2*n_cols + i + 1)
            sns.lineplot( x='block_id', y='hotkey', hue="technique_name", ci = ci, style = 'model', style_order = style_order, data=df )
            plt.xlabel( '' )
            plt.ylabel( 'Hotkey Use (%)' )
            plt.ylim( 0, 100 )
            ax.legend().remove()

            ax = self.figure.add_subplot( n_rows, n_cols, 3*n_cols + i + 1)
            sns.lineplot( x='block_id', y='hotkey_success', hue="technique_name", ci = ci, style = 'model', style_order = style_order, data=df )
            plt.xlabel( 'Block id' )
            plt.ylabel( 'Correct Hotkey Use (%)' )
            plt.ylim( 0, 100 )
            ax.legend().remove()



        #plt.tight_layout()
        self.canvas.draw()
        self.show()


    ####################################
    def update_canvas( self, res_vec, users_df ):
        simulation_df = simulation_vec_to_data_frame( res_vec )
        self.update_figure( simulation_df, users_df )



