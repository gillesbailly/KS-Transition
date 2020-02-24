import random
from util import *
from model_interface import *
import copy



            


###############################
#                             #
#   Rescorla Wagner MODEL     #
#   alpha and beta.           #
###############################
class Rescorla_Wagner_Model(Model):


    class Memory(Model):

        def __init__(self, env, q_0):
            self.q = dict()
            for cmd in env.commands:
                for s in q_0.keys() :
                    self.q[ Action(cmd, s).to_string() ] = q_0[s]


    def __init__(self, env, q0_as_parameter = False):
        tmp_name = "rescorla_wagner_q0" if q0_as_parameter else "rescorla_wagner"
        super().__init__(tmp_name, env)
        self.description = "In this model, participants first learn the expected value of each method based on the history of previous outcomes and then use these values to make a decision about what to do next. A simple model of learning is the Rescorla-Wagner learning rule (Rescorla et al., 1972) whereby the value of option k, Q_t^k is updated in response to reward rt according to: \n \n Q_{t+1}^k = Q_t^k + alpha(r_t - Q_t^k) \n \n where alpha is the learning rate, which takes a value between 0 and 1 and captures the extent to which the prediction error, (r_t − Q_t^k ), updates the value. A simple model of decision making is to assume that participants use the options values to guide their decisions, choosing the most valuable option most frequently, but occasionally making mistakes (or exploring) by choosing a low value option. One choice rule with these properties is known as the softmax choice rule."
        self.description += "Generally, all qvalues are initialized to 0. However, in the context of command selection, the initial q_value of the default method is higher and equal to 0.3. The extended version of this model includes the parameter q0 (initial qValue of the default method) which indicates the propension of the user to favor the default method"
        self.memory = None
        self.initial_q_value_default_method = 0.3
        self.reset(self.available_strategies)

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
    def action_probs(self, cmd, date):
        q_vec = self.q_values( cmd, date )
        return soft_max( self.params.value['beta'], q_vec)
        

    ###########################
    def has_q_values(self):
        return True
    


    ###########################
    def update_q_values(self, action, time):
        a = action.to_string()
        alpha = self.params.value['alpha']
        cleaned_time = time if time < self.max_time else self.max_time
        reward = 1. - cleaned_time / self.max_time
        self.memory.q[ a ] = self.memory.q[ a ] + alpha * (reward -  self.memory.q[ a ] )

        # if action.cmd == 0:
        #     q_menu = self.memory.q[ Action(0, Strategy.MENU).to_string() ]
        #     q_hotkey = self.memory.q[ Action(0, Strategy.HOTKEY).to_string() ]
        #     q_learning = self.memory.q[ Action(0, Strategy.LEARNING).to_string() ]

        #     print(self.max_time, time, "[", q_menu, q_hotkey, q_learning, "]")



    ###########################
    def generate_step(self, cmd_id, date, action):
        result = StepResult()
        result.cmd = cmd_id
        result.action = action.copy()
        result.success = (action.cmd == cmd_id)  #always correct
        result.time = self.time(action, result.success)   
        return result

    ##########################
    def q_0(self, available_strategies):
        q_0 = dict()
        q0_value = self.params.value['q0'] if 'q0' in self.params.value else self.initial_q_value_default_method
        default_strategy = Strategy.MENU
        if not (default_strategy in self.available_strategies):
            default_strategy = Strategy.LEARNING
            if not (default_strategy in self.available_strategies):
                default_strategy = Strategy.HOTKEY
            
        for s in self.available_strategies:
            q_0[ s ] = q0_value if s == default_strategy else 0
        return q_0


    ##########################
    def update_model(self, step):
        self.update_q_values( Action(step.cmd, step.action.strategy) , step.time )


    ##########################
    def reset(self, available_strategies):
        self.set_available_strategies( available_strategies )
        self.memory = Rescorla_Wagner_Model.Memory(self.env, self.q_0( self.available_strategies) )
