import sys

#from simulationWidget import *
#from simulator import *
import numpy as np
import argparse
from experiment import *
from gui_util import *
from simulator import *
from simple_episode_view import *
from alpha_beta_model import *
from transD import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QPageLayout
from PyQt5.QtPrintSupport import *
from confusion_matrix import *


    



class ModelGallery (QTabWidget) :
    def __init__(self):
        super(QTabWidget,self).__init__()
        self.move(20,20)
        self.resize(1000, 800)
        self.gallery = dict()
        self.view_vec = []    
        self.confusion_matrix = ConfusionMatrix()
        self.show()



    def set_optimal_parameter(self, model, user_id) :
        filename = './likelyhood/optimisation/log_' + model.name + '_' + str(user_id) + '.csv'
        param_name = []
        param_value = []

        with open(filename, 'r') as csvFile:
            reader = csv.reader(csvFile, delimiter= ';')
            header_flag = True

            for row in reader:
                if header_flag :
                    header_flag = False

                    for i in range(5, len(row) ) :
                        param_name.append( row[i] )

                else :
                    for i in range(5, len(row) ) :
                        v = float( row[i] )
                        if param_name[i-5] == "HORIZON" :
                            param_value.append( int( v ) )
                        else :
                            param_value.append( v )

        for i in range(0, len(param_name) ) :
             model.params.value[ param_name[i] ] = param_value[i]

    
    ################################
    def set_page_row(self, page_vec, row_vec, experiment) : # page == user ; row == model and column == command
        

        for title in page_vec : #user id
            container = QWidget()
            container_layout = QVBoxLayout()
            container.setLayout( container_layout )
            user_gallery = SerieGallery()
            model_gallery = SerieGallery()
            container_layout.addWidget( user_gallery )
            container_layout.addWidget( model_gallery, stretch=4 )
            self.gallery[ title ] = model_gallery
            self.addTab( container, title )
            model_gallery.horizontalScrollBar().valueChanged.connect( user_gallery.horizontalScrollBar().setValue )
            

            nb_cmds = 14
            user_id = int( title )
            experiment = Experiment( './experiment/hotkeys_formatted_dirty.csv', 3, True, 'user_id=' + str(title) )
            d = copy.deepcopy( experiment.data[0] )
            for cmd in range(0, nb_cmds) :
                user_view = EpisodeView( )
                user_view.set_full_history( d, cmd, show_user = True, show_meta_info = False)
                user_gallery.add_view( user_view, 0, cmd )


                #self.view_vec.append( view )

            #print("experiment             :", title, experiment )
            count = 0 
            for model in row_vec :
                self.set_optimal_parameter( model, user_id )
                d = copy.deepcopy( experiment.data[0] )
                d = self.simulator.simple_simulate( model, d )
                self.confusion_matrix.run(d)
                
                for cmd in range(0, nb_cmds) :
                    model_view = EpisodeView( )
                    model_view.set_full_history( d, cmd, show_user= False, show_meta_info = True)
                    model_gallery.add_view( model_view, count, cmd )
                    self.view_vec.append( model_view )

                    matrix_view = ConfusionMatrixView()
                    mat = self.confusion_matrix.mat(model.name, user_id, cmd)
                    matrix_view.set_matrix(model.name, user_id, cmd, mat)
                    model_gallery.add_view( matrix_view, count + len(row_vec), cmd )
                count = count + 1
                    #user_action_prob[count], trial = self.user_action_prob( d[0], cmd )
                    
        #self.confusion_matrix.print()
        self.confusion_matrix.save( './meta_analysis/free_simulation_confusion_matrix.csv' )
    

    


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
    
    env = Environment("./parameters/environment.csv")
    env.value['n_strategy'] = 3 #only menus and hotkeys
    filename = './experiment/hotkeys_formatted_dirty.csv'
    experiment = Experiment( filename, env.value['n_strategy'] )

    #model_vec = [ TransD(env, 'TRANS_D'), TransD(env, 'TRANS_DCK'), TransD(env, 'TRANS_DK0'), TransD(env, 'TRANS_DCK0'), Alpha_Beta_Model(env, 'RW_CK') ]
    model_vec = [ TransD(env, 'TRANS_D'), TransD(env, 'TRANS_DCK'), Alpha_Beta_Model(env, 'RW_CK') ]
    
    user_vec = ['1', '4', '7', '10', '13']
    
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("Fitting Models to User data")
    model_gallery = ModelGallery()
    model_gallery.simulator = Simulator(env)
    model_gallery.set_page_row( user_vec, model_vec, experiment)
    model_gallery.show()
    sys.exit(app.exec_())

