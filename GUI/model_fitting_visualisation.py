import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from gui_util import *
import seaborn as sns
from dataframe_util import *


######################################
#                                    #
#           FITTING TABLE            #
#                                    #
######################################
class Fitting_Table( QWidget ) :

    ##########################
    def __init__( self ):
        super().__init__()
        self.l = QGridLayout()
        self.l.setHorizontalSpacing( 1 )
        self.l.setVerticalSpacing( 1 )
        self.setLayout( self.l )
        self.model_row = dict()
        self.user_col  = dict()
        self.w         = dict()
        self.setMaximumHeight(120)


    ##########################
    def update_data( self, model_fitting_result_vec ):
        self.l.addWidget(QLabel(""),0,0)
        for model_result in model_fitting_result_vec :
            name = model_result.name  if model_result.variant == '' else  model_result.name + ' - ' + model_result.variant
            k = model_result.n_parameters

            row = 0

            if name in self.model_row:
               row = self.model_row[ name ]
            else: 
                row = self.l.rowCount()
                self.model_row[ name ] = row
                self.l.addWidget( QLabel( "<b>" + name + " </b>" ), row, 0 )
            
            for user_id, likelihood, n  in zip( model_result.user_id, model_result.log_likelihood, model_result.n_observations) :
                bic = bic_score(  n, k, likelihood )
                if not user_id in self.user_col :
                    self.l.addWidget(QLabel( str(user_id) ), 0, user_id + 1 )
                key = row * 100 + user_id
                if not key in self.w:
                    bic_label = QLabel( str( round( bic, 2 ) ) )
                    self.w[ key ] = bic_label
                    self.l.addWidget( bic_label, row, user_id+1 )
                else:
                    self.w[ key ].setText( str( round( bic, 2 ) ) )


######################################
#                                    #
#    MODEL FITTING VISUALISATION     #
#                                    #
######################################
class Model_Fitting_Visualisation( Serie2DGallery ):
    
    ################################
    def __init__( self ):
        super().__init__()
        self.setMinimumWidth( 250 )
        self.resize( 750, 900 )
        self.l.setHorizontalSpacing( 1 )
        self.l.setVerticalSpacing( 1 )        
        self.table = Fitting_Table()
        self.table.setSizePolicy( QSizePolicy( QSizePolicy.Minimum, QSizePolicy.Expanding  ) )
        self.l.addWidget( QLabel( 'BIC' ) )
        self.l.addWidget( self.table )

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
#mpl.rcParams["savefig.facecolor"]
        
        self.canvas = FigureCanvas( self.figure )
        self.canvas.setSizePolicy( QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding ) )

        #self.dialog = QDialog()
        #self.dialog.setWindowTitle("Model Fitting Results")
        self.toolbar = NavigationToolbar( self.canvas, self )
        #dialog_layout = QVBoxLayout()
        #self.dialog.setLayout( dialog_layout )
        self.l.addWidget( self.toolbar )
        self.l.addWidget( self.canvas )

    ############################
    def update_table( self, model_result_vec ):
        self.table.update_data( model_result_vec )
        self.table.show()


    ############################
    def update_figure( self, model_result_vec ):
        bar_width = 0.2
        opacity   = 1
        self.figure.clear()
        #plt.subplots_adjust(wspace=0.001, hspace=0.001, left=0.01, right=0.99, bottom=0.01, top=0.99)
        
        fit_df = model_res_vec_to_data_frame( model_result_vec )
        df = fit_df.copy()

        df['log_likelihood'] = - df['log_likelihood']
        df['name'] = df['variant']
        df.loc[ df.variant == '', 'name'] = df[ 'model' ]

        model_color = dict()
        model_color[ 'RW' ] = [153/255, 204/255, 1, 1]
        model_color[ 'RW2' ] = [255/255, 204/255, 1, 1]
        model_color[ 'CK' ] = [1, 153/255, 1, 1]
        model_color[ 'CK2' ] = [1, 153/255, 1, 1]
        model_color[ 'RWCK' ] = [153/255, 51/255, 1, 1]
        model_color[ 'Observations' ] = [1,1,1,1]
        model_color[ 'random' ] = [1,1,153/255,1]
        model_color[ 'ILHP' ] = [153/255,0,0,1]
        model_color[ 'T' ] = [0.5,0.5,0.5,1]
        model_color[ 'T_I' ] = [102/255,255/255,102/255,1]
        model_color[ 'T_H' ] = [0,204/255,0,1]
        model_color[ 'T_P' ] = [0,153/255,0,1]
        model_color[ 'T_I_P' ] = [255/255,51/255,51/255,1]
        model_color[ 'T_I_H' ] = [255/255,0,0,1]
        model_color[ 'T_H_P' ] = [153/255,0,0,1]
        model_color[ 'T_I_H_P' ] = [102/255,51/255,0,1]

        dependent_variable = [ '- Log Likelihood', 'BIC' ]
        for i, v in enumerate( dependent_variable ) :
            ax = self.figure.add_subplot( 3, 2, i + 1 )
            y_value = 'BIC' if v == 'BIC' else 'log_likelihood'
            sns.barplot( x='user_id', y=y_value, hue="name", palette= model_color, data = df )
            ax.set_ylabel( v )
            ax.set_xlabel( "Participant Id" )
            ax.set_title( v )
            if v == 'BIC': 
                 ax.legend( framealpha = 0, fontsize='x-small' )
            else:
                ax.legend().remove()

        # model_color_bis = dict()
        # for model in df['model'].unique() :
        #     model_color_bis[ model ] = model_color[ model ]

        for i, v in enumerate( dependent_variable ) :
            ax = self.figure.add_subplot(3, 2, 3 + i)
            y_value = 'BIC' if v == 'BIC' else 'log_likelihood'
            sns.barplot( x='name', y=y_value, palette= model_color, data = df )
            ax.set_ylabel( v )
            ax.legend().remove()
            

        for k, v in enumerate( dependent_variable ) :
            ax = self.figure.add_subplot( 3, 2, 5+k )
            y_value = 'BIC' if v == 'BIC' else 'log_likelihood'
            sns.barplot( x='technique', y=y_value, hue="name", palette = model_color, data = df )
            ax.set_ylabel( v )
            if v == 'BIC': 
                 ax.legend( framealpha = 0, fontsize='x-small' )
            else:
                ax.legend().remove()

        self.canvas.draw()
        self.show()

    #################################
    def update_canvas( self, res ):
        self.update_figure( res )
        self.update_table( res )






