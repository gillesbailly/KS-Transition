import random
from util import *
from model_interface import *
import copy


#####################################
#                                   #
#    Random MODEL                   #
#   Users select randomly an action #
#   If error, users perform the correct menu action and got temporal penality for that ("error cost")
###############################
class Random_Model(Model):

    def __init__(self, env):
        super().__init__(env)
        self.params = Parameters('./parameters/random_model.csv')

    ##########################
    def select_action(self, cmd, date):
        actions = self.get_actions_from( cmd )
        return random.choice( actions )


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


