import sys
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.Qt import PYQT_VERSION_STR
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygonF, QImage, QColor, QKeySequence, QTransform, QPixmap
from PyQt5.QtPrintSupport import *
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QBarSeries, QHorizontalBarSeries, QBarSet, QScatterSeries, QValueAxis, QBarCategoryAxis
from transitionModel import *
from util import *
#from matplotlib_canvas import *


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
    symbol = QImage(20,20, QImage.Format_ARGB32)
    symbol.fill(Qt.transparent)

    painter = QPainter()
    painter.begin(symbol)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.black)
    painter.drawText(2,9, c)
    painter.end()
    return symbol

def createCheckBox(initial_value, handle):
    checkBox = QCheckBox()
    checkBox.setCheckState(initial_value)
    checkBox.stateChanged.connect(handle)
    checkBox.setTristate(False)
    return checkBox

def createCheckBoxLayout(checkBoxInfo, layout):
    checkBoxes = []
    for sinfo in checkBoxInfo:
        checkBox = createCheckBox(sinfo['initial_value'], sinfo['handleValueChanged'] )
        layout.addWidget(QLabel(sinfo['label']))
        layout.addWidget(checkBox)
        checkBoxes. append(checkBox)
    return checkBoxes


############################
def createSpinbox(range,initialValue,handleValueChanged,step,isSpinbox=False):
    spinbox = QSpinBox() if isSpinbox else QDoubleSpinBox()
    spinbox.setRange(range[0],range[1])
    spinbox.setValue(initialValue)
    spinbox.setSingleStep(step)
    spinbox.valueChanged.connect(handleValueChanged)
    return spinbox


############################
def createSpinBoxLayout(spinboxInfo,layout):
    spinBoxes = []
    for sinfo in spinboxInfo:
        isSpinbox = sinfo['is_spinbox'] if 'is_spinbox' in sinfo.keys() else False
        spinBox = createSpinbox(sinfo['range'],sinfo['initial_value'],sinfo['handleValueChanged'],sinfo['step'],isSpinbox=isSpinbox)
        l = QHBoxLayout(); l.addWidget(QLabel(sinfo['label'])); l.addWidget(spinBox); l.addStretch(10)
        layout.addLayout(l)
        spinBoxes.append(spinBox)
    return tuple(spinBoxes)


