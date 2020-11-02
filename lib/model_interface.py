from util import *
import copy
import csv

class Parameter( object ):

    ##############################
    def __init__( self, _name="", _value=0, _min = 0, _max = 0, _step = 0,  _freedom = Freedom.USER_FREE, _comment = "" ):
        self.name  = _name
        self.value = _value
        self.min   = _min
        self.max   = _max
        self.step  = _step
        self.freedom  = _freedom
        self.comment = _comment

##########################################
#                                        #
#             Parameters                 #
#                                        #
##########################################
class Parameters(dict):

    ###############################
    def __init__( self, name, path ):
        self.load(path)
        self.name = name

    #######################
    def load(self, path):
        if not path:
            return
        with open(path, 'r') as csvFile:
            reader = csv.reader(csvFile, delimiter= ';')
            header = True
            for row in reader:
                if not header:
                    parameter = Parameter()
                    parameter.name    = row[ 0 ]
                    parameter.value   = float( row[1] ) if '.' in row[1] else int( row[1] )
                    parameter.min     = float( row[2] ) if '.' in row[2] else int( row[2] )
                    parameter.max     = float( row[3] ) if '.' in row[3] else int( row[3] )
                    parameter.step    = float( row[4] ) if '.' in row[4] else int( row[4] )
                    parameter.freedom = int( row[5] )
                    parameter.comment = row[ 6 ]
                    self[ parameter.name ] = parameter
                else:
                    header = False
    #########################
    def n( self, freedom_type = Freedom.USER_FREE ):
        res = 0
        for parameter in self.values():
            if parameter.freedom == freedom_type:
                res += 1
        return res


    #########################
    def values_str( self ):
        res = ''
        first = True
        for key, param in self.items():
            if first:
                first = False
            else:
                res += ','
            res += key + ':' + str( param.value )
        return res




##########################################
#                                        #
#             Model Interface            #
#                                        #
##########################################
class Model(object):

    ######################################
    def __init__( self, name ):
        self.name = name
        self.description = 'Model description is empty'
        #path = './parameters/'
        #ext = '_model.csv'
        self.params = Parameters( name, self.default_parameters_path() )
        self.available_strategies = [ Strategy.HOTKEY ]
        self.max_time = 7.0




    ##########################################################################
    # Reset the models: define the list of states, actions and reset         #
    #  the internal variables of the model                                   #
    # Input:                                                                 #
    #    - cmd_ids (array<int>) : lists of the ids of available commands     #
    #                        the agent can select (i.e. list of states)      #
    #    - strategies (array<Strategy> ): list of available strategies       #
    #                                     (action)                           #
    # Output: stepResult (StepResult) containing state, action and reward    #
    ########################################################################## 
    def reset( self, cmd_ids,  strategies ):
    	raise ValueError(" model.reset(): method to implement ")
    

    ##########################################################################
    # Given a state and action, estimate the reward and return a stepResult  #
    # Input:                                                                 #
    #    - cmd id (int)   : the command to select (state)                    #
    #    - action (Action): pair <cmd, strategy>                             #
    # Output: stepResult (StepResult) containing state, action and reward    #
    # The reward is                                                          #
    #    - sucess (True/False) : The command is correctly selected)          #
    #    - time (float)        : Execution Time)                             #
    ########################################################################## 
    def generate_step(self, cmd_id, action, date = 0):
        result = StepResult()
        result.cmd = cmd_id
        result.action = Action( action.cmd, action.strategy )
        result.success = self.success(action)
        result.time = self.time(action, result.success)
        return result

    
    ##########################################################################
    # Update the internal variables of the model/agent                       #
    # Input:                                                                 #
    #    - stepResult (StepResult):                             #
    #    - action : pair <cmd, strategy>                                     #
    # Output: stepResult containing state, action and reward                 #
    # The reward is                                                          #
    #    - sucess (does the command is correctly selected)                   #
    #    - time (execution Time)                                             #
    ########################################################################## 
    def update_model(self, step_result):
            raise ValueError(" update_model: method to implement ")

    
 
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
    def select_strategy( self, cmd, date =0):
        probs   = self.action_probs( cmd, date )
        return self.choice( self.available_strategies, probs ), probs


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
    def action_probs(self, cmd, date = 0 ):
        raise ValueError(" method to implement")



    ##########################################################################
    # return the proabability of the given action to be chosen               #
    # given the current command to select (state)                            #
    # Input:                                                                 #
    #    - cmd (int) : command to select (state)                             #
    #    - action (Action): action (only the action.strategy is considered   #
    # Output:                                                                #
    #    - prob (float): the probability to choose this action               #
    ########################################################################## 
    def action_prob( self, cmd, action, date=0 ):
        action_vec = self.get_actions_from( cmd )
        prob = self.action_probs( cmd )
        for i in range(0, len(action_vec)):
            action_res = action_vec[i]
            if action_res.cmd == action.cmd and action_res.strategy == action.strategy:
                return prob[i]
        raise ValueError("The action has not been found....", action, action_vec)
        return -1

  
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
        return './parameters/' + self.name + '_model.csv'

    ###########################
    def get_params( self ):
        return self.params

    ###########################
    def get_param_value_str( self ):
        return self.params.values_str()

    ###########################
    def set_params( self, params ):
        self.params = params

    ###########################
    def n_strategy( self ):
        return len( self.available_strategies )
    
    ###########################
    def set_available_strategies( self, strategies ):
        self.available_strategies = strategies.copy()

    ###########################
    def get_actions_from( self, cmd_id ):
        return [ Action( cmd_id , s) for s in self.available_strategies ]

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
    def default_strategy(self) :
        if not Strategy.MENU in self.available_strategies :
            return Strategy.LEARNING
        return Strategy.MENU

    # def select_action( self, cmd, date=0 ):
    #     actions = self.get_actions_from( cmd )
    #     probs   = self.action_probs( cmd, date )
    #     return self.choice( actions, probs ), probs   
