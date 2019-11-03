import sys
from transitionModel import *
from random_model import *
from simulationWidget import *
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
    # run the model on n_episode
    def run(self, model, n_episode):
        print('\n========================= run simulation =====================')
        print("model: ", model)
        sims = []

        for i in range(n_episode):
            history = History( self.env.commands )
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
    model = Random_Model(env)
    model_view = Model_View(model)
    window.add_model( "Random", model_view )

    model2 = TransitionModel(env)
    model_view2 = Model_View(model2)
    window.add_model( "Trans model", model_view2 )


    window.show()
    sims = simulator.run(model, 2)
    window.simulatorUI.add_sims( sims, "oki" )
    sys.exit(app.exec_())
