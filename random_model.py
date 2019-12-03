import random
from util import *
from model_interface import *
import copy


#####################################
#                                   #
#   Random MODEL                    #
#   Users select randomly an action #
#   If error, users perform the correct menu action and got temporal penality for that ("error cost")
###############################
class Random_Model(Model):

    def __init__(self, env):
        super().__init__("random", env)
        self.description = "In this model, we assume that participants do not engage with the task at all and simply choose methods at random, perhaps with a bias for one option over the other. Such random behavior is not uncommon in behavioral experiments, especially when participants have no external incentives for performing well"
        #self.params = Parameters('./parameters/random_model.csv')

    ##########################
    def select_action(self, cmd, date):
        actions = self.get_actions_from( cmd )

        #self.cmd_seq = np.random.choice( self.commands, self.value['n_selection'], p = zipfian( self.value['s_zipfian'] , len(self.commands) ))
        #return random.choice( actions )
        b = self.params.value['b']
        prob = [ b ]
        if len(actions) == 2:   # Menu and Hotkey actions
            prob.append( 1.-b )
        else:                   # Menu, Hotkey and Learning actions
            prob.append( (1.-b) /2.)
            prob.append( (1.-b) /2.)
        return np.random.choice( actions, 1, p=prob)[0]            

    ###########################
    def generate_step(self, cmd_id, date, state, action):
        result = StepResult()
        result.cmd = cmd_id
        result.state = state
        result.action = action.copy()
        result.success = (action.cmd == cmd_id)
        result.time = self.time(action, result.success)
        is_legal = True
        return result, is_legal


