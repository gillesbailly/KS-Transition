import sys
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.Qt import PYQT_VERSION_STR
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygonF, QImage, QColor, QKeySequence
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
        container.setMinimumHeight(400)
        layout.insertWidget(0,container)
        #todo this VBoxLayout is probably useless
        l = QVBoxLayout()
        container.setLayout(l)
        chart = QChart()
        chart.setDropShadowEnabled(False)
        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        l.addWidget(view)
        return chart       

    #########################
    def add_sims(self, sims, name_sims): #updatecanvas
        l = self.add_page(name_sims)
        

        name_sims_lab = QLabel(name_sims)
        l.addWidget( name_sims_lab )


        for history in sims:
            chart = self.create_episode(l)
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



##########################################
#                                        #
#   Display Environment                  #
#                                        #
##########################################
class EnvironmentUI(QWidget):

    #########################
    def __init__(self, environment):
        super(QWidget,self).__init__()
        self.env = environment

        self.layout = QVBoxLayout(self)
#        self.parameterLayout.addLayout(self.taskLayout)
        userLab = QLabel('Environment')
        userLab.setStyleSheet("QLabel { background-color : gray; color : white; }");
        userLab.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(userLab)

        self.n_commandsSpinBox, self.n_selectionSpinBox, self.s_zipfianSpinBox, self.error_costSpinbox = createSpinBoxLayout(
            [
                {'range': [1, 14], 'initial_value': self.env.n_commands,
                 'handleValueChanged': self.update_values, 'step': 1, 'label': '#Commands: \t\t', 'is_spinbox':True},
                {'range': [10, 144], 'initial_value': self.env.n_selection,
                 'handleValueChanged': self.update_values, 'step': 10, 'label': '#Selections: \t\t', 'is_spinbox':True},
                {'range': [0, 5], 'initial_value': self.env.s_zipfian,
                 'handleValueChanged': self.update_values, 'step': 1, 'label': 'Zipfian_s: \t\t', 'is_spinbox':True},
                {'range': [0.0, 2.0], 'initial_value': self.env.error_cost,
                 'handleValueChanged': self.update_values, 'step': 0.1, 'label': 'Error cost: \t\t'}],
            self.layout)

        self.seqLineEdit = QLineEdit()
        self.layout.addWidget(self.seqLineEdit)

        self.seq_chart = QChart()
        self.seq_chart_view = QChartView(self.seq_chart)
        self.seq_chart_view.setRenderHint(QPainter.Antialiasing)
        self.seq_chart_view.setMinimumHeight(200)
        self.axisX = None
        self.axisY = None
        self.layout.addWidget(self.seq_chart_view)
        self.layout.addStretch()

        self.refresh()

    #########################
    def update_values(self):
        print("Environment UI: update_values UI->Env")
        self.env.reset(self.n_commandsSpinBox.value(), int( self.n_selectionSpinBox.value() ), self.s_zipfianSpinBox.value(), self.error_costSpinbox.value())
        self.refresh()
        # if len(self.model.commands) != self.n_commandsSpinBox.value():
        #     self.model.commands = self.create_command_list( self.n_commandsSpinBox.value() ) 
        # #self.model.n_commands = self.n_commandsSpinBox.value()
        
        # self.model.s_zipfian = self.s_zipfianSpinBox.value()
        # self.model.error_cost = self.penaltySpinbox.value()
        # self.model.n_selection = int( self.n_selectionSpinBox.value() )
        



    #########################
    def refresh(self):
        print("refresh Env -> UI")
        if len(self.env.cmd_seq) == 0:
            return

        self.n_commandsSpinBox.setValue(self.env.n_commands)
        self.n_selectionSpinBox.setValue(self.env.n_selection)
        self.s_zipfianSpinBox.setValue(self.env.s_zipfian)
        self.error_costSpinbox.setValue(self.env.error_cost)
        


        self.seqLineEdit.hide()
        self.seqLineEdit.setText( ''.join(str(e) for e in self.env.cmd_seq) )
        self.seqLineEdit.show()

        uniq, count = np.unique(self.env.cmd_seq, return_counts=True)
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
        
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)



        self.envUI = EnvironmentUI(simulator.env)
        self.model_container = QWidget()

        model_lab = QLabel("   Models   ")
        model_lab.setStyleSheet("QLabel { background-color : red; color : white; }");
        model_lab.setAlignment(Qt.AlignHCenter)
        self.model_tab = QTabWidget()
        self.model_tab.currentChanged.connect(self.select_model)
        
        model_layout = QVBoxLayout()
        model_layout.addWidget(model_lab)
        model_layout.addWidget(self.model_tab)
        model_layout.addStretch()

        param_layout = QHBoxLayout()
        mainLayout.addLayout(param_layout)
        param_layout.addWidget(self.envUI)
        param_layout.addLayout(model_layout)



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
        mainLayout.addLayout(runLayout)

        self.simulatorUI = SimulatorUI()
        mainLayout.addWidget( self.simulatorUI )
        

    ############################
    def add_model(self, title, model_view):
        print("add model", title)
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollArea.setWidget(model_view)
        model_view.show()
        index = self.model_tab.addTab(scrollArea, title)
        
        self.model_dic[index] = model_view.model
        self.model_tab.setCurrentIndex( index )
        print("coucou")

    ############################
    def select_model(self, index):
        print(self.model_dic, index)
        if index in self.model_dic:
            self.model = self.model_dic[index]

    ############################
    def simulate(self):
        sims = self.simulator.run(self.model, self.n_episodeSpinBox.value() )
        self.simulatorUI.add_sims(sims, self.sim_name1.text() + self.simulator.env.to_string() )

    def update_values(self):
        pass


