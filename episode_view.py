from PyQt5.QtChart import QChart, QChartView, QLineSeries, QBarSeries, QHorizontalBarSeries, QBarSet, QScatterSeries, QValueAxis, QBarCategoryAxis
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygonF, QImage, QColor, QKeySequence, QTransform, QPixmap, QPageSize
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QSlider
from util import *
import sys


##########################################
#                                        #
#             Util functions             #
#                                        #
##########################################
def create_scatter_series(name, marker_size, marker_shape, brush):
    series = QScatterSeries()
    series.setUseOpenGL(True)
    series.setName(name)
    series.setBrush(brush)
    series.setMarkerSize(marker_size)
    series.setMarkerShape(marker_shape)
    series.setPen(Qt.transparent)
    return series

def my_scatter_symbol(c):
    symbol = QImage(40,20, QImage.Format_ARGB32)
    symbol.fill(Qt.transparent)

    painter = QPainter()
    painter.begin(symbol)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.black)
    painter.drawText(4,11, c)
    painter.end()
    return symbol



##########################################
#                                        #
#    Proxy between history and View      #
#                                        #
##########################################
class EpisodeData():
    def __init__(self, history, view):
        self.history = None
        self.view = None
        self.menu_series = dict()
        self.hotkey_series = dict()
        self.learning_series = dict()
        self.error_series = dict()
        self.cmd_id_series = dict()
        self.block_id = None
        self.load(history,view)
        self.add_to_view(self.view)


    ###################
    def load(self, history, view):
        self.history = history
        self.view = view
        for id in self.history.commands:
            self.menu_series[id] = create_scatter_series("Menu", 10, QScatterSeries.MarkerShapeCircle, Qt.blue)
            self.hotkey_series[id] = create_scatter_series("Hotkey", 10, QScatterSeries.MarkerShapeCircle, Qt.darkGreen)
            self.learning_series[id] = create_scatter_series("Menu Learning", 10, QScatterSeries.MarkerShapeCircle, Qt.darkMagenta)
            self.error_series[id] = create_scatter_series("Error", 10, QScatterSeries.MarkerShapeRectangle, Qt.red )
            if self.view.param["show_cmd_id"]:
                self.cmd_id_series[id] = create_scatter_series("Cmd", 20, QScatterSeries.MarkerShapeCircle, QBrush( my_scatter_symbol( str(id) ) ))
            if self.view.param["show_block"]:
                self.block_id = create_scatter_series("Block", 7, QScatterSeries.MarkerShapeCircle, Qt.black)

        show_pred = view.param["show_pred"]
        action_vec = history.action if show_pred else history.user_action
        time_vec = history.time if show_pred else history.user_time
        success_vec = history.success if show_pred else history.user_success 

        for i in range( len(action_vec) ):
            #print(i, history.action[i].bin_number, history.time[i])
            s = action_vec[i].strategy
            cmd = history.cmd[i]    #add the id of the comand on the graph
            time = round(time_vec[i],1)
            time = min(time,7)
            if s == Strategy.MENU :
                self.menu_series[cmd].append( i, time )

            elif s == Strategy.HOTKEY:
                self.hotkey_series[cmd].append(i, time)

            elif s == Strategy.LEARNING:
                self.learning_series[cmd].append(i, time )

            if success_vec[i] == 0:
                y = time if self.view.param["error_on_place"] else 0.0
                self.error_series[cmd].append(i, y )
            
            if self.view.param["show_cmd_id"]:
                self.cmd_id_series[cmd].append(i, time + 0.2 )   
            
            if self.view.param["show_block"] and history.block_trial[i] == 0:
                self.block_id.append(i,0) 


    ############################
    def add_to_view(self, view):
        for id in self.history.commands:
            view.chart().addSeries(self.menu_series[id])
            view.chart().addSeries(self.hotkey_series[id])
            view.chart().addSeries(self.learning_series[id])
            view.chart().addSeries(self.error_series[id])

            if self.view.param["show_cmd_id"]:
                view.chart().addSeries(self.cmd_id_series[id])

        if self.view.param["show_block"]:
            view.chart().addSeries( self.block_id )


    ##############################
    def set_visible(self,id, visible):
        if self.menu_series[id].isVisible() != visible:
            self.menu_series[id].setVisible( visible )
            self.hotkey_series[id].setVisible( visible )
            self.learning_series[id].setVisible( visible )
            self.error_series[id].setVisible( visible )


##########################################
#                                        #
#    Draw Information for one user       #
#                                        #
##########################################
class EpisodeView(QChartView):

    def __init__(self):
        super().__init__()
        chart = QChart()
        chart.setDropShadowEnabled(False)
        chart.legend().setVisible(False)
        self.setChart(chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumHeight(300)
        self.param = dict()
        self.param["show_cmd_id"] = False
        self.param["show_block"] = True
        self.param["error_on_place"] = False
        self.param["show_pred"] = True
        self.episode_series = dict()
        self.current_id = -1

 
    ######################    
    def filter(self, value):
        for id in self.commands:
            cmd = -1
            if value < len(self.commands):
                cmd = self.commands[value]

            visible = (value == len(self.commands)) or id == cmd
            self.episode_series[self.current_id].set_visible(id, visible)

        type_title = "Model" if self.param["show_pred"] else "User"
        cmd_title = "all commands" if cmd == -1 else "command " + str(cmd)
        self.chart().setTitle( type_title + " data for " + cmd_title)
  

    ######################    
    def set_full_history(self, history, show_pred=False):
        self.chart().removeAllSeries()
        self.param["show_pred"] = show_pred
        self.commands = history.commands
        self.episode_series[ history.episode_id ] = EpisodeData( history, self )
        self.current_id = history.episode_id

        
        slider = QSlider(Qt.Horizontal,self)
        slider.setMinimum(0)
        slider.setMaximum( len(self.commands) )
        slider.setSingleStep(1)
        slider.setValue( len(self.commands) )
        slider.valueChanged.connect( self.filter )

        type_title = "Model" if self.param["show_pred"] else "User"
        cmd_title = "all commands"
        self.chart().setTitle( type_title + " data for " + cmd_title)
           

        self.chart().createDefaultAxes()
        self.chart().axisY().setRange(0, 7)
        self.chart().axisX().setRange(0, len(history.action)+1)

