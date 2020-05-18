import sys
from trans import *
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtChart import * 
import argparse


hotkey_time   = [0.6, 0.8,1,1.2,1.4]
learning_cost = [0.4,0.7,1,1.3, 1.6]
error_cost    = [2.5, 3, 3.5, 4]
KM = [0.01, 0.05, 0.07, 0.09]
KL = [0.1, 0.2, 0.3,0.4]
HORIZON = [1,2,3,4,5,6,7,8]
DISCOUNT = [1,0.6,0.2]
K0 = [0.2,0.3,0.4,0.5,0.6,0.7,0.8]



class Controler(QObject) :
    value_changed =pyqtSignal(str, float) #name #value
    def __init__(self, name, values, layout ) :
        super(QObject,self).__init__()
        self.value_vec = values
        self.name = name
        self.value = self.value_vec[0]
        lab_name = QLabel(name)
        self.lab_value = QLabel( str( self.value) )
        slider = QSlider()
        slider = QSlider(Qt.Horizontal)
        slider.setRange( 0, len( values) -1)
        slider.valueChanged.connect( self.set_value )

        controler_layout = QHBoxLayout()
        controler_layout.addWidget( lab_name )
        controler_layout.addWidget( self.lab_value )
        controler_layout.addWidget( slider )
        layout.addLayout( controler_layout )

    def set_value( self, index ) :
        self.value = self.value_vec[ index ]
        self.lab_value.setText( str( self.value ) )
        self.value_changed.emit(self.name, self.value)


class Win(QMainWindow) :
    def __init__(self):
        super(Win,self).__init__()
        self.move(20,20)
        self.resize(1000, 800)
        self.df = pd.read_csv('./analysis/trans.csv', delimiter= ';')
        self.df2 = self.prepare_data( self.df )
        container = QWidget()
        l = QVBoxLayout()
        container.setLayout(l)
        self.setCentralWidget( container )

        self.control = dict()
        self.control['time_h'] = Controler('time_h', hotkey_time, l)
        self.control['cost_l'] = Controler('cost_l', learning_cost, l)
        self.control['cost_e'] = Controler('cost_e', error_cost, l)
        self.control['km'] = Controler('km', KM, l)
        self.control['kl'] = Controler('kl', KL, l)
        self.control['horizon'] = Controler('horizon', HORIZON, l)
        self.control['discount'] = Controler('discount', DISCOUNT, l)
        self.control['k0'] = Controler('k0', K0, l)

        for key in self.control.keys() :
         self.control[key].value_changed.connect( self.set_value )


        self.chart_view = QChartView()
        chart = QChart()
        self.chart_view.setChart( chart )

        l.addWidget( self.chart_view )

        #print(self.df)
        self.create_chart()


    def prepare_data(self, df) : 
        df_bis = df.sort_values(by=['time_h', 'cost_l', 'cost_e', 'km', 'kl', 'discount', 'horizon', 'k0'])
        df_filtered = df.groupby(['time_h', 'cost_l', 'cost_e', 'km', 'kl', 'discount', 'horizon']).apply( lambda g: (g[ (g["learning"] <= g["menu"]) & (g["learning"] <= g["hotkey"]) ] ) )
        print( df_filtered )
        exit(0)

    def set_value(self, name, value ) :
        self.control[name].value = value
        print( name, value )
        self.create_chart()
    
    def create_chart(self) :
        chart = self.chart_view.chart()
        chart.removeAllSeries()

        keys = list( self.control.keys() )
        keys.remove('horizon')
        df_filtered  = self.df
        print(df_filtered)
        for k in keys :
            df_filtered = df_filtered[ df_filtered[ k ] == self.control[ k ].value ]
        print( df_filtered )

        self.menu_series = QLineSeries()
        self.menu_series.setPen(Qt.blue)
        self.hotkey_series = QLineSeries()
        self.hotkey_series.setPen(Qt.green)
        self.learning_series = QLineSeries()
        self.learning_series.setPen(Qt.red)
        
        h = df_filtered['horizon'].tolist()
        m = df_filtered['menu'].tolist()
        rc = df_filtered['hotkey'].tolist()
        l = df_filtered['learning'].tolist()

        for i in range(1, len( h ) ) :
            self.menu_series << QPointF( h[i], m[i])
            self.hotkey_series << QPointF( h[i],  rc[i])
            self.learning_series << QPointF( h[i], l[i])
            
        chart.addSeries(self.menu_series)
        chart.addSeries(self.hotkey_series)
        chart.addSeries(self.learning_series)
        chart.createDefaultAxes()
        chart.axisY().setTitleText('Esperance of cummulative time')
        chart.axisY().setRange(0,15)
        chart.axisX().setRange(1,8)
        chart.axisX().setTitleText('Horizon')
        
        chart.legend().setVisible(False)





