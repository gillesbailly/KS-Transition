import sys
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.Qt import PYQT_VERSION_STR
from PyQt5.QtWidgets import (QApplication, QCheckBox, QScrollArea, QPushButton, QSlider, QWidget, QGroupBox, QTextEdit, QHBoxLayout, QVBoxLayout, QSpinBox,QDoubleSpinBox, QComboBox,QLabel,QLineEdit)
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygonF, QImage, QColor
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QBarSeries, QHorizontalBarSeries, QBarSet, QScatterSeries, QValueAxis, QBarCategoryAxis
from transitionModel import *
from util import *
#from matplotlib_canvas import *


class SimulationWidget(QWidget):

    def __init__(self):
        print("PyQt version:", PYQT_VERSION_STR)
        print(sys.path)
        super(SimulationWidget,self).__init__()
        
        self.model = TransitionModel()
        self.initGui()
        self.init_charts()
        self.init_visu_params()
        self.simulate()
        
    #############################
    #run the simulation for 51 occurances
    def runSimulation(self):
        print('\n========================= run simulation =====================', self.model.s_zipfian)
        


        history = History()
        self.model.reset_simulation()
        n_episode = 1

        #belief = None
        for i in range(n_episode):

            self.model.reset_episode()        
            belief = self.model.initial_belief()
            state = self.model.initial_state()

            print("================================= ", self.model.n_selection)
            for i in range( 1, self.model.n_selection):
                is_legal = False
                action = self.model.select_action(belief, self.model.horizon, self.model.eps) #action correct
                #print(debug_str)
                #exit(0)
                action = self.model.select_action_and_success(action, state.k_h, state.k_m)
                res, is_legal = self.model.generate_step(state, action)
                next_belief = self.model.update_belief(belief, res.action.bin_number, res.time, history )
                history.update_history(res.state, res.next_state, res.action, res.time, belief.copy(), next_belief.copy() )
                state = res.next_state.copy()
                belief = next_belief
            return history



        # print episode

    def init_visu_params(self):
        self.show_KH = True
        self.show_B_KH = True
        
        
    def series_to_polyline(self, xdata, ydata):
        """Convert series data to QPolygon(F) polyline
    
        This code is derived from PythonQwt's function named 
        `qwt.plot_curve.series_to_polyline`"""
        size = len(xdata)
        polyline = QPolygonF(size)
        pointer = polyline.data()
        dtype, tinfo = np.float, np.finfo  # integers: = np.int, np.iinfo
        pointer.setsize(2*polyline.size()*tinfo(dtype).dtype.itemsize)
        memory = np.frombuffer(pointer, dtype)
        memory[:(size-1)*2+1:2] = xdata
        memory[1:(size-1)*2+2:2] = ydata
        return polyline  



    def init_charts(self):
        self.menu_chart = QChart()
        self.menu_chart_view = QChartView(self.menu_chart)
        self.menu_chart_view.setRenderHint(QPainter.Antialiasing)
        self.menuPlotLayout.addWidget(self.menu_chart_view)
        

        self.hotkey_chart = QChart()
        self.hotkey_chart_view = QChartView(self.hotkey_chart)
        self.hotkey_chart_view.setRenderHint(QPainter.Antialiasing)
        self.hotkeyPlotLayout.addWidget(self.hotkey_chart_view)

        self.seq_chart = QChart()
        self.seq_chart_view = QChartView(self.seq_chart)
        self.seq_chart_view.setRenderHint(QPainter.Antialiasing)
        self.seq_chart_view.setMinimumHeight(300)
        self.axisX = None
        self.axisY = None

        self.taskLayout.addWidget(self.seq_chart_view)
        self.taskLayout.addStretch()
        

        # self.chart = QChart()
        # self.chart.setTitle("Menu to Hotkey transition")
        # #self.chart.createDefaultAxes()
        # self.chart.setDropShadowEnabled(False)

        # self.view = QChartView(self.chart)
        # self.view.setRenderHint(QPainter.Antialiasing)
        # self.mainLayout.addWidget(self.view)

    def create_result_chart(self):
        chart = QChart()
        chart.setTitle( self.model.to_string() )
        #self.chart.createDefaultAxes()
        chart.setDropShadowEnabled(False)

        container = QWidget()
        container.setMinimumHeight(400)
        #container.setMinimumWidth (400)
        self.result_layout.insertWidget(0,container)
        l = QVBoxLayout()
        container.setLayout(l)
        
        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        l.addWidget(view)
        return chart       



    def initGui(self):

        # LAYOUTS: main
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.parameterLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.parameterLayout)

        powerLawLayout = QVBoxLayout()
        self.parameterLayout.addLayout(powerLawLayout)

        modelPlotLayout = QVBoxLayout()
        self.mainLayout.addLayout(modelPlotLayout)


        # powerLaw Layouts
        self.menuPlotLayout = QVBoxLayout()
        powerLawLayout.addLayout(self.menuPlotLayout)
        menuLab = QLabel("Menu parameters")
        menuLab.setStyleSheet("QLabel { background-color : blue; color : white; }");
        menuLab.setAlignment(Qt.AlignHCenter)
        self.menuPlotLayout.addWidget(menuLab)


        lMenuSpinBoxes = QHBoxLayout()
        self.menuPlotLayout.addLayout(lMenuSpinBoxes)
        menuPlpLab = QLabel('Power Law of Practice: ')
        lMenuSpinBoxes.addWidget(menuPlpLab)



        self.hotkeyPlotLayout = QVBoxLayout()
        powerLawLayout.addLayout(self.hotkeyPlotLayout)
        hotkeyLab = QLabel("Hotkey parameters")
        hotkeyLab.setStyleSheet("QLabel { background-color : green; color : white; }");
        hotkeyLab.setAlignment(Qt.AlignHCenter)
        self.hotkeyPlotLayout.addWidget(hotkeyLab)


        lHotkeySpinBoxes = QHBoxLayout()
        self.hotkeyPlotLayout.addLayout(lHotkeySpinBoxes)
        hotkeyPlpLab = QLabel('Power Law of Practice: ')
        lHotkeySpinBoxes.addWidget(hotkeyPlpLab)


        self.taskLayout = QVBoxLayout()
        self.parameterLayout.addLayout(self.taskLayout)
        userLab = QLabel('Task - Context')
        userLab.setStyleSheet("QLabel { background-color : gray; color : white; }");
        userLab.setAlignment(Qt.AlignHCenter)
        self.taskLayout.addWidget(userLab)

        self.n_commandsSpinBox, self.n_selectionSpinBox, self.s_zipfianSpinBox, self.penaltySpinbox,  self.epsSpinbox = self.createSpinBoxLayout(
            [
                {'range': [1, 14], 'initial_value': self.model.n_commands,
                 'handleValueChanged': self.updateValues, 'step': 1, 'label': '#Commands: \t\t', 'is_spinbox':True},
                {'range': [10, 144], 'initial_value': self.model.n_selection,
                 'handleValueChanged': self.updateValues, 'step': 10, 'label': '#Selections: \t\t', 'is_spinbox':True},
                {'range': [0, 5], 'initial_value': self.model.s_zipfian,
                 'handleValueChanged': self.updateValues, 'step': 1, 'label': 'Zipfian_s: \t\t', 'is_spinbox':True},
                {'range': [0.0, 2.0], 'initial_value': self.model.error_cost,
                 'handleValueChanged': self.updateValues, 'step': 0.1, 'label': 'Error cost: \t\t'},
                {'range': [0.0, 1.0], 'initial_value': self.model.eps,
                 'handleValueChanged': self.updateValues, 'step': 0.01, 'label': 'Epsilon: \t\t\t'}],
            self.taskLayout)

        
        self.seqLineEdit = QLineEdit()
        self.taskLayout.addWidget(self.seqLineEdit)

        





        self.transPlotLayout = QVBoxLayout()
        self.parameterLayout.addLayout(self.transPlotLayout)
        transLab = QLabel("   Transition parameters   ")
        transLab.setStyleSheet("QLabel { background-color : red; color : white; }");
        transLab.setAlignment(Qt.AlignHCenter)
        self.transPlotLayout.addWidget(transLab)

        self.tLearnSpinbox, self.implicitLearningSpinbox, self.explicitLearningSpinbox, self.kSpinBox, self.discountSpinBox, self.riskAversionSpinbox, self.overReactionSpinBox = self.createSpinBoxLayout([
            {'range': [0.0, 10.0], 'initial_value': self.model.learning_cost, 'handleValueChanged': self.updateValues,'step':0.1,'label': 'Cue Fixation time: \t'},
            {'range': [0.0, 1.0], 'initial_value': self.model.implicit_hotkey_knowledge_incr, 'handleValueChanged': self.updateValues, 'step': 0.01, 'label': 'Implicit Learning Incr: \t'},
            {'range': [0.0, 1.0], 'initial_value': self.model.explicit_hotkey_knowledge_incr, 'handleValueChanged': self.updateValues, 'step': 0.01, 'label': 'Explicit Learning Incr: \t'},
            {'range': [0, 10], 'initial_value': self.model.horizon, 'handleValueChanged': self.updateValues, 'step': 1, 'label': 'Horizon: \t\t', 'is_spinbox': True},
            {'range': [0, 1], 'initial_value': self.model.discount, 'handleValueChanged': self.updateValues, 'step': 0.01, 'label': 'Discount: \t\t' },
            {'range': [0.0, 1.0], 'initial_value': self.model.risk_aversion, 'handleValueChanged': self.updateValues, 'step': 0.05, 'label': 'Risk aversion: \t\t'},
            {'range': [0.0, 1.0], 'initial_value': self.model.overreaction, 'handleValueChanged': self.updateValues, 'step': 0.05, 'label': 'Over reaction: \t\t'},],
            self.transPlotLayout)

        self.transPlotLayout.addStretch()



        button = QPushButton('Relaunch')
        self.transPlotLayout.addWidget(button)
        self.transPlotLayout.addStretch()
        button.clicked.connect(self.simulate)



        # model Layouts
        lModelSpinBoxes = QHBoxLayout()
        modelPlotLayout.addLayout(lModelSpinBoxes)


        ############################################
        # MENUS: (parameters + plot) of the Power law of practice
        ############################################

        self.menuACSpinBox, self.menuBSpinbox, self.menuCSpinbox = self.createSpinBoxLayout([
                    {'range':[0.0,10.0],'initial_value':self.model.menuParams[0]+self.model.menuParams[2],'handleValueChanged':self.updateValues,'step':0.1,'label':'a+c'},
                    {'range':[0.0,10.0],'initial_value':self.model.menuParams[1],'handleValueChanged':self.updateValues,'step':0.1,'label':'b'},
                    {'range':[0.0,10.0],'initial_value':self.model.menuParams[2],'handleValueChanged':self.updateValues,'step':0.1,'label':'c'}],
                    lMenuSpinBoxes)
        lMenuSpinBoxes.addStretch()

        # self.menuPlotCanvas = PlotMultilines()
        # self.menuPlotCanvas.setLineInfo([
        #     ('item_order_of_appearance', 'menu_curve_actual_time', 'b','-'),
        #     ('item_order_of_appearance','menu_curve_expected_time','b','--')
        # ])



        ############################################
        # HOTKEYS: parameters + plots of the power law of practice
        ############################################
        self.hotkeyACSpinBox, self.hotkeyBSpinbox, self.hotkeyCSpinbox = self.createSpinBoxLayout([
            {'range': [0.0, 10.0], 'initial_value': self.model.hotkeyParams[0] + self.model.hotkeyParams[2],'handleValueChanged': self.updateValues,'step':0.1, 'label': 'a+c'},
            {'range': [0.0, 10.0], 'initial_value': self.model.hotkeyParams[1], 'handleValueChanged': self.updateValues,'step':0.1,'label': 'b'},
            {'range': [0.0, 10.0], 'initial_value': self.model.hotkeyParams[2],'handleValueChanged': self.updateValues,'step':0.1, 'label': 'c'}],
            lHotkeySpinBoxes)
        lHotkeySpinBoxes.addStretch()


        visu_widget = QWidget()
        visu_layout = QVBoxLayout()
        visu_widget.setLayout(visu_layout)
        self.mainLayout.addWidget(visu_widget)
        visuLab = QLabel('Visualization parameters')
        visuLab.setStyleSheet("QLabel { background-color : black; color : white; }");
        visuLab.setAlignment(Qt.AlignHCenter)
        visu_layout.addWidget(visuLab)
        visu_layout_h = QHBoxLayout()
        visu_layout_h.setAlignment(Qt.AlignLeft)
        visu_layout.addLayout(visu_layout_h)
        self.kh_checkbox, self.b_kh_checkbox = self.createCheckBoxLayout([
            {'initial_value': True, 'handleValueChanged': self.handle_state_changed, 'label': 'Hotkey Knowledge: \t'},
            {'initial_value': True, 'handleValueChanged': self.handle_state_changed, 'label': 'Hotkey Knowledge Belief: \t'}],
            visu_layout_h)

        scrollArea = QScrollArea()
        self.mainLayout.addWidget(scrollArea)
        self.result_widget = QWidget()
        self.result_layout = QVBoxLayout()
        self.result_widget.setLayout(self.result_layout)
        scrollArea.setWidget(self.result_widget)
        self.result_widget.show()
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)


        #self.updateValues() #launch simulate()


    ####################################
    # call when when the user change a parameter
    # in the spinboxes
    ####################################
    def updateValues(self):
        self.model.n_commands = self.n_commandsSpinBox.value()
        self.model.s_zipfian = self.s_zipfianSpinBox.value()

        self.model.horizon = self.kSpinBox.value()
        self.model.discount = self.discountSpinBox.value()
        self.model.learning_cost = self.tLearnSpinbox.value()
        print("learning cost: ", self.model.learning_cost)
        self.model.implicit_hotkey_knowledge_incr = self.implicitLearningSpinbox.value()
        if self.model.implicit_hotkey_knowledge_incr > 0:
            self.model.n_hotkey_knowledge = int(1. / self.model.implicit_hotkey_knowledge_incr )


        self.model.explicit_hotkey_knowledge_incr = self.explicitLearningSpinbox.value()
        print("explicit knowledge: ", self.model.explicit_hotkey_knowledge_incr)

        self.model.risk_aversion = self.riskAversionSpinbox.value()
        self.model.error_cost = self.penaltySpinbox.value()
        self.model.n_selection = int( self.n_selectionSpinBox.value() )
        #print("n selection spinbox: ", self.n_selectionSpinBox.value(), self.model.n_selection )
        self.model.eps = self.epsSpinbox.value()
        self.model.overreaction = self.overReactionSpinBox.value()


        sum = self.menuACSpinBox.value()
        b = self.menuBSpinbox.value()
        c = self.menuCSpinbox.value()
        if c > sum:
            c = sum
        a = sum - c

        self.menuCSpinbox.setRange(0, sum)
        self.menuCSpinbox.setValue(c)
        self.model.menuParams = [a,b,c]

        sum = self.hotkeyACSpinBox.value()
        b = self.hotkeyBSpinbox.value()
        c = self.hotkeyCSpinbox.value()
        if c > sum:
            c = sum
        a = sum - c

        self.hotkeyCSpinbox.setRange(0, sum)
        self.hotkeyCSpinbox.setValue(c)
        self.model.hotkeyParams = [a, b, c]

        # print(self.model)
        #self.simulate()

    def create_sequence(self):
        return np.random.choice(self.model.n_commands, self.model.n_selection, p = zipfian(self.model.s_zipfian, self.model.n_commands))
        
    def update_sequence_canvas(self):
        if len(self.model.sequence) == 0:
            return

        self.seqLineEdit.hide()
        self.seqLineEdit.setText( ''.join(str(e) for e in self.model.sequence) )
        self.seqLineEdit.show()

        uniq, count = np.unique(self.model.sequence, return_counts=True)
        print("unique: ", uniq, " count: ", count)
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

        # line = QLineSeries()
        # line.setPen(Qt.black)



    ############################
    def simulate(self):
        self.model.sequence = self.create_sequence()
        self.update_menu_canvas()
        self.update_hotkey_canvas()
        self.update_sequence_canvas()
        history = self.runSimulation()
        self.updateCanvas(history)


    def update_menu_canvas(self):
        self.menu_chart.removeAllSeries()
        line = QLineSeries()
        line.setPen(Qt.black)

        scatter = QScatterSeries()
        scatter.setBrush(Qt.blue)
        scatter.setMarkerSize(8)

        for i in range(self.model.n_selection):
            line.append(i, self.model.plp_menu(i) )
            scatter.append(i, self.model.plp_menu(i))
        self.menu_chart.addSeries(line)
        self.menu_chart.addSeries(scatter)
        self.menu_chart.createDefaultAxes()
        self.menu_chart.axisY().setRange(0, 3)

        self.menu_chart.legend().setVisible(False)
        