##########################################
#                                        #
#   Display the result of one simulation #
#                                        #
##########################################
class SimulatorUI(QTabWidget):
    def __init__(self):
        super(QTabWidget,self).__init__()
        
    ###################
    def add_page(self, title):
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        result_widget = QWidget()
        result_layout = QVBoxLayout()
        result_widget.setLayout(result_layout)
        scrollArea.setWidget(result_widget)
        result_widget.show()
        index = self.addTab(scrollArea, title)
        self.setCurrentIndex( index )


        return result_layout


    ###################
    def create_episode(self, layout):
        container = QWidget()
        container.setMinimumHeight(300)
        layout.insertWidget(0,container)
        #todo this VBoxLayout is probably useless
        l = QVBoxLayout()
        container.setLayout(l)
        chart = QChart()
        chart.setDropShadowEnabled(False)
        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        l.addWidget(view)
        return view       

    #########################
    def add_sims(self, sims, name_sims): #updatecanvas
        chart_view_vec = []

        l = self.add_page(name_sims)
        

        name_sims_lab = QLabel(name_sims)
        l.addWidget( name_sims_lab )


        for history in sims:
            chart_view = self.create_episode(l)
            chart_view_vec.append( chart_view )
            chart = chart_view.chart()
            title = history.model_name + ' ' + history.params
            chart.setTitle( title )
            chart.legend().setVisible(False)

            menu_series = create_scatter_series("Menu", 10, QScatterSeries.MarkerShapeCircle, Qt.blue)
            hotkey_series = create_scatter_series("Hotkey", 10, QScatterSeries.MarkerShapeCircle, Qt.darkGreen)
            learning_series = create_scatter_series("Menu Learning", 10, QScatterSeries.MarkerShapeRectangle, Qt.darkMagenta)
            error_series = create_scatter_series("Error", 10, QScatterSeries.MarkerShapeRectangle, QBrush( my_scatter_symbol('x') ) )

            kh_series = QLineSeries()
            kh_series.setName("Hotkey Know.")
            kh_series.setPen(Qt.lightGray)

            cmd_series_all = []
            for i in range( len( history.commands) ):
                cmd_series_all.append( create_scatter_series("Cmd", 10, QScatterSeries.MarkerShapeCircle, QBrush( my_scatter_symbol( str(i) ) )) )
        
            for i in range( len(history.action) ):
                #print(i, history.action[i].bin_number, history.time[i])
                s = history.action[i].strategy
                time = round(history.time[i],1)
                if s == Strategy.MENU :
                    menu_series.append( i, time )

                elif s == Strategy.HOTKEY:
                    hotkey_series.append(i, time)

                elif s == Strategy.LEARNING:
                    learning_series.append(i, time )

                if history.success[i] == 0:
                    error_series.append(i, time )

                #if a == ActionType.MENU_E or a == ActionType.HOTKEY_E or a == ActionType.MENU_LEARNING_E:
                #    error_series.append(i, time )

                cmd = history.cmd[i]    #add the id of the comand on the graph
                cmd_series_all[cmd].append(i, time + 0.2 )

                #kh_series.append(i, 3*history.state[i].k_h)
                #b_kh = history.belief[i].get_most_likely_kh() / self.model.n_hotkey_knowledge
                #b_kh_series.append(i,3*b_kh)            


            chart.addSeries(menu_series)
            chart.addSeries(hotkey_series)
            chart.addSeries(learning_series)
            chart.addSeries(error_series)
            for i in cmd_series_all:
                chart.addSeries( i )

        #if self.show_KH:
        #    chart.addSeries(kh_series)
        #if self.show_B_KH:    
        #    chart.addSeries(b_kh_series)

            chart.createDefaultAxes()
            chart.axisY().setRange(0, 3)


        print("add _sims: ", len(chart_view_vec) )
        return chart_view_vec


max_w = 200
##########################################
#                                        #
#   Param envUI                          #
#                                        #
##########################################
class ParamUI(QWidget):
    #########################
    def __init__(self, param):
        super(QWidget,self).__init__()
        self.setMaximumWidth( max_w)
        self.param = param
        self.param_spinbox = dict()
        self.setLayout( QVBoxLayout() )

    def add_spinboxes(self):
        vl = self.layout()
        for key in self.param.value:
            spinBox = createSpinbox(self.param.range[key], self.param.value[key], self.update_values, self.param.step[key], self.param.step[key] >= 1)
            self.param_spinbox[key] = spinBox
            hl = QHBoxLayout()
            lab = QLabel(key)
            lab.setToolTip( self.param.comment[key])
            hl.addWidget(lab)
            hl.addWidget(spinBox)
            hl.addStretch(10)
            vl.addLayout(hl)
        vl.addStretch()    

    #########################
    def update_values(self):
        for key in self.param.value:
            self.param.value[key] = self.param_spinbox[key].value()
        self.param.update()
        self.refresh()

    #########################
    def refresh(self):
        for key in self.param.value:
            self.param_spinbox[key].setValue( self.param.value[key] )        


