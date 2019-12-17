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
        sims = []

        for d in experiment.data:
            data = copy.deepcopy(d)

            self.env.cmd_seq = copy.copy(data.cmd)
            self.env.value['n_commands'] = len( data.commands )
            self.env.value['n_strategy'] = 2
            self.env.commands = data.commands
            model.reset()

            for date in range( 0, len(self.env.cmd_seq) ):
                cmd = self.env.cmd_seq[date]
                action, action_prob = model.select_action( cmd, date ) #action correct
                res = model.generate_step(cmd, date, action)
                
                data.action.append( action )
                data.action_prob.append( action_prob )
                data.time.append( res.time )
                data.success.append( res.success ) 

                user_step = StepResult()
                user_step.cmd = cmd

                user_step.action = Action(cmd, data.user_action[date])
                user_step.time = data.user_time[date]
                user_step.success = data.user_success[date] 
                print("a_pred:", action.to_string(True), " m_user:", user_step.action.to_string(True), "time:", user_step.time)
                model.update_model( user_step )
                
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
                action, action_prob = model.select_action( cmd, date) #action correct
                res = model.generate_step(cmd, date, action)
                model.update_model(res)
                history.update_history(res.cmd, res.action, action_prob, res.time, res.success)

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




if __name__=="__main__":
    # experiment = Experiment('./experiment/grossman_cleaned_data.csv')
    # print("experiment length: ", len(experiment.data) )
    # for h in experiment.data:
    #     h.print_general()
    #     h.print()

    # exit(0)


    app = QApplication(sys.argv)
    
    env = Environment("./parameters/environment.csv")
    print(env.value)

    simulator = Simulator(env)
    window = Window(simulator)
    
    model_vec = [Random_Model(env), Win_Stay_Loose_Shift_Model(env), Rescorla_Wagner_Model(env), Choice_Kernel_Model(env), Rescorla_Wagner_Choice_Kernel_Model(env), TransitionModel(env)]
    for model in model_vec:
        window.add_model(model)    

    window.show()
    window.select_model(0)
    #sims = simulator.run(model_vec[3], 5)
    #window.simulatorUI.add_sims( sims, "oki" )
    #simulator.save('./results/log1.csv', sims)
    


    sys.exit(app.exec_())
