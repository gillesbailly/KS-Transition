import sys
#from transitionModel import *
from random_model import *
from win_stay_loose_shift_model import *
from rescorla_wagner_model import *
from choice_kernel_model import *
from rescorla_wagner_choice_kernel_model import *
from alpha_beta_model import *
from experiment import *
from simulator import *


if __name__=="__main__":
    overwrite = True
    env = Environment("./parameters/environment.csv")
    env.value['n_strategy'] = 3 #only menus and hotkeys
    simulator = Simulator(env)
    filename = './experiment/grossman_cleaned_data.csv'
    experiment = Experiment( filename, env.value['n_strategy'] )

    #model_vec_long = [Alpha_Beta_Model(env, ['RWD', 'D'], [0.3, 0]), Random_Model(env), Win_Stay_Loose_Shift_Model(env), Alpha_Beta_Model(env, ['IG'], [0]), Alpha_Beta_Model(env, ['RW', 'IG'], [0.3, 0]), Alpha_Beta_Model(env, ['RW', 'CK'], [0.3, 1]), Alpha_Beta_Model(env, ['CK'], [1]), Alpha_Beta_Model(env, ['RW'], [0.3]), Rescorla_Wagner_Model(env), Rescorla_Wagner_Model(env, True), Choice_Kernel_Model(env), Rescorla_Wagner_Choice_Kernel_Model(env), TransitionModel(env)]
    #model_vec_short = [Rescorla_Wagner_Model(env, True)]
    #model_vec_short = [  Alpha_Beta_Model(env, ['RW', 'CK'], [0.3, 1]), Rescorla_Wagner_Choice_Kernel_Model(env) ]
    #model_vec_short = [  Alpha_Beta_Model(env, ['RWD', 'D'], [0.3, 0]), Alpha_Beta_Model(env, ['RW'], [0.3]), Alpha_Beta_Model(env, ['RW', 'IG'], [0.3, 0]), Alpha_Beta_Model(env, ['CK'], [1]), Alpha_Beta_Model(env, ['RW', 'CK'], [0.3, 1]) ]
    #model_vec_short = [  Alpha_Beta_Model(env, ['RWD', 'D'], [0.3, 0])]
    #model_vec_short = [ Alpha_Beta_Model(env, 'RW_D') ]
    args = sys.argv
    model_vec = []
    for i in range(1, len(sys.argv) ) :
        name = sys.argv[i]
        if name == "RW": 
            model_vec.append( Alpha_Beta_Model(env, 'RW') )
        elif name == "CK":
            model_vec.append( Alpha_Beta_Model(env, 'CK') )
        elif name == "RW_D":
            model_vec.append( Alpha_Beta_Model(env, 'RW_D') )
        elif name == "RW_CK":
            model_vec.append( Alpha_Beta_Model(env, 'RW_CK') )
        elif name == "RW_IG":
            model_vec.append( Alpha_Beta_Model(env, 'RW_IG') )
        elif name == "CK_D":
            model_vec.append( Alpha_Beta_Model(env, 'CK_D') )
        elif name == "CK_IG":
            model_vec.append( Alpha_Beta_Model(env, 'CK_IG') )
        elif name == "RW_IGM":
            model_vec.append( Alpha_Beta_Model(env, 'RW_IGM') )



    print("------------- EXPLORATION ---------------")
    sims = simulator.explore_model_and_parameter_space(model_vec, experiment, overwrite)