#        // we select the marker associated with serie_without_marker
#chart.legend().markers(serie_without_marker)[0].setVisible(false);



    def update_hotkey_canvas(self):
        self.hotkey_chart.removeAllSeries()

        line = QLineSeries()
        line.setPen(Qt.black)

        scatter = QScatterSeries()
        scatter.setBrush(Qt.darkGreen)
        scatter.setMarkerSize(8)

        for i in range(self.model.n_selection):
            line.append(i, self.model.plp_hotkey(i) )
            scatter.append(i, self.model.plp_hotkey(i))
        self.hotkey_chart.addSeries(line)
        self.hotkey_chart.addSeries(scatter)
        self.hotkey_chart.createDefaultAxes()
        self.hotkey_chart.axisY().setRange(0, 3)
        self.hotkey_chart.legend().setVisible(False)

    #########################
    def updateCanvas(self,history):
        chart = self.create_result_chart()
        
        menu_series = QScatterSeries()
        menu_series.setName("Menu")
        menu_series.setMarkerSize(10)
        menu_series.setBrush(Qt.blue)
        #menu_series.setPointLabelsVisible(True)
        #menu_series.setPointLabelsFormat("@yPoint")

        hotkey_series = QScatterSeries()
        hotkey_series.setName("Hotkey")
        hotkey_series.setMarkerSize(10)
        hotkey_series.setBrush(Qt.darkGreen)
        
        learning_series = QScatterSeries()
        learning_series.setName("Menu learning")
        learning_series.setMarkerShape(QScatterSeries.MarkerShapeRectangle)
        learning_series.setMarkerSize(10)
        learning_series.setBrush(Qt.darkMagenta)

        kh_series = QLineSeries()
        kh_series.setName("Hotkey Know.")
        kh_series.setPen(Qt.lightGray)

        b_kh_series = QLineSeries()
        b_kh_series.setName("Hotkey Know. Belief")
        b_kh_series.setPen(Qt.darkGray)


        error_series = QScatterSeries()
        error_series.setName("Error")

        cross = QImage(20,20, QImage.Format_ARGB32)
        cross.fill(Qt.transparent)

        painter = QPainter()
        painter.begin(cross)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.black)
        painter.drawText(4,10, "x")
        painter.end()
        
        error_series.setBrush(QBrush(cross) )
        error_series.setPen(QColor(Qt.transparent))

        for i in range( len(history.action) ):
            #print(i, history.action[i].bin_number, history.time[i])
            a = history.action[i].bin_number
            if a == ActionType.MENU_C or a == ActionType.MENU_E :
                menu_series.append( i, round(history.time[i],1) )

            elif a == ActionType.HOTKEY_C or a == ActionType.HOTKEY_E:
                hotkey_series.append(i, history.time[i])

            elif a == ActionType.MENU_LEARNING_C or a == ActionType.MENU_LEARNING_E:
                learning_series.append(i, history.time[i])

            if a == ActionType.MENU_E or a == ActionType.HOTKEY_E or a == ActionType.MENU_LEARNING_E:
                error_series.append(i, history.time[i])


            kh_series.append(i, 3*history.state[i].k_h)
            b_kh = history.belief[i].get_most_likely_kh() / self.model.n_hotkey_knowledge
            b_kh_series.append(i,3*b_kh)

        chart.addSeries(menu_series)
        chart.addSeries(hotkey_series)
        chart.addSeries(learning_series)
        chart.addSeries(error_series)

        if self.show_KH:
            chart.addSeries(kh_series)
        if self.show_B_KH:    
            chart.addSeries(b_kh_series)


        chart.createDefaultAxes()
        chart.axisY().setRange(0, 3)


    def handle_state_changed(self, v):
        self.show_KH = self.kh_checkbox.checkState()
        self.show_B_KH = self.b_kh_checkbox.checkState()
        print("handle state changed", v)


    def createCheckBox(self, initial_value, handle):
        checkBox = QCheckBox()
        checkBox.setCheckState(initial_value)
        checkBox.stateChanged.connect(handle)
        checkBox.setTristate(False)
        return checkBox

    def createCheckBoxLayout(self, checkBoxInfo, layout):
        checkBoxes = []
        for sinfo in checkBoxInfo:
            checkBox = self.createCheckBox(sinfo['initial_value'], sinfo['handleValueChanged'] )
            layout.addWidget(QLabel(sinfo['label']))
            layout.addWidget(checkBox)
            checkBoxes. append(checkBox)
        return checkBoxes


    ############################
    def createSpinbox(self,range,initialValue,handleValueChanged,step,isSpinbox=False):
        spinbox = QSpinBox() if isSpinbox else QDoubleSpinBox()
        spinbox.setRange(range[0],range[1])
        spinbox.setValue(initialValue)
        spinbox.setSingleStep(step)
        spinbox.valueChanged.connect(handleValueChanged)
        return spinbox


    ############################
    def createSpinBoxLayout(self,spinboxInfo,layout):
        spinBoxes = []
        for sinfo in spinboxInfo:
            isSpinbox = sinfo['is_spinbox'] if 'is_spinbox' in sinfo.keys() else False
            spinBox = self.createSpinbox(sinfo['range'],sinfo['initial_value'],sinfo['handleValueChanged'],sinfo['step'],isSpinbox=isSpinbox)
            l = QHBoxLayout(); l.addWidget(QLabel(sinfo['label'])); l.addWidget(spinBox); l.addStretch(10)
            layout.addLayout(l)
            spinBoxes.append(spinBox)
        return tuple(spinBoxes)


if __name__=="__main__":
    app = QApplication(sys.argv)
    sys.path.append("/Users/gbailly/GARDEN/transition_model/one_command_model/lib/python3.5/site-packages/")
    print( '\n'.join(sys.path) )
    window = SimulationWidget()# Window()
    window.setWindowTitle("Model of the transition from menus to shortcuts")
    window.resize(900, 900)
    window.move(20,20)
    window.show()
    sys.exit(app.exec_())
