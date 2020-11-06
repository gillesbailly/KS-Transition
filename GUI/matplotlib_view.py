from PyQt5.QtCore import pyqtSignal, Qt, QObject
from PyQt5.QtWidgets import QSlider, QComboBox, QLabel, QWidget, QHBoxLayout
from util import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.lines import *

import matplotlib.pyplot as plt
import seaborn as sns


max_y = 10




                
##########################################
#                                        #
#    Draw Information for one user       #
#                                        #
##########################################
class EpisodeView( QObject ):
    view_selected = pyqtSignal( int, int, int ) #user id, cmd, trial_id
    cursor_moved = pyqtSignal( int )

    def __init__(self):
        super().__init__()

        self.figure = plt.figure( tight_layout = True )       

        COLOR = 'white'
        plt.rcParams[ 'text.color'      ] = COLOR
        plt.rcParams[ 'axes.labelcolor' ] = COLOR
        plt.rcParams[ 'xtick.color'     ] = COLOR
        plt.rcParams[ 'ytick.color'     ] = COLOR
        plt.rcParams[ 'font.size'       ] = 8
        plt.rcParams[ 'figure.facecolor'] = 'dimgray'
        plt.rcParams[ 'axes.facecolor'  ] = 'dimgray'
        self.canvas = FigureCanvas( self.figure )
        #self.toolbar = NavigationToolbar(self.canvas, self.dialog)
        self.canvas.setMinimumHeight(200)
        self.canvas.setMaximumHeight(200)        
        self.canvas.setMinimumWidth(750)
        #self.canvas.mpl_connect( 'button_press_event', self.button_press_callback )
        self.canvas.mpl_connect('button_press_event', self.on_button_press )
        self.canvas.draw()
        self.canvas.show()
        self.cmd            = -1
        self.user_id        = -1
        self.technique_name = ""
        self.trial_id       = -1
        self.model_name     = "None"
        self.strategy_color = dict()
        self.strategy_color[ 0 ] = [0/255, 0/255, 1, 0.8]
        self.strategy_color[ 1 ] = [0/255, 1, 0, 0.8]
        self.strategy_color[ 2 ] = [1, 153/255, 0, 0.8]

        self.transition_color = [255/255,100/255,50/255,0.2]

    def set_user_df( self, user_df, user_id, technique_name ):
        self.figure.clear()
        self.user_id = user_id
        self.technique_name = technique_name
        title = "User: " + str( self.user_id) + " - technique: " + technique_name
        s_size = np.full( user_df.shape[0] , 1 )
        s_line_width = np.full( user_df.shape[0] , 0 )

        #self.ax = sns.scatterplot( x='trial_id', y='bounded_time', hue="strategy", palette = self.strategy_color, size =1, linewidth = 0, data=user_df )
        self.ax = sns.scatterplot( x='trial_id', y='bounded_time', hue="strategy", palette = self.strategy_color, size = s_size , linewidth = s_line_width, data=user_df )
        
        self.ax.set_title( title )
        self.ax.set_ylabel( 'Time (s)' )
        self.ax.set_xlabel( 'Trial id' )
        self.ax.set_ylim( 0, 10 )
        self.ax.set_xlim( 0, 750 )

        legend_labels = ['Menu', 'Hotkey', 'Learning']

        # Custom legend
        legend_patches = [Line2D( [0], [0], marker='o', color=C, label=L ) for 
        C, L in zip(self.strategy_color.values(), legend_labels) ] 


        plt.legend(handles=legend_patches) 
        self.canvas.draw()
        self.canvas.show()

    ###########################    
    def set_user_cmd_df(self, user_df, user_id, cmd, technique_name):
        self.user_id = user_id
        self.cmd = cmd
        self.technique_name = technique_name
        self.figure.clear()
        s_size = np.full( user_df.shape[0] , 1 )
        s_line_width = np.full( user_df.shape[0] , 0 )

        start_transition = np.mean( user_df.start_transition ) 
        stop_transition  = np.mean( user_df.stop_transition )
        #self.add_transition_region( self.x_start_transition( user_data, cmd ), self.x_stop_transition( user_data, cmd ) )
        title = "User: " + str( self.user_id) + " - Cmd: " + str( self.cmd ) + " - technique: " + self.technique_name
        plt.fill_between( [start_transition, stop_transition ] , 0, 10, color=self.transition_color )
        self.ax = sns.scatterplot( x='trial_id', y='bounded_time', hue="strategy", palette = self.strategy_color, size = s_size, linewidth = s_line_width, data=user_df )
        self.ax.set_title( title )
        self.ax.set_ylabel( 'Time (s)' )
        self.ax.set_xlabel( 'Trial id' )
        self.ax.set_ylim( 0, 10 )
        self.ax.set_xlim( 0, 750 )
        
        self.ax.get_legend().remove()
        self.canvas.draw()
        self.canvas.show()

    ############################
    def set_model_data( self, user_df, user_id, cmd, technique_name, model_name ):
        self.user_id = user_id
        self.cmd = cmd
        self.technique_name = technique_name
        self.model_name = model_name
        self.figure.clear()
        s_size = np.full( user_df.shape[0] , 1 )
        s_line_width = np.full( user_df.shape[0] , 0 )

        #self.add_transition_region( self.x_start_transition( user_data, cmd ), self.x_stop_transition( user_data, cmd ) )
        title = "User: " + str( self.user_id) + " - Cmd: " + str( self.cmd ) + " - technique: " + self.technique_name
        self.ax = sns.scatterplot( x='trial_id', y='bounded_time', hue="strategy", palette = self.strategy_color, size =s_size, linewidth = s_line_width, data=user_df )
        self.ax.set_title( title )
        self.ax.set_ylabel( 'Time (s)' )
        self.ax.set_xlabel( 'Trial id' )
        self.ax.set_ylim( 0, 10 )
        self.ax.set_xlim( 0, 750 )
        if 'model_prob' in user_df.columns:
            self.ax.plot( user_df['trial_id'], user_df['model_prob'], linewidth=3 , color = [1,1,1,1] )
        self.ax.plot( user_df['trial_id'], user_df['menu_prob'], color = self.strategy_color[0] )
        self.ax.plot( user_df['trial_id'], user_df['hotkey_prob'], color = self.strategy_color[1] )
        self.ax.plot( user_df['trial_id'], user_df['learning_prob'], color = self.strategy_color[2] )
         
        self.ax.get_legend().remove()
        self.canvas.draw()
        self.canvas.show()
        # self.model_name = model_name
        

    ###########################
    def on_button_press( self, event ):
        print( 'on click ' )
        trial_id = int( event.xdata )
        self.view_selected.emit( self.user_id, self.cmd, trial_id )
       

    ############################
    def add_cursor_line( self ) :
        pass

        

    

    

    
    
    

