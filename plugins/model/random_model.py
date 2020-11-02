from model_interface import *
import math



################################################
#                                              #
# Random Model                                 #
#                                              #
################################################
class Random_Model( Model ):


    ###############################
    def __init__( self, name = "random" ):
        super().__init__( name )
        self.command_ids = []
        
    ##########################
    def custom_reset_params(self) : 
        self.hotkey_prob    = self.params[ 'HOTKEY_PROB' ].value
        self.s_time         = [ self.params[ 'MENU_TIME' ].value, self.params[ 'HOTKEY_TIME' ].value, self.params[ 'MENU_TIME' ].value + self.params[ 'LEARNING_COST' ].value]
        self.error_cost     = self.params[ 'ERROR_COST' ].value
        
  
    ###########################
    # nothing to implement for this model
    def update_model(self, step, _memory = None):
        pass


    ##########################
    def action_probs(self, cmd, date=0 ):
        p = np.zeros( len( self.available_strategies ) )
        for i, strategy in enumerate( self.available_strategies):
            if strategy == Strategy.HOTKEY:
                p[i] = self.hotkey_prob
            else:
                p[i] = ( 1. - self.hotkey_prob ) / ( len(self.available_strategies) - 1 )
        return p



    ###########################
    def time(self, action, success):
        t = self.s_time[ action.strategy ]
        if success == False :
            t += self.s_time[ self.default_strategy() ] + self.error_cost 
        return t

    #########################
    def success(self,action):
        return True
            

    ###########################
    def meta_info_1( self, cmd ):
        return 0

    #########################
    def reset( self, command_ids, available_strategies ):
        self.custom_reset_params()
        self.command_ids = command_ids
        self.set_available_strategies( available_strategies )
            
        



        



