import sys

#from simulationWidget import *
#from simulator import *
import numpy as np
import argparse
from gui_util import *
from experiment import *
from simulator import *
from simple_episode_view import *
from alpha_beta_model import *
from transD import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QPageLayout
from PyQt5.QtPrintSupport import *
from confusion_matrix import *

    
GUI = False  



class ModelGallery (QTabWidget) :
    def __init__(self):
        super(QTabWidget,self).__init__()
        
        self.gallery = dict()
        self.view_vec = []
        self.diff_view_vec = []
        self.confusion_matrix = ConfusionMatrix()    
        if GUI:
            self.move(20,20)
            self.resize(1000, 800)
            self.show()


    ##############################
    def load_model_user(self,model, user_id) :
        
        #get optimized parameters for this moel and this user
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


        #run the model with optimized parameters for this user.
        experiment = Experiment( './experiment/hotkeys_formatted_dirty.csv', 3, True, 'user_id=' + str(user_id) )
        return self.simulator.test_model_data(model, experiment)
        

    ################################
    def user_action_prob(self, h, target_cmd) :
        res = []
        trial = []
        for i in range( len( h.user_action ) ):
            cmd = h.cmd[i]
            if cmd == target_cmd : 
                res.append( h.user_action_prob[i] )
                trial.append( i )
        return res, trial


    ################################
    def set_page_row(self, page_vec, row_vec) : # page == user ; row == model and column == command

        for title in page_vec :
            if GUI :
                self.gallery[ title ] = SerieGallery()
                self.addTab( self.gallery[ title ], title )

            for cmd in range(0, 14) :
                user_action_prob = dict()
                trial = []

                for count, row in enumerate (row_vec) :
                    model = row
                    user_id = int( title )
                    d = self.load_model_user( model, user_id )
                    self.confusion_matrix.run(d[0])
                    if GUI :
                        view = EpisodeView( )
                        view.set_full_history( d[0], cmd, show_user= True)
                        self.gallery[ title ].add_view( view, count, cmd )
                        self.view_vec.append( view )
                        user_action_prob[count], trial = self.user_action_prob( d[0], cmd )
                if GUI:
                    diff_view = QChartView()
                    diff_view.setMinimumHeight(300)
                    diff_view.setMinimumWidth(850)
                    diff_chart = QChart()
                    diff_view.setChart( diff_chart )
                    diff_vec = ( np.array( user_action_prob[0] ) - np.array( user_action_prob[1] )  )* 1.
                    #print(user_action_prob[0])
                    self.diff_line = QLineSeries()
                    for i in range(0, len(trial) ) :
                        self.diff_line << QPointF( trial[i], diff_vec[i] )
                    diff_chart.addSeries( self.diff_line )
                    diff_view.chart().createDefaultAxes()
                    diff_view.chart().axisY().setRange(-1, 1)
                    diff_view.chart().axisX().setTitleText("Trial id")
                    diff_view.chart().axisY().setTitleText("Diff")
                    self.gallery[title].add_view(diff_view, len(row_vec), cmd)
        self.confusion_matrix.save( './meta_analysis/model_fit_confusion_matrix.csv' )
    

            # for count, row in enumerate (row_vec) :
            #     model = row
            #     user_id = int( title )
            #     d = self.load_model_user( model, user_id )

            #     for cmd in range(0, 14) :
            #         view = EpisodeView( )
            #         view.set_full_history( d[0], cmd)
            #         self.gallery[ title ].add_view( view, count, cmd )
            #         self.view_vec.append( view )

        

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
    model_vec = [ TransD(env, 'TRANS_DCK'), Alpha_Beta_Model(env, 'RW_CK') ]
    #user_vec = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10','11','12','13']
    user_vec = ['1']
    #user_vec = ['1']
    app = QApplication(sys.argv)
    if GUI :
        
        app.setApplicationName("Fitting Models to User data")
        gallery = ModelGallery()
        gallery.simulator = Simulator(env)
        gallery.set_page_row( user_vec, model_vec)
        gallery.show()
        sys.exit(app.exec_())
    else:
        gallery = ModelGallery()
        gallery.simulator = Simulator(env)
        gallery.set_page_row( user_vec, model_vec)


