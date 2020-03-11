import random
from util import *
from model_interface import *
import copy



            


################################################
#                                              #
#   Abstract class Alpha/Beta Models           #
#                                              #
################################################
class Alpha_Beta_Model_Abstract(Model):

        
    class Memory(Model):
        
        def __init__(self, env, value_names):            
            self.value = dict()
            for name in value_names:
                self.value[ name ] = dict()
            
            self.hotkey_knowledge = dict()
            for cmd in env.commands:
                self.hotkey_knowledge[ cmd ] = 0.0


        def set_initial_value(self, env, name, value_0):
            for cmd in env.commands:
                for s in value_0.keys() :
                    self.value[name][ Action(cmd, s).to_string() ] = value_0[s]
                    #print("CK: ", cmd, s, value_0[s])

    # e.g. value_names = ['RW', 'CK', 'G']
    # e.g. initial_value_default_method = {'RW': 0.5; 'CK': 1; 'G':0} 
    def __init__(self, env, name):
        super().__init__(name, env)
        self.description = "alpha_beta_model"
        self.memory = None
        self.v0 = dict()
        self.alpha = dict()
        self.beta = dict()
        self.reset(self.available_strategies)


    ##########################
    def has_RW_values(self) :
        return 'RW' in self.alpha.keys()

    def has_CK_values(self) :
        return 'CK' in self.alpha.keys()

    def has_CTRL_values(self) :
        return 'CTRL' in self.alpha.keys()


    ##########################
    def build_alpha_beta_dicts(self):
        for key in self.params.value.keys():
            key_vec = key.split('_')
            print(key_vec)
            if 'ALPHA' in key_vec[0] :
                self.alpha[ key_vec[1] ] = self.params.value[ key ]
            if 'BETA' in key_vec[0] :
                self.beta[ key_vec[1] ]  = self.params.value[ key ]
            if 'V0' in key_vec[0] :
                self.v0[ key_vec[1] ]    = self.params.value[ key ]


    # ##########################
    # def alpha_from_name(self, name):
    #     return self.alpha[ self.value_names.index(name) ]

    # ##########################
    # def beta_from_name(self, name):
    #     return self.beta[ self.value_names.index(name) ]


    ##########################
    def values(self, value_name, cmd, date):
        action_vec = self.get_actions_from( cmd )
        value_vec = np.empty( len(action_vec) )
        for i in range( 0, len(action_vec) ):
            s = action_vec[i].to_string()
            value_vec[i] = self.memory.value[ value_name ][ s ]

        return value_vec


    ##########################
    def action_probs(self, cmd, date):
        keys = self.beta.keys()
        value_vec = np.empty( len(keys) , dtype=object )
        beta_vec  = np.empty( len(keys), dtype=object)

        for i, key in enumerate(self.beta) :
            value_vec[i] = self.values(key, cmd, date)
            beta_vec[i] = self.beta[ key ]
        return extended_soft_max( beta_vec, value_vec )


    ###########################
    def generate_step(self, cmd_id, date, action):
        result = StepResult()
        result.cmd = cmd_id
        result.action = action.copy()
        result.success = self.success(action) 
        result.time = self.time(action, result.success)
        return result


    ##########################
    def update_model(self, step, _memory = 0):
        raise ValueError(" update_values: method to implement ")
        #self.update_values( step.action, step.time, step.error )


    ##########################
    def value_0(self, available_strategies, name):
        value_0 = dict()
        #v0_name = 'v0_' + name
        #v0 = self.params.value[v0_name] if v0_name in self.params.value else self.initial_value_default_method[name]
        default_strategy = Strategy.MENU
        if not (default_strategy in self.available_strategies):
            default_strategy = Strategy.LEARNING
            if not (default_strategy in self.available_strategies):
                default_strategy = Strategy.HOTKEY
            
        for s in self.available_strategies:
            value_0[ s ] = self.v0[ name ] if s == default_strategy else 0
            #print("value 0: ", s, value_0[ s ], self.available_strategies)
        return value_0

    #########################
    def custom_reset_memory(self):
        pass 

    #########################
    def reset(self, available_strategies):
        #print(" reset abstract: ", available_strategies)
        self.set_available_strategies( available_strategies )
        self.build_alpha_beta_dicts()
        value_names = self.alpha.keys()    
        self.memory = Alpha_Beta_Model_Abstract.Memory(self.env, value_names )
        for name in value_names :
            self.memory.set_initial_value( self.env, name, self.value_0(available_strategies, name) )
        self.custom_reset_memory()

