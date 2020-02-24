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
                self.value[name] = dict()
                
            self.hotkey_knowledge = dict()
            for cmd in env.commands:
                self.hotkey_knowledge[cmd] = 0.0


        def set_initial_value(self, env, name, value_0):
            for cmd in env.commands:
                for s in value_0.keys() :
                    self.value[name][ Action(cmd, s).to_string() ] = value_0[s]
                    #print("CK: ", cmd, s, value_0[s])

    # e.g. value_names = ['RW', 'CK', 'G']
    # e.g. initial_value_default_method = {'RW': 0.5; 'CK': 1; 'G':0} 
    def __init__(self, env, value_names, initial_value):
        tmp_name = '_'.join(value_names)
        super().__init__(tmp_name, env)
        self.description = "alpha_beta_model"
        self.memory = None
        self.value_names = copy.copy(value_names)
        self.initial_value_default_method = dict( zip(value_names,initial_value) )
        self.alpha = np.empty( len(self.value_names) )
        self.beta = np.empty( len(self.value_names) )
        self.reset(self.available_strategies)


    ##########################
    def build_alpha_beta_dicts(self):
        for key in self.params.value.keys():
            key_vec = key.split('_')
            #print(key_vec)
            if "alpha" in key_vec[0] :
                index = self.value_names.index( key_vec[1] )
                self.alpha[ index ] = self.params.value[ key ]
            if "beta" in key_vec[0] :
                index = self.value_names.index( key_vec[1] )
                self.beta[ index ] = self.params.value[ key ]

    ##########################
    def alpha_from_name(self, name):
        return self.alpha[ self.value_names.index(name) ]

    ##########################
    def beta_from_name(self, name):
        return self.beta[ self.value_names.index(name) ]


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
        l = len(self.value_names)
        value_vec = np.empty( l, dtype=object )

        for i in range(0, l):
            value_vec[i] = self.values(self.value_names[i], cmd, date)
        #print("action_probs: ", value_vec, self.beta)
        return extended_soft_max( self.beta, value_vec )


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
        raise ValueError(" update_values: method to implement ")
        #self.update_values( step.action, step.time, step.error )


    ##########################
    def value_0(self, available_strategies, name):
        value_0 = dict()
        v0_name = 'v0_' + name
        v0 = self.params.value[v0_name] if v0_name in self.params.value else self.initial_value_default_method[name]
        default_strategy = Strategy.MENU
        if not (default_strategy in self.available_strategies):
            default_strategy = Strategy.LEARNING
            if not (default_strategy in self.available_strategies):
                default_strategy = Strategy.HOTKEY
            
        for s in self.available_strategies:
            value_0[ s ] = v0 if s == default_strategy else 0
            #print("value 0: ", s, value_0[ s ], self.available_strategies)
        return value_0


    #########################
    def reset(self, available_strategies):
        #print(" reset abstract: ", available_strategies)
        self.set_available_strategies( available_strategies )
        self.build_alpha_beta_dicts()       
        self.memory = Alpha_Beta_Model_Abstract.Memory(self.env, self.value_names)
        for name in self.value_names :
            self.memory.set_initial_value( self.env, name, self.value_0(available_strategies, name) )

