from PyQt5.QtChart import QChart, QChartView, QLineSeries, QBarSeries, QAbstractSeries, QHorizontalBarSeries, QBarSet, QScatterSeries, QValueAxis, QBarCategoryAxis
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygonF, QImage, QColor, QKeySequence, QTransform, QPixmap, QPageSize
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QPointF
from PyQt5.QtWidgets import QSlider, QComboBox, QLabel, QWidget, QHBoxLayout
from util import *
import sys

max_y = 10

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

def create_line_series(name, color, size=1):
    series = QLineSeries()
    series.setUseOpenGL(True)
    series.setName(name)
    pen = series.pen()
    pen.setWidth(size);
    pen.setColor(color);
    series.setPen(pen);
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
#             GROUP                      #
#                                        #
##########################################
class Group():
    def __init__(self, name, _type, size, default_color=Qt.white):
        self.default_color = Qt.white
        self.view = None
        self.name = name
        self.menu = dict()
        self.param = None
        self.hotkey = dict()
        self.learning = dict()
        self.type = _type
        self.size = size
        

    ###########################
    def menu_series_clicked(self):
        print(self.name, " menu: " )

    ###########################
    def hotkey_series_clicked(self, p):
        print(self.name, " hotkey: ", p )

    ###########################
    def learning_series_clicked(self, p):
        print(self.name, " learning: ", p )


    ###########################
    def load(self, commands):
        for id in commands:
            if self.type == "scatter" :
                self.menu[id] = create_scatter_series("Menu", self.size, QScatterSeries.MarkerShapeCircle, Qt.blue if self.default_color == Qt.white else self.default_color)
                self.menu[id].clicked.connect( self.menu_series_clicked )
                self.hotkey[id] = create_scatter_series("Hotkey", self.size, QScatterSeries.MarkerShapeCircle, Qt.darkGreen if self.default_color == Qt.white else self.default_color)
                self.hotkey[id].clicked.connect( self.hotkey_series_clicked )
                self.learning[id] = create_scatter_series("Menu Learning", self.size, QScatterSeries.MarkerShapeCircle, Qt.darkMagenta if self.default_color == Qt.white else self.default_color)
                self.learning[id].clicked.connect( self.learning_series_clicked )
            elif self.type == "line" :
                self.menu[id] = create_line_series("Prob", Qt.blue if self.default_color == Qt.white else self.default_color, self.size)
                self.menu[id].clicked.connect( self.menu_series_clicked )
                self.hotkey[id] = create_line_series("Prob", Qt.darkGreen if self.default_color == Qt.white else self.default_color, self.size)
                self.hotkey[id].clicked.connect( self.hotkey_series_clicked )
                self.learning[id] = create_line_series("Prob", Qt.darkMagenta if self.default_color == Qt.white else self.default_color, self.size)
                self.learning[id].clicked.connect( self.learning_series_clicked )



    ############################
    def add_item(self, id, strategy, x, y):
        if strategy == Strategy.MENU :
            self.menu[id].append( x, y )
        elif strategy == Strategy.HOTKEY:
            self.hotkey[id].append(x,y)
        elif strategy == Strategy.LEARNING:
            self.learning[id].append(x,y )


    ############################
    def add_items(self, id, x, y_vec):   #len vec == 2 or 3 
        self.menu[id].append( x, y_vec[0] )
        self.hotkey[id].append( x, y_vec[1] )
        if len(y_vec) ==3:
            self.learning[id].append( x, y_vec[2] )

    ##############################
    def add_to_chart(self, chart):
        
        for series in self.menu.values():
            chart.addSeries(series)
            series.clicked.connect( self.menu_series_clicked )
        for series in self.hotkey.values():
            chart.addSeries(series)
            series.clicked.connect( self.hotkey_series_clicked )
        for series in self.learning.values():
            chart.addSeries(series)
            series.clicked.connect( self.learning_series_clicked )