if __name__=="__main__":
    
    if not ( sys.argv[1] == 'GUI'  or  sys.argv[1] == 'SIM' ) :
        exit(0)


    if sys.argv[1] == 'GUI' :
        app = QApplication(sys.argv)
        win = Win()
        win.show()
        sys.exit(app.exec_())


    env = Environment("./parameters/environment.csv")
    env.value['n_strategy'] = 3
    trans_model = Trans(env, 'trans')
    trans_model.available_strategies = [ Strategy.MENU, Strategy.HOTKEY, Strategy.LEARNING ]

    writer = None
    filename = './analysis/trans.csv'
    log_file = open(filename, mode = 'a')
    writer = csv.writer(log_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #header = ['time_h', 'cost_l', 'cost_e', 'km', 'kl','horizon', 'discount', 'k0', 'menu','hotkey', 'learning']
    #writer.writerow( header)
    #log_file.close()

    for time_h in hotkey_time :
        env.value['hotkey_time'] = time_h
        print( time_h, '---------------------------------------')
        for cost_l in learning_cost :
            env.value['learning_cost'] = cost_l    

            for cost_e in error_cost :
                env.value['error_cost'] = cost_e    

                for km in KM :
                    trans_model.params.value['KM'] = km

                    for kl in KL :
                        trans_model.params.value['KL'] = kl
                    
                        for horizon in HORIZON :
                            trans_model.params.value['HORIZON'] = horizon
                    
                            for discount in DISCOUNT :
                                trans_model.params.value['DISCOUNT'] = discount

                                for k0 in K0:
                                    trans_model.reset( trans_model.available_strategies )
                                    trans_model.memory.hotkey_knowledge[0] = k0 
                                    gv = trans_model.goal_values_recursive( 0, trans_model.memory, horizon,[])
                                    if horizon == 0 :
                                        gv[0] = 1
                                    row = [time_h, cost_l, cost_e, km, kl, horizon, discount, k0, round(gv[0],3), round(gv[1],3), round(gv[2],3) ]
                                    writer.writerow(row)



                                    #print("gv")

                    



    # env = Environment("./parameters/environment.csv")
    # env.
    # env.value['n_strategy'] = 3
    # simulator = Simulator(env)
    # model_vec_long = [Trans(env, 'trans'), Alpha_Beta_Model(env, 'RW_IG_CTRL'), Alpha_Beta_Model(env, 'RW_IGM'), Alpha_Beta_Model(env, 'RW_D'), Random_Model(env), Win_Stay_Loose_Shift_Model(env), Alpha_Beta_Model(env, 'IG'), Alpha_Beta_Model(env, 'RW_IG'), Alpha_Beta_Model(env, 'RW_CK'), Alpha_Beta_Model(env, 'CK'), Alpha_Beta_Model(env, 'RW'), Rescorla_Wagner_Model(env)]
    # #index_model = sys.args[1] if len(sys.args) == 2 else 0

    # print("-- model ", args.model)
    # app = QApplication(sys.argv)
    # window = Window(simulator)
    # for model in model_vec_long:
    #     window.add_model(model)    
    # window.show()
    # window.select_model(args.model)
    # window.filter_edit.setText(args.filter)
    # if args.exec == "test" :
    #     window.test_model()
    # elif args.exec == "simulate" :
    #     window.simulate()
    # elif args.exec == "explore" :
    #     window.explore()

    # window.select_command( args.command )

    # sys.exit(app.exec_())

