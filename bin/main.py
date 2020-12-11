import sys
import time as TIME
import timeit
import numpy as np

import os.path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication
import argparse
sys.path.append("./GUI/")
sys.path.append("./lib/")
sys.path.append("./plugins/")
sys.path.append("./plugins/loader/")
sys.path.append("./plugins/export/")
sys.path.append("./plugins/model/")

import util
from user_data_loader import *
from user_overview import User_Overview
#from matplotlib_view import *
from filter import *
from data_explorer import  Empirical_Panel
from random_model import Random_Model
from CK_model import CK_Model
from RW_model import RW_Model
from ILHP_model import ILHP_Model
from RWCK_model import RWCK_Model



from model_fit import Model_Fitting
from model_simulation import Model_Simulation
from model_fitting_visualisation import *
from model_simulation_visualisation import *
from parameter_view import *
from parameter_matrix_view import Parameter_Matrix_View
from paper_figure import *
from parameters_export import Parameters_Export
from parameters_loader import Parameters_Loader

#import seaborn as sns
from scipy.optimize import *

##########################################################################
# function used to see more details how well the model fits              #
# the data of one users                                                  #
# INPUT:                                                                 #
#   - fitting_explorer (Empirical_Panel) : Qt Widget to display data     #
#   - fitting_res (list< Model_Result > ): output of model_fitting.run() #
#   - users_df ( Datframe) : information about users                     #
#   - user_id : id of the user we want to investigate                    #
#                                                                        #
# NOTE                                                                   #
#  to efficiently use this method, you can augment the amount of         #
#  information contained in Model_Result. To do that, in the method      #
#  run_debug() in model_fit.py (step 3.a), add the following             #
#   lines:                                                               #
#       prob_vec      = self.model.action_probs( cmd )                   #                                                              #
#       res.output.menu[ i ]     = probs[ Strategy.MENU ]                #
#       res.output.hotkey[ i ]   = probs[ Strategy.HOTKEY ]              #
#       res.output.learning[ i ] = probs[ Strategy.LEARNING ]            #
#                                                                        #
#  This displays the probability for each action to be chosen            # 
##########################################################################
def show_fitting_details( fitting_explorer, fitting_res, users_df, user_id ):
    df = users_df[ users_df.user_id == user_id ]
    df = df.copy()
    fitting_explorer.set_model_fitting_df( fitting_res, df )
    fitting_explorer.show()

def show_simulation_details( simulation_explorer, simulation_res, user_id ):
    df = simulation_vec_to_data_frame( simulation_res )
    simulation_explorer.set_model_simulation_df( df, [ user_id ] )
    simulation_explorer.show()


def my_func( v ):
    return (30-v[0])**2 +  (40-v[1])**2 + (70-v[2])**2

