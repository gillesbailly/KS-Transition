import numpy as np
from util import *
from math import *
import pandas as pd
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QBarSeries, QAreaSeries, QAbstractSeries, QStackedBarSeries, QHorizontalBarSeries, QBarSet, QScatterSeries, QValueAxis, QBarCategoryAxis
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygonF, QImage, QColor, QKeySequence, QTransform, QPixmap, QPageSize
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QPointF
from PyQt5.QtWidgets import QSlider, QComboBox, QLabel, QWidget, QHBoxLayout
import csv

##########################################
#                                        #
#             Experiment                 #
#                                        #
##########################################



class ConfusionMatrix(object) :

    ###################
    def __init__(self):
        self.conf_mat_vec = dict()
        self.n_conf_mat_vec  = dict()

    def mat(self, model, user_id, cmd) :
        return self.conf_mat_vec[ (model, user_id, cmd ) ]

    def n_mat(self, model, user_id, cmd) :
        return self.conf_mat_count_vec[ (model, user_id, cmd ) ]

    def create_input(self, model, user_id, cmd_id ):
        self.conf_mat_vec[ (model, user_id, cmd_id ) ] = np.zeros( (3,3) )
        self.n_conf_mat_vec[ (model, user_id, cmd_id ) ] = np.zeros( (3,3) )


    ##################################
    def update(self, model, user_id, user_action, model_action, value_vec ) :
        m = self.conf_mat_vec[ (model, user_id, user_action.cmd ) ]
        #m[ user_action.strategy ][ model_action.strategy ] += value
        m[ user_action.strategy ] += value_vec

        mc = self.n_conf_mat_vec[ (model, user_id, user_action.cmd ) ]
        mc[ user_action.strategy ][ model_action.strategy ] += 1


    ##################################
    def run(self, h) :
        user_id = h.user_id
        model = h.model_name
        commands = h.commands
        for cmd_id in h.commands:
            self.create_input( model, user_id, cmd_id)

        for i in range( len( h.action ) ):
            self.update( model, user_id, h.user_action[i], h.action[i], h.prob_vec[i] ) 

        return self.conf_mat_vec


    #################################
    def save(self, path) :
        with open(path, mode= 'w' ) as out:
            writer = csv.writer(out, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            header = ['model', 'user', 'cmd', 'user_strategy', 'pred_strategy', 'likelyhood', 'n', 'total_user', 'total_model']
            strategy_name = ['Menu', 'Hotkey', 'Learning']
            writer.writerow(header)

            for key in self.conf_mat_vec :
            	#sum_vec = [0,0,0]
            	#sum_vec[0] = self.conf_mat_vec[key] [user_strategy]
            	#print(mat, "total user: ", np.sum(mat, axis=1), "total pred: ", np.sum(mat, axis=0))
                for user_strategy in [0,1,2] :
                    for model_strategy in [0,1,2] :
                        n = self.n_conf_mat_vec[key] [user_strategy][model_strategy]
                        sum_user = np.sum( self.n_conf_mat_vec[key], axis=1 )[user_strategy]
                        sum_model = np.sum( self.n_conf_mat_vec[key], axis =0 )[model_strategy]
                        ll = self.conf_mat_vec[key] [user_strategy][model_strategy] / float(sum_user) if sum_user > 0 else 0
                        row = [key[0], key[1], key[2], strategy_name[ user_strategy ], strategy_name[ model_strategy ], ll, n, sum_user, sum_model ]
                        writer.writerow(row)


    #################################
    def print(self) :
        for key in self.conf_mat_vec.keys() :
            print( key, '\n', self.n_conf_mat_vec[key], self.conf_mat_vec[key], '\n' )


class ConfusionMatrixView(QChartView):
    def __init__(self):
        super().__init__()
        chart = QChart()
        chart.setDropShadowEnabled(False)
        chart.legend().setVisible(False)
        self.setChart(chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumHeight(200)
        self.setMaximumHeight(200)
        self.setMinimumWidth(750)


######################    
    def set_matrix(self, model_name, user_id, cmd, matrix, count_matrix):   
        self.chart().removeAllSeries()
        
        alpha_color = 255
        hotkey_color = QColor(0,100,0, alpha_color)
        menu_color = QColor(0,0,200, alpha_color)
        learning_color = QColor(200,0,100, alpha_color)

        set_menu = QBarSet("Menu")
        set_menu.setBrush(menu_color)
        set_hotkey = QBarSet("Hotkey")
        set_hotkey.setBrush(hotkey_color)
        set_learning = QBarSet("Learning")
        set_learning.setBrush(learning_color)
        #set_all = QBarSet("All")
        #set_all.setBrush(Qt.black)

        set_menu     << matrix[0][0] / float( count_matrix[0][0] ) << matrix[1][0] / float( count_matrix[1][0] )<< matrix[2][0] / float( count_matrix[2][0] )
        set_hotkey   << matrix[0][1] / float( count_matrix[0][1] ) << matrix[1][1] / float( count_matrix[1][1] ) << matrix[2][1] / float( count_matrix[2][1] )
        set_learning << matrix[0][2] / float( count_matrix[0][2] ) << matrix[1][2] / float( count_matrix[1][2] ) << matrix[2][2] / float( count_matrix[2][2] )
        #set_all << matrix[0][0] + matrix[0][1] + matrix[0][2] << matrix[1][0] + matrix[1][1] + matrix[1][2] << matrix[2][0] + matrix[2][1] + matrix[2][2]
        



        self.series = QStackedBarSeries()
        #self.series.append(set_all)
        self.series.append(set_menu)
        self.series.append(set_hotkey)
        self.series.append(set_learning)
        self.chart().addSeries( self.series )
        
        self.chart().setTitle( "MODEL: " + model_name + "      user: " + str(user_id) + " - cmd: " + str(cmd) )
        self.chart().layout().setContentsMargins(0, 0, 0, 0);
        self.chart().createDefaultAxes()
        categories = ["Menu", "Hotkey", "Learning"]
        axis = QBarCategoryAxis()
        axis.append(categories)
        axis.setTitleText("User")
        self.chart().setAxisX(axis, self.series)





if __name__=="__main__":
	mat = np.zeros( (3,3) )
	mat[0,0] = 1
	mat[0,1] = 2
	mat[0,2] = 3
	mat[1,1] = 10
	mat[2,2] = 100
	print(mat)
	m =[7,7,7]

	mat[1] += m
	print(mat)
#	print(mat, "total user: ", np.sum(mat, axis=1), "total pred: ", np.sum(mat, axis=0))
	


     #confMat = ConfusionMatrix()
     #res = confMat.get_confusion_matrix_list( 0)

     #for key in res.keys() :
     #    print( key, res[key] )



     #user_id = 1
    #cmd_id = 1
    #    model = "TRANS_D"
        # self.conf_mat_vec[ (model, user_id, cmd_id) ] = np.zeros( (3,3) )

        # user_id = 7
        # cmd_id = 8
        # self.conf_mat_vec[ (model, user_id, cmd_id) ] = np.zeros( (3,3) )


        # user_action = Action(1, Strategy.MENU)
        # model_action = Action(1, Strategy.MENU)
        # self.update( model, 1, user_action, model_action )
        # model_action = Action(1, Strategy.HOTKEY)
        # self.update( model, 1, user_action, model_action )
        # model_action = Action(1, Strategy.LEARNING)
        # self.update( model, 1, user_action, model_action )
        # self.update( model, 1, user_action, model_action )
        # self.update( model, 1, user_action, model_action )
        # self.update( model, 1, user_action, model_action )
        
        # user_action = Action(8, Strategy.HOTKEY)
        # model_action = Action(8, Strategy.HOTKEY)    

#     print(annotation.trial_range(1, 'Strawberry'), annotation.occurence_range(1, 'Strawberry') )
