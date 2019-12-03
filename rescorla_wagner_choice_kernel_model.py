import random
from util import *
from model_interface import *
import copy



            


################################################
#                                              #
#   Rescorla Wagner CHOICE KERNEL MODEL        #
#                                              #
################################################
class Rescorla_Wagner_Choice_Kernel_Model(Model):

    
        
    class Memory(Model):

        def __init__(self, env):
            self.q = dict()     # q values related to performance
            self.CK = dict()    # CK related to habits

            for cmd in env.commands:
                self.q[ Action(cmd, Strategy.MENU).to_string() ] = 0.5
                self.q[ Action(cmd, Strategy.HOTKEY).to_string() ] = 0.1
                self.q[ Action(cmd, Strategy.LEARNING).to_string() ] = 0.1

                self.CK[ Action(cmd, Strategy.MENU).to_string() ] = 0
                self.CK[ Action(cmd, Strategy.HOTKEY).to_string() ] = 0
                self.CK[ Action(cmd, Strategy.LEARNING).to_string() ] = 0



    def __init__(self, env):
        super().__init__("rescorla_wagner_choice_kernel", env)
        self.memory = Rescorla_Wagner_Choice_Kernel_Model.Memory(env)
        self.max_time = 2


    ##########################
    def select_action(self, cmd, date):
        actions = self.get_actions_from( cmd )
        
        q_vec = []
        for a in actions: 
            q_vec.append( self.memory.q[ a.to_string() ] )

        CK_vec = []
        for a in actions: 
            CK_vec.append( self.memory.CK[ a.to_string() ] )

        prob = compound_soft_max( self.params.value['beta'], q_vec, self.params.value['beta_c'], CK_vec)
        prob = np.array(prob)
        prob = prob / sum(prob)
        return np.random.choice( actions, 1, p=prob)[0]


    ###########################
    def update_q_values(self, action, time):
        a = action.to_string()
        alpha = self.params.value['alpha']

        self.memory.q[ a ] = self.memory.q[ a ] + alpha * (self.max_time - time -  self.memory.q[ a ] )


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
        self.update_q_values( result.action, result.time )
        self.update_CK_values( result.action )
        is_legal = True
        return result, is_legal


    def reset(self):
        self.memory = Rescorla_Wagner_Choice_Kernel_Model.Memory(self.env)
