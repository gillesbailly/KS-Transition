import sys

#from simulationWidget import *
#from simulator import *
import numpy as np
import argparse
from experiment import *
from simple_episode_view import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QPageLayout
from PyQt5.QtPrintSupport import *
from confusion_matrix import *


    

class Serie2DGallery(QScrollArea):

    def __init__(self):
        super(Serie2DGallery,self).__init__()
        self.setBackgroundRole(QPalette.Dark);
        self.setWidgetResizable( True )
        self.container = QWidget()
        self.l = QGridLayout()
        self.container.setLayout( self.l )
        self.setWidget( self.container )
        self.container.show()
       

        
    def add_view(self, view, user_id, cmd):
        self.l.addWidget( view, user_id, cmd)
    

    def select_command(self,c):
        print("select command ", c)


class Win (QMainWindow) :
    def __init__(self):
        super(Win,self).__init__()
        self.move(20,20)
        self.resize(1000, 800)
        #experiment = Experiment( './experiment/grossman_cleaned_data.csv', 3, "" )
        experiment = Experiment( './experiment/hotkeys_formatted_dirty.csv', 3, True, "" )
        
        tab_widget = QTabWidget()
        self.setCentralWidget( tab_widget )

        self.confusion_matrix = ConfusionMatrix()

        technique_vec = ["traditional", "audio", "disable"]
        self.gallery = dict()
        for t in technique_vec :
            self.gallery[t] = Serie2DGallery()
            tab_widget.addTab(self.gallery[t], t)
            self.gallery[t].show()

        self.view_vec = []        
        self.set_data( experiment.data )
        self.show()

        self.text_edit = QTextEdit()
        self.text_edit.setMaximumHeight(50)
        dock = QDockWidget()
        dock.setWidget( self.text_edit )
        self.addDockWidget( Qt.BottomDockWidgetArea, dock )
        #self.print_all()
        #self.print_unit()
        



    def set_data(self, data_vec ) :
        occ = dict()
        occ["traditional"] = 0
        occ["audio"] = 0
        occ["disable"] = 0


        for d in data_vec :
            technique = d.technique_name
            for cmd in range(0, 1) :
                view = EpisodeView( )
                view.set_full_history( d, cmd)
                view.view_selected.connect( self.set_info )
                self.gallery[technique].add_view( view, occ[technique], cmd )
                self.view_vec.append( view )

            occ[technique] += 1
        

    def set_info(self, user_id, cmd, trial_id, extra_infos) :
        self.text_edit.setPlainText( "user: " + str(user_id) + "\t cmd:" + str(cmd) + "\t trial:" + str(trial_id) + "->" + "\n" +extra_infos + "\n" + self.text_edit.toPlainText()   )

    def print_all( self ) :
        technique_vec = ["traditional", "audio", "disable"]
        res = 750
        for t in technique_vec :
            printer = QPrinter()
            printer.setOutputFormat( QPrinter.PdfFormat )
            printer.setPageOrientation(QPageLayout.Landscape)
            printer.setOutputFileName('./graphs/' + t + '_gallery.pdf')
            #logicalDPIX = printer.logicalDpiX()
            #PointsPerInch = 200.0
            painter = QPainter()
            if not painter.begin(printer):
                print("failed to open file, is it writable?");
        
            pix = QPixmap( self.gallery[t].container.grab() )
            print(t + "pix to print: ", pix.width(), pix.height() )
            painter.drawPixmap(0,0, 750,pix.height() * 750. / pix.width(), pix)        
            painter.end()


    def print_unit(self) :
        res = 750
        for view in self.view_vec :
            technique = view.d.technique_name
            #print(technique, str(view.d.user_id), str(view.cmd))
            path = './graphs/empirical_series/' + technique + '/user_'+ str(view.d.user_id) + '_cmd_' + str(view.cmd) + '.pdf'
            print(path)
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

if __name__=="__main__":

    #experiment = Experiment( './experiment/hotkeys_formatted_dirty.csv', 3, True, "" )
    #experiment.add_and_save( './experiment/hotkeys_formatted_dirty.csv', './experiment/hotkeys_strategy.csv')
    #exit(0)
    
    parser = argparse.ArgumentParser()
    #parser.add_argument("-p", "--path", help="path of the empirical data", action="store_true")
    #parser.add_argument("-f", "--filter", help="filter, e.g. \"user_id=1\", default=\"\" meaning all" , default="user_id=1")
    #parser.add_argument("-c", "--command", help="choose the command, -1 means all", type=int, default=-1 )
    
    args = parser.parse_args()
    #if args.verbose:
    #    print("verbosity turned on (but not used...)")

    
    app = QApplication(sys.argv)
    win = Win()
    win.show()
    #window.select_command( args.command )

    sys.exit(app.exec_())

