import sys
import os
import numpy as np
from datetime import datetime
import argparse
import itertools
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QPageLayout
from PyQt5.QtPrintSupport import *
from PyQt5.QtCore import QCoreApplication
import numpy as np

from gui_util import *
from data_loader import *
from hotkeycoach_loader import *

from simple_episode_view import *

######################################
#                                    #
#          TRIAL INFO                #
#                                    #
######################################
class Trial_Info(QScrollArea) :

    ##################################
    def __init__(self ):
        super( QScrollArea, self ).__init__()
        
        #self.setBackgroundRole(QPalette.Shadow);
        self.setWidgetResizable( True )
        
        self.resize( 250, 350 )
        self.setMinimumWidth(250)
        

    ##################################
    def set_info(self, infos) :
        #print( infos )
        self.container = QWidget()
        self.l = QGridLayout()
        self.container.setLayout( self.l )
        self.setWidget( self.container )
        self.container.show()
        for i, key in enumerate( infos.keys() ) :
            #print(i, key)
            name_label = QLabel( key )
            value_text = Trial_Info.strategy( infos[key] ) if key == "Strategy" else infos[ key ]
            value_label = LineEdit( value_text )
            value_label.setReadOnly( True )
            self.l.addWidget( name_label, i, 0 )
            self.l.addWidget( value_label, i, 1 )
        self.hide()
        self.show()

    #################################
    def strategy( strategy_id ):
        if strategy_id == "0" :
            return "Menu"
        elif strategy_id == "1" :
            return "Hotkey"
        elif strategy_id == "2" :
            return "Learning"
        else:
            return "Unknow (" + strategy_id + ")"
    




