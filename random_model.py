import random
from util import *
from model_interface import *
import copy


#####################################
#                                    #
#    Random MODEL                    #
#   Users select randomly an action #
#   If error, users perform the correct menu action and got temporal penality for that ("learning cost")
###############################
class Random_Model(Model):

    def __init__(self, env):
        super().__init__(env)
        self.params['n_strategy'] = 3                    # if == 2 actions {Menu; Hotkey}; == 3 actions: {Menu; Hotkey; Learning}
        self.params['menu_time'] = 1                    # menu selection time (seconds)
        self.params['hotkey_time'] = 0.5                    # hotkey selection time (seconds)
        self.params['learning_cost'] = 0.5                # additional temporal cost when learning keyboard shortcuts in the menu 


    ##########################
    def select_action(self, cmd, date):
        actions = self.get_all_actions()
        return random.choice( actions )


    ###########################
    def time(self, action, success):
        s = action.strategy
        t = 0
        if s == Strategy.MENU:
            t = self.params['menu_time']
        elif s == Strategy.LEARNING:
            t = self.params['menu_time'] + self.params['learning_cost']
        elif s == Strategy.HOTKEY:
            t = self.params['hotkey_time']

        if success == False:
            t += self.params['menu_time'] + self.env.error_cost
        return t

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