#######################################################
#                       MAIN                          #
#######################################################
if __name__=="__main__":
    
    # linear_mat = np.zeros( 3 )
    # linear_mat[ 0 ] = 4
    # linear_mat[ 1 ] = 1
    # linear_constraint = LinearConstraint( linear_mat, 0, 40 )
    # res = differential_evolution( my_func,
    #                             constraints = (linear_constraint), 
    #                             bounds      = [[0,100], [0,100], [0,100] ])
                             
    # print( res )
    # exit(0)    

    # strategies = np.array([1,2,3])

    # print( timeit.timeit( 'util.soft_max(2, np.array([2,3]) )', number =10000, setup='import numpy as np; import util'  ) )
    # print( util.soft_max(2, np.array([2,3]) ) )

    # #print( timeit.timeit( 'util.soft_max2(2, np.array([0,2,3]), 1 )', number =10000, setup='import numpy as np; import util'  ) )
    # #print( util.soft_max2( 2, np.array([0,2,3]), 1 ), np.sum( util.soft_max2( 2, np.array([0,2,3]), 1 ) )  )

    # #print( timeit.timeit( 'util.soft_max2(2, np.array([2,3]) )', number =10000, setup='import numpy as np; import util'  ) )
    # #print( util.soft_max( 2, np.array([2,3]) ), np.sum( util.soft_max( 2, np.array([2,3]) ) )  )

    # print( timeit.timeit( 'util.soft_max3(2, np.array([0,2,3]) )', number =10000, setup='import numpy as np; import util'  ) )
    # print( util.soft_max3( 2, np.array([0,2,3]) ), np.sum( util.soft_max3( 2, np.array([0,2,3]) ) )  )

    # print( timeit.timeit( 'util.soft_max3(2, np.array([0,2,3]), np.array([0,1,1]) )', number =10000, setup='import numpy as np; import util'  ) )
    # print( util.soft_max3( 2, np.array([0,2,3]), np.array([0,1,1]) ), np.sum( util.soft_max3( 2, np.array([0,2,3]), np.array([0,1,1]) ) )  )


    # exit(0)
    parser = argparse.ArgumentParser()
    #parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-m", "--models", help="parameters", choices=['RW', 'CK', 'RWCK', 'ILHP'], default = '')
    parser.add_argument("-u", "--users", help="list of user ids", nargs="+", type=int )
    parser.add_argument("-t", "--technique", help="techniques", choices=['audio', 'disable', 'traditional'] )
    parser.add_argument("-a", "--analyse", help="type of analyse", choices=['overview', 'fitting', 'simulation', 'optimisation', 'figure', 'parameter', 'user'] )
    parser.add_argument("-n", "--min", help="min user id", type=int )
    parser.add_argument("-x", "--max", help="max user id", type=int )
    
    
    #parser.add_argument("-h", "--help", help="help" )
    
    args = parser.parse_args()
    # if len(sys.argv) == 1 :
    #     parser.print_help()
    #     exit(0)

    # if args.help:
    #     parser.print_help()
    #     exit(0)

    analyse_vec = ['fitting', 'simulation']
    if args.analyse :
        analyse_vec = [ args.analyse ]
    min_user_id = 0
    max_user_id = 1
    if args.min:
        min_user_id = args.min
    if args.max:
        max_user_id = args.max

    
    #######  Load Empirical data ##########
    path = './data/user_data.csv'
    loader = User_Data_Loader()
    users_data = loader.load( path )                        #users_data: array< User_Data > (see util.py )
    # keep only a subset of the data 
    #( 5 participants with traditional and 5 participants with audio )
    #my_filter = Filter( user_min = 1, user_max = 1, techniques=["traditional", "audio"] )  
    my_filter = Filter( user_min = min_user_id, user_max = max_user_id )  
    #my_filter.users = [4,7]
    user_data_vec = my_filter.filter( users_data )
    users_df = user_data_vec_to_data_frame( user_data_vec ) # users_df : DataFrame (seaborn)
    
    ###### Load models ##########
    model_vec = [ CK_Model(), RW_Model(), RWCK_Model() ] 
    #model_vec = [  RW_Model()  ] 
    #model_vec = [ RW_Model(), CK_Model(), RWCK_Model(), ILHP_Model('T_I'), ILHP_Model('T_I_P') ]
    #model_vec = [ ILHP_Model('T_I_H2_P'), ILHP_Model('T_I_H3_P'), ILHP_Model('T_I_H4_P') ]
    #model_vec = [ ILHP_Model('T'), ILHP_Model('T_I'), ILHP_Model('T_H'), ILHP_Model('T_P'), ILHP_Model('T_I_P'), ILHP_Model('T_I_H'), RWCK_Model()  ]
    #model_vec = [ ILHP_Model('T_I'), ILHP_Model('T_I_P') ]
    #model_vec = [ ILHP_Model('T'), ILHP_Model('T_I'), ILHP_Model('T_H'), ILHP_Model('T_P'), ILHP_Model('T_I_P'), ILHP_Model('T_I_H'), ILHP_Model('T_H_P'), ILHP_Model('T_I_H_P')  ]
    model_vec = [ ILHP_Model('T_I_H_P') ]
    #model_vec = [ ILHP_Model('T'), ILHP_Model('T_I'), ILHP_Model('T_H'), ILHP_Model('T_P'), ILHP_Model('T_I_P'), ILHP_Model('T_I_H'), ILHP_Model('T_H_P'), ILHP_Model('T_I_H_P')  ]
    #model_vec = [ ILHP_Model('H1-D_H1'), ILHP_Model('H1-D_H2'), ILHP_Model('H1-D_H3'), ILHP_Model('H1-D_H4'), ]

    print( "----------------------------------------------------------" )
    print( "\nlist of users id: ", users_df['user_id'].unique() )
    print( "list of models: ", [model.long_name() for model in model_vec ] )
    print( "\n--------------------------------------------------------" )
    
    if 'optimisation' in analyse_vec:
        ###############################################################
        #######           PARAMETER ESTIMATION               ##########
        ###############################################################
        model_fitting       = Model_Fitting()
        model_fitting.debug = True
        model_fitting.command_ids   = range(0,14)
        model_fitting.user_data_vec = user_data_vec
        model_fitting.model_vec     = model_vec
        fitting_res = model_fitting.optimize()
        # save parameters
        Parameters_Export.write(fitting_res, './optimal_parameters/')
        print("the optimisation is done")
        exit(0)



    if 'figure' in analyse_vec :
        fitting_df = Parameters_Loader.load( './optimal_parameters_rwck/' )
        path = './figures/'
        ilhp_fitting_figures( fitting_df, path )

        model_simulation = Model_Simulation()
        model_simulation.command_ids   = range(0,14)
        model_simulation.user_data_vec = user_data_vec
        model_simulation.model_vec     = [ CK_Model(), RW_Model(), RWCK_Model() ] 
        model_simulation.n_simulations = 10
        model_simulation.parameters    = Parameters_Loader.load('./optimal_parameters_rwck/')
        print( 'Run', model_simulation.n_simulations, 'simulations for each model and participant'  ) 
        simulation_res = model_simulation.run()
        simulation_df = simulation_vec_to_data_frame( simulation_res )
        ilhp_simulation_figures( simulation_df, users_df, path )
        
        exit(0)



    app = QApplication(sys.argv)
    fitting_explorer = Empirical_Panel()
    fitting_explorer.hide()
    simulation_explorer = Empirical_Panel()
    simulation_explorer.hide()
    explorer = None
    
    if 'overview' in analyse_vec :
        #####################################################
        ######  Show an overview of the data (1.a) ##########
        #####################################################
        overview = User_Overview()
        overview.set_users_df( users_df )
        overview.show()

        overview2 = User_Overview()
        overview2.set_cmd_users_df( users_df )
        overview2.show()

        ###### Show the sequence of commands (TODO 1.b) ##########
        explorer = Empirical_Panel()
        explorer.subwin_height = 750   
        explorer.set_users_df( users_df )
        explorer.show()




    if 'fitting' in analyse_vec:
        #############################################################
        #####                 Model fitting                ##########
        #############################################################
        model_fitting  = Model_Fitting()
        model_fitting.parameters    = Parameters_Loader.load( './optimal_parameters/' )
        model_fitting.debug = True
        model_fitting.command_ids   = range(0,14)    # 14 commands
        model_fitting.user_data_vec = user_data_vec
        model_fitting.model_vec     = model_vec
        fitting_res = model_fitting.run()            # res: list < Model_Result > ( see util.py )
        # display the results
        fitting_visu = Model_Fitting_Visualisation()
        fitting_visu.update_canvas( fitting_res )
        #explorer = Empirical_Panel()
        #show_fitting_details( explorer, fitting_res, users_df, 5 )
    
        


    if 'simulation' in analyse_vec:
        ###############################################################
        #######            MODEL SIMULTION                   ##########
        ###############################################################
        model_simulation = Model_Simulation()
        model_simulation.command_ids   = range(0,14)
        model_simulation.user_data_vec = user_data_vec
        model_simulation.model_vec     = model_vec
        model_simulation.n_simulations = 10
        model_simulation.parameters    = Parameters_Loader.load('./optimal_parameters/')
        simulation_res = model_simulation.run()
        # # display the results
        simulation_visu = Model_Simulation_Visualisation()
        simulation_visu.update_canvas( simulation_res, users_df )
        explorer = Empirical_Panel()
        show_simulation_details( explorer, simulation_res, 4)



    if 'parameter' in analyse_vec:
        parameters = Parameters_Loader.load('./optimal_parameters_D/')
        view = Parameter_Matrix_View()
        view.set_data( parameters, model_vec[ 0 ].variant_name )
        #parameter_view.analyze_by_model_param2( parameters, [model.variant_name for model in model_vec ] )
        view.show()


    if 'user' in analyse_vec:
        users_data = loader.load( path )
        columns = np.array( ['user', 'technique', 'n_hotkeys'] )
        df = pd.DataFrame( columns = columns )    
        row = dict()

        for user in users_data:
            strategy_list = [ action.strategy for action in user.output.action ] 
            row[ 'user' ] = user.id
            row[ 'technique' ] = user.technique_name
            row[ 'n_hotkeys' ] = strategy_list.count(1)
            #print( "user:",user.id, 'technique:', user.technique_name, 'n hotkeys:', strategy_list.count(1) )
            df = df.append( row, ignore_index = True )
        df.to_csv( './data/n_hotkeys.csv', index=False, mode = 'w' )
        exit(0)


    sys.exit(app.exec_())




