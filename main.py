import sys
import os.path
from transitionModel import *
from random_model import *
from win_stay_loose_shift_model import *
from rescorla_wagner_model import *
from choice_kernel_model import *
from rescorla_wagner_choice_kernel_model import *
from alpha_beta_model import *
from simulationWidget import *
from experiment import *
import csv
import numpy as np
from util import *
from math import *
import pandas as pd
import time

##########################################
# how to deal with q0?
# it is technique dependent
# how to deal wiht errors...

##########################################
#                                        #
#             Simulator                  #
#                                        #
##########################################
class Simulator(object):


    ###################
    def __init__(self, environment):
        self.name = "Simulator"
        self.env = environment
        self.ignore_count = 0


    ###################################
    def save(self, filename, sims):
        with open(filename, mode='w') as log_file:
            writer = csv.writer(log_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            header = ['model', 'param', 'sim', 'episode', 'trial', 'n_selection', 'stimulus', 'occ', 'cmd', 'strategy', 'method', 'time', 'success']
            writer.writerow( header)
    
            for i in range( len(sims) ):
                h = sims[i]
                n_selection = len(h.command_sequence)
                episode = h.episode_id
                occ = dict()
                for cmd in h.commands:
                    occ[cmd] = 0
                for j in range( n_selection ):
                    stimulus = h.command_sequence[j]
                    strategy = h.action[j].strategy_str()
                    method = h.action[j].method_str()

                    occ[ stimulus ] = occ[ stimulus ] + 1
                    row = [h.model_name, h.params, i, episode, j + 1, n_selection, stimulus, occ[ stimulus ],  h.cmd[j], strategy, method, h.time[j], h.success[j] ]
                    writer.writerow(row)


    ###################################
    #
    # Test model against empirical data
    # 
    ###################################
    def test_model(self, model, filename, _filter):
        experiment = Experiment( filename, env.value['n_strategy'], _filter )
        sims = self.test_model_data(model, experiment)
        return sims


        
    ###################################
    def test_model_data(self,model, experiment):
        sims = []
        #print("debug experiment data: ", len(experiment.data) )
        for d in experiment.data:
            data = copy.deepcopy(d)
            self.env.update_from_empirical_data( copy.copy(data.commands), copy.copy(data.cmd), 3 )
            available_strategies = self.strategies_from_technique( data.technique_name )
            model.reset( available_strategies )
            log_likelyhood = 0
            data.model_name = model.name
            data.params = model.get_param_value_str()
            #print("debug env cmd seq: ", len(self.env.cmd_seq) )
            #print( data.user_action )
            for date in range( 0, len(self.env.cmd_seq) ):
                cmd = self.env.cmd_seq[date]

                #result from the model
                action, prob_vec = model.select_action( cmd, date ) #action correct
                res = model.generate_step(cmd, date, action)
                a_vec = model.get_actions_from( cmd )
                probs = values_long_format(a_vec, prob_vec)
                data.update_history_short( action, probs, res.time, res.success )
                if model.has_q_values():
                    data.q_value_vec.append( values_long_format(a_vec, model.q_values( cmd, date )) )

                # model against empirical data
                user_step = StepResult(cmd, Action(cmd,data.user_action[date].strategy),  data.user_time[date], data.user_success[date])
                user_action_prob = model.prob_from_action( user_step.action, date)
                data.user_action_prob.append( user_action_prob)
                #if user_action_prob == 0:
                #    user_action_prob = 0.000001
                log_likelyhood += log2(user_action_prob)

                #update the model with empirical data
                model.update_model( user_step )
                
            
            data.log_likelyhood = log_likelyhood
            sims.append(data)
        return sims        




    ###################################
    # run the model on n_episode
    # do not change the values of the parameters
    ###################################
    def run(self, model, n_episode):
        #print('\n========================= run simulation =====================')
        #print("model: ", model)
        sims = []

        for i in range(n_episode):
            self.env.update()
            history = History()
            history.set_commands( self.env.commands, self.env.cmd_seq, None, None)
            history.set_model( model.name, model.get_param_value_str() )
            history.episode_id = i
            model.reset( [Strategy.MENU, Strategy.HOTKEY, Strategy.LEARNING ] )
            
            for date in range( 0, len(self.env.cmd_seq) ):
                cmd = self.env.cmd_seq[date]
                action, prob_vec = model.select_action( cmd, date) #action correct
                res = model.generate_step(cmd, date, action)
                model.update_model(res)
                history.update_history_long(res.cmd, res.action, prob_vec, res.time, res.success)

            sims.append( history )
        return sims


    ###################################
    # explore model
    # this method is recursive.
    # 
    ###################################
    def explore(self, model, params, n_episode):
        if len(params) == 0:
            return []

        params_saved = copy.deepcopy( model.params )
        res = []
        p = params[0]
        print("p: ", params[0])
        a_info = model.params.get_info(p)

        for v in np.arange(a_info[1], a_info[2], a_info[3]):    #1 min, 2. max, 3. step
            model.params.value[p] = v
            sims = []
            if len(params) == 1:
                sims = self.run( model, n_episode)
            else:
                sublist = params[1: len(params) ]
                sims = self.explore(model, sublist, n_episode)
            res = res + sims
            #print("explore: ",  len(res) )

        model.params = params_saved
        return res



    # ###################################
    # def analyze( self, model_vec, filename ):
    #     print(env.value['n_strategy'])
    #     experiment = Experiment( filename, env.value['n_strategy'] )
    #     print("------------- EXPLORATION ---------------")
    #     #model_name_vec = []
    #     #for m in model_vec : 
    #     #    model_name_vec.append( m.name )
    #     #print( "models: ", model_name_vec )
        
    #     sims = self.explore_model_and_parameter_space(model_vec, experiment)
        
    #     # for d in sims : 
    #     #     print(d.model_name, d.model_params, d.user_id, d.technique_id, d.log_likelyhood)
    #     # return sims


    def parse_params(self, params):
        name_vec = []
        value_vec = []
        param_vec = params.split(',')
        for p in param_vec:
            d = p.split(':')
            name_vec.append( d[0] )
            value_vec.append( d[1] )
        return name_vec, value_vec


    ###################################
    def save_loglikelyhood(self, filename, sims, overwrite = False):
        mode = 'w' if overwrite else 'a'
        exist = os.path.exists(filename)

        with open(filename, mode= mode ) as log_file:
            writer = csv.writer(log_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            if not exist or mode == 'w':
                header = ['model_name', 'user_id', 'hotkey_count', 'technique_id', 'log_likelyhood', 'n_params', 'N', 'p1', 'p2', 'p3', 'p4', 'p5']
                writer.writerow( header)
    
            for d in sims:
                name_vec, value_vec = self.parse_params( d.model_params )
                n_params = len( value_vec)
                for i in range( n_params, 5 ):  # fill with null values
                    value_vec.append(-1)
                row = [d.model_name, d.user_id, d.hotkey_count, d.technique_id, d.log_likelyhood, n_params, d.N] + value_vec
                writer.writerow(row)


    def is_tested_parameter(self, params, df_log_model):
        name_vec, value_vec = self.parse_params( params )
        n_params = len( value_vec)
        for i in range( n_params, 5 ):  # fill with null values
            value_vec.append(-1)
        #print(df_log_model.p1)
        #print(value_vec)

        res = df_log_model[ (df_log_model.p1 == float(value_vec[0])) & (df_log_model.p2 == float(value_vec[1]) ) & (df_log_model.p3 == float(value_vec[2]) )& (df_log_model.p4 == float(value_vec[3])) & (df_log_model.p5 == float(value_vec[4]))] 
        #print("---------------------- res: ", res, len(res.user_id))
        return len(res.user_id) == 0


    ###################################
    def explore_model_and_parameter_space(self, model_vec, experiment, overwrite= True):
        res = []

        for model in model_vec :
            self.ignore_count = 0
            df_log_model = None if overwrite else pd.read_csv('./likelyhood/log_' + model.name + '.csv', delimiter=';')

            start = time.time()
            params = list( model.get_params().value.keys() )
            sims = self.explore_parameter_space(model, params, experiment, overwrite, df_log_model)
            end = time.time()
            print("explore the model: ", model.name, " in ",  end - start)
            print("------------- ANALYSIS ---------------")
            file_name = './likelyhood/log_' + model.name + '.csv'
            self.save_loglikelyhood(file_name, sims, overwrite)
            print("we ignore ", self.ignore_count, " parameter estimations")
            res += sims
        return res


    ###################################
    def explore_parameter_space(self, model, param_vec, experiment, overwrite, df_log_model):
        if len(param_vec) == 0:
            return []

        param_vec_saved = copy.deepcopy( model.params )
        res = []
        #print("explore_parameter_space: ", param_vec)
        param_name = param_vec[0]
        #print("param: ", param_name)
        param_info = model.params.get_info(param_name)

        for value in np.arange(param_info[1], param_info[2] + param_info[3], param_info[3]):    #1 min, 2. max, 3. step
            model.params.value[param_name] = value
            sims = []
            if len(param_vec) == 1:
                execute = overwrite
                if not execute :
                    execute = self.is_tested_parameter(model.get_param_value_str(), df_log_model)

                if execute:
                    start = time.time()
                    sims = self.fast_test_model(model, experiment)
                    end = time.time()
                    print("wip: ", model.name, model.get_param_value_str(), end-start)
                else:
                    self.ignore_count+=1

            else:
                sub_param_vec = param_vec[ 1: len(param_vec) ]
                sims = self.explore_parameter_space(model, sub_param_vec, experiment, overwrite, df_log_model)
            res = res + sims
            

        model.params = param_vec_saved
        return res

    ###################################
    def strategies_from_technique(self, technique_name):
        #print(technique_name)
        if technique_name == "disable":
            return [Strategy.HOTKEY, Strategy.LEARNING]
        else:
            return[Strategy.MENU, Strategy.HOTKEY, Strategy.LEARNING]     

    ###################################
    def fast_test_model(self,model, experiment):
        #debug_step = 1
        sims = []
        max_user_id = 12
        for data in experiment.data:
            if data.user_id < max_user_id:
                self.env.update_from_empirical_data(data.commands, data.cmd, 3 )
                available_strategies = self.strategies_from_technique( data.technique_name )
                #print("fast test: ", available_strategies)
                model.reset( available_strategies )
                log_likelyhood = 0
                #print("debug env cmd seq: ", len(self.env.cmd_seq) )
                for date in range( 0, len(self.env.cmd_seq) ):
                    #debug_step +=1
                    cmd = self.env.cmd_seq[date]

                    # model against empirical data
                    user_step = StepResult(cmd, Action(cmd, data.user_action[date].strategy),  data.user_time[date], data.user_success[date])
                    user_action_prob = model.prob_from_action( user_step.action, date)
                
                    #if debug_step == 100:
                    #    exit(0)
                    #data.user_action_prob.append( user_action_prob)
                    if user_action_prob == 0:
                        user_action_prob = 0.000001
                    log_likelyhood += log2(user_action_prob)
                    #print(model.name, user_action_prob, log_likelyhood)
                    #update the model with empirical data
                    model.update_model( user_step )
 
                fd = FittingData( model, data.user_id, data.technique_id, log_likelyhood, len(self.env.cmd_seq),  data.get_hotkey_count() )
                sims.append( fd )
        return sims       




    ###################################
    # test all parameters of the model
    def run_sims(self, model, n_episode):
        print("params alpha: ", model.params.get_info('alpha') )
        a_info = model.params.get_info('alpha')
        printer = QPrinter()
        printer.setOutputFormat( QPrinter.PdfFormat )
        printer.setOutputFileName('./graphs/results.pdf')
        painter = QPainter()

        if not painter.begin(printer):
            print("failed to open file, is it writable?");
    
        for a in np.arange(a_info[1], a_info[2], a_info[3]):
            sims = self.run( model, n_episode)
            filename = './results/log_' + 'alpha_' + str(a) + '.csv'
        #simulator.save(filename, sims)
            w = window.simulatorUI.add_sims(sims, filename).parentWidget()
            w.show()
            w.render( painter )

        painter.end()


##################################
def use_gui(simulator, model_vec):    
    app = QApplication(sys.argv)
    window = Window(simulator)
    for model in model_vec:
        window.add_model(model)    
        window.show()
        window.select_model(2)
    sys.exit(app.exec_())


##################################
def use_terminal(simulator, model_vec, overwrite = True):
    
    #simulator.analyze( model_vec, './experiment/grossman_cleaned_data.csv' )
    filename = './experiment/grossman_cleaned_data.csv'
    experiment = Experiment( filename, env.value['n_strategy'] )
    print("------------- EXPLORATION ---------------")
    sims = simulator.explore_model_and_parameter_space(model_vec, experiment, overwrite)
        #model_name_vec = []
        #for m in model_vec : 
        #    model_name_vec.append( m.name )
        #print( "models: ", model_name_vec )
        
        #sims = self.explore_model_and_parameter_space(model_vec, experiment)
        
        # for d in sims : 
        #     print(d.model_name, d.model_params, d.user_id, d.technique_id, d.log_likelyhood)
        # return sims





if __name__=="__main__":
    
    env = Environment("./parameters/environment.csv")
    env.value['n_strategy'] = 3 #only menus and hotkeys
    print(env.value)
    simulator = Simulator(env)
    model_vec_long = [Alpha_Beta_Model(env, ['RWD', 'D'], [0.3, 0]), Random_Model(env), Win_Stay_Loose_Shift_Model(env), Alpha_Beta_Model(env, ['IG'], [0]), Alpha_Beta_Model(env, ['RW', 'IG'], [0.3, 0]), Alpha_Beta_Model(env, ['RW', 'CK'], [0.3, 1]), Alpha_Beta_Model(env, ['CK'], [1]), Alpha_Beta_Model(env, ['RW'], [0.3]), Rescorla_Wagner_Model(env), Rescorla_Wagner_Model(env, True), Choice_Kernel_Model(env), Rescorla_Wagner_Choice_Kernel_Model(env), TransitionModel(env)]
    #model_vec_short = [Rescorla_Wagner_Model(env, True)]
    #model_vec_short = [  Alpha_Beta_Model(env, ['RW', 'CK'], [0.3, 1]), Rescorla_Wagner_Choice_Kernel_Model(env) ]
    model_vec_short = [  Alpha_Beta_Model(env, ['RWD', 'D'], [0.3, 0]), Alpha_Beta_Model(env, ['RW'], [0.3]), Alpha_Beta_Model(env, ['RW', 'IG'], [0.3, 0]), Alpha_Beta_Model(env, ['CK'], [1]), Alpha_Beta_Model(env, ['RW', 'CK'], [0.3, 1]) ]
    #model_vec_short = [  Alpha_Beta_Model(env, ['RWD', 'D'], [0.3, 0])]

    model_vec_short = [ Alpha_Beta_Model(env, ['RW'], [0.3]) ]


    #use_gui(simulator, model_vec_long)
    use_terminal(simulator, model_vec_short, True)

