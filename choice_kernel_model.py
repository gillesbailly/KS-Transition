import random
from util import *
from model_interface import *
import copy



            


#####################################
#                                   #
#   CHOICE KERNEL MODEL             #
#                                   #
#####################################
class Choice_Kernel_Model(Model):

    
        
    class Memory(Model):

        def __init__(self, env):
            self.CK = dict()
            for cmd in env.commands:
                self.CK[ Action(cmd, Strategy.MENU).to_string() ] = 0
                self.CK[ Action(cmd, Strategy.HOTKEY).to_string() ] = 0
                self.CK[ Action(cmd, Strategy.LEARNING).to_string() ] = 0



    def __init__(self, env):
        super().__init__("choice_kernel", env)
        self.description = "This model tries to capture the tendency for people to repeat their previous actions. In particular, we assume that participants compute a ‘choice kernel,’ CK_t^k, for each action, which keeps track of how frequently they have chosen that option in the recent past."
        self.memory = Choice_Kernel_Model.Memory(env)


    ##########################
    def action_probs(self, cmd, date):
        actions = self.get_actions_from( cmd )
        CK_vec = []
        for a in actions: 
            CK_vec.append( self.memory.CK[ a.to_string() ] )
        prob = soft_max( self.params.value['beta_c'], CK_vec)
        prob = np.array(prob)
        prob = prob / sum(prob)
        return prob


    ###########################
    def update_CK_values(self, action):
        alpha = self.params.value['alpha_c']
        strategies = [Strategy.MENU, Strategy.HOTKEY, Strategy.LEARNING]
        cmd = action.cmd
        for s in strategies:
            a = Action(cmd, s).to_string()
            a_t_k = 1 if action.strategy == s else 0
            self.memory.CK[ a ] = self.memory.CK[ a ] + alpha * (a_t_k -  self.memory.CK[ a ] )
         

    ###########################
    def generate_step(self, cmd_id, date, action):
        result = StepResult()
        result.cmd = cmd_id
        result.action = action.copy()
        result.success = (action.cmd == cmd_id)  #always correct
        result.time = self.time(action, result.success)
        return result


    ##########################
    def update_model(self, step):
        self.update_CK_values( step.action)


    def reset(self):
        self.memory = Choice_Kernel_Model.Memory(self.env)
