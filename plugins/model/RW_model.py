from model_interface import *
import numpy as np




################################################
#                                              #
#               RANDOM MODEL                   #
#                                              #
################################################
class RW_Model( Model ):


    ###############################
    def __init__( self, variant_name = '' ):
        super().__init__( 'RW', variant_name )
        self.Q = np.zeros( (0,0 ) )
        
    ##########################
    def custom_reset_params(self) :
        self.ALPHA_RW   = self.params[ 'ALPHA_RW' ].value
        self.BETA_RW    = self.params[ 'BETA_RW' ].value
        self.s_time     = [ self.params[ 'MENU_TIME' ].value, self.params[ 'HOTKEY_TIME' ].value, self.params[ 'MENU_TIME' ].value + self.params[ 'LEARNING_COST' ].value]
        self.error_cost = self.params[ 'ERROR_COST' ].value
        
  
    ##########################################################################
    # Update the internal variables of the model/agent                       #
    # Input:                                                                 #
    #    - stepResult (StepResult):                                          #
    #    - memory : ignore (used for code efficiency)                        #
    #                                                                        #
    ########################################################################## 
    def update_model(self, step, _memory = None):
        strategy = step.action.strategy
        cmd      = step.cmd
        time     = step.time
        cleaned_time = time if time < self.max_time else self.max_time
        reward = self.max_time - cleaned_time 
        self.Q[ cmd ] [ strategy ] = self.Q[ cmd ][ strategy ] + self.ALPHA_RW * ( reward - self.Q[ cmd ][ strategy ] )
        # if cmd==0 :
        #     print( 'time', time, 'reward', reward, 'Q', self.Q[ 0 ] )

    

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
        # if cmd == 0 :
        #     print( self.BETA_RW, self.Q[ cmd ], self.present_strategies)
        return soft_max3( self.BETA_RW, self.Q[ cmd ], self.present_strategies ) #see util.py



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
        self.Q = np.zeros( ( len(command_ids), 3 ) )
        
            
        



        



