from alpha_beta_model_abstract import *
import math


################################################
#                                              #
#Implementation of the alpha/beta abstractclas #
#                                              #
################################################
class Alpha_Beta_Model(Alpha_Beta_Model_Abstract):

    ###########################
    def __init__( self, name ):
        super().__init__( name )
        self.min_time = 0.4
        
    # ###########################
    # def cleaned_time(self, strategy, time) :
    #     max_menu_time     = 5.3
    #     max_hotkey_time   = 5.3
    #     max_learning_time = 5.3
    #     if strategy == Strategy.MENU :
    #         return min(time, max_menu_time)
    #     if strategy == Strategy.HOTKEY :
    #         return min(time, max_hotkey_time)
    #     if strategy == Strategy.LEARNING :
    #         return min(time, max_learning_time)

    ###########################
    def update_model(self, step, _memory = None):
        memory = self.memory if _memory == None else _memory

        encoded_action = encode_cmd_s(step.cmd, step.action.strategy)
        
        #TODO, WHY DID YOU POLISH THE TIME?
        cleaned_time = step.time if step.time < self.max_time else self.max_time
        reward = 1. - math.log(1+ cleaned_time - self.min_time) / math.log(1+ self.max_time - self.min_time)

        for name in self.alpha.keys():
            alpha = self.alpha[ name ]
            mem_val = memory.value[ name ]
            if name == 'RW' :           # Rescorla Wagner
                #memory.value[ name ][ a ] += alpha * (reward -  memory.value[name][ a ] )
                mem_val[ encoded_action ] += alpha * (reward -  mem_val[ encoded_action ] )

            if name == "CK" :           # Choice Kernel
                #print("updaate CK")
                for s in self.available_strategies:
                    #a_ck = Action(step.cmd, s).to_string()
                    a_t_k = 1. if step.action.strategy == s else 0.
                    mem_val[ encode_cmd_s(step.cmd, s) ] +=  alpha * (a_t_k -  mem_val[ encode_cmd_s(step.cmd, s) ] )

        

        
                