#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################



class Trans_model_view(QWidget):

    ###########################
    def __init__(self, model):
        super(QWidget, self).__init__()
        self.model = model

        v_layout = QVBoxLayout()
        self.setLayout(v_layout)

        self.tLearnSpinbox, self.implicitLearningSpinbox, self.explicitLearningSpinbox, self.kSpinBox, self.discountSpinBox, self.riskAversionSpinbox, self.overReactionSpinBox = createSpinBoxLayout([
            {'range': [0.0, 10.0], 'initial_value': self.model.learning_cost, 'handleValueChanged': self.updateValues,'step':0.1,'label': 'Cue Fixation time: \t'},
            {'range': [0.0, 1.0], 'initial_value': self.model.implicit_hotkey_knowledge_incr, 'handleValueChanged': self.updateValues, 'step': 0.01, 'label': 'Implicit Learning Incr: \t'},
            {'range': [0.0, 1.0], 'initial_value': self.model.explicit_hotkey_knowledge_incr, 'handleValueChanged': self.updateValues, 'step': 0.01, 'label': 'Explicit Learning Incr: \t'},
            {'range': [0, 10], 'initial_value': self.model.horizon, 'handleValueChanged': self.updateValues, 'step': 1, 'label': 'Horizon: \t\t', 'is_spinbox': True},
            {'range': [0, 1], 'initial_value': self.model.discount, 'handleValueChanged': self.updateValues, 'step': 0.01, 'label': 'Discount: \t\t' },
            {'range': [0.0, 1.0], 'initial_value': self.model.risk_aversion, 'handleValueChanged': self.updateValues, 'step': 0.05, 'label': 'Risk aversion: \t\t'},
            {'range': [0.0, 1.0], 'initial_value': self.model.overreaction, 'handleValueChanged': self.updateValues, 'step': 0.05, 'label': 'Over reaction: \t\t'},],
            v_layout)

        v_layout.addWidget(QLabel())

        self.menuACSpinBox, self.menuBSpinbox, self.menuCSpinbox = createSpinBoxLayout([
            {'range':[0.0,10.0],'initial_value':self.model.menuParams[0]+self.model.menuParams[2],'handleValueChanged':self.updateValues,'step':0.1,'label':'a+c'},
            {'range':[0.0,10.0],'initial_value':self.model.menuParams[1],'handleValueChanged':self.updateValues,'step':0.1,'label':'b'},
            {'range':[0.0,10.0],'initial_value':self.model.menuParams[2],'handleValueChanged':self.updateValues,'step':0.1,'label':'c'}],
            v_layout)
        
        self.hotkeyACSpinBox, self.hotkeyBSpinbox, self.hotkeyCSpinbox = createSpinBoxLayout([
            {'range': [0.0, 10.0], 'initial_value': self.model.hotkeyParams[0] + self.model.hotkeyParams[2],'handleValueChanged': self.updateValues,'step':0.1, 'label': 'a+c'},
            {'range': [0.0, 10.0], 'initial_value': self.model.hotkeyParams[1], 'handleValueChanged': self.updateValues,'step':0.1,'label': 'b'},
            {'range': [0.0, 10.0], 'initial_value': self.model.hotkeyParams[2],'handleValueChanged': self.updateValues,'step':0.1, 'label': 'c'}],
            v_layout)
        

        # visu_widget = QWidget()
        # visu_widget.setLayout(visu_layout)
        # self.mainLayout.addWidget(visu_widget)
        # visu_lab = QLabel('Visualization parameters')
        # visu_lab.setStyleSheet("QLabel { background-color : black; color : white; }");
        # visu_lab.setAlignment(Qt.AlignHCenter)
        # v_layout.addWidget(visu_lab)
        
        # visu_layout.addWidget(visuLab)
        # visu_layout_h = QHBoxLayout()
        # visu_layout_h.setAlignment(Qt.AlignLeft)
        # visu_layout.addLayout(visu_layout_h)

        # self.plp_chart = QChart()
        # plp_chart_view = QChartView(self.plp_chart)
        # plp_chart_view.setRenderHint(QPainter.Antialiasing)
        # v_layout.addWidget(self.menu_chart_view)


    ##############################
    def updateValues(self):
        self.model.horizon = self.kSpinBox.value()
        self.model.discount = self.discountSpinBox.value()
        self.model.learning_cost = self.tLearnSpinbox.value()
        self.model.implicit_hotkey_knowledge_incr = self.implicitLearningSpinbox.value()
        if self.model.implicit_hotkey_knowledge_incr > 0:
            self.model.n_hotkey_knowledge = int(1. / self.model.implicit_hotkey_knowledge_incr )
        self.model.explicit_hotkey_knowledge_incr = self.explicitLearningSpinbox.value()
        self.model.risk_aversion = self.riskAversionSpinbox.value()
        #self.model.eps = self.epsSpinbox.value()
        self.model.overreaction = self.overReactionSpinBox.value()


