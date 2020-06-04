import sys
#from transitionModel import *
from random_model import *
from win_stay_loose_shift_model import *
from rescorla_wagner_model import *
from choice_kernel_model import *
from rescorla_wagner_choice_kernel_model import *
from trans import *
from transD import *
from alpha_beta_model import *
from experiment import *
from simulator import *
import argparse

# ssh gbailly@gateway.isir.upmc.fr
# ssh gbailly@cluster.isir.upmc.fr
#T3

if __name__=="__main__":
    overwrite = True
    env = Environment("./parameters/environment.csv")
    env.value['n_strategy'] = 3 #only menus and hotkeys
    simulator = Simulator(env)
    #filename = './experiment/grossman_cleaned_data.csv'
    filename = './experiment/hotkeys_formatted_dirty.csv'
    experiment = Experiment( filename, env.value['n_strategy'] )
    #model_vec_long = [Alpha_Beta_Model(env, ['RWD', 'D'], [0.3, 0]), Random_Model(env), Win_Stay_Loose_Shift_Model(env), Alpha_Beta_Model(env, ['IG'], [0]), Alpha_Beta_Model(env, ['RW', 'IG'], [0.3, 0]), Alpha_Beta_Model(env, ['RW', 'CK'], [0.3, 1]), Alpha_Beta_Model(env, ['CK'], [1]), Alpha_Beta_Model(env, ['RW'], [0.3]), Rescorla_Wagner_Model(env), Rescorla_Wagner_Model(env, True), Choice_Kernel_Model(env), Rescorla_Wagner_Choice_Kernel_Model(env), TransitionModel(env)]

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-m", "--model", help="Class of models: ", choices=['TransD', 'Alpha_Beta'] )
    parser.add_argument("-p", "--model_parameters", help="parameters", choices=['RW_without', 'CK_without', 'RW_CK_without', 'RW', 'ÇK', 'RW_CK', 'TRANS_D', 'TRANS_DCK', 'TRANS_DK0', 'TRANS_DCK0'], default = '')
    parser.add_argument("-u", "--users", help="list of user ids", nargs="+", type=int )
    parser.add_argument("-f", "--fixed_parameters", help="list of fixed parameters" )
    args = parser.parse_args()
    if len(sys.argv) == 1 :
        parser.print_help()
        exit(0)
    model = None
    if args.model == "TransD" :
        model = TransD( env, args.model_parameters )
    elif args.model == "Alpha_Beta" :
        model = Alpha_Beta_Model( env, args.parameter )


    print("-------------------optimisation------------")
    for target in args.users : 
        print("target users: ", target)
        #target = "9"
        #fixed_params = {'HORIZON':1}
        fixed_params = dict()
        simulator.optimize_models([model], experiment, str( target ), fixed_params)
