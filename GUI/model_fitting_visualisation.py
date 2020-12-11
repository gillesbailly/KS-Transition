import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from gui_util import *
import seaborn as sns
from dataframe_util import *


# ######################################
# #                                    #
# #           FITTING TABLE            #
# #                                    #
# ######################################
# class Fitting_Table( QWidget ) :

#     ##########################
#     def __init__( self ):
#         super().__init__()
#         self.l = QGridLayout()
#         self.l.setHorizontalSpacing( 1 )
#         self.l.setVerticalSpacing( 1 )
#         self.setLayout( self.l )
#         self.model_row = dict()
#         self.user_col  = dict()
#         self.w         = dict()
#         self.setMaximumHeight(120)

    
#     ##########################
#     def update_data( self, model_fitting_result_vec ):
#         self.l.addWidget(QLabel(""),0,0)
#         for model_result in model_fitting_result_vec :
#             name = model_result.name  if model_result.variant == '' else  model_result.name + ' - ' + model_result.variant
#             k = model_result.n_parameters

#             row = 0

#             if name in self.model_row:
#                row = self.model_row[ name ]
#             else: 
#                 row = self.l.rowCount()
#                 self.model_row[ name ] = row
#                 self.l.addWidget( QLabel( "<b>" + name + " </b>" ), row, 0 )
            
