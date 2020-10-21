import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSignalMapper, Qt, QObject, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from gui_util import *
from util import *


#########################
def foo( data, indices ):
  d <- data[indices] # allows boot to select sample 
  return( mean( d) )

#########################
def bootstrap_lower_ci( v ) :
  results <- boot(data = v, statistic = foo, R = 1000 )
  ci <- boot.ci(results, type="bca")
  l <- unlist( ci[4] )
  return l[4]

#########################
def bootstrap_upper_ci( v ):
  results <- boot(data = v, statistic = foo, R = 1000 )
  ci <- boot.ci(results, type="bca")
  l <- unlist( ci[4] )
  return l[5]


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

    ##########################
    def update_data( self, model_fitting_result_vec ):
        self.l.addWidget(QLabel(""),0,0)
        for model_result in model_fitting_result_vec :
            name = model_result.name
            row = 0

            if name in self.model_row:
               row = self.model_row[ name ]
            else: 
                row = self.l.rowCount()
                self.model_row[ model_result.name ] = row
                self.l.addWidget( QLabel( "<b>" + name + "</b>" ), row, 0 )
            
            for user_id, likelihood in zip( model_result.user_id, model_result.log_likelihood) :
                if not user_id in self.user_col :
                    self.l.addWidget(QLabel( str(user_id) ), 0, user_id + 1 )
                key = row * 100 + user_id
                if not key in self.w:
                    likelihood_label = QLabel( str( round( likelihood, 2 ) ) )
                    self.w[ key ] = likelihood_label
                    self.l.addWidget( likelihood_label, row, user_id+1 )
                else:
                    self.w[ key ].setText( str( round( likelihood, 2 ) ) )


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
        self.l.setHorizontalSpacing( 1 )
        self.l.setVerticalSpacing( 1 )
        
        self.table = Fitting_Table()
        self.l.addWidget( self.table, 0, 0 )

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
        
        self.canvas = FigureCanvas(self.figure)
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Model Fitting Results")
        self.toolbar = NavigationToolbar(self.canvas, self.dialog)
        dialog_layout = QVBoxLayout()
        self.dialog.setLayout( dialog_layout )
        dialog_layout.addWidget( self.toolbar )
        dialog_layout.addWidget( self.canvas  )

    ############################
    def update_table( self, model_result_vec ):
        self.table.update_data( model_result_vec )
        self.table.show()


    ############################
    def update_figure( self, model_result_vec ):
        bar_width = 0.2
        opacity   = 0.8
        self.figure.clear()
        #plt.subplots_adjust(wspace=0.001, hspace=0.001, left=0.01, right=0.99, bottom=0.01, top=0.99)
        
        dependent_variable = [ '- Log Likelihood', 'BIC' ]
        for i, v in enumerate( dependent_variable ) :
            ax = self.figure.add_subplot( 3, 2, i + 1 )
            plt.title( v )
            plt.xlabel( 'Individual' )
            plt.ylabel( v )
            #plt.title( v + ' per individual and model' )
            for i, model_result in enumerate( model_result_vec ):
                x = np.array( model_result.user_id )
                y = None
                if v == 'BIC': 
                    y = model_result.n_parameters * model_result.n_observations[ i ]- 2 * np.array( model_result.log_likelihood )
                else:    
                    y = - np.array( model_result.log_likelihood )
                plt.bar( x + i * bar_width - bar_width, y, bar_width, alpha=opacity, label= model_result.name )


            #plt.legend( loc = 1, ncol= len( model_result_vec ), framealpha = 0, fontsize='small' )
            plt.legend( framealpha = 0, fontsize='x-small' )

            
        for i, v in enumerate( dependent_variable ) :
            ax = self.figure.add_subplot(3, 2, 3 + i)
            #ax.set_facecolor('dimgray')
            plt.xlabel( 'Model' )
            plt.ylabel( v )
            #plt.title( v + ' per model' )
            x = np.array( [ mr.name for mr in model_result_vec ] )
            y = None
            ci = None 
            if v == 'BIC' :
                y = model_result.n_parameters * 720 - 2 * np.array( [ np.mean( mr.log_likelihood) for mr in model_result_vec ] )
                ci = np.array( [ bootstrap_ci( model_result.n_parameters * 720 - 2 * mr.log_likelihood) for mr in model_result_vec ] )
                #ci = np.array( [ np.percentile( model_result.n_parameters * 720 - 2 * mr.log_likelihood, [2.5, 97.5] ) for mr in model_result_vec ] )
            else: 
                y = - np.array( [ np.mean( mr.log_likelihood) for mr in model_result_vec ] )
                #ci = np.array( [ np.percentile( - mr.log_likelihood, [2.5, 97.5] ) for mr in model_result_vec ] )
                ci = np.array( [ bootstrap_ci( - mr.log_likelihood) for mr in model_result_vec ] )
                #print( "mean : ", y)
                #print( "bootstrap ci:", np.transpose( ci ) )
                #print( "bootstrap ci - mean: ", np.transpose( ci ) - y)
            ci = np.transpose( ci )
            ci[0,:] = y - ci[0,:]
            ci[1,:] = ci[1,:] - y
            
            plt.bar( x, y, bar_width, alpha=opacity )
            ax.errorbar(x, y, yerr= ci , fmt='', color='w', ls='none', elinewidth=1  )
            for k, v in enumerate(y):
                ax.text(k, v + 3, str( round(v,2) ), color='blue', fontweight='bold')

        #plt.legend( loc=1, ncol= len( model_result_vec ), framealpha = 0, fontsize='small' )
        #plt.legend( framealpha = 0,  fontsize='xx-small' )


        for k, v in enumerate( dependent_variable ) :
            ax = self.figure.add_subplot( 3, 2, 5+k )
            plt.xlabel( 'Model' )
            plt.ylabel( v )
            #plt.title( v + ' per model and Technique' )

            x_name = np.array( [ mr.name for mr in model_result_vec ] )
            x = np.arange(0, len( model_result_vec ), 1 )
            y_mat  = np.zeros( ( len( model_result_vec ), 3 ) )
            ci_mat_low = np.empty( ( len( model_result_vec ), 3 ) )
            ci_mat_up  = np.empty( ( len( model_result_vec ), 3 ) )
            for i, mr in enumerate( model_result_vec ):
                for j in range(0,3):
                    if v == 'BIC' :
                        y_mat[ i , j ] = model_result.n_parameters * 720 - 2 * np.mean( mr.log_likelihood[ j::3 ] )
                        ci_tmp = bootstrap_ci( model_result.n_parameters * 720 - 2 * mr.log_likelihood[ j::3 ] )
                    else: 
                        y_mat[ i , j ] = - np.mean( mr.log_likelihood[j::3] )
                        ci_tmp = bootstrap_ci( - mr.log_likelihood[j::3] )

                    ci_mat_low[ i , j ] = y_mat[ i, j ] - ci_tmp[ 0 ]
                    ci_mat_up[ i , j ]  = ci_tmp[ 1 ] - y_mat[ i, j ]
            #print("y_mat:", y_mat)
            #print("ci_mat_low:", ci_mat_low )
            
            plt.bar( x-bar_width, y_mat[ :, 0 ], bar_width, alpha=opacity, label = "Traditional" )
            ax.errorbar(x-bar_width, y_mat[ :, 0 ], yerr= [ ci_mat_low[:,0], ci_mat_up[:,0] ], fmt='', color='w', ls='none', elinewidth=1 ) 
            
            plt.bar( x, y_mat[ :, 1 ], bar_width, alpha=opacity, label = "Audio" )
            ax.errorbar(x, y_mat[ :, 1 ], yerr= [ ci_mat_low[:,1] , ci_mat_up[:,1] ], fmt='', color='w', ls='none', elinewidth=1 ) 
            
            plt.bar( x+bar_width, y_mat[ :, 2 ], bar_width, alpha=opacity, label = "Disable" )
            ax.errorbar(x+bar_width, y_mat[ :, 2 ], yerr= [ ci_mat_low[:,2], ci_mat_up[:,2] ], fmt='', color='w', ls='none', elinewidth=1 )

            plt.legend( framealpha = 0,  fontsize='x-small' )
            ax.set_xticks( x )
            ax.set_xticklabels( x_name )

        plt.tight_layout()
        self.canvas.draw()
        self.dialog.show()







