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

        def __init__(self, env, CK_0 ):
            self.CK = dict()
            for cmd in env.commands:
                for s in CK_0.keys() :
                    self.CK[ Action(cmd, s).to_string() ] = CK_0[s]


    def __init__(self, env):
        super().__init__("choice_kernel", env)
        self.description = "This model tries to capture the tendency for people to repeat their previous actions. In particular, we assume that participants compute a ‘choice kernel,’ CK_t^k, for each action, which keeps track of how frequently they have chosen that option in the recent past."
        self.memory = None
        #Choice_Kernel_Model.Memory(env, self.available_strategies)
        self.reset(self.available_strategies)

    ##########################
    def CK_values(self, cmd):
        action_vec = self.get_actions_from(cmd)
        CK_vec = np.empty( len(action_vec) )
        for i in range( 0, len(action_vec) ) :
            s = action_vec[i].to_string()
            CK_vec[i] = self.memory.CK[ s ]
        return CK_vec


    ##########################
    def action_probs(self, cmd, date):
        CK_vec = self.CK_values(cmd)
        return soft_max( self.params.value['beta_c'], CK_vec)


    ###########################
    def update_CK_values(self, action):
        alpha = self.params.value['alpha_c']
        for s in self.available_strategies:
            a = Action(action.cmd, s).to_string()
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


    ##########################
    def CK_0(self, available_strategies):
        CK_0 = dict()
        default_strategy = Strategy.MENU
        if not (default_strategy in self.available_strategies):
            default_strategy = Strategy.LEARNING
            if not (default_strategy in self.available_strategies):
                default_strategy = Strategy.HOTKEY
            
        for s in self.available_strategies:
            CK_0[ s ] = 1 if s == default_strategy else 0
        return CK_0

    ##########################
    def reset(self, available_strategies):
        self.set_available_strategies( available_strategies )
        self.memory = Choice_Kernel_Model.Memory(self.env, self.CK_0( self.available_strategies) )
