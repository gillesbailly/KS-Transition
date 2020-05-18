import sys
from trans import *
from transD import *
from random_model import *
from win_stay_loose_shift_model import *
from rescorla_wagner_model import *
from choice_kernel_model import *
from rescorla_wagner_choice_kernel_model import *
from alpha_beta_model import *
from simulationWidget import *
from simulator import *
import numpy as np
import argparse




if __name__=="__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-m", "--model", type=int, help="choose model", default=0)
    parser.add_argument("-e", "--exec", help="exec", choices=['', 'test', 'simulate', 'explore'], default = '')
    parser.add_argument("-f", "--filter", help="filter, e.g. \"user_id=1\", default=\"\" meaning all" , default="user_id=1")
    parser.add_argument("-c", "--command", help="choose the command, -1 means all", type=int, default=-1 )
    
    args = parser.parse_args()
    if args.verbose:
        print("verbosity turned on (but not used...)")

    env = Environment("./parameters/environment.csv")
    env.value['n_strategy'] = 3
    simulator = Simulator(env)
    model_vec_long = [TransD(env, 'TRANS_D'), Trans(env, 'trans'), Alpha_Beta_Model(env, 'RW_IG_CTRL'), Alpha_Beta_Model(env, 'RW_IGM'), Alpha_Beta_Model(env, 'RW_D'), Random_Model(env), Win_Stay_Loose_Shift_Model(env), Alpha_Beta_Model(env, 'IG'), Alpha_Beta_Model(env, 'RW_IG'), Alpha_Beta_Model(env, 'RW_CK'), Alpha_Beta_Model(env, 'CK'), Alpha_Beta_Model(env, 'RW'), Rescorla_Wagner_Model(env)]
    #index_model = sys.args[1] if len(sys.args) == 2 else 0

    print("-- model ", args.model)
    app = QApplication(sys.argv)
    window = Window(simulator)
    for model in model_vec_long:
        window.add_model(model)    
    window.show()
    window.select_model(args.model)
    window.filter_edit.setText(args.filter)
    if args.exec == "test" :
        window.test_model()
    elif args.exec == "simulate" :
        window.simulate()
    elif args.exec == "explore" :
        window.explore()

    window.select_command( args.command )

    sys.exit(app.exec_())

