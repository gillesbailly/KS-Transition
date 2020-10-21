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


    ######################################
    def default_parameters_path( self ):
        return './parameters/' + self.name + '_model.csv'

    ######################################
    def reset( self, command_ids,  available_strategies ):
    	raise ValueError(" model.reset(): method to implement ")
    
    ######################################
    # def count_BIC_params( self ) : #TODO REMOVE FROM HERE
    #     count = 0
    #     for name in self.params.range.keys() :
    #         if self.params.range[name][0] < self.params.range[name][1] : # min != max
    #             count += 1
    #     return count

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
    # def get_all_actions( self ):
    #     return env.action_list

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
    # should return an action and the prob for each action
    def select_action( self, cmd, date ):
        actions = self.get_actions_from( cmd )
        probs   = self.action_probs( cmd, date )
        return self.choice( actions, probs ), probs
         
# should return an action and the prob for each action
    def select_strategy( self, cmd, date =0):
        probs   = self.action_probs( cmd, date )
        return self.choice( self.available_strategies, probs ), probs


    ###########################
    def prob_from_action( self, a, date=0 ):
        action_vec = self.get_actions_from( a.cmd )
        prob = self.action_probs(a.cmd, date)
        for i in range(0, len(action_vec)):
            action = action_vec[i]
            if action.cmd == a.cmd and action.strategy == a.strategy:
                return prob[i]
        raise ValueError("The action has not been found....", a, action_vec)
        return -1

    ###########################
    def action_probs(self, cmd, date = 0 ):
        raise ValueError(" method to implement")

    ###########################
    def initial_state(self):
        return 0

    ###########################
    def make_next_state(self, state, action):
        return state
    
    ###########################
    def initial_belief(self):
        return 0

    ###########################
    def strategy_time( self, strategy, success, default_strategy = Strategy.MENU ) :
        pass

        # t = 0
        # if strategy == Strategy.MENU :
        #     t = self.env.value['menu_time']

        # elif strategy == Strategy.LEARNING:
        #     t = self.env.value['menu_time'] + self.env.value['learning_cost']

        # elif strategy == Strategy.HOTKEY:
        #     t = self.env.value['hotkey_time']

        # if success == False:
        #     t += self.env.value['menu_time'] + self.env.value['error_cost']
        #     if default_strategy  == Strategy.LEARNING : 
        #         t += self.env.value['learning_cost'] 
            
        # return t

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


    ###########################
    def generate_step(self, cmd_id, action, date = 0):
        result = StepResult()
        result.cmd = cmd_id
        result.action = Action( action.cmd, action.strategy )
        result.success = self.success(action)
        result.time = self.time(action, result.success)
        return result

    
    ############################
    def update_model(self, step_result):
            raise ValueError(" update_model: method to implement ")