#             for user_id, likelihood, n  in zip( model_result.user_id, model_result.log_likelihood, model_result.n_observations) :
#                 bic = bic_score(  n, k, likelihood )
#                 if not user_id in self.user_col :
#                     self.l.addWidget(QLabel( str(user_id) ), 0, user_id + 1 )
#                 key = row * 100 + user_id
#                 if not key in self.w:
#                     bic_label = QLabel( str( round( bic, 2 ) ) )
#                     self.w[ key ] = bic_label
#                     self.l.addWidget( bic_label, row, user_id+1 )
#                 else:
#                     self.w[ key ].setText( str( round( bic, 2 ) ) )


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
        # self.table = Fitting_Table()
        # self.table.setSizePolicy( QSizePolicy( QSizePolicy.Minimum, QSizePolicy.Expanding  ) )
        # self.l.addWidget( QLabel( 'BIC' ) )
        # self.l.addWidget( self.table )

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

    def create_table( self, horizontal_header, vertical_header ):
        table = QTableWidget( len( vertical_header ), len( horizontal_header ) )
        table.setVerticalHeaderLabels( vertical_header )
        table.setHorizontalHeaderLabels( horizontal_header )
        return table


    ##########################
    def participant_table( self, df ):
        participant_vec = df['user_id'].unique()
        model_vec = df['name'].unique()
        traditional_color = QColor(150,150,255)
        audio_color       = QColor(255,200,100)
        disable_color     = QColor(150,255,150)

        self.participant_table = self.create_table([ str(p) for p in participant_vec ], model_vec )

        for i, model in enumerate( model_vec ) :
            for j, participant in enumerate( participant_vec ):
                value = df.loc[ ( df.name == model ) & ( df.user_id == participant )  , 'log_likelihood' ]
                item = QTableWidgetItem( str( round( value.iloc[0], 1)  ) )
                if j % 3 == 0 :
                    item.setBackground( traditional_color )
                elif j % 3 == 1 :
                    item.setBackground( audio_color )
                elif j % 3 == 2 :
                    item.setBackground( disable_color )                
                 
                self.participant_table.setItem( i, j, item )

        header = self.participant_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents);
        self.participant_table.setMaximumHeight( 110 )
        self.participant_table.setMinimumHeight( 110 )
        
        return self.participant_table


    ##########################
    def technique_model_table( self, df, measure= 'log_likelihood' ):
        mean_df = df.groupby( [ 'name' ] ).mean()
        mean_df = mean_df.add_suffix('_mean').reset_index()

        technique_mean_df = df.groupby( ['name', 'technique'] ).mean()
        technique_mean_df = technique_mean_df.add_suffix('_mean').reset_index()

        technique_vec = technique_mean_df['technique'].unique()
        ext = '(-Likelihood)' if measure == 'log_likelihood' else '(BIC)'
        technique_vec = np.concatenate( ( ['All ' + ext ], technique_vec), axis=0 )
        model_vec = mean_df['name'].unique()

        table = self.create_table( model_vec, technique_vec )
        for j, model in enumerate( model_vec ) :
            for i, technique in enumerate( technique_vec ):
                if i == 0 :
                    value = mean_df.loc[ mean_df.name == model , measure + '_mean' ]
                    v =  round( value.iloc[0], 1) if measure == 'BIC' else - round( value.iloc[0], 1) 
                    table.setItem( i, j, QTableWidgetItem( str( v ) ) )
                else :
                    value = technique_mean_df.loc[ ( technique_mean_df.name == model ) & ( technique_mean_df.technique == technique )  , measure + '_mean' ] 
                    v =  round( value.iloc[0], 1) if measure == 'BIC' else - round( value.iloc[0], 1) 
                    table.setItem( i, j, QTableWidgetItem( str( v  ) ) )
       
        return table



    ############################
    def update_figure( self, df ):
        bar_width = 0.2
        opacity   = 1
        self.figure.clear()
        #plt.subplots_adjust(wspace=0.001, hspace=0.001, left=0.01, right=0.99, bottom=0.01, top=0.99)
        
        #fit_df = model_res_vec_to_data_frame( model_result_vec )
        #df = fit_df.copy()

        df['log_likelihood'] = - df['log_likelihood']
        #df['name'] = df['variant']
        #df.loc[ df.variant == '', 'name'] = df[ 'model' ]

        

        dependent_variable = [ '- Log Likelihood', 'BIC' ]

        participant_traditional = np.arange(0,41,3)
        participant_audio       = np.arange(1,41,3)
        participant_disable     = np.arange(2,41,3)
        participant_order = np.concatenate((participant_traditional, participant_audio, participant_disable), axis=0)
    

        #ALL
        for i, v in enumerate( dependent_variable ) :
            ax = self.figure.add_subplot(3, 2, 1 + i)
            y_value = 'BIC' if v == 'BIC' else 'log_likelihood'
            sns.barplot( x='name', y=y_value, palette= model_color, data = df )
            ax.set_ylabel( v )
            ax.set_xlabel( 'Model' )
            
            ax.legend().remove()

        # TECHNIQUES
        for i, v in enumerate( dependent_variable ) :
            ax = self.figure.add_subplot( 3, 2, 3 + i )
            y_value = 'BIC' if v == 'BIC' else 'log_likelihood'
            sns.barplot( x='technique', y=y_value, hue="name", palette = model_color, data = df )
            ax.set_ylabel( v )
            ax.set_xlabel( "Technique" )
            if v == 'BIC': 
                 ax.legend( framealpha = 0, fontsize='x-small' )
            else:
                ax.legend().remove()

        #INDIVIDUALS
        for i, v in enumerate( dependent_variable ) :
            ax = self.figure.add_subplot( 3, 2, 5 + i )
            y_value = 'BIC' if v == 'BIC' else 'log_likelihood'
            sns.barplot( x='user_id', y=y_value, hue="name", palette= model_color, order = participant_order, data = df )
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

        
            

        
        self.canvas.draw()
        self.show()

    #################################
    def update_canvas( self, res ):
        df = model_res_vec_to_data_frame( res )
        df['name'] = df['variant']
        df.loc[ df.variant == '', 'name'] = df[ 'model' ]
        print( df.loc[ df.user_id == 5 ] )

        self.ll_model_table    = self.technique_model_table( df )
        self.bic_model_table   = self.technique_model_table( df, 'BIC')
        self.participant_table = self.participant_table( df )
        h_layout = QHBoxLayout()
        w= QWidget()
        w.setMaximumHeight( 170 )
        w.setMinimumHeight( 170 )
        
        w.setLayout( h_layout )
        h_layout.addWidget( self.ll_model_table )
        h_layout.addWidget( self.bic_model_table )
        self.l.addWidget( w )
        self.l.addWidget( self.participant_table )
        self.update_figure( df )
        #self.update_table( res )






