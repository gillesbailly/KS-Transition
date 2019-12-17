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

        self.menu_series = dict()
        self.hotkey_series = dict()
        self.learning_series = dict()
        self.error_series = dict()
        self.cmd_id_series = dict()
        # self.menu_series = create_scatter_series("Menu", 10, QScatterSeries.MarkerShapeCircle, Qt.blue)
        # self.hotkey_series = create_scatter_series("Hotkey", 10, QScatterSeries.MarkerShapeCircle, Qt.darkGreen)
        # self.learning_series = create_scatter_series("Menu Learning", 10, QScatterSeries.MarkerShapeRectangle, Qt.darkMagenta)
        # self.error_series = create_scatter_series("Error", 10, QScatterSeries.MarkerShapeRectangle, QBrush( my_scatter_symbol('x') ) )

        # chart.addSeries(self.menu_series)
        # chart.addSeries(self.hotkey_series)
        # chart.addSeries(self.learning_series)
        # chart.addSeries(self.error_series)


    def filter(self, value):
        for id in self.commands:
            cmd = -1
            if value < len(self.commands):
                cmd = self.commands[value]

            visible = (value == len(self.commands)) or id == cmd
            if self.menu_series[id].isVisible() != visible:
                self.menu_series[id].setVisible( visible )
                self.hotkey_series[id].setVisible( visible )
                self.learning_series[id].setVisible( visible )
                self.error_series[id].setVisible( visible )
                self.cmd_id_series[id].setVisible( visible )
                

    def set_full_history(self, history, show_pred=False):
        print("set full history")
        self.commands = history.commands
        slider = QSlider(Qt.Horizontal,self)
        slider.setMinimum(0)
        slider.setMaximum( len(self.commands) )
        slider.setSingleStep(1)
        slider.setValue( len(self.commands) )
        slider.valueChanged.connect( self.filter )
        for id in history.commands:
            self.menu_series[id] = create_scatter_series("Menu", 10, QScatterSeries.MarkerShapeCircle, Qt.blue)
            self.chart().addSeries(self.menu_series[id])
            self.hotkey_series[id] = create_scatter_series("Hotkey", 10, QScatterSeries.MarkerShapeCircle, Qt.darkGreen)
            self.chart().addSeries(self.hotkey_series[id])
            self.learning_series[id] = create_scatter_series("Menu Learning", 10, QScatterSeries.MarkerShapeRectangle, Qt.darkMagenta)
            self.chart().addSeries(self.learning_series[id])
            self.error_series[id] = create_scatter_series("Error", 10, QScatterSeries.MarkerShapeRectangle, QBrush( my_scatter_symbol('x') ) )
            self.chart().addSeries(self.error_series[id])
            self.cmd_id_series[id] = create_scatter_series("Cmd", 20, QScatterSeries.MarkerShapeCircle, QBrush( my_scatter_symbol( str(id) ) ))
            self.chart().addSeries(self.cmd_id_series[id])



        # cmd_series_all = []
        # for i in range( len( history.commands) ):
        #     cmd_series_all.append( create_scatter_series("Cmd", 10, QScatterSeries.MarkerShapeCircle, QBrush( my_scatter_symbol( str(i) ) )) )

        action_vec = history.action if show_pred else history.user_action
        time_vec = history.time if show_pred else history.user_time
        success_vec = history.success if show_pred else history.user_success 

        for i in range( len(action_vec) ):
                #print(i, history.action[i].bin_number, history.time[i])
                s = action_vec[i].strategy
                cmd = history.cmd[i]    #add the id of the comand on the graph
                time = round(time_vec[i],1)
                if s == Strategy.MENU :
                    self.menu_series[cmd].append( i, time )

                elif s == Strategy.HOTKEY:
                    self.hotkey_series[cmd].append(i, time)

                elif s == Strategy.LEARNING:
                    self.learning_series[cmd].append(i, time )

                if success_vec[i] == 0:
                    self.error_series[cmd].append(i, time )

                self.cmd_id_series[cmd].append(i, time + 0.2 )      

        self.chart().createDefaultAxes()
        self.chart().axisY().setRange(0, 7)
        self.chart().axisX().setRange(0, len(history.action)+1)   
