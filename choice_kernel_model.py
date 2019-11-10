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
        self.memory = Choice_Kernel_Model.Memory(env)


    ##########################
    def select_action(self, cmd, date):
        actions = self.get_actions_from( cmd )
        CK_vec = []
        for a in actions: 
            CK_vec.append( self.memory.CK[ a.to_string() ] )
        print("---------: softmax", CK_vec)
        prob = soft_max( self.params.value['beta_c'], CK_vec)
        print("---------: prob 1", prob)
        
        prob = np.array(prob)
        print("---------: prob 2", prob)
        prob = prob / sum(prob)
        print("select_action, prob: ", cmd, CK_vec, prob )
        return np.random.choice( actions, 1, p=prob)[0]


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
    def generate_step(self, cmd_id, date, state, action):
        result = StepResult()
        result.cmd = cmd_id
        result.state = state
        result.action = action.copy()
        result.success = (action.cmd == cmd_id)  #always correct
        result.time = self.time(action, result.success)
        self.update_CK_values( result.action)
        is_legal = True
        return result, is_legal


    def reset(self):
        self.memory = Choice_Kernel_Model.Memory(self.env)
