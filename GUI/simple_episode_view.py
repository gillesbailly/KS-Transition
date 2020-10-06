from PyQt5.QtChart import QChart, QChartView, QLineSeries, QBarSeries, QAreaSeries, QAbstractSeries, QHorizontalBarSeries, QBarSet, QScatterSeries, QValueAxis, QBarCategoryAxis
from PyQt5.QtGui import QPalette, QPainter, QPen, QBrush, QPolygonF, QImage, QColor, QKeySequence, QTransform, QPixmap, QPageSize
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
    series.setOpacity(0.7)
    return series

def create_line_series(name, color, size=1):
    series = QLineSeries()
    series.setUseOpenGL(True)
    series.setName(name)
    pen = series.pen()
    pen.setWidth(size);
    pen.setColor(color);
    series.setPen(pen);
    series.setOpacity(0.7)
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
    def __init__(self, cmd, name, _type, size, default_color=Qt.white):
        self.cmd = cmd
        self.default_color = default_color
        alpha_color = 100
        hotkey_color   = QColor(100,250,100, alpha_color)
        menu_color     = QColor(50,150,255, alpha_color)
        learning_color = QColor(250,50,100, alpha_color)
        self.type = _type
        self.name = name
        self.size = size
        
        if self.type == "scatter" :
            self.menu     = create_scatter_series("Menu", self.size, QScatterSeries.MarkerShapeCircle, menu_color if self.default_color == Qt.white else self.default_color)
            self.hotkey   = create_scatter_series("Hotkey", self.size, QScatterSeries.MarkerShapeCircle, hotkey_color if self.default_color == Qt.white else self.default_color)
            self.learning = create_scatter_series("Menu Learning", self.size, QScatterSeries.MarkerShapeCircle, learning_color if self.default_color == Qt.white else self.default_color)
        elif self.type == "line" :
            self.menu     = create_line_series( name +" prob", menu_color if self.default_color == Qt.white else self.default_color, self.size)
            self.hotkey   = create_line_series( name +" prob", hotkey_color if self.default_color == Qt.white else self.default_color, self.size)
            self.learning = create_line_series( name + "prob", learning_color if self.default_color == Qt.white else self.default_color, self.size)
                

        
    ############################
    def add_item(self, strategy, x, y):
        if strategy == Strategy.MENU :
            self.menu.append( x, y )
        elif strategy == Strategy.HOTKEY:
            self.hotkey.append(x,y)
        elif strategy == Strategy.LEARNING:
            self.learning.append(x,y )


    ############################
    def add_items(self, x, y_vec):   #len vec == 2 or 3 
        self.menu.append( x, y_vec[0] )
        self.hotkey.append( x, y_vec[1] )
        if len(y_vec) ==3:
            self.learning.append( x, y_vec[2] )

    ##############################
    def add_to_chart(self, chart):
        chart.addSeries( self.menu )
        chart.addSeries( self.hotkey )
        chart.addSeries( self.learning ) 

    ###############################
    def remove_to_chart( self, chart ):
        chart.removeSeries( self.menu )
        chart.removeSeries( self.hotkey )
        chart.removeSeries( self.learning ) 