##########################################
#                                        #
#   Display Environment                  #
#                                        #
##########################################
class EnvironmentUI(ParamUI):

    #########################
    def __init__(self, env):
        super().__init__(env)
 
        userLab = QLabel('Environment')
        userLab.setStyleSheet("QLabel { background-color : green; color : white; }");
        userLab.setAlignment(Qt.AlignHCenter)
        vl = self.layout()

        vl.addWidget(userLab)

        self.add_spinboxes()

        self.seqLineEdit = QLineEdit()
        vl.addWidget(self.seqLineEdit)

        self.seq_chart = QChart()
        self.seq_chart_view = QChartView(self.seq_chart)
        self.seq_chart_view.setRenderHint(QPainter.Antialiasing)
        self.seq_chart_view.setMinimumHeight(200)
        self.axisX = None
        self.axisY = None
        vl.addWidget(self.seq_chart_view)
        vl.addStretch()

        self.refresh()


    #########################
    def update_values(self):
        toUpdate = False
        for key in self.param.value:
            print(key)
            if key == 'n_commands' or key == 'n_selection' or key == 's_zipfian':
                print("target cmd", key)
                if self.param.value[key] != self.param_spinbox[key].value():
                    print("value diff: ", self.param.value[key], self.param_spinbox[key].value())
                    toUpdate = True
            self.param.value[key] = self.param_spinbox[key].value()
        if toUpdate:
            self.param.update()
        self.refresh()

    #########################
    def refresh(self):
        if len(self.param.cmd_seq) == 0:
            return

        for key in self.param.value:
            self.param_spinbox[key].setValue( self.param.value[key] )        


        self.seqLineEdit.hide()
        self.seqLineEdit.setText( ''.join(str(e) for e in self.param.cmd_seq) )
        self.seqLineEdit.show()

        uniq, count = np.unique(self.param.cmd_seq, return_counts=True)
        self.seq_chart.removeAllSeries()
        serie = QHorizontalBarSeries()
        set = QBarSet("frequency")
        categories = []
        for i in range( len(uniq) ):
            categories.append( str (i ) )
            set.append( count[i] )
        serie.append(set)
        
        self.seq_chart.addSeries(serie)
        self.seq_chart.removeAxis(self.axisY)
        self.seq_chart.removeAxis(self.axisX)


        self.axisY = QBarCategoryAxis()
        self.axisY.append(categories)
        self.seq_chart.setAxisY(self.axisY, serie)
        self.axisX = QValueAxis()
        self.axisX.setRange(0, np.max(count) )
        self.axisX.setLabelFormat('%i')
        self.seq_chart.setAxisX(self.axisX, serie)
        #axisX.applyNiceNumbers()

        self.seq_chart.legend().setVisible(False)
        self.seq_chart.setTitle( "Command Frequency" )
        #self.seq_chart.createDefaultAxes()
        self.seq_chart.setDropShadowEnabled(False)




