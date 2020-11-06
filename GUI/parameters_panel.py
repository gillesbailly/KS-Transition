from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QObject, pyqtSignal

from model_interface import *
from gui_util import *


######################################
#                                    #
#   PARAMETER GROUP PANEL            #
#                                    #
######################################
class Parameters_Group_Panel( Serie2DGallery ):
    reload = pyqtSignal()

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
        self.reload_button = QPushButton( "Reload" )
        self.l.addWidget( self.reload_button )
        self.reload_button.clicked.connect( self.reload )


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
#           PARAM WIDGET             #
#                                    #
######################################
class Param_Widget( QObject ):
    changed = pyqtSignal()

    ########################
    def __init__( self, param ):
        super(QObject, self).__init__()
        self.param = param
        self.freedom_vec = ["Fixed", "USER FREE", "TECHNIQUE FREE", "EXPERIMENT_FREE"]
        self.name  = QLabel( param.name )
        self.value = LineEdit( str( param.value ) )
        self.value.editingFinished.connect( self.view_changed )
        #value_edit.setPalette( QPalette.Shadow )
        s = '[' + str( param.min ) + ', ' + str(param.max) + ']'
        self.min_max = LineEdit( s )
        self.min_max.editingFinished.connect( self.view_changed )
        self.freedom = QComboBox()
        self.freedom.addItems( self.freedom_vec )
        self.freedom.setCurrentIndex( param.freedom )
        self.freedom.currentIndexChanged.connect( self.view_changed )


    ########################
    def update_view( self ):
        self.value.setText( self.param.value )
        s = '[' + str( self.param.min ) + ', ' + str(self.param.max) + ']'
        self.min_max.setText( s )
        self.freedom.setCurrentIndex( param.freedom )

    ########################
    def view_changed( self ):
        print( self.name.text(), "view changed" )
        value = self.value.text()
        self.param.value = float( value ) if '.' in value else int( value )
        self.param.freedom = self.freedom.currentIndex() 
        self.changed.emit()


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
        self.param_widget_vec = []
        #category_vec = ["Name", "Value", "Range", "Freedom"]
        #for i, category in enumerate( category_vec ):
        #    category_button = QPushButton( category )
        #    category_button.clicked.connect( lambda: self.select_category( i ) )
        #    self.l.addWidget(category_button, 0, i)
        self.l.addWidget( QLabel( '----' + parameters.name + '----' ), 0, 0, 1, 4, Qt.AlignHCenter)
        for i, param in enumerate( parameters.values() ) :
            param_widget = Param_Widget( param )
            param_widget.changed.connect( self.update_data )
            self.param_widget_vec.append( param_widget )

            self.l.addWidget( param_widget.name   , i+1, 0 )
            self.l.addWidget( param_widget.value  , i+1, 1 )
            self.l.addWidget( param_widget.min_max, i+1, 2 )
            self.l.addWidget( param_widget.freedom, i+1, 3 )
            self.l.setRowStretch(0,1)
        self.show()

    ###############################
    def select_category( self, i ):
        for j in range( 0, self.l.rowCount() ):
            w = self.l.itemAtPosition( j, i ).widget()
            print( "visible: ", not w.isVisible() )
            w.hide()
            #w.setVisible( not w.isVisible() )
    
    def update_data( self ):
        print( "update parameters" )

    ###############################
    def update_view( self ):
        for param_widget in self.param_widget_vec:
            param_widget.update_view()


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