##########################################
#                                        #
#    Proxy between history and View      #
#                                        #
##########################################
class EpisodeData():

    def __init__(self, user_data, cmd ):
        self.error_color = QColor(255,250,150,50)
        self.group = dict()
        self.individual = dict()
        
        #user
        self.group[ "empirical" ]         = Group( cmd, "empirical", "scatter", 10 )
        self.group[ "empirical_error" ]   = Group( cmd, "empirical_error", "scatter", 18, self.error_color )
        self.outlier_1 = None
        self.outlier_2 = None

        #model
        
        #self.individual["user_action_prob"] = None
        #self.individual["knowledge"]        = None        

        #all
        self.block_id = None

        self.load_user_output( user_data, cmd )

    ##############################
    def show_group( self, name, b ) :
        if name in self.group :
            g = self.group[ name ]
            g.menu.setVisible( b )
            g.hotkey.setVisible( b )
            g.learning.setVisible( b )

    ##############################
    def show_individual( self, name, b ) :
        if name in self.individual :
            self.individual[ name ].setVisible( b )


    ##############################
    def add_user_series_to_chart(self, chart):
        chart.addSeries( self.outlier_2 )
        chart.addSeries( self.outlier_1 )        
        self.group[ "empirical" ].add_to_chart( chart )
        self.group[ "empirical_error" ].add_to_chart( chart )
    

    ##############################
    def add_model_series_to_chart(self, model_name, chart):     
        self.group[ model_name ].add_to_chart( chart )
        chart.addSeries( self.individual[ model_name ] )
        
    ###############################

        #for i in self.individual.values() :
        #    chart.addSeries(i)

    ##############################
    def add_other_series_to_chart( self, chart ):
        chart.addSeries( self.block_id )

    ##############################
    def load_model_output( self, model_name, user_input, model_output, model_prob, cmd ):
        self.group[ model_name ] = Group(cmd, model_name, "line", 2 )
        for i in range(0, len( user_input ) ):
            if cmd == user_input[ i ] :
                self.group[ model_name ].add_items( i,  [ model_output.menu[ i ]*10., model_output.hotkey[ i ]*10, model_output.learning[ i ]*10. ] )
        
 
        line = create_line_series( model_name,  Qt.white, 4)
        for i, (user_cmd, prob)  in enumerate( zip( user_input, model_prob )  ):
            if cmd == user_cmd :
                line.append( i, prob * 10. )
        self.individual[ model_name ] = line        

    ##############################
    def load_user_output(self, user_data, cmd):
        self.block_id  = create_scatter_series( "Block"    ,  7, QScatterSeries.MarkerShapeCircle, Qt.white)
        self.outlier_1 = create_scatter_series( "outlier_1", 18, QScatterSeries.MarkerShapeCircle, self.error_color)
        self.outlier_2 = create_scatter_series( "outlier_2", 18, QScatterSeries.MarkerShapeCircle, self.error_color)
        
        action_vec  =  user_data.output.action
        time_vec    =  user_data.output.time
        success_vec =  user_data.output.success

        max_time = 7.5

        for i in range( len(action_vec) ):
            
            if user_data.cmd[i] == cmd :
                s = action_vec[i].strategy
                time = round(time_vec[i],1)
                time_band1 = min(time, max_time)

                self.group["empirical"].add_item( s, i, time_band1 )
                if success_vec[i] == 0:     #error
                    self.group["empirical_error"].add_item( s, i, time_band1 )

                if time >= 2 * max_time :
                    self.outlier_1.append(i, time_band1+0.5 )
                if time >= 3 * max_time :
                    self.outlier_2.append(i, time_band1+1 )
                

            if user_data.other.block_trial[i] == 0:
                self.block_id.append(i,0)





                