##########################################
#                                        #
#   Main Window                          #
#                                        #
##########################################
class Window(QWidget):

    def __init__(self, simulator):
        super(Window,self).__init__()

        self.simulator = simulator
        self.model = None
        self.model_dic = dict()

        self.setWindowTitle("Model of the transition from menus to shortcuts")
        self.resize(900, 900)
        self.move(20,20)
        
        mainLayout = QHBoxLayout()
        self.setLayout(mainLayout)


        self.envUI = EnvironmentUI(simulator.env)
        self.model_container = QWidget()

        model_lab = QLabel("   Models   ")
        model_lab.setStyleSheet("QLabel { background-color : red; color : white; }");
        model_lab.setAlignment(Qt.AlignHCenter)
        
        
        self.model_menu = QComboBox()
        self.model_menu.activated.connect(self.select_model)
        self.model_menu.setMaximumWidth( max_w )
        self.model_container = QStackedWidget()
        self.model_container.setMaximumWidth( max_w )

        model_layout = QVBoxLayout()
        model_layout.addWidget(model_lab)
        model_layout.addWidget(self.model_menu)
        model_layout.addWidget(self.model_container)
        model_layout.addStretch()

        exploration_lab = QLabel("Param Exploration")
        exploration_lab.setStyleSheet("QLabel { background-color : blue; color : white; }");
        exploration_lab.setAlignment(Qt.AlignHCenter)

        self.exploration_edit = QLineEdit( "b")
        self.exploration_edit.setMaximumWidth( max_w )
        exploration_button = QPushButton("Exhaustive Test")
        exploration_button.clicked.connect( self.explore )


        param_layout = QVBoxLayout()
        mainLayout.addLayout(param_layout)
        param_layout.addWidget(self.envUI)
        param_layout.addLayout(model_layout)
        param_layout.addWidget(exploration_lab)
        param_layout.addWidget(self.exploration_edit)
        param_layout.addWidget(exploration_button)


        n_episodeLab = QLabel("# episodes: ")
        self.n_episodeSpinBox = createSpinbox([1,100],1,self.update_values,10,isSpinbox=True)
        button = QPushButton('Relaunch')
        button.clicked.connect(self.simulate)
        self.sim_name1 = QLineEdit( "[Sim]")
        #sim_name2 = QLabel( simulator.env.to_string() )

        
        runLayout = QHBoxLayout(self)
        runLayout.addWidget(n_episodeLab)
        runLayout.addWidget(self.n_episodeSpinBox)        
        runLayout.addWidget(button)
        runLayout.addWidget(self.sim_name1)
        #runLayout.addWidget(sim_name2)
        runLayout.addStretch()
        self.simulatorUI = SimulatorUI()

        result_layout = QVBoxLayout()
        mainLayout.addLayout( result_layout)
        result_layout.addWidget( self.simulatorUI )
        result_layout.addLayout(runLayout)

    

    ############################
    def add_model(self, model):
        print("add model: ", model.name)
        model_view = Model_View(model)

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollArea.setWidget(model_view)
        model_view.show()
        #index = self.model_tab.addTab(scrollArea, model.name)
        self.model_menu.addItem( model.name )
        index = self.model_container.addWidget(scrollArea)
        
        self.model_dic[index] = model_view.model
        self.model_menu.setCurrentIndex( index )
        self.model_container.setCurrentIndex( index )
        self.model = model



    ############################
    def select_model(self, index):
       if index in self.model_dic:
            print("select model: ", self.model_dic[index].name )
            self.model = self.model_dic[index]
            self.model_menu.setCurrentIndex( index )
            self.model_container.setCurrentIndex( index )

    ############################
    def simulate(self):
        #print("simulate: ", self.model, self.model_dic)
        sims = self.simulator.run(self.model, self.n_episodeSpinBox.value() )
        view_vec = self.simulatorUI.add_sims(sims, self.sim_name1.text() )

        to_print = True
        if to_print:
            printer = QPrinter()
            printer.setOutputFormat( QPrinter.PdfFormat )
            printer.setOutputFileName('./graphs/results.pdf')
            #logicalDPIX = printer.logicalDpiX()
            #PointsPerInch = 200.0
            painter = QPainter()
            if not painter.begin(printer):
                print("failed to open file, is it writable?");
            print( "len view_vec: ", len(view_vec))
            for view in view_vec:
                print("view........")
                
                #t = QTransform()
                #scaling = float(logicalDPIX ) / PointsPerInch  #16.6
                #print("scale: ", logicalDPIX, PointsPerInch, scaling)
                #t.scale( scaling, scaling )
                #painter.setTransform( t )
                #view.render( painter )
                pix = QPixmap( view.grab() )
                painter.drawPixmap(0,0, 500,pix.height() * 500. / pix.width(), pix)        
                printer.newPage()
            painter.end()

    def explore(self):
        print("explore model")
        params = self.exploration_edit.text()
        params = [ params ]
        sims = self.simulator.explore(self.model, params, 1 )
        view_vec = self.simulatorUI.add_sims(sims, "exploration" )


    def print_results(self):
        pass

    ###########################
    def update_values(self):
        pass


#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################



##########################################
#                                        #
#   Model View                           #
#                                        #
##########################################
class Model_View(ParamUI):
    def __init__(self, model):
        super().__init__(model.params)
        self.model = model
        self.add_spinboxes()

    ##############################
    def update_values(self):
        for key in self.model.params.value:
            self.model.params.value[key] = self.param_spinbox[key].value()


    ##############################
    def refresh(self):
        for key in self.model.default_params.value:
            self.param_spinbox[key].setValue( self.model.params.value[key] )


