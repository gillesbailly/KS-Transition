import sys
from transitionModel import *
from random_model import *
from win_stay_loose_shift_model import *
from rescorla_wagner_model import *
from choice_kernel_model import *
from rescorla_wagner_choice_kernel_model import *
from simulationWidget import *
from experiment import *
import csv
import numpy as np
from util import *
from math import *
import time



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
        experiment = Experiment( filename, _filter )
        sims = self.test_model_data(model, experiment)
        return sims

        
    ###################################
    def test_model_data(self,model, experiment):
        sims = []
        #print("debug experiment data: ", len(experiment.data) )
        for d in experiment.data:
            data = copy.deepcopy(d)
            self.env.update_from_empirical_data( copy.copy(data.commands), copy.copy(data.cmd), 3 )

            model.reset()
            log_likelyhood = 0
            data.model_name = model.name
            data.params = model.get_param_value_str()
            #print("debug env cmd seq: ", len(self.env.cmd_seq) )
            for date in range( 0, len(self.env.cmd_seq) ):
                cmd = self.env.cmd_seq[date]

                #result from the model
                action, prob_vec = model.select_action( cmd, date ) #action correct
                res = model.generate_step(cmd, date, action) 
                data.update_history_short( action, prob_vec, res.time, res.success )
                if model.has_q_values():
                    data.q_value_vec.append( model.q_values( cmd, date ) )

                # model against empirical data
                user_step = StepResult(cmd, Action(cmd,data.user_action[date].strategy),  data.user_time[date], data.user_success[date])
                user_action_prob = model.prob_from_action( user_step.action, date)
                data.user_action_prob.append( user_action_prob)
                if user_action_prob == 0:
                    user_action_prob = 0.000001
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
            model.reset()
            
            for date in range( 0, len(self.env.cmd_seq) ):
                cmd = self.env.cmd_seq[date]
                action, prob_vec = model.select_action( cmd, date) #action correct
                res = model.generate_step(cmd, date, action)
                model.update_model(res)
                history.update_history(res.cmd, res.action, prob_vec, res.time, res.success)

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



    ###################################
    def analyze( self, model_vec, filename ):
        experiment = Experiment( filename )
        print("------------- EXPLORATION ---------------")
        model_name_vec = []
        for m in model_vec : 
            model_name_vec.append( m.name )
        print( "models: ", model_name_vec )
        
        sims = self.explore_model_and_parameter_space(model_vec, experiment)
        print("------------- ANALYSIS ---------------")
        self.save_loglikelyhood('./likelyhood/log.csv', sims)
        for d in sims : 
            print(d.model_name, d.model_params, d.user_id, d.technique_id, d.log_likelyhood)
        return sims


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
    def save_loglikelyhood(self, filename, sims):
        with open(filename, mode='w') as log_file:
            writer = csv.writer(log_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            header = ['model_name', 'user_id', 'technique_id', 'log_likelyhood', 'p1', 'p2', 'p3', 'p4', 'p5']
            writer.writerow( header)
    
            for d in sims:
                name_vec, value_vec = self.parse_params( d.model_params )
                for i in range( len( value_vec ), 5 ):
                    value_vec.append(-1)
                row = [d.model_name, d.user_id, d.technique_id, d.log_likelyhood] + value_vec
                writer.writerow(row)


    ###################################
    def explore_model_and_parameter_space(self, model_vec, experiment):
        res = []
        for model in model_vec :
            start = time.time()
            params = list( model.get_params().value.keys() )
            sims = self.explore_parameter_space(model, params, experiment)
            end = time.time()
            print("explore the model: ", model.name, " in ",  end - start)
            res += sims
        return res


    ###################################
    def explore_parameter_space(self, model, param_vec, experiment):
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
                start = time.time()
                sims = self.fast_test_model(model, experiment)
                end = time.time()
                print("wip: ", model.name, model.get_param_value_str(), end-start)
                
            else:
                sub_param_vec = param_vec[ 1: len(param_vec) ]
                sims = self.explore_parameter_space(model, sub_param_vec, experiment)
            res = res + sims
            

        model.params = param_vec_saved
        return res

    ###################################
    def fast_test_model(self,model, experiment):
        sims = []
        for data in experiment.data:
            self.env.update_from_empirical_data(data.commands, data.cmd, 3 )
            model.reset()
            log_likelyhood = 0
            #print("debug env cmd seq: ", len(self.env.cmd_seq) )
            for date in range( 0, len(self.env.cmd_seq) ):
                cmd = self.env.cmd_seq[date]

                # model against empirical data
                user_step = StepResult(cmd, Action(cmd,data.user_action[date].strategy),  data.user_time[date], data.user_success[date])
                user_action_prob = model.prob_from_action( user_step.action, date)
                #data.user_action_prob.append( user_action_prob)
                if user_action_prob == 0:
                    user_action_prob = 0.000001
                log_likelyhood += log2(user_action_prob)

                #update the model with empirical data
                model.update_model( user_step )
                
            
            sims.append( FittingData( model, data.user_id, data.technique_id, log_likelyhood) )
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
def use_terminal(simulator, model_vec):
    simulator.analyze( model_vec, './experiment/grossman_cleaned_data.csv' )



if __name__=="__main__":
    
    env = Environment("./parameters/environment.csv")
    print(env.value)
    simulator = Simulator(env)
    model_vec_long = [Random_Model(env), Win_Stay_Loose_Shift_Model(env), Rescorla_Wagner_Model(env), Choice_Kernel_Model(env), Rescorla_Wagner_Choice_Kernel_Model(env), TransitionModel(env)]
    model_vec_short = [Random_Model(env)]

    #use_gui(simulator, model_vec_long)
    use_terminal(simulator, model_vec_short)

