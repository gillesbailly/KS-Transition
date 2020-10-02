from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSignalMapper, Qt
from filter import *

######################################
#                                    #
#          TRIAL INFO                #
#                                    #
######################################
class Filter_Panel(QWidget) :

    #################################
    def __init__(self, filter):
        super(QWidget,self).__init__()
        self.filter = filter
        self.l = QGridLayout()
        self.setLayout( self.l )
        self.technique_checkbox_dict = dict()
        self.user_checkbox_dict = dict()
        self.l.addWidget( QLabel("Input: ") )
        self.input_label = QLabel()
        self.l.addWidget( self.input_label, 0, 1,1,2 )
        self.output_label = QLabel()
        self.output_label.setText("Empty")
        self.available_user_id = []



        for i, name in enumerate( self.filter.all_technique_vec ) :
            technique_checkbox = QCheckBox( name )
            technique_checkbox.setCheckState( Qt.Checked )
            technique_checkbox.stateChanged.connect( self.activate_technique )
            self.technique_checkbox_dict[ i ] = technique_checkbox
            self.l.addWidget( technique_checkbox, 1, i )

        print( self.filter.all_user_vec )
        for i, name in enumerate( self.filter.all_user_vec ) :
            user_checkbox = QCheckBox( "User " + str(name) )
            user_checkbox.setCheckState( Qt.Checked )
            user_checkbox.stateChanged.connect( self.activate_user )
            self.user_checkbox_dict[ name ] = user_checkbox
            self.l.addWidget( user_checkbox, i/3 +2 , name%3 )

        self.l.addWidget(QLabel("Output: "), self.l.rowCount() + 1, 0 )
        self.l.addWidget(self.output_label, self.l.rowCount() + 1, 1, 1, 2)

        self.show()

    ################################
    def apply( self ):
        technique_vec = []
        user_vec      = []
        
        for w in self.technique_checkbox_dict.values() :
            if w.checkState() == Qt.Checked :
                technique_vec.append( w.text() )

        for key in self.user_checkbox_dict:
            w = self.user_checkbox_dict[ key ]
            if w.isEnabled() and w.checkState() == Qt.Checked :
                user_vec.append( key )
        print("technique_vec: ", technique_vec )
        print("user_vec: ", user_vec )
        self.filter.techniques = technique_vec
        self.filter.users     = user_vec


    ################################
    def set_user_data( self, user_data_vec ):
        self.available_user_id = []
        

        for user_data in user_data_vec:
            self.available_user_id.append( user_data.id )
        #self.available_user_id = [i for i in range(0,6) ]

        self.input_label.setText( ", ".join( str( self.available_user_id ) ) )

        for key in self.user_checkbox_dict :
                if not key in self.available_user_id : 
                    self.user_checkbox_dict[ key ].setEnabled ( False )

        self.preview_output()


    ################################
    def activate_technique( self ):
        for key_technique in self.technique_checkbox_dict :
            state = self.technique_checkbox_dict[ key_technique ].checkState() == Qt.Checked
    
            for key_user in self.user_checkbox_dict :
                if key_user%3 == key_technique :
                    self.user_checkbox_dict[ key_user ].setEnabled( state )
                if not key_user in self.available_user_id :
                    self.user_checkbox_dict[ key_user ].setEnabled ( False )

        self.preview_output()



    ################################
    def activate_user( self ):
        self.preview_output()


    ################################
    def preview_output( self ):
        user_id_vec = []
        user_id_input = self.input_label.text().split(", ")
        for key_user in self.user_checkbox_dict :
            if str(key_user) in user_id_input :
                w = self.user_checkbox_dict[ key_user ]
                if w.isEnabled() and w.checkState() == Qt.Checked :
                    user_id_vec.append( str( key_user) )
        self.output_label.setText( ", ".join(user_id_vec) ) 