######################################
#                                    #
#      Empirical Panel               #
#                                    #
######################################
class Empirical_Panel ( QTabWidget ) :

    view_selected = pyqtSignal( str ) #trial infos

    ##################################
    def __init__(self):
        super( QTabWidget, self ).__init__()
        self.move(20,20)
        self.resize(1000, 800)
        config_element = ["Technique", "User", "Command"]
        self.configuration_vec = list(itertools.permutations( config_element ) )
        self.configuration_id = 1
        print( "Configuration:", self.configuration() )

        
        self.gallery = dict()
        #print( self.categories() )
        #exit(0)
        for category in self.categories() :
            self.gallery[ category ] = Serie2DGallery()
            self.addTab(self.gallery[ category ], category )
            self.gallery[ category ].show()

        self.view_vec = dict()
        self.trial_info = Trial_Info( )
      
        self.show()


    ##################################
    def ensure_view_visible( self, technique, user_id, cmd ) :
        index = 0
        gallery = None
        print("ensure view visible")
        tab_title = list( self.gallery.keys() )
        if self.configuration()[0] == "Technique" :
            self.setCurrentIndex( tab_title.index( technique ) )
            gallery = self.gallery[ technique ]          

        elif self.configuration()[0] == "Command" :
            self.setCurrentIndex( tab_title.index( str( cmd ) ) )
            gallery = self.gallery[ str( cmd ) ]            
        
        elif self.configuration()[0] == "User" :
            self.setCurrentIndex( tab_title.index( str( user_id ) ) )
            gallery = self.gallery[ str( user_id ) ]            
        
        QCoreApplication.processEvents()
        key = self.key(technique, user_id, cmd )

        gallery.ensureWidgetVisible( self.view_vec[ key ], 750, 500 )


    ##################################
    def configuration( self ) :
        return self.configuration_vec[ self.configuration_id ]


    ##################################
    def categories( self ) :
        if self.configuration()[0] == "Technique" :
            return ["traditional", "audio", "disable"]
        
        elif self.configuration()[0] == "Command" :
            res = []
            for i in range( 0, 14 ) :
                res.append( str( i ) )
            return res
        
        elif self.configuration()[0] == "User" :
            res = []
            for i in range( 0, 42 ) :
                res.append( str( i ) )
            return res
        else:
            print("EFFOR IN Categories - Configuration", self.configuration()[0], "--- ", self.configuration() )
            exit(0)


    ##################################
    def category( self, d, cmd ) :
        if self.configuration()[0] == "Technique" :
            return d.technique_name
        
        elif self.configuration()[0] == "Command" :
            return str( cmd )
        
        elif self.configuration()[0] == "User" :
            return str( d.id )
        
        else:
            print("EFFOR IN Category - Configuration", self.configuration()[0], "--- ", self.configuration() )
            exit(0)
        

    ##################################
    def row( self, d, cmd ) :

        if self.configuration()[1] == "Technique" :
            return self.technique_pos( d, cmd )
        
        elif self.configuration()[1] == "Command" :
            return self.command_pos( d, cmd )
        
        elif self.configuration()[1] == "User" :
            return self.user_pos( d, cmd )
        
        else:
            print("EFFOR in Row - Configuration", self.configuration()[1], "--- ", self.configuration() )
            exit(0)



    ##################################
    def column( self, d, cmd ):
        if self.configuration()[2] == "Technique" :
            return self.technique_pos( d, cmd )
        
        elif self.configuration()[2] == "Command" :
            return self.command_pos( d, cmd )
        
        elif self.configuration()[2] == "User" :
            return self.user_pos( d, cmd )
        
        else:
            print("EFFOR in Row - Configuration", self.configuration()[1], "--- ", self.configuration() )
            exit(0)

        

    ##################################
    def command_pos(self, d, cmd ) :
        ordered_freq_index = np.argsort( d.command_info.frequency )
        res = len(ordered_freq_index) - 1 - np.where( np.array( ordered_freq_index ) == cmd )[0][0] 
        return res

    ##################################
    def user_pos( self, d, cmd ) :
        return int( d.id / 3 )

    ##################################
    def technique_pos( self, d, cmd ) :
        techniques = ["traditional", "audio", "disable"]
        return np.where( np.array( techniques ) == d.technique_name )[0][0]


    #####################################
    def key( self, technique, user_id, cmd ) :
        return technique + "," + str(user_id) + "," + str(cmd) 


    #####################################
    def set_sequences( self, data_vec ) :
        self.data_vec = data_vec
        for d in data_vec :
            ordered_freq_index = np.argsort( d.command_info.frequency )

            for cmd in d.command_info.id :         
                c = self.category( d, cmd )
                row_id = self.row( d, cmd )
                col_id = self.column( d, cmd )
                key = self.key(d.technique_name, d.id, cmd )

                view = EpisodeView( )
                view.set_user_data( d, cmd )
                view.view_selected.connect( self.set_info )
                self.gallery[ c ].add_view( view, row_id, col_id )

                self.view_vec[ key ] = view 
                QCoreApplication.processEvents()


    ##################################
    def update_configuration( self, id ) :
        self.configuration_id = id
        print("Update configuration: ", self.configuration() )
        self.gallery.clear()
        self.clear() #TODO THIS DOES NOT REALLY REMOVE ELEMENTS.....

        for category in self.categories() :
            self.gallery[ category ] = Serie2DGallery()
            self.addTab(self.gallery[ category ], category )
            self.gallery[ category ].show()

        for d in self.data_vec :
            for cmd in d.command_info.id :           
                c = self.category( d, cmd )
                row_id = self.row( d, cmd )
                col_id = self.column( d, cmd )
                key = self.key( d.technique_name, d.id, cmd )
                view = self.view_vec[ key ]
                self.gallery[ c ].add_view( view, row_id, col_id )
        self.show()

        
    ##################################
    def set_info(self, user_id, cmd, trial_id ) :
        #self.text_edit.setPlainText( "user: " + str(user_id) + "\t cmd:" + str(cmd) + "\t trial:" + str(trial_id) + "->" + "\n" +extra_infos + "\n" + self.text_edit.toPlainText()   )
        info = None
        for user in self.data_vec :
            if user.id == user_id:
                info = user.trial_info( trial_id )
        self.trial_info.set_info( info )
        #self.view_selected.emit( extra_infos )
        print( "user: " + str(user_id) + "\t cmd:" + str(cmd) + "\t trial:" + str(trial_id) + "\n"   )


    def print_all( self, graph_path ) :
        technique_vec = ["traditional", "audio", "disable"]
        res = 750
        if not graph_path[-1]  == '/': 
            graph_path = graph_path + '/'
        if not os.path.isdir( graph_path ) :
            os.mkdir( graph_path )


        now = datetime.now()
        now_str = now.strftime("%Y_%m_%d__%H_%M_%S")
        graph_path += now_str + '/'
        if not os.path.isdir( graph_path ) :
            os.mkdir( graph_path )


        for t in technique_vec :
            printer = QPrinter()
            printer.setOutputFormat( QPrinter.PdfFormat )
            printer.setPageOrientation(QPageLayout.Landscape)
            printer.setOutputFileName(graph_path + t + '_gallery.pdf')
            #logicalDPIX = printer.logicalDpiX()
            #PointsPerInch = 200.0
            painter = QPainter()
            if not painter.begin(printer):
                print("failed to open file, is it writable?");
        
            pix = QPixmap( self.gallery[t].container.grab() )
            print(t + "pix to print: ", pix.width(), pix.height() )
            painter.drawPixmap(0,0, 750,pix.height() * 750. / pix.width(), pix)        
            painter.end()


    def print_unit(self, graph_path) :
        res = 750

        if not graph_path[-1]  == '/': 
            graph_path = graph_path + '/'
        if not os.path.isdir( graph_path ) :
            os.mkdir( graph_path )

        now = datetime.now()
        now_str = now.strftime("%Y_%m_%d__%H_%M_%S") 
        graph_path += now_str + '/'
        if not os.path.isdir( graph_path ) :
            os.mkdir( graph_path )


        technique_vec = ["traditional", "audio", "disable"]
        for technique in technique_vec :
            if not os.path.isdir( graph_path + technique + '/' ) :
                os.mkdir( graph_path + technique + '/' )


        for key in self.view_vec :
            technique = key.split(',')[0]
            user_id = key.split(',')[1]
            cmd = key.split(',')[2]
            view = self.view_vec[ key ]
            #print(technique, str(view.d.user_id), str(view.cmd))
            path = graph_path + technique + '/technique_' + technique + '_user_'+ user_id + '_cmd_' + cmd + '.pdf'
            #print(path)
            printer = QPrinter()
            printer.setOutputFormat( QPrinter.PdfFormat )
            printer.setPageOrientation(QPageLayout.Landscape)
            printer.setOutputFileName(path)
            painter = QPainter()
            if not painter.begin(printer):
                print("failed to open file, is it writable?");
            pix = QPixmap( view.grab() )
            painter.drawPixmap(0,0, res,pix.height() * res / pix.width(), pix)        
            painter.end()


#####################################
#                                   #
#              MAIN                 #
#                                   #
#####################################
if __name__=="__main__":
    path = './experiment/hotkeys_formatted_dirty.csv'
    parser = argparse.ArgumentParser()
    parser.add_argument( "-p", "--path", help="path of the empirical data" )
    
    args = parser.parse_args()
    if args.path != None :
        path = args.path
    print("sequences path: ", path)
    loader = HotkeyCoach_Loader()
    users_data = loader.experiment( path )
    print( "data of ", len( users_data ), "participants loaded" )

    my_filter = Filter(user_max = 3, techniques=["traditional", "audio"] )
    filtered_users_data = my_filter.filter( users_data )
    print( "data of ",  len( filtered_users_data ), "users once filtered" )

    app = QApplication(sys.argv)
    
    panel = Empirical_Panel()
    

    panel.set_sequences( filtered_users_data )
    #panel.print_all('./tmp_graphs')
    #panel.print_unit('./tmp_graphs')
    #panel.ensure_view_visible("audio", 4, 2)
    #panel.update_configuration(4)
    panel.ensure_view_visible("traditional", 3, 2)

    




    #win.show()
    #window.select_command( args.command )

    sys.exit(app.exec_())
