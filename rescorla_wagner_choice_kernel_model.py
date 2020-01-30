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

                self.CK[ Action(cmd, Strategy.MENU).to_string() ] = 1
                self.CK[ Action(cmd, Strategy.HOTKEY).to_string() ] = 0
                self.CK[ Action(cmd, Strategy.LEARNING).to_string() ] = 0



    def __init__(self, env):
        super().__init__("rescorla_wagner_choice_kernel", env)
        self.description = "This model mixes the reinforcement learning model with the choice kernel model: The values update according to the reward (alpha, beta), while capturing the tendency for people to repeat their previous actions."
        self.memory = Rescorla_Wagner_Choice_Kernel_Model.Memory(env)
        self.max_time = 7


    ##########################
    def q_values(self, cmd, date):
        action_vec = self.get_actions_from( cmd )
        q_vec = np.empty( len(action_vec) )
        for i in range( 0, len(action_vec) ):
            s = action_vec[i].to_string()
            q_vec[i] = self.memory.q[ s ]
        #for a in actions: 
        #    q_vec.append( self.memory.q[ a.to_string() ] )
        return q_vec


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
        q_vec = self.q_values( cmd, date )
        CK_vec = self.CK_values(cmd)
        return compound_soft_max( self.params.value['beta'], q_vec, self.params.value['beta_c'], CK_vec)
        

    ###########################
    def update_q_values(self, action, time):
        a = action.to_string()
        alpha = self.params.value['alpha']
        cleaned_time = time if time <6.5 else 6.5
        self.memory.q[ a ] = self.memory.q[ a ] + alpha * (self.max_time - cleaned_time -  self.memory.q[ a ] )


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
        self.update_q_values( step.action, step.time )
        self.update_CK_values( step.action )


    def reset(self):
        self.memory = Rescorla_Wagner_Choice_Kernel_Model.Memory(self.env)
