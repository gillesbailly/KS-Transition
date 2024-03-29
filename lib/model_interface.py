from util import *
from parameters import Parameter, Parameters
import copy




##########################################
#                                        #
#             Model Interface            #
#                                        #
##########################################
class Model(object):

    ######################################
    def __init__( self, name = 'model', variant_name = '' ):
        self.name   = name               # name of the model 
        self.variant_name = variant_name    # name of the variant 
        self.description  = 'Model description is empty'
        self.command_ids = []
        self.params = Parameters( self.long_name()  , self.default_parameters_path() )
        self.all_strategies = [Strategy.MENU, Strategy.HOTKEY, Strategy.LEARNING]
        self.available_strategies = [ Strategy.HOTKEY ]
        self.present_strategies = np.array([0,1,0])   # for optimisation
        self.max_time = 7.0

    def long_name( self ):
        return self.name if self.variant_name == '' else self.name + '_' + self.variant_name 

    ##########################################################################
    # return the proabability of the given action to be chosen               #
    # given the current command to select (state)                            #
    # Input:                                                                 #
    #    - cmd (int) : command to select (state)                             #
    #    - action (Action): action (only the action.strategy is considered   #
    # Output:                                                                #
    #    - prob (float): the probability to choose this action               #
    ########################################################################## 
    def action_prob( self, cmd, action ):
        prob = self.action_probs( cmd ) #[0.3,0.3,0.3] or [0, 0.5, 0.5]
        return prob[ action.strategy ]
        
    
    ##########################################################################
    # Update the internal variables of the model/agent                       #
    # Input:                                                                 #
    #    - step ( StepResult ):  necessary information to                    #
    #                            update the model (see util.py)              #
    ########################################################################## 
    def update_model(self, step_result):
            raise ValueError(" update_model: method to implement ")

    
 

    ##########################################################################
    # Reset the models: define the list of states, actions and reset         #
    #  the internal variables of the model                                   #
    # Input:                                                                 #
    #    - cmd_ids (array<int>) : lists of the ids of available commands     #
    #                        the agent can select (i.e. list of states)      #
    #    - strategies (array<Strategy> ): list of available strategies       #
    #                                     (action)                           #
    #                                                                        #
    ########################################################################## 
    def reset( self, cmd_ids,  strategies ):
    	raise ValueError(" model.reset(): method to implement ")
    

    ##########################################################################
    # Given a state and action, estimate the reward and return a stepResult  #
    # Input:                                                                 #
    #    - cmd id (int)   : the command to select (state)                    #
    #    - action (Action): pair <cmd, strategy>                             #
    # Output:                                                                #
    #   - stepResult (StepResult) containing state, action and reward        #
    ########################################################################## 
    def generate_step( self, cmd_id, action ):
        result = StepResult()
        result.cmd = cmd_id
        result.action = Action( action.cmd, action.strategy )
        result.success = self.success(action)
        result.time = self.time(action, result.success)
        return result

    ##########################################################################
    # Select an strategy given a state (cmd)                                 #
    # we select a strategy rather than an action <cmd, strategy>             #
    # to simplify the problem and performance                                #
    # Input:                                                                 #
    #    - cmd (int) : command to select (state)                             #
    #                                                                        #
    # Output: [action, probs]                                                #
    #    - strategy (Strategt): the chose strategy                           #
    #    - probs (array<float>): the probability for each strategy           #
    #                            to be selected.                             #
    #                           len( probs ) = len(self.available_strategies)#
    ########################################################################## 
    def select_strategy( self, cmd ):
        probs   = self.action_probs( cmd )
        return self.choice( self.all_strategies, probs ), probs


    ##########################################################################
    # return the proabability of each strategy (action) to be chosen         #
    # given the current command to select (state)                            #
    # Input:                                                                 #
    #    - cmd (int) : command to select (state)                             #
    #                                                                        #
    # Output:                                                                #
    #    - probs (array<float>): the probability for each strategy           #
    #                            to be selected.                             #
    #                           len( probs ) = len(self.available_strategies)#
    ########################################################################## 
    def action_probs(self, cmd ):
        raise ValueError(" method to implement")


  
    ###########################
    def strategy_time( self, strategy, success, default_strategy = Strategy.MENU ) :
        pass

    ###########################
    def success(self, action):
        return True


    ###########################
    def time(self, action, success):
        return self.strategy_time(action.strategy, success)

    ###########################
    def meta_info_1( self, cmd ):
        return 0

    ###########################
    def meta_info_2( self, cmd ):
        return 0

    ######################################
    def default_parameters_path( self ):
        return './parameters/' + self.long_name() + '_model.csv'

    # ###########################
    # def get_params( self ):
    #     return self.params

    ###########################
    def get_param_value_str( self ):
        return self.params.values_str()

    # ###########################
    # def set_params( self, params ):
    #     self.params = params

    # ###########################
    # def n_strategy( self ):
    #     return len( self.available_strategies )
    
    ###########################
    def set_available_strategies( self, strategies ):
        self.available_strategies = strategies.copy()
        self.present_strategies = np.zeros( 3, dtype=int )
        for s in self.available_strategies:
            #print(s, self.present_strategies )
            self.present_strategies[ s ] = 1
        self.default_strategy = self.default_strategy_long()
        #print("available_s:", self.available_strategies, 'present:', self.present_strategies, 'default:', self.default_strategy)

    # ###########################
    # def get_actions_from( self, cmd_id ):
    #     return [ Action( cmd_id , s) for s in self.available_strategies ]

    ##############################
    def choice( self, options, probs ):
        x = np.random.rand()
        cum = 0
        for i,p in enumerate( probs ):
            cum += p
            if x < cum:
                break
        return options[ i ]


    ##########################
    def default_strategy_long(self) :
        if not Strategy.MENU in self.available_strategies :
            return Strategy.LEARNING
        return Strategy.MENU
