import random
from util import *
from model_interface import *
import copy




# def decode_cmd_s( self, id) :
#     cmd = int( id / 3)
#     s = id - 3* cmd
#     return cmd, s

        


################################################
#                                              #
#   Abstract class Alpha/Beta Models           #
#                                              #
################################################
class Alpha_Beta_Model_Abstract(Model):

    
    #class SmallMemory()

    class Memory():
        
        ###############################
        def __init__(self, command_ids, value_names):            
            self.value = dict()
            for name in value_names:
                self.value[ name ] = np.zeros(3 * len( command_ids ) )
            self.hotkey_knowledge = np.zeros( len( command_ids ) ) #TOOD ???


        #############################
        def set_initial_value(self, command_ids , name, value_0):
            for cmd in command_ids :
                for s in value_0.keys() :
                    self.value[ name ] [ encode_cmd_s(cmd, s) ] = value_0[s]
                    

    # e.g. value_names = ['RW', 'CK', 'G']
    # e.g. initial_value_default_method = {'RW': 0.5; 'CK': 1; 'G':0} 
    def __init__( self, name ):
        super().__init__( name )
        self.description = "alpha_beta_model"
        self.memory = None
        self.v0 = dict()
        self.alpha = dict()
        self.beta = dict()


    ##########################
    # def has_RW_values(self) :
    #     return 'RW' in self.alpha.keys()

    # def has_CK_values(self) :
    #     return 'CK' in self.alpha.keys()

    # def has_CTRL_values(self) :
    #     return 'CTRL' in self.alpha.keys()


    ##########################
    def build_alpha_beta_dicts(self):
        for key in self.params: 
            key_vec = key.split('_')
            if 'ALPHA' in key_vec[ 0 ] :
                self.alpha[ key_vec[ 1 ] ] = self.params[key].value
            if 'BETA' in key_vec[ 0 ] :
                self.beta[ key_vec[ 1 ] ]  = self.params[key].value
            if 'V0' in key_vec[ 0 ] :
                self.v0[ key_vec[ 1 ] ]    = self.params[key].value

    ##########################
    def values(self, value_name, cmd, date):
        #print("values: ", self.available_strategies )
        mem_value = self.memory.value[value_name]
        value_vec = np.zeros( len(self.available_strategies) )
        for i, s in enumerate( self.available_strategies ):
            value_vec[ i ] = mem_value[ encode_cmd_s( cmd, s ) ]
        return value_vec


    ##########################
    def action_probs(self, cmd, date = 0):
        keys = self.beta.keys()
        value_vec = np.empty( len(keys) , dtype=object )
        beta_vec  = np.empty( len(keys), dtype=object)

        for i, key in enumerate(self.beta) :
            value_vec[i] = self.values(key, cmd, date)
            beta_vec[i] = self.beta[ key ]
        return extended_soft_max( beta_vec, value_vec )



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
        if not ( default_strategy in self.available_strategies ):
            default_strategy = Strategy.LEARNING
            if not ( default_strategy in self.available_strategies ):
                default_strategy = Strategy.HOTKEY
            
        for s in self.available_strategies:
            value_0[ s ] = 0
            if ( s == default_strategy ) and ( name in self.v0 ) :
                value_0[ s ] = self.v0[ name ]
        return value_0

    #########################
    def custom_reset_memory(self, available_strategies):
        pass 
    
    #########################
    def custom_reset_params(self) :
        self.s_time         = [ self.params[ 'MENU_TIME' ].value, self.params[ 'HOTKEY_TIME' ].value, self.params[ 'MENU_TIME' ].value + self.params[ 'LEARNING_COST' ].value]
        self.error_cost     = self.params[ 'ERROR_COST' ].value
        
    ###########################
    def time(self, action, success):
        t = self.s_time[ action.strategy ]
        if success == False :
            t += self.s_time[ self.default_strategy() ] + self.error_cost 
        return t

    #########################
    def reset(self, command_ids, available_strategies):
        #print(" reset abstract: ", available_strategies)
        self.custom_reset_params()
        self.set_available_strategies( available_strategies )
        self.build_alpha_beta_dicts()
        value_names = self.alpha.keys()
        
        self.memory = Alpha_Beta_Model_Abstract.Memory( command_ids , value_names )
        for name in value_names :
            self.memory.set_initial_value( command_ids, name, self.value_0( available_strategies, name ) )
        self.custom_reset_memory(available_strategies)

