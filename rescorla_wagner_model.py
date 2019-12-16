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
        self.description = "In this model, participants first learn the expected value of each method based on the history of previous outcomes and then use these values to make a decision about what to do next. A simple model of learning is the Rescorla-Wagner learning rule (Rescorla et al., 1972) whereby the value of option k, Q_t^k is updated in response to reward rt according to: \n \n Q_{t+1}^k = Q_t^k + alpha(r_t - Q_t^k) \n \n where alpha is the learning rate, which takes a value between 0 and 1 and captures the extent to which the prediction error, (r_t − Q_t^k ), updates the value. A simple model of decision making is to assume that participants use the options values to guide their decisions, choosing the most valuable option most frequently, but occasionally making mistakes (or exploring) by choosing a low value option. One choice rule with these properties is known as the softmax choice rule."
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
        return np.random.choice( actions, 1, p=prob)[0], prob


    ###########################
    def update_q_values(self, action, time):
        a = action.to_string()
        alpha = self.params.value['alpha']

        self.memory.q[ a ] = self.memory.q[ a ] + alpha * (self.max_time - time -  self.memory.q[ a ] )


    ###########################
    def generate_step(self, cmd_id, date, action):
        result = StepResult()
        result.cmd = cmd_id
        result.action = action.copy()
        result.success = (action.cmd == cmd_id)  #always correct
        result.time = self.time(action, result.success)   
        return result

    def update_model(self, step):
        self.update_q_values( step.action, step.time )


    def reset(self):
        self.memory = Rescorla_Wagner_Model.Memory(self.env)
