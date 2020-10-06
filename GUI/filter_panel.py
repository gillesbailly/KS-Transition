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
    def __init__( self, filter ):
        super(QWidget,self).__init__( )
        self.dialog = None
        self.f = filter
        self.l = QGridLayout( self )
        self.setLayout( self.l )
        self.technique_checkbox_dict = dict()
        self.user_checkbox_dict = dict()
        self.l.addWidget( QLabel("Input: ") )
        self.input_label = QLabel( self )
        self.input_label.setWordWrap( True )
        self.l.addWidget( self.input_label, 0, 1,1,3 )
        self.output_label = QLabel( self )
        self.output_label.setText("Empty")
        self.output_label.setWordWrap( True )
        self.available_user_id = []

        for i, name in enumerate( self.f.all_technique_vec ) :
            technique_checkbox = QCheckBox( name, self )
            technique_checkbox.setCheckState( Qt.Checked )
            technique_checkbox.stateChanged.connect( self.activate_technique )
            self.technique_checkbox_dict[ i ] = technique_checkbox
            self.l.addWidget( technique_checkbox, 1, i )

        print( self.f.all_user_vec )
        for i, name in enumerate( self.f.all_user_vec ) :
            user_checkbox = QCheckBox( "User " + str(name), self )
            user_checkbox.setCheckState( Qt.Checked )
            user_checkbox.stateChanged.connect( self.activate_user )
            self.user_checkbox_dict[ name ] = user_checkbox
            self.l.addWidget( user_checkbox, i/3 +2 , name%3 )

        self.l.addWidget(QLabel("Output: "), self.l.rowCount() + 1, 0 )
        self.l.addWidget(self.output_label, self.l.rowCount() + 1, 1, 1, 3)

        self.update_view()
        self.show()


    ################################
    def update_view( self ):
        self.input_label.setText( ", ".join( [ str(i) for i in self.f.all_user_vec ] ) )

        for user in self.user_checkbox_dict :
            if user in self.f.users:
                 self.user_checkbox_dict[ user ].setCheckState( Qt.Checked )
            else:
                self.user_checkbox_dict[ user ].setCheckState( Qt.Unchecked )              
        
        for technique_id in self.technique_checkbox_dict :
            technique = self.f.all_technique_vec[ technique_id ]
            if technique in self.f.techniques:
                self.technique_checkbox_dict[ technique_id ].setCheckState( Qt.Checked )
            else:
                self.technique_checkbox_dict[ technique_id ].setCheckState( Qt.Unchecked )
        self.preview_output()


    ################################
    def apply( self ):

        technique_vec = []
        user_vec      = []
        #print( "apply:  ", list( self.technique_checkbox_dict.keys() ) )
        for w in self.technique_checkbox_dict.values() :
            if w.checkState() == Qt.Checked :
                technique_vec.append( w.text() )

        for key in self.user_checkbox_dict:
            w = self.user_checkbox_dict[ key ]
            if w.isEnabled() and w.checkState() == Qt.Checked :
                user_vec.append( key )
        print("technique_vec: ", technique_vec )
        print("user_vec: ", user_vec )
        self.f.techniques = technique_vec
        self.f.users     = user_vec


    ################################
    def activate_technique( self ):
        print("activate technique ")
        for key_technique in self.technique_checkbox_dict :
            state = self.technique_checkbox_dict[ key_technique ].checkState() == Qt.Checked
            
            for key_user in self.user_checkbox_dict :
                if key_user%3 == key_technique :
                    self.user_checkbox_dict[ key_user ].setEnabled( state )
                if not key_user in self.f.all_user_vec :
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



