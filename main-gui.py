import sys
from transitionModel import *
from random_model import *
from win_stay_loose_shift_model import *
from rescorla_wagner_model import *
from choice_kernel_model import *
from rescorla_wagner_choice_kernel_model import *
from alpha_beta_model import *
from simulationWidget import *
from simulator import *
import numpy as np


    # ###################################
    # # test all parameters of the model
    # def run_sims(self, model, n_episode):
    #     print("params alpha: ", model.params.get_info('alpha') )
    #     a_info = model.params.get_info('alpha')
    #     printer = QPrinter()
    #     printer.setOutputFormat( QPrinter.PdfFormat )
    #     printer.setOutputFileName('./graphs/results.pdf')
    #     painter = QPainter()

    #     if not painter.begin(printer):
    #         print("failed to open file, is it writable?");
    
    #     for a in np.arange(a_info[1], a_info[2], a_info[3]):
    #         sims = self.run( model, n_episode)
    #         filename = './results/log_' + 'alpha_' + str(a) + '.csv'
    #     #simulator.save(filename, sims)
    #         w = window.simulatorUI.add_sims(sims, filename).parentWidget()
    #         w.show()
    #         w.render( painter )

    #     painter.end()





if __name__=="__main__":
    
    env = Environment("./parameters/environment.csv")
    env.value['n_strategy'] = 3
    simulator = Simulator(env)
    model_vec_long = [Alpha_Beta_Model(env, 'RW_IGM'), Alpha_Beta_Model(env, 'RW_D'), Random_Model(env), Win_Stay_Loose_Shift_Model(env), Alpha_Beta_Model(env, 'IG'), Alpha_Beta_Model(env, 'RW_IG'), Alpha_Beta_Model(env, 'RW_CK'), Alpha_Beta_Model(env, 'CK'), Alpha_Beta_Model(env, 'RW'), Rescorla_Wagner_Model(env), TransitionModel(env)]
    

    app = QApplication(sys.argv)
    window = Window(simulator)
    for model in model_vec_long:
        window.add_model(model)    
        window.show()
        window.select_model(2)
    sys.exit(app.exec_())

