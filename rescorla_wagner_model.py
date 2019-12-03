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
class Rescorla_Wagner_Model(Model):


    class Memory(Model):

        def __init__(self, env):
            self.q = dict()
            for cmd in env.commands:
                self.q[ Action(cmd, Strategy.MENU).to_string() ] = 0.5
                self.q[ Action(cmd, Strategy.HOTKEY).to_string() ] = 0.1
                self.q[ Action(cmd, Strategy.LEARNING).to_string() ] = 0.1



    def __init__(self, env):
        super().__init__("rescorla_wagner", env)
        self.memory = Rescorla_Wagner_Model.Memory(env)
        self.max_time = 2

        
    ##########################
    def select_action(self, cmd, date):
        actions = self.get_actions_from( cmd )
        q_vec = []
        for a in actions: 
            q_vec.append( self.memory.q[ a.to_string() ] )
        prob = soft_max( self.params.value['beta'], q_vec)
        prob = np.array(prob)
        prob = prob / sum(prob)
        return np.random.choice( actions, 1, p=prob)[0]


    ###########################
    def update_q_values(self, action, time):
        a = action.to_string()
        alpha = self.params.value['alpha']

        self.memory.q[ a ] = self.memory.q[ a ] + alpha * (self.max_time - time -  self.memory.q[ a ] )


    ###########################
    def generate_step(self, cmd_id, date, state, action):
        result = StepResult()
        result.cmd = cmd_id
        result.state = state
        result.action = action.copy()
        result.success = (action.cmd == cmd_id)  #always correct
        result.time = self.time(action, result.success)
        self.update_q_values( result.action, result.time )
        is_legal = True
        return result, is_legal


    def reset(self):
        self.memory = Rescorla_Wagner_Model.Memory(self.env)
