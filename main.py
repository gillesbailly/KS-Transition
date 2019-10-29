import sys
from transitionModel import *
from simulationWidget import *
from util import *



##########################################
#                                        #
#             Environment (context)      #
#                                        #
##########################################
class Environment(object):

    ###################
    def __init__(self, n_commands, n_selection, s_zipfian, error_cost):
        self.reset(n_commands, n_selection, s_zipfian, error_cost)
        
    ###################
    # create the list of commands in the application
    def create_command_list(self, nb):
        l = np.zeros( nb, dtype=int )
        for i in range(nb):
            l[i] = int(i)
        return l

    ##################
    def reset(self, n_commands, n_selection, s_zipfian, error_cost):
        self.n_commands = n_commands
        self.commands = self.create_command_list( self.n_commands )
        self.n_selection = n_selection
        self.s_zipfian = s_zipfian
        self.error_cost = error_cost
        self.cmd_seq = np.random.choice( self.commands, self.n_selection, p = zipfian( self.s_zipfian, len(self.commands) ))



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
    # run the model on n_episode
    def run(self, model, n_episode):
        print('\n========================= run simulation =====================')
        if model.env != self.env:
            print("error sim environment != model environment")
            exit(0)
        model.commands = self.env.commands        

        history = History( model.commands)
        model.reset_simulation()
        n_episode = 1

        #belief = None
        for i in range(n_episode):

            model.reset_episode()        
            belief = model.initial_belief()
            state = model.initial_state()
            
            for date in range( 0, len(self.env.cmd_seq) ):
                print(date, " ", self.env.cmd_seq[i])
                is_legal = False
                action = model.select_action(self.env.cmd_seq[date], date, belief, model.horizon, model.eps) #action correct
                res, is_legal = model.generate_step(self.env.cmd_seq[date], date, state, action)
                next_belief = belief
                history.update_history(res.cmd, res.state, res.next_state, res.action, res.time, res.success, belief.copy(), belief.copy() )
                state = res.next_state
                belief = next_belief
                print("=============")
            return history


if __name__=="__main__":
    app = QApplication(sys.argv)
    env = Environment(n_commands = 3, n_selection= 10, s_zipfian = 1, error_cost = 2)
    sim = Simulator(env)
    model = TransitionModel(env)
    window = Window(sim, model)
    window.show()
    history = sim.run(model, 1)
    window.simulatorUI.add_history( history )
    sys.exit(app.exec_())
