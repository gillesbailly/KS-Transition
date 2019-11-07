import sys
from transitionModel import *
from random_model import *
from win_stay_loose_shift_model import *
from simulationWidget import *
import csv
from util import *



##########################################
#                                        #
#             Simulator                  #
#                                        #
##########################################
class Experiment(object):

    ####################
    def __init__(self, path):
        self.data = self.load(path)

    #######################
    def load(self, path):
        if not path:
            return
        with open(path, 'r') as csvFile:
            reader = csv.reader(csvFile, delimiter= ';')
            header = True
            for row in reader:
                if not header:
                    self.value[ row[0] ] = float( row[2] ) if '.' in row[2] else int( row[2] )
                    min_  = float( row[3] ) if '.' in row[3] else int( row[3] )
                    max_  = float( row[4] ) if '.' in row[4] else int( row[4] )
                    self.range[ row[0] ] = [ min_, max_ ]
                    self.step[ row[0] ] = float( row[5] ) if '.' in row[5] else int( row[5] )
                    self.comment[ row[0] ] = row[6]
                else:
                    header = False


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
            header = ['model', 'sim', 'trial', 'n_selection', 'stimulus', 'occ', 'cmd', 'strategy', 'method', 'time', 'success']
            writer.writerow( header)
    
            for i in range( len(sims) ):
                h = sims[i]
                n_selection = len(h.command_sequence)
                occ = dict()
                for cmd in h.commands:
                    occ[cmd] = 0
                for j in range( n_selection ):
                    stimulus = h.command_sequence[j]
                    strategy = h.action[j].strategy_str()
                    method = h.action[j].method_str()
                    occ[ stimulus ] = occ[ stimulus ] + 1
                    row = [h.model_name, i, j + 1, n_selection, stimulus, occ[ stimulus ],  h.cmd[j], strategy, method, h.time[j], h.success[j] ]
                    writer.writerow(row)


    ###################################
    # run the model on n_episode
    def run(self, model, n_episode):
        print('\n========================= run simulation =====================')
        print("model: ", model)
        sims = []

        for i in range(n_episode):
            self.env.update()
            history = History( self.env.commands, self.env.cmd_seq, model.name )
            model.reset()

            belief = model.initial_belief()
            state = model.initial_state()
            
            for date in range( 0, len(self.env.cmd_seq) ):
                is_legal = False
                cmd = self.env.cmd_seq[date]
                action = model.select_action( cmd, date) #action correct
                res, is_legal = model.generate_step(cmd, date, state, action)
                next_belief = belief
                history.update_history(res.cmd, res.state, res.next_state, res.action, res.time, res.success, belief, belief )
                state = res.next_state
                belief = next_belief
                print("=============")
            sims.append( history )
        return sims



if __name__=="__main__":
    app = QApplication(sys.argv)
    #env = Environment(n_commands = 3, n_selection= 5, s_zipfian = 1, error_cost = 0.25)
    
    env = Environment("./parameters/environment.csv")
    print(env.value)
    simulator = Simulator(env)
    window = Window(simulator)
    random_model = Random_Model(env)
    window.add_model( random_model )

    trans_model = TransitionModel(env)
    window.add_model( trans_model )

    win_stay_model = Win_Stay_Loose_Shift_Model(env)
    window.add_model( win_stay_model )

    window.show()
    sims = simulator.run(win_stay_model, 5)
    window.simulatorUI.add_sims( sims, "oki" )
    simulator.save('./results/log1.csv', sims)
    sys.exit(app.exec_())