class Random_Model_View(QWidget):

    ##############################
    def __init__(self, model):
        super(QWidget, self).__init__()
        self.model = model
        param_range = dict()
        param_step = dict()
        self.param_spinbox = dict()

        param_range['n_strategy'] = [2,3]
        param_range['menu_time'] = [0.5,3]                    
        param_range['hotkey_time'] = [0,2.5]            
        param_range['learning_cost'] = [0,2]                 
        
        param_step['n_strategy'] = 1
        param_step['menu_time'] = 0.1                    
        param_step['hotkey_time'] = 0.1            
        param_step['learning_cost'] = 0.1

        vl = QVBoxLayout()
        self.setLayout(vl)

        for key in self.model.params:
            spinBox = createSpinbox(param_range[key], self.model.params[key], self.update_values, param_step[key], param_step[key] == 1)
            self.param_spinbox[key] = spinBox
            hl = QHBoxLayout()
            hl.addWidget(QLabel(key))
            hl.addWidget(spinBox)
            hl.addStretch(10)
            vl.addLayout(hl)
        vl.addStretch()    


    ##############################
    def update_values(self):
        print("update values")
        for key in self.model.params:
            self.model.params[key] = self.param_spinbox[key].value()


    ##############################
    def refresh(self):
        for key in self.model.default_params:
            self.param_spinbox[key].setValue( self.model.params[key] )




        # sum = self.menuACSpinBox.value()
        # b = self.menuBSpinbox.value()
        # c = self.menuCSpinbox.value()
        # if c > sum:
        #     c = sum
        # a = sum - c

        # self.menuCSpinbox.setRange(0, sum)
        # self.menuCSpinbox.setValue(c)
        # self.model.menuParams = [a,b,c]

        # sum = self.hotkeyACSpinBox.value()
        # b = self.hotkeyBSpinbox.value()
        # c = self.hotkeyCSpinbox.value()
        # if c > sum:
        #     c = sum
        # a = sum - c

        # self.hotkeyCSpinbox.setRange(0, sum)
        # self.hotkeyCSpinbox.setValue(c)
        # self.model.hotkeyParams = [a, b, c]

        

        # self.kh_checkbox, self.b_kh_checkbox = self.createCheckBoxLayout([
        #     {'initial_value': True, 'handleValueChanged': self.handle_state_changed, 'label': 'Hotkey Knowledge: \t'},
        #     {'initial_value': True, 'handleValueChanged': self.handle_state_changed, 'label': 'Hotkey Knowledge Belief: \t'}],
        #     visu_layout_h)



    #def init_charts(self):



        
        

        # self.chart = QChart()
        # self.chart.setTitle("Menu to Hotkey transition")
        # #self.chart.createDefaultAxes()
        # self.chart.setDropShadowEnabled(False)

        # self.view = QChartView(self.chart)
        # self.view.setRenderHint(QPainter.Antialiasing)
        # self.mainLayout.addWidget(self.view)

  


    # def initGui(self):

    #     # LAYOUTS: main
    #     self.parameterLayout = QHBoxLayout()
    #     self.mainLayout.addLayout(self.parameterLayout)

    #     self.powerLawLayout = QVBoxLayout()
    #     self.parameterLayout.addLayout(self.powerLawLayout)

    #     modelPlotLayout = QVBoxLayout()
    #     self.mainLayout.addLayout(modelPlotLayout)


    #     methodLab = QLabel("Methods")
    #     methodLab.setStyleSheet("QLabel { background-color : black; color : white; }");
    #     methodLab.setAlignment(Qt.AlignHCenter)
    #     self.powerLawLayout.addWidget(methodLab)


    #     lMenuSpinBoxes = QHBoxLayout()
    #     self.powerLawLayout.addLayout(lMenuSpinBoxes)
    #     menuPlpLab = QLabel(' Menu PLP:    ')
    #     menuPlpLab.setStyleSheet("QLabel { background-color : blue; color : white; }");
    #     lMenuSpinBoxes.addWidget(menuPlpLab)

    #     lHotkeySpinBoxes = QHBoxLayout()
    #     self.powerLawLayout.addLayout(lHotkeySpinBoxes)
    #     hotkeyPlpLab = QLabel(' Hotkey PLP: ')
    #     hotkeyPlpLab.setStyleSheet("QLabel { background-color : green; color : white; }");
    #     lHotkeySpinBoxes.addWidget(hotkeyPlpLab)




        





    #     self.transPlotLayout = QVBoxLayout()
    #     self.parameterLayout.addLayout(self.transPlotLayout)
    #     transLab = QLabel("   Transition parameters   ")
    #     transLab.setStyleSheet("QLabel { background-color : red; color : white; }");
    #     transLab.setAlignment(Qt.AlignHCenter)
    #     self.transPlotLayout.addWidget(transLab)

    #     self.tLearnSpinbox, self.implicitLearningSpinbox, self.explicitLearningSpinbox, self.kSpinBox, self.discountSpinBox, self.riskAversionSpinbox, self.overReactionSpinBox = self.createSpinBoxLayout([
    #         {'range': [0.0, 10.0], 'initial_value': self.model.learning_cost, 'handleValueChanged': self.updateValues,'step':0.1,'label': 'Cue Fixation time: \t'},
    #         {'range': [0.0, 1.0], 'initial_value': self.model.implicit_hotkey_knowledge_incr, 'handleValueChanged': self.updateValues, 'step': 0.01, 'label': 'Implicit Learning Incr: \t'},
    #         {'range': [0.0, 1.0], 'initial_value': self.model.explicit_hotkey_knowledge_incr, 'handleValueChanged': self.updateValues, 'step': 0.01, 'label': 'Explicit Learning Incr: \t'},
    #         {'range': [0, 10], 'initial_value': self.model.horizon, 'handleValueChanged': self.updateValues, 'step': 1, 'label': 'Horizon: \t\t', 'is_spinbox': True},
    #         {'range': [0, 1], 'initial_value': self.model.discount, 'handleValueChanged': self.updateValues, 'step': 0.01, 'label': 'Discount: \t\t' },
    #         {'range': [0.0, 1.0], 'initial_value': self.model.risk_aversion, 'handleValueChanged': self.updateValues, 'step': 0.05, 'label': 'Risk aversion: \t\t'},
    #         {'range': [0.0, 1.0], 'initial_value': self.model.overreaction, 'handleValueChanged': self.updateValues, 'step': 0.05, 'label': 'Over reaction: \t\t'},],
    #         self.transPlotLayout)

    #     self.transPlotLayout.addStretch()



    #     # button = QPushButton('Relaunch')
    #     # self.transPlotLayout.addWidget(button)
    #     # self.transPlotLayout.addStretch()
    #     # button.clicked.connect(self.simulate)



    #     # model Layouts
    #     lModelSpinBoxes = QHBoxLayout()
    #     modelPlotLayout.addLayout(lModelSpinBoxes)


    #     ############################################
    #     # MENUS: (parameters + plot) of the Power law of practice
    #     ############################################

    #     self.menuACSpinBox, self.menuBSpinbox, self.menuCSpinbox = self.createSpinBoxLayout([
    #                 {'range':[0.0,10.0],'initial_value':self.model.menuParams[0]+self.model.menuParams[2],'handleValueChanged':self.updateValues,'step':0.1,'label':'a+c'},
    #                 {'range':[0.0,10.0],'initial_value':self.model.menuParams[1],'handleValueChanged':self.updateValues,'step':0.1,'label':'b'},
    #                 {'range':[0.0,10.0],'initial_value':self.model.menuParams[2],'handleValueChanged':self.updateValues,'step':0.1,'label':'c'}],
    #                 lMenuSpinBoxes)
    #     lMenuSpinBoxes.addStretch()

    #     # self.menuPlotCanvas = PlotMultilines()
    #     # self.menuPlotCanvas.setLineInfo([
    #     #     ('item_order_of_appearance', 'menu_curve_actual_time', 'b','-'),
    #     #     ('item_order_of_appearance','menu_curve_expected_time','b','--')
    #     # ])



    #     ############################################
    #     # HOTKEYS: parameters + plots of the power law of practice
    #     ############################################
    #     self.hotkeyACSpinBox, self.hotkeyBSpinbox, self.hotkeyCSpinbox = self.createSpinBoxLayout([
    #         {'range': [0.0, 10.0], 'initial_value': self.model.hotkeyParams[0] + self.model.hotkeyParams[2],'handleValueChanged': self.updateValues,'step':0.1, 'label': 'a+c'},
    #         {'range': [0.0, 10.0], 'initial_value': self.model.hotkeyParams[1], 'handleValueChanged': self.updateValues,'step':0.1,'label': 'b'},
    #         {'range': [0.0, 10.0], 'initial_value': self.model.hotkeyParams[2],'handleValueChanged': self.updateValues,'step':0.1, 'label': 'c'}],
    #         lHotkeySpinBoxes)
    #     lHotkeySpinBoxes.addStretch()


    #     visu_widget = QWidget()
    #     visu_layout = QVBoxLayout()
    #     visu_widget.setLayout(visu_layout)
    #     self.mainLayout.addWidget(visu_widget)
    #     visuLab = QLabel('Visualization parameters')
    #     visuLab.setStyleSheet("QLabel { background-color : black; color : white; }");
    #     visuLab.setAlignment(Qt.AlignHCenter)
    #     visu_layout.addWidget(visuLab)
    #     visu_layout_h = QHBoxLayout()
    #     visu_layout_h.setAlignment(Qt.AlignLeft)
    #     visu_layout.addLayout(visu_layout_h)
    #     self.kh_checkbox, self.b_kh_checkbox = self.createCheckBoxLayout([
    #         {'initial_value': True, 'handleValueChanged': self.handle_state_changed, 'label': 'Hotkey Knowledge: \t'},
    #         {'initial_value': True, 'handleValueChanged': self.handle_state_changed, 'label': 'Hotkey Knowledge Belief: \t'}],
    #         visu_layout_h)

    #     self.simulatorUI = SimulatorUI()
        # scrollArea = simulator()
        # self.mainLayout.addWidget(scrollArea)
        # self.result_widget = SimulatorUI()

        

        #self.updateValues() #launch simulate()


    ####################################
    # call when when the user changes a parameter
    # in the spinboxes
    ####################################
    
        # print(self.model)
        #self.simulate()


        






    # def update_plp_view(self):
    #     self.plp_chart.removeAllSeries()
    #     lineMenu = QLineSeries()
    #     lineMenu.setPen(Qt.black)
    #     scatterMenu = QScatterSeries()
    #     scatterMenu.setBrush(Qt.blue)
    #     scatterMenu.setMarkerSize(8)

    #     lineHotkey = QLineSeries()
    #     lineHotkey.setPen(Qt.black)
    #     scatterHotkey = QScatterSeries()
    #     scatterHotkey.setBrush(Qt.darkGreen)
    #     scatterHotkey.setMarkerSize(8)


    #     for i in range(self.model.env.n_selection):
    #         lineMenu.append(i, self.model.plp_menu(i) )
    #         scatterMenu.append(i, self.model.plp_menu(i))
    #         lineHotkey.append(i, self.model.plp_hotkey(i) )
    #         scatterHotkey.append(i, self.model.plp_hotkey(i))


    #     self.menu_chart.addSeries(scatterMenu)
    #     self.menu_chart.addSeries(lineMenu)
    #     self.menu_chart.addSeries(scatterHotkey)
    #     self.menu_chart.addSeries(lineHotkey)

    #     self.menu_chart.createDefaultAxes()
    #     self.menu_chart.axisY().setRange(0, 3)

    #     self.menu_chart.legend().setVisible(False)
        






    # def handle_state_changed(self, v):
    #     self.show_KH = self.kh_checkbox.checkState()
    #     self.show_B_KH = self.b_kh_checkbox.checkState()
    #     print("handle state changed", v)




