from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSignalMapper, Qt

from model_interface import *
from gui_util import *


######################################
#                                    #
#   PARAMETER GROUP PANEL            #
#                                    #
######################################
class Parameters_Group_Panel( Serie2DGallery ):

    ###############################
    def __init__(self):
        super().__init__()
        self.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Minimum )
        self.setMinimumWidth(250)

    ###############################
    def set_group( self, parameters_vec ):
        deleteLayoutContent( self.l )
        self.l.setRowStretch(0,1)
        for i, parameters in enumerate( parameters_vec ):
            parameters_panel = Parameters_Panel( parameters )
            self.l.addWidget( parameters_panel, i, 0)
        self.l.setRowStretch(0,1)
        self.l.addWidget( self.save_parameters_panel() ) 


    ##############################
    def save_parameters_panel( self ):
        label = QLabel("path to save: ")
        path_edit = LineEdit("my path: ")
        save_button = QPushButton( " Save" )
        save_button.clicked.connect( self.save_settings )

        container = QWidget()
        hl = QHBoxLayout()
        container.setLayout( hl )
        hl.addWidget( label )
        hl.addWidget( path_edit )
        hl.addWidget( save_button )
        return container




    ##############################
    def save_settings( self ):
        print( "save settings" )


        #self.l.addItem( QSpacerItem(10,10, QSizePolicy.Expanding ), self.l.rowCount() + 1, 0)
        #self.l.setColumnStretch(0, 10)


######################################
#                                    #
#      PARAMETER PANEL               #
#                                    #
######################################
class Parameters_Panel( QWidget ):
    
    ################################
    def __init__( self, parameters ):
        super(QWidget, self).__init__()
        self.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Minimum )
        self.l = QGridLayout()
        self.l.setHorizontalSpacing( 1 )
        self.l.setVerticalSpacing( 1 )
        self.setLayout( self.l )
        freedom_vec = ["Fixed", "USER FREE", "TECHNIQUE FREE", "EXPERIMENT_FREE"]
        #category_vec = ["Name", "Value", "Range", "Freedom"]
        #for i, category in enumerate( category_vec ):
        #    category_button = QPushButton( category )
        #    category_button.clicked.connect( lambda: self.select_category( i ) )
        #    self.l.addWidget(category_button, 0, i)
        self.l.addWidget( QLabel( '----' + parameters.name + '----' ), 0, 0, 1, 4, Qt.AlignHCenter)
        for i, param in enumerate( parameters.values() ) :
            name_label  = QLabel( param.name )
            value_edit = LineEdit( str( param.value ) )
            #value_edit.setPalette( QPalette.Shadow )
            s = '[' + str( param.min ) + ', ' + str(param.max) + ']'
            min_max_edit   = LineEdit( s )
            freedom_chooser = QComboBox()
            freedom_chooser.addItems( freedom_vec )
            freedom_chooser.setCurrentIndex( param.freedom )

            self.l.addWidget( name_label     , i+1, 0 )
            self.l.addWidget( value_edit     , i+1, 1 )
            self.l.addWidget( min_max_edit   , i+1, 2 )
            self.l.addWidget( freedom_chooser, i+1, 3 )
            self.l.setRowStretch(0,1)
        self.show()

    ###############################
    def select_category( self, i ):
        for j in range( 0, self.l.rowCount() ):
            w = self.l.itemAtPosition( j, i ).widget()
            print( "visible: ", not w.isVisible() )
            w.hide()
            #w.setVisible( not w.isVisible() )
    

######################################
#                                    #
#    PARAMETER COMPARISON PANEL      #
#                                    #
######################################
class Parameters_Comparison_Panel( QWidget ):
    
    ################################
    def __init__( self, user_vec, parameters_vec ):
        super(QWidget, self).__init__()
        self.l = QGridLayout()
        self.l.setHorizontalSpacing( 1 )
        self.l.setVerticalSpacing( 1 )
        self.setLayout( self.l )

        category_vec = [ name for name in parameters_vec[ 0 ] ]
        self.l.addWidget( QLabel( '(' + parameters_vec[0].name + ')' ), 0, 0 )

        for i, category in enumerate( category_vec ) :
            self.l.addWidget( QLabel( "<b>" + category + "</b>" ), 0, i+1 )

        for i, parameters in enumerate( parameters_vec ) :
            self.l.addWidget( QLabel( user_vec[ i ] + " " ), i+1, 0 )
            for j, param in enumerate( parameters.values() ) :
                print( i+1, j+1, param.name)
                value_edit = QLineEdit( str( param.value ) )
                self.l.addWidget( value_edit, i+1, j+1 )
            
        self.show()


######################################
#                                    #
#        FITTING RESULT PANEL        #
#                                    #
######################################
class Model_Result_Panel( Serie2DGallery ):
    
    ################################
    def __init__( self ):
        super().__init__()
        self.setMinimumWidth(250)
        self.l.setHorizontalSpacing( 1 )
        self.l.setVerticalSpacing( 1 )
        self.setLayout( self.l )
        self.model_row = dict()
        self.user_col = dict()

    def set_group( self, model_result_vec ):
        self.l.addWidget(QLabel(""),0,0)
        for model_result in model_result_vec :
            name = model_result.name
            row = 0

            if name in self.model_row:
               row = self.model_row[ name ]
            else: 
                row = self.l.rowCount()
                self.model_row[ model_result.name ] = row
                self.l.addWidget( QLabel( "<b>" + name + "</b>" ), row, 0 )
            
            for user_id, likelihood in zip( model_result.user_id, model_result.log_likelihood) :
                likelihood_label = QLabel( str( round( likelihood, 2 ) ) )
                if not user_id in self.user_col :
                    self.l.addWidget(QLabel( str(user_id) ), 0, user_id + 1 )
                self.l.addWidget( likelihood_label, row, user_id+1 )


            
        self.show()







