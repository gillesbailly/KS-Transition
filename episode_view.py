from PyQt5.QtChart import QChart, QChartView, QLineSeries, QBarSeries, QAbstractSeries, QHorizontalBarSeries, QBarSet, QScatterSeries, QValueAxis, QBarCategoryAxis
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygonF, QImage, QColor, QKeySequence, QTransform, QPixmap, QPageSize
from PyQt5.QtCore import pyqtSignal, Qt, QObject
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
        self.combo = QComboBox()
        self.combo.activated.connect(self.select)
        self.combo.setVisible( False )
        self.combo.addItem(name + " (none)")
        self.combo.addItem(name +" (menu) " )
        self.combo.addItem(name +" (hotkey) " )
        self.combo.addItem(name +" (learning) " )
        self.combo.addItem(name +" (all)")
        self.combo.setCurrentText(name +" (all)")
        
        self.filter = Strategy_Filter.ALL

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

    ###########################
    def select(self, v):
        value = self.combo.currentText()
        print("select: ", value)
        self.filter = Strategy_Filter.NONE
        if "menu" in value :
            self.filter = Strategy_Filter.MENU
        if "hotkey" in value :
            self.filter = Strategy_Filter.HOTKEY
        if "learning" in value :
            self.filter = Strategy_Filter.LEARNING
        if "all" in value :
            self.filter = Strategy_Filter.ALL
        self.view.filter(-1)


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
    def set_visible(self,id, visible):
        self.menu[id].setVisible( visible and ( self.filter == Strategy_Filter.MENU or self.filter == Strategy_Filter.ALL) )
        self.hotkey[id].setVisible( visible and ( self.filter == Strategy_Filter.HOTKEY or self.filter == Strategy_Filter.ALL))
        self.learning[id].setVisible( visible and ( self.filter == Strategy_Filter.LEARNING or self.filter == Strategy_Filter.ALL))


    ##############################
    def set_all_visible(self, id, all, visible):
        for cmd in self.menu.keys():
            self.set_visible(cmd, visible and ( cmd == id or all ) )

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


    def __init__(self, history, prediction, empirical_data ):
        self.history = history
        self.group = dict()
        self.individual = dict()
        self.individual["user_action_prob"] = dict()
        self.individual["knowledge"] = dict()
        self.group[ "prob" ]              = Group("prob", "line", 5)
        self.group[ "RW" ]         = Group("RW", "line", 1)
        self.group[ "CK" ]         = Group("CK", "line", 1)
        self.group[ "CTRL" ]       = Group("CTRL", "line", 1)
        self.group[ "empirical" ]         = Group("empirical", "scatter", 10)
        self.group[ "prediction" ]        = Group("prediction", "scatter", 10)
        self.group[ "empirical_error" ]   = Group("empirical_error", "scatter", 20, Qt.red)
        self.group[ "prediction_error" ]  = Group("prediction_error", "scatter", 20, Qt.black)

        
        
        #self.cmd_id_series = dict()

        self.block_id = None
        self.prediction = prediction
        self.empirical_data = empirical_data
        self.load_history()
        #self.add_to_view(self.view)


    def set_visible(self, id, all, show_prediction, show_empirical_data):
        for key in self.group.keys():
            self.group[key].set_all_visible(id , all, True)
        self.group["empirical"].set_all_visible(id , all, show_empirical_data)
        self.group["prediction"].set_all_visible(id , all, show_prediction)
        
        for key in self.individual.keys() :
            ind = self.individual[key]
            for cmd in ind.keys() :
                ind[cmd].setVisible( cmd == id or all )    
                
    #############################
    def activate_control(self, show_prediction):
        for key in self.group.keys() : 
            if not "empirical" in key :
                self.group[ key ].combo.setVisible( show_prediction )         

    ##############################
    def attach_control(self, layout ):
        for g in self.group.values():
            layout.addWidget( g.combo)
        
    def set_view(self, view):
        for g in self.group.values():
            g.view = view

    ##############################
    def add_series_to_chart(self, chart):
        for g in self.group.values() :
            g.add_to_chart( chart )

        for id in self.history.commands:
            for ind in self.individual.values() :
                chart.addSeries( ind[id] )
        
        chart.addSeries( self.block_id )


    ##############################
    def load_history(self):
        for g in self.group.values():
            g.load( self.history.commands )
        
        for id in self.history.commands:
            self.individual["user_action_prob"] [id] = create_line_series("user_action_prob", Qt.yellow, 3)
            self.individual["knowledge"] [id] = create_line_series("knowledge", Qt.black, 10)    
            self.block_id = create_scatter_series("Block", 7, QScatterSeries.MarkerShapeCircle, Qt.black)

        
        if self.prediction:
            action_vec = self.history.action 
            time_vec = self.history.time 
            success_vec = self.history.success  

            for i in range( len(action_vec) ):
                s = action_vec[i].strategy
                cmd = self.history.cmd[i]    #add the id of the comand on the graph
                time = round(time_vec[i],1)
                time = min(time,7)

                self.group["prediction"].add_item(cmd, s, i, time)
                if success_vec[i] == 0:
                    y = 0.0
                    self.group["prediction_error"].add_item(cmd, s, i, y )

                prob_vec = np.array( self.history.prob_vec[i] ) * float(max_y)
                self.group["prob"].add_items(cmd, i, prob_vec )

                if len( self.history.rw_vec) > 0 :
                    rw_vec = np.array(self.history.rw_vec[i]) * float(max_y)
                    self.group["RW"].add_items(cmd, i, rw_vec)
                    
                if len( self.history.ck_vec) > 0 :
                    ck_vec = np.array(self.history.ck_vec[i]) * float(max_y)
                    self.group["CK"].add_items(cmd, i, ck_vec)
                    
                if len( self.history.ctrl_vec ) > 0 :
                    ctrl_vec = np.array(self.history.ctrl_vec[i]) * float(max_y)
                    self.group["CTRL"].add_items(cmd, i, ctrl_vec)

                print( "len knowledge: ", len( self.history.knowledge ) )
                if len( self.history.knowledge ) > 0 :
                    self.individual[ "knowledge" ][cmd].append(i, self.history.knowledge[i] * float(max_y) )
                
                #for name in self.history.value.keys():
                #   g_name = 'v_' + name
                #    self.group[ 'v_' + name ] = Group( g_name, "line", 1)
                #    v_vec = p.array( self.history.value[name][i] ) * float(max_y)
                #    self.group[ g_name ].add_items(cmd, i, v_vec)
            
            #self.cmd_id_series[cmd].append(i, time + 0.2 )   
        if self.empirical_data:
            action_vec =  self.history.user_action
            time_vec =  self.history.user_time
            success_vec =  self.history.user_success 

            for i in range( len(action_vec) ):
                s = action_vec[i].strategy
                cmd = self.history.cmd[i]    #add the id of the comand on the graph
                time = round(time_vec[i],1)
                time = min(time,7)

                self.group["empirical"].add_item(cmd, s, i, time)
                if success_vec[i] == 0:
                    y = 0.0
                    self.group["empirical_error"].add_item(cmd, s, i, time )

                #self.user_action_prob_series[cmd].append(i, self.history.user_action_prob[i] * float(max_y) )

                if self.history.block_trial[i] == 0:
                    self.block_id.append(i,0)

        if self.prediction and self.empirical_data : 
            for i in range( len(action_vec) ) :
                cmd = self.history.cmd[i]
                self.individual[ "user_action_prob" ][cmd].append(i, self.history.user_action_prob[i] * float(max_y) )
               
                    
                

    


                
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
        #self.param["show_cmd_id"] = False
        #self.param["show_block"] = True
        #self.param["error_on_place"] = False    #not used...
        self.param["show_prediction"] = False
        self.param["show_empirical_data"] = False
        
        self.slider = QSlider(Qt.Horizontal,self)
        self.slider.setMinimum(0)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect( self.filter )
        self.slider.setMinimumWidth(100)

        self.user_combo = QComboBox()
        self.user_combo.activated.connect(self.select)
        self.user_combo.setVisible( False )
        self.user_combo.addItem("None")

        self.likelyhood_label = QLabel()
        self.bic_label = QLabel()

        control_widget = QWidget(self)
        self.h_layout = QHBoxLayout()
        control_widget.setLayout(self.h_layout)
        self.h_layout.addWidget( self.slider )
        self.h_layout.addWidget( self.user_combo )
        self.h_layout.addWidget(self.likelyhood_label)
        self.h_layout.addWidget(self.bic_label)
        control_widget.move(0,-10)
        control_widget.resize(1000,60)
        control_widget.setVisible( True )

        
     
    ######################
    # def mouseReleaseEvent(self, e):
    #     print( "#series: ", len( self.chart().series() ) ) 
    #     for s in self.chart().series():
    #         if s.isVisible() :
    #             p = e.pos()
    #             p_prev  = e.pos()
    #             p_series = self.chart().mapToValue(p, s)
    #             print("prev: ", p_prev, " ", p, " ", p_series)
    #         #print( p_series.x(), p_series.y() )
    #             if s :
    #                 print( s.name() )
    #         #else:
    #             #print("series = none")

    ######################    
    def filter(self, v):
        #todo. We do not manage title very well as it takes information from the last d
        #functon only works if d.history has the same commands vec
        value = self.slider.value()
        params = None
        user_id = -1
        for d in self.d:
            commands = d.history.commands
            params = d.history.params
            if d.empirical_data:
                user_id = d.history.user_id
            
            cmd = -1
            show_all = False
            if value < len( commands ):
                cmd = commands[value]
            else: 
                show_all = True

            d.set_visible(cmd, show_all, self.param["show_prediction"], self.param["show_empirical_data"])  
                
        self.update_title(cmd, self.param["show_prediction"], user_id, params)
  

    ######################    
    def set_full_history(self, history, show_prediction=False, show_empirical_data=False):   
        self.chart().removeAllSeries()
        self.param["show_prediction"] = show_prediction
        self.param["show_empirical_data"] = show_empirical_data
        self.commands = history.commands
        if isinstance(history, User_History) :
            self.likelyhood_label.setText( str(history.fd.log_likelyhood) )
            self.bic_label.setText( str(history.fd.bic() ) )


        data = EpisodeData( history, show_prediction, show_empirical_data )
        data.add_series_to_chart( self.chart() )
        data.attach_control( self.h_layout )
        data.set_view( self )
        self.d.append( data )

        if show_prediction:
            self.user_combo.addItem("Model only")
            self.user_combo.setCurrentText("Model only")
            data.activate_control( True )

        if show_empirical_data:
            self.user_combo.addItem("User only")
            self.user_combo.setCurrentText("User only")
            
        if show_prediction and show_empirical_data:
            self.user_combo.addItem("Both")
            self.user_combo.setCurrentText("User only")
            self.user_combo.setVisible(True)

        self.slider.setMaximum( len(self.commands) )
        self.slider.setValue( len(self.commands) )
        
        self.update_title(-1, True, True, history.params)
        self.chart().createDefaultAxes()
        self.chart().axisY().setRange(0, max_y)
        self.chart().axisY().setTitleText("Time")        
        self.chart().axisX().setRange(0, len(history.action))
        self.chart().axisX().setTitleText("Trial id")
        self.chart().axisX().setTickType(QValueAxis.TicksFixed)
        self.chart().axisX().setTickCount(13)
        self.chart().axisX().setLabelFormat("%i")
    


    ############################
    def update_title(self, cmd, model, user_id, params=""):
        type_title = "Model" if model else "User" + str( user_id )
        param = params if model else ""
        cmd_title = "all commands" if cmd == -1 else "command " + str(cmd)
        self.chart().setTitle( type_title + " data for " + cmd_title + " " + params)

    ###########################
    def select(self, v):
        value = self.user_combo.currentText()
        self.param["show_empirical_data"] = False
        self.param["show_prediction"] = False
        if "User" in value :
            self.param["show_empirical_data"] = True
        if "Model" in value :
            self.param["show_prediction"] = True
        if "Both" in value :
            self.param["show_empirical_data"] = True
            self.param["show_prediction"] = True
        self.filter( self.slider.value() )

    

