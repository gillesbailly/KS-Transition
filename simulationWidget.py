import sys
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.Qt import PYQT_VERSION_STR
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygonF, QImage, QColor, QKeySequence, QTransform, QPixmap, QPageSize
from PyQt5.QtPrintSupport import *
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QBarSeries, QHorizontalBarSeries, QBarSet, QScatterSeries, QValueAxis, QBarCategoryAxis
from transitionModel import *
from episode_view import *
from util import *
#from matplotlib_canvas import *




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
    #spinbox = QSlider()
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
        l = QHBoxLayout()
        l.addWidget(QLabel(sinfo['label']))
        l.addWidget(spinBox)
        l.addStretch(10)
        l.addWidget( QCheckbox() )
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
        self.chart_view_dict = dict()


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



    #########################
    def add_sims(self, sims, name_sims, show_pred=True): #updatecanvas
        chart_view_vec = []

        l = self.add_page(name_sims)
        

        name_sims_lab = QLabel(name_sims)
        l.addWidget( name_sims_lab )

        for history in sims:
            chart_view = EpisodeView()
            l.addWidget(chart_view)
            chart_view.set_full_history(history, True)
            if history.has_user_data():
                chart_view_user = EpisodeView()
                l.addWidget(chart_view_user)
                chart_view_user.set_full_history(history, False)

        print("add _sims: ", len(chart_view_vec) )
        self.chart_view_dict[ self.currentIndex() ] = chart_view_vec
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

    def add_spinboxes(self, vl):
        #vl = self.layout()
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
        vl2 = self.layout()

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        container = QWidget()
        scrollArea.setWidget(container)
        vl2.addWidget(userLab)
        vl2.addWidget(scrollArea)
        
        vl = QVBoxLayout()
        container.setLayout(vl)


        self.add_spinboxes(vl)

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

        test_model_lab = QLabel("Test")
        test_model_lab.setStyleSheet("QLabel { background-color : purple; color : white; }")
        test_model_lab.setAlignment(Qt.AlignHCenter)

        path_lab = QLabel("Path: ")
        path_lab.setMaximumWidth(40)
        self.user_data_edit = QLineEdit()
        test_path_layout = QHBoxLayout()
        self.user_data_edit.setText('./experiment/grossman_cleaned_data.csv')
        self.user_data_edit.setMaximumWidth( max_w - 50 )
        test_path_layout.addWidget(path_lab)
        test_path_layout.addWidget(self.user_data_edit)

        filter_lab = QLabel("Filter: ")
        filter_lab.setMaximumWidth( 40 )
        self.filter_edit = QLineEdit()
        test_filter_layout = QHBoxLayout()
        self.filter_edit.setText('user_id=1')
        self.filter_edit.setMaximumWidth( max_w - 50 )
        test_filter_layout.addWidget(filter_lab)
        test_filter_layout.addWidget(self.filter_edit)

        test_button = QPushButton("test")
        test_button.clicked.connect( self.test_model )

        param_layout = QVBoxLayout()
        mainLayout.addLayout(param_layout)
        param_layout.addWidget(self.envUI)
        param_layout.addLayout(model_layout)
        param_layout.addWidget(exploration_lab)
        param_layout.addWidget(self.exploration_edit)
        param_layout.addWidget(exploration_button)
        param_layout.addWidget(test_model_lab)
        param_layout.addLayout(test_path_layout)
        param_layout.addLayout(test_filter_layout)
        param_layout.addWidget(test_button)



        #######################
        n_episodeLab = QLabel("# episodes: ")
        self.n_episodeSpinBox = createSpinbox([1,100],1,self.update_values,10,isSpinbox=True)
        launch_button = QPushButton('Launch')
        launch_button.clicked.connect(self.simulate)
        self.sim_name1 = QLineEdit( "[Sim]")
        #sim_name2 = QLabel( simulator.env.to_string() )
        save_button = QPushButton('Save')
        save_button.clicked.connect( self.save )
        

        runLayout = QHBoxLayout(self)
        runLayout.addWidget(n_episodeLab)
        runLayout.addWidget(self.n_episodeSpinBox)        
        runLayout.addWidget(launch_button)
        runLayout.addWidget(self.sim_name1)
        #runLayout.addWidget(sim_name2)
        runLayout.addStretch()
        runLayout.addWidget(save_button)
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


    ###########################
    def explore(self):
        print("explore model")
        params = self.exploration_edit.text()

        params = params.split(',')
        print(params)
        sims = self.simulator.explore(self.model, params, 1 )
        view_vec = self.simulatorUI.add_sims(sims, "exploration" )


    ###########################
    def test_model(self):
        print("test model")
        filename = self.user_data_edit.text()
        _filter = self.filter_edit.text()
        sims = self.simulator.test_model(self.model, filename, _filter)
        view_vec = self.simulatorUI.add_sims(sims, "Test", True)
        self.envUI.refresh()


    ###########################
    def save(self):
        index = self.simulatorUI.currentIndex()
        self.save_chart_views( self.simulatorUI.chart_view_dict[index] )


    ###########################    
    def save_chart_views(self, view_vec):
        if len(view_vec) == 0:
            return

        filename = QFileDialog.getSaveFileName(self, "Save views", "./graphs/trans.pdf", ".pdf" )
        print(filename)

        printer = QPrinter()
        printer.setOutputFormat( QPrinter.PdfFormat )
        printer.setOutputFileName( filename[0] )
        printer.setPageSize( QPageSize( view_vec[0].size() ))
        painter = QPainter()
        if not painter.begin(printer):
            print("failed to open file, is it writable?");
            print( "len view_vec: ", len(view_vec))
        for view in view_vec:
            pix = QPixmap( view.grab() )
            painter.drawPixmap(0,0, 500,pix.height() * 500. / pix.width(), pix)        
            printer.newPage()
        painter.end()


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
        self.add_spinboxes( self.layout() )
        lab = QLabel(self.model.description)
        lab.setWordWrap(True)
        self.layout().addWidget(lab)


    ##############################
    def update_values(self):
        for key in self.model.params.value:
            self.model.params.value[key] = self.param_spinbox[key].value()


    ##############################
    def refresh(self):
        for key in self.model.default_params.value:
            self.param_spinbox[key].setValue( self.model.params.value[key] )


