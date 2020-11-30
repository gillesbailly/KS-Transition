import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from sklearn.metrics import mean_squared_error
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
        self.toolbar = NavigationToolbar(self.canvas, self )
        self.l.addWidget( self.toolbar )
        self.l.addWidget( self.canvas )


        bar_width = 0.2
        opacity   = 0.8
        ci = None
        self.figure.clear()
        n_rows = 4
        n_cols = 1
        
        model_df = pd.concat( [ user_df, model_simulation_df ], ignore_index=True )

        model_df['success_plot'] = model_df['success'] * 100
        model_df['hotkey'] = 0
        model_df.loc[ model_df.strategy == Strategy.HOTKEY, 'hotkey' ] = 100
        model_df['hotkey_success'] = 0
        model_df.loc[ (model_df.strategy == Strategy.HOTKEY) & (model_df.success == 1), 'hotkey_success' ] = 100
        
        model_df.loc[ model_df.model == 'Observations', 'variant'] = ''
        model_df[ 'name' ] = model_df[ 'variant' ]
        model_df.loc[ model_df.variant == '', 'name'] = model_df[ 'model' ]

        model_vec = list( model_df.name.unique() )
        print("model_vec", model_vec)
        model_vec.remove( 'Observations')
        n_cols = len( model_vec )
        #dependent variables: time, hotkey, success_plot, hotkey_success,
        #independent variables: model, user_id, technique_name, block_id
        #model_df = model_df.groupby([]) 
        
        for i, model_name in enumerate( model_vec ) :
            
            style_order = [model_name, 'Observations']
            df = model_df[ (model_df['name'] == model_name) | (model_df['name'] == 'Observations') ]
            mean_df = df.groupby(['name', 'block_id', 'technique_name']).mean()
            mean_df = mean_df.add_suffix('_mean').reset_index()
            
            ax = self.figure.add_subplot( n_rows, n_cols, 1 + i )
            sns.lineplot( x='block_id', y="time", hue="technique_name", ci = ci, style = 'name', style_order = style_order, data=df )
            self.add_mse( mean_df, model_name, 'time_mean' , ax, 0, 1 )

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
            sns.lineplot( x='block_id', y='success_plot', hue="technique_name", ci = ci, style = 'name', style_order = style_order, data=df )
            self.add_mse( mean_df, model_name, 'success_plot_mean' , ax, 0, 83 )

            plt.ylabel( 'Correct Execution (%)' )
            plt.xlabel( '' )
            plt.ylim( 80, 100 )
            ax.legend().remove()

            ax = self.figure.add_subplot( n_rows, n_cols, 2 * n_cols + i + 1)
            sns.lineplot( x='block_id', y='hotkey', hue="technique_name", ci = ci, style = 'name', style_order = style_order, data=df )
            self.add_mse( mean_df, model_name, 'hotkey_mean' , ax, 0, 80 )

            plt.xlabel( '' )
            plt.ylabel( 'Hotkey Use (%)' )
            plt.ylim( 0, 100 )
            ax.legend().remove()

            ax = self.figure.add_subplot( n_rows, n_cols, 3 * n_cols + i + 1)
            sns.lineplot( x='block_id', y='hotkey_success', hue="technique_name", ci = ci, style = 'name', style_order = style_order, data=df )
            self.add_mse( mean_df, model_name, 'hotkey_success_mean' , ax, 0, 80 )

            plt.xlabel( 'Block id' )
            plt.ylabel( 'Correct Hotkey Use (%)' )
            plt.ylim( 0, 100 )
            ax.legend().remove()



        #plt.tight_layout()
        self.canvas.draw()
        self.show()


    ####################################
    def add_mse( self, mean_df, model_name, col_name, ax , x, y):
        mse_vec = [0,0,0]
        technique_vec = ['traditional', 'audio', 'disable']
        for i, technique in enumerate( technique_vec) :
            #print( tech_df )
            #print( mean_df.columns )
            #print( mean_df  )
            tech_df = mean_df.loc[ mean_df.technique_name == technique, : ]
            #tech_df = tech_df.copy()
            #tech_df.reset_index()
            #print(tech_df)
            y_true = tech_df.loc[ tech_df.name == 'Observations', col_name ]
            y_pred = tech_df.loc[ tech_df.name == model_name    , col_name ] 
            mse_vec[ i ] = round( mean_squared_error( y_true, y_pred ), 2 )


        y_true = mean_df.loc[ mean_df.name == 'Observations', col_name ]
        y_pred = mean_df.loc[ mean_df.name == model_name    , col_name ] 
        mse = round( mean_squared_error( y_true, y_pred ) , 2 )
        res_str = 'MSE=' + str( mse ) + '\n(' + str( mse_vec[0] ) + '; ' + str( mse_vec[1] )  + '-' + str( mse_vec[2] ) + ')' 
        ax.text(x, y, res_str, fontsize=8) #add text 

    ####################################
    def update_canvas( self, res_vec, users_df ):
        simulation_df = simulation_vec_to_data_frame( res_vec )
        self.update_figure( simulation_df, users_df )