##########################################
#                                        #
#    Proxy between history and View      #
#                                        #
##########################################
class EpisodeData():

    def __init__(self, history, target_cmd ):
        self.history = history
        self.group = dict()
        self.group[ "empirical" ]         = Group("empirical", "scatter", 10)
        self.group[ "empirical_error" ]   = Group("empirical_error", "scatter", 18, Qt.red)
        self.group[ "prob" ]              = Group("prob", "line", 5)

        
        self.individual = dict()
        self.individual["user_action_prob"] = None
        self.individual["knowledge"] = None        

        self.block_id = None
        self.outlier_1 = None
        self.outlier_2 = None
        self.load_history(target_cmd)


    ##############################
    def add_series_to_chart(self, chart):
        chart.addSeries( self.outlier_2 )
        chart.addSeries( self.outlier_1 )

        for g in self.group.values() :
            g.add_to_chart( chart )

        for i in self.individual.values() :
            chart.addSeries(i)
        chart.addSeries( self.block_id )


    ##############################
    def load_history(self, target_cmd):
        for g in self.group.values():
            g.load( self.history.commands )
        
        self.individual["user_action_prob"] = create_line_series("user_action_prob", Qt.yellow, 3)
        self.individual["knowledge"] = create_line_series("knowledge", Qt.black, 10)   

        self.block_id = create_scatter_series("Block", 7, QScatterSeries.MarkerShapeCircle, Qt.black)
        self.outlier_1 = create_scatter_series("outlier_1", 18, QScatterSeries.MarkerShapeCircle, Qt.magenta)
        self.outlier_2 = create_scatter_series("outlier_2", 18, QScatterSeries.MarkerShapeCircle, Qt.magenta)
        #self.outlier_3 = create_scatter_series("outlier_3", 18, QScatterSeries.MarkerShapeCircle, Qt.magenta)
        #self.outlier_4 = create_scatter_series("outlier_4", 18, QScatterSeries.MarkerShapeCircle, Qt.magenta)

        action_vec =  self.history.user_action
        time_vec =  self.history.user_time
        success_vec =  self.history.user_success 
        max_time = 7.5

        for i in range( len(action_vec) ):
            cmd = self.history.cmd[i]
            if cmd == target_cmd : 
                s = action_vec[i].strategy

                time = round(time_vec[i],1)
                time_band1 = min(time, max_time)

                self.group["empirical"].add_item(cmd, s, i, time_band1)
                if success_vec[i] == 0:
                    self.group["empirical_error"].add_item(cmd, s, i, time_band1 )

                if time >= 2 * max_time :
                    self.outlier_1.append(i, time_band1+0.5 )
                if time >= 3 * max_time :
                    self.outlier_2.append(i, time_band1+1 )
                if time >= 4 * max_time :
                    self.outlier_2.append(i, time_band1+1.5 )
                if time >= 5 * max_time :
                    self.outlier_2.append(i, time_band1+2 )

                if len( self.history.prob_vec ) > 0 :
                    prob_vec = np.array( self.history.prob_vec[i] ) * float(max_y)
                    self.group["prob"].add_items(cmd, i, prob_vec )
                if len( self.history.user_action_prob) > 0 :
                    self.individual[ "user_action_prob" ].append(i, self.history.user_action_prob[i] * float(max_y) )

                if len( self.history.knowledge ) > 0 :
                    self.individual[ "knowledge" ].append(i, self.history.knowledge[i] * float(max_y) )

            if self.history.block_trial[i] == 0:
                self.block_id.append(i,0)
    


                
##########################################
#                                        #
#    Draw Information for one user       #
#                                        #
##########################################
class EpisodeView(QChartView):
    view_selected = pyqtSignal(int, int, int, str) #user id, cmd, trial_id
    cursor_moved = pyqtSignal(int, int)
    def __init__(self):
        super().__init__()
        chart = QChart()
        chart.setDropShadowEnabled(False)
        chart.legend().setVisible(False)
        self.setChart(chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumHeight(300)
        self.setMinimumWidth(850)
        self.d = None
        self.cmd = -1
        
        


    ######################    
    def set_full_history(self, history, target_cmd ):   
        self.chart().removeAllSeries()
        self.commands = history.commands
        self.d = history
        self.cmd = target_cmd
        self.trial_id = -1
        data = EpisodeData( history, target_cmd )
        data.add_series_to_chart( self.chart() )

        self.cursorLine = QLineSeries()
        self.cursorLine << QPointF(0,0) << QPointF(0,10)
        self.chart().addSeries( self.cursorLine )

        self.start_transition = QLineSeries()
        x_start_trans = history.start_transition[ history.commands.index(target_cmd) ]
        self.start_transition << QPointF(x_start_trans, 0) << QPointF(x_start_trans,10)
        self.chart().addSeries( self.start_transition )
        

        
        self.chart().setTitle( "user: " + str(history.user_id) + " - cmd: " + str(target_cmd) + " - technique: " + history.technique_name  )
        self.chart().layout().setContentsMargins(0, 0, 0, 0);
        self.chart().createDefaultAxes()
        self.chart().axisY().setRange(0, max_y)
        self.chart().axisY().setTitleText("Time")        
        self.chart().axisX().setRange(0, 750)
        self.chart().axisX().setTitleText("Trial id")
        self.chart().axisX().setTickType(QValueAxis.TicksFixed)
        self.chart().axisX().setTickCount(11)
        self.chart().axisX().setLabelFormat("%i")

    #caputre mouse move event to show the vertical cursor line
    def mouseMoveEvent(self, e) :
        scene_pos = self.mapToScene( e.pos() )
        chartItemPos = self.chart().mapFromScene( scene_pos )
        value = self.chart().mapToValue( chartItemPos )
        self.cursorLine.replace(0, value.x(), 0)
        self.cursorLine.replace(1, value.x(), 10)
        
        #print(value)
        #self.cursor_moved.emit( value.x(), value.y() )
        self.trial_id = int(value.x())

    def infos(self, trial_id):
        if (trial_id >= 0 and trial_id < len( self.d.cmd ) ) :
            if self.d.cmd[ trial_id ] == self.cmd :
                row = self.d.user_extra_info[ trial_id]
                return ', '.join(row)
        return ""

    #caputre mouse move event to show the vertical cursor line
    def mouseReleaseEvent(self, e) :
        scene_pos = self.mapToScene( e.pos() )
        chartItemPos = self.chart().mapFromScene( scene_pos )
        value = self.chart().mapToValue( chartItemPos )
        #print(value)
        #self.cursor_moved.emit( value.x(), value.y() )
        trial_id = int(value.x())
        infos = self.infos( trial_id )
        #if self.trial_id
        #info_str = 

        self.view_selected.emit( self.d.user_id, self.cmd, trial_id, infos)
    
    

