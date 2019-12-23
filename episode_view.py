from PyQt5.QtChart import QChart, QChartView, QLineSeries, QBarSeries, QHorizontalBarSeries, QBarSet, QScatterSeries, QValueAxis, QBarCategoryAxis
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygonF, QImage, QColor, QKeySequence, QTransform, QPixmap, QPageSize
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QSlider, QComboBox
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
    def __init__(self, history, model):
        self.history = history
        self.menu_series = dict()
        self.hotkey_series = dict()
        self.learning_series = dict()
        self.error_series = dict()
        self.cmd_id_series = dict()
        self.block_id = None
        self.model = model
        self.load_history()
        #self.add_to_view(self.view)


    ###################
    def load_history(self):
        for id in self.history.commands:
            self.menu_series[id] = create_scatter_series("Menu", 10, QScatterSeries.MarkerShapeCircle, Qt.blue)
            self.hotkey_series[id] = create_scatter_series("Hotkey", 10, QScatterSeries.MarkerShapeCircle, Qt.darkGreen)
            self.learning_series[id] = create_scatter_series("Menu Learning", 10, QScatterSeries.MarkerShapeCircle, Qt.darkMagenta)
            self.error_series[id] = create_scatter_series("Error", 10, QScatterSeries.MarkerShapeRectangle, Qt.red )
            #if self.view.param["show_cmd_id"]:
            self.cmd_id_series[id] = create_scatter_series("Cmd", 20, QScatterSeries.MarkerShapeCircle, QBrush( my_scatter_symbol( str(id) ) ))
            #if self.view.param["show_block"]:
            self.block_id = create_scatter_series("Block", 7, QScatterSeries.MarkerShapeCircle, Qt.black)

        action_vec = self.history.action if self.model else self.history.user_action
        time_vec = self.history.time if self.model else self.history.user_time
        success_vec = self.history.success if self.model else self.history.user_success 

        for i in range( len(action_vec) ):
            #print(i, history.action[i].bin_number, history.time[i])
            s = action_vec[i].strategy
            cmd = self.history.cmd[i]    #add the id of the comand on the graph
            time = round(time_vec[i],1)
            time = min(time,7)
            if s == Strategy.MENU :
                self.menu_series[cmd].append( i, time )

            elif s == Strategy.HOTKEY:
                self.hotkey_series[cmd].append(i, time)

            elif s == Strategy.LEARNING:
                self.learning_series[cmd].append(i, time )

            if success_vec[i] == 0:
                #y = time if self.view.param["error_on_place"] else 0.0
                y = 0.0
                self.error_series[cmd].append(i, y )
            
            #if self.view.param["show_cmd_id"]:
            self.cmd_id_series[cmd].append(i, time + 0.2 )   
            
            #if self.view.param["show_block"] and history.block_trial[i] == 0:
            if not self.model and self.history.block_trial[i] == 0:
                self.block_id.append(i,0) 


    


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
        self.d =[]
        self.param = dict()
        self.param["show_cmd_id"] = False
        self.param["show_block"] = True
        self.param["error_on_place"] = False    #not used...
        self.param["show_pred"] = False
        self.param["show_user"] = False
        
        self.slider = QSlider(Qt.Horizontal,self)
        self.slider.setMinimum(0)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect( self.filter )

        self.type_combo = QComboBox(self)
        self.type_combo.move(200,10)
        self.type_combo.activated.connect(self.select_type)
        self.type_combo.setVisible( False )
        
               
    ######################
    def select_type(self, value):
        type_value = self.type_combo.currentText()
        print("type value: ", type_value)
        self.param["show_pred"] = True
        self.param["show_user"] = True
        if type_value == "User only":
            self.param["show_pred"] = False
        if type_value == "Model only":
            self.param["show_user"] = False

        # for d in self.d:
        #     for id in d.history.commands:
        #         if d.model:
        #             self.set_visible(d, id, show_model)
        #         else
        #             self.set_visible(d, id, show_user)
        
        self.filter(self.slider.value() )


    ######################    
    def filter(self, value):
        #todo. We do not manage title very well as it takes information from the last d
        #functon only works if d.history has the same commands vec
        params = None
        user_id = -1
        print(value)
        for d in self.d:
            commands = d.history.commands
            params = d.history.params
            if not d.model:
                user_id = d.history.user_id
            for id in commands:
                cmd = -1
                if value < len( commands ):
                    cmd = commands[value]
                type_visible = True if (self.param["show_pred"] and d.model) or (self.param["show_user"] and not d.model) else False
                visible = ((value == len( commands) ) or id == cmd) and type_visible
                self.set_visible(d, id, visible)

        self.update_title(cmd, self.param["show_pred"], user_id, params)
  

    ######################    
    def set_full_history(self, history, show_pred=False, show_user=False):   
        self.chart().removeAllSeries()
        self.param["show_pred"] = show_pred
        self.param["show_user"] = show_user
        self.commands = history.commands
        if show_pred:
            data = EpisodeData( history, True )
            self.add_data( data )
            self.type_combo.addItem("Model only")
            self.type_combo.setCurrentText("Model only")
        if show_user:
            data = EpisodeData( history, False )
            self.type_combo.addItem("User only")
            self.type_combo.setCurrentText("User only")
            self.add_data( data )
            
        if show_pred and show_user:
            self.type_combo.addItem("User & Model")
            self.type_combo.setCurrentText("User & Model")

        self.type_combo.setVisible(True)

        self.slider.setMaximum( len(self.commands) )
        self.slider.setValue( len(self.commands) )
        
        self.update_title(-1, True, True, history.params)
        self.chart().createDefaultAxes()
        self.chart().axisY().setRange(0, 7)
        self.chart().axisX().setRange(0, len(history.action)+1)


    ############################
    def update_title(self, cmd, model, user_id, params=""):
        type_title = "Model" if model else "User" + str( user_id )
        param = params if model else ""
        cmd_title = "all commands" if cmd == -1 else "command " + str(cmd)
        self.chart().setTitle( type_title + " data for " + cmd_title + " " + params)


    ############################
    def add_data(self, d):
        self.d.append( d )
        for id in d.history.commands:
            self.chart().addSeries(d.menu_series[id])
            self.chart().addSeries(d.hotkey_series[id])
            self.chart().addSeries(d.learning_series[id])
            self.chart().addSeries(d.error_series[id])

            if self.param["show_cmd_id"]:
                self.chart().addSeries(d.cmd_id_series[id])

        if self.param["show_block"]:
            self.chart().addSeries( d.block_id )


    ##############################
    def set_visible(self,d, id, visible):
        if d.menu_series[id].isVisible() != visible:
            d.menu_series[id].setVisible( visible )
            d.hotkey_series[id].setVisible( visible )
            d.learning_series[id].setVisible( visible )
            d.error_series[id].setVisible( visible )




