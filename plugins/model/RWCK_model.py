from model_interface import *
import numpy as np




################################################
#                                              #
#               RANDOM MODEL                   #
#                                              #
################################################
class RWCK_Model( Model ):


    ###############################
    def __init__( self, name = "RWCK" ):
        super().__init__( name )
        self.command_ids = []
        self.Q  = np.zeros( (0,0 ) )
        self.CK = np.zeros( (0,0 ) )
        
    ##########################
    def custom_reset_params(self) :
        self.ALPHA_CK       = self.params[ 'ALPHA_RW' ].value
        self.BETA_CK        = self.params[ 'BETA_RW' ].value
        self.ALPHA_RW       = self.params[ 'ALPHA_RW' ].value
        self.BETA_RW        = self.params[ 'BETA_RW' ].value
        self.s_time         = [ self.params[ 'MENU_TIME' ].value, self.params[ 'HOTKEY_TIME' ].value, self.params[ 'MENU_TIME' ].value + self.params[ 'LEARNING_COST' ].value]
        self.error_cost     = self.params[ 'ERROR_COST' ].value
        
  
    ##########################################################################
    # Update the internal variables of the model/agent                       #
    # Input:                                                                 #
    #    - stepResult (StepResult):                                          #
    #    - memory : ignore (used for code efficiency)                        #
    #                                                                        #
    ########################################################################## 
    def update_model(self, step, _memory = None):
        all_strategies = self.available_strategies
        strategy = step.action.strategy
        time     = step.time
        self.min_time = 0.4
        cleaned_time = step.time if step.time < self.max_time else self.max_time
        reward = 1. - math.log(1+ cleaned_time - self.min_time) / math.log(1+ self.max_time - self.min_time)
        cmd      = step.cmd
        
        # TODO 7
        self.Q[ cmd ] [ strategy] = self.Q[ cmd ][ strategy ] + self.ALPHA_RW * ( reward - self.Q[ cmd ][ strategy ] )
        for s in all_strategies: 
            b = 1 if s == strategy else 0
            self.CK[ cmd ][ s ] = self.CK[ cmd ][ s ] + self.ALPHA_CK * ( b - self.CK[ cmd ][ s ] ) 




    ##########################################################################
    # Select an strategy given a state (cmd)                                 #
    # we select a strategy rather than an action <cmd, strategy>             #
    # to simplify the problem and performance                                #
    # Input:                                                                 #
    #    - cmd (int) : command to select (state)                             #
    #                                                                        #
    # Output: [action, probs]                                                #
    #    - probs (array<float>): the probability for each strategy           #
    #                            to be selected.                             #
    #                           len( probs ) = len(self.available_strategies)#
    ########################################################################## 
    def action_probs( self, cmd ):
        return double_soft_max(self.BETA_CK, self.CK[ cmd ], self.BETA_RW, self.Q[ cmd ] )



    ##########################################################################
    # Estimate the time to perform the action action in case or success      #
    # or error                                                               #
    # Input:                                                                 #
    #   - action (Action)    : the action to perform                         #
    #   - success (boolearn) : whether the agent executed the right command  #
    # Output:                                                                #
    #   - time (float)                                                       #
    ##########################################################################
    def time( self, action, success ):
        t = self.s_time[ action.strategy ]
        if success == False :
            t += self.s_time[ self.default_strategy() ] + self.error_cost 
        return t

    ##########################################################################
    # return whether the user sucessfully perform this action                #
    # (TODO GB)                                                              #
    # Input:                                                                 #
    #   - action (Action)    : the action to perform                         #
    # Output:                                                                #
    #   - success (boolean) : 1: success, 0: error                           #
    ##########################################################################
    def success( self, action ):
        return True
            

    ##########################################################################
    # method used for debug. return the value of one variable of our model   #
    # Input:                                                                 #
    #   - cmd (int)    : the command (state) to execute                      #
    # Output:                                                                #
    #   - v: (float)   : a value of your model between 0 and 1               #
    ##########################################################################
    def meta_info_1( self, cmd ):
        return 0


    ##########################################################################
    # Reset the models: define the list of states, actions and reset         #
    #  the internal variables of the model                                   #
    # Input:                                                                 #
    #    - cmd_ids (array<int>) : lists of the ids of available commands     #
    #                        the agent can select (i.e. list of states)      #
    #    - strategies (array<Strategy> ): list of available strategies       #
    #                                     (action)                           #
    ########################################################################## 
    def reset( self, command_ids, available_strategies ):
        self.custom_reset_params()
        self.command_ids = command_ids
        self.set_available_strategies( available_strategies )
        
        self.Q = np.zeros( ( len(command_ids), len(self.available_strategies) ) )
        self.CK = np.zeros( ( len(command_ids), len(self.available_strategies) ) )
        
        
            
        



        