##########################################
#                                        #
#    Draw Information for one user       #
#                                        #
##########################################
class EpisodeView(QChartView):
    view_selected = pyqtSignal(int, int, int) #user id, cmd, trial_id
    cursor_moved = pyqtSignal(int, int)
    def __init__(self):
        super().__init__()

        self.setChart( QChart() )
        self.chart().setTheme( QChart.ChartThemeDark )
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumHeight(200)
        self.setMaximumHeight(200)        
        self.setMinimumWidth(750)
        self.setBackgroundRole( QPalette.Dark )

        self.cmd      = -1
        self.user_id  = -1
        self.trial_id = -1
        self.data = None

    ###########################
    def show_strategy_probs( self, name, b ):
        self.data.show_group( name, b )

    ###########################
    def show_action_probs( self, name, b ):
        self.data.show_individual( name, b )

    ###########################
    def show_user_data( self , b):
        self.data.show_group( "empirical", b )
        self.data.show_group( "empirical_error", b )
        self.data.outlier_1.setVisible( b )
        self.data.outlier_2.setVisible( b )
        #self.data.show_group( "outlier_1", b )
        #self.data.show_group( "outlier_2", b )



    ###########################    
    def set_user_data(self, user_data, cmd):   
        self.chart().removeAllSeries()
        self.cmd     = cmd
        self.user_id = user_data.id

        self.data = EpisodeData( user_data, cmd )
        self.data.add_user_series_to_chart( self.chart() )
        self.data.add_other_series_to_chart( self.chart() )
        self.add_transition_region( self.x_start_transition( user_data, cmd ), self.x_stop_transition( user_data, cmd ) )
        title = "User: " + str( self.user_id) + " - Cmd: " + str( cmd ) + " - technique: " + user_data.technique_name
        
        self.add_cursor_line()
        self.set_chart_decoration( title )

    ############################
    def set_model_data( self, model_name, user_input, model_output, model_prob ):
        if model_name in self.data.group or model_name in self.data.individual :
            group = self.data.group[ model_name ]
            group.remove_to_chart( self.chart() )
            self.chart().removeSeries( self.data.individual[ model_name ] )
            #print( "The model", model_name, "is already displayed" )
            
        self.data.load_model_output( model_name, user_input, model_output, model_prob, self.cmd )
        self.data.add_model_series_to_chart( model_name, self.chart() )
        #self.chart().createDefaultAxes()
        title = self.chart().title()
        title += "\t " + model_name
        self.set_chart_decoration( title ) 

    


    ############################
    def set_chart_decoration( self, title_str ) :
        self.chart().setTitle(  title_str )
        
        self.chart().setDropShadowEnabled(False)
        self.chart().legend().setVisible(False)
        self.chart().layout().setContentsMargins(0, 0, 0, 0);
        self.chart().createDefaultAxes()
        self.chart().axisY().setRange(0, max_y)
        self.chart().axisY().setTitleText("Time")
        self.chart().axisX().setRange(0, 750)
        self.chart().axisX().setTitleText("Trial id")
        self.chart().axisX().setTickType(QValueAxis.TicksFixed)
        self.chart().axisX().setTickCount(11)
        self.chart().axisX().setLabelFormat("%i")
        self.chart().axisX().setGridLineVisible( False )
        self.chart().axisY().setGridLineVisible( False )
        

    ############################
    def add_cursor_line( self ) :
        self.cursorLine = QLineSeries()
        self.cursorLine << QPointF(0,0) << QPointF(0,10)
        self.chart().addSeries( self.cursorLine )

    ###########################  
    def add_transition_region( self, x_start_trans, x_stop_trans ) :
        self.top_transition = QLineSeries()
        self.bottom_transition = QLineSeries()
        self.top_transition << QPointF(x_start_trans, max_y) << QPointF(x_stop_trans, max_y)
        self.bottom_transition << QPointF(x_start_trans, 0) << QPointF(x_stop_trans, 0)
        self.area_transition = QAreaSeries(self.top_transition, self.bottom_transition)
        self.area_transition.setBrush( QColor(255,100,50,50) )
        self.area_transition.setPen( QColor(255,100,50,50) )
        self.chart().addSeries( self.area_transition )
    
    ###########################  
    def x_start_transition( self, user_data, cmd ) :
        return user_data.command_info.start_transition[ user_data.command_info.id.index( cmd ) ]

    ###########################  
    def x_stop_transition( self, user_data, cmd ) :
        return user_data.command_info.stop_transition[ user_data.command_info.id.index( cmd ) ]

    
        

    #caputre mouse move event to show the vertical cursor line
    ###########################  
    def mouseMoveEvent(self, e) :
        scene_pos = self.mapToScene( e.pos() )
        chartItemPos = self.chart().mapFromScene( scene_pos )
        value = self.chart().mapToValue( chartItemPos )
        self.cursorLine.replace(0, value.x(), 0)
        self.cursorLine.replace(1, value.x(), 10)
        self.trial_id = int(value.x())

    

    #caputre mouse click event to get information on demand
    ###########################  
    def mouseReleaseEvent(self, e) :
        scene_pos = self.mapToScene( e.pos() )
        chartItemPos = self.chart().mapFromScene( scene_pos )
        value = self.chart().mapToValue( chartItemPos )
        trial_id = int(value.x())
        self.view_selected.emit( self.user_id, self.cmd, trial_id )
    
    

