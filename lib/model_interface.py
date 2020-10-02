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

    # #######################
    # def merge_with(self, params):
    #     self
    #     self.value.update( params.value )
    #     self.range.update( params.range )
    #     self.step.update( params.step )
    #     self.comment.update( params.comment )
        
    # def get_info( self, name ):
    #     return [self.value[name], self.range[name][0], self.range[name][1], self.step[name], self.comment[name] ]

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


    # #####################
    # def update(self):
    #     pass

##########################################
#                                        #
#             Environment (context)      #
#                                        #
##########################################
# class Environment(Parameters):
#     def __init__(self, path):
#         super().__init__(path)
#         self.commands = []


        #self.action_list = self.create_action_list()
        #self.cmd_seq = np.random.choice( self.commands, self.value['n_selection'], p = zipfian( self.value['s_zipfian'] , len(self.commands) ))
        
        #self.commands = self.create_command_list( self.value['n_commands'] )
        #self.action_list = self.create_action_list()
        #self.cmd_seq = np.random.choice( self.commands, self.value['n_selection'], p = zipfian( self.value['s_zipfian'] , len(self.commands) ))
        

    ###################
    # create the list of commands in the application
    # def create_command_list(self, nb):
    #     l = np.zeros( nb, dtype=int )
    #     for i in range(nb):
    #         l[i] = int(i)
    #     return l
    
    # ###################
    # def create_action_list(self):
    #     res =[]
    #     for cmd in self.commands:
    #         res.append( Action(cmd, Strategy.MENU) )
    #         res.append( Action(cmd, Strategy.HOTKEY) )
    #         if self.value['n_strategy'] == 3:
    #             res.append( Action(cmd, Strategy.LEARNING) )
    #     return res


   


    # ###################
    # def update_from_empirical_data( self, command_ids, command_seq, n_strategy ):
    #     self.value['n_commands'] = len(command_ids)
    #     self.value['n_strategy'] = n_strategy
    #     self.commands = command_ids
    #     self.cmd_seq = command_seq
    #     self.create_action_list()


    # ##################
    # def update(self):
    #     self.commands = self.create_command_list( self.value['n_commands'] )
    #     self.cmd_seq = np.random.choice( self.commands, self.value['n_selection'], p = zipfian( self.value['s_zipfian'] , len(self.commands) ))





##########################################
#                                        #
#             Model Interface            #
#                                        #
##########################################
class Model(object):

    ######################################
    def __init__( self, name, env ):
        self.env = env
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
        self.available_strategies = copy.copy( strategies )

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
    def time_strategy(self, strategy, success, default_strategy = Strategy.MENU) :
        t = 0
        if strategy == Strategy.MENU :
            t = self.env.value['menu_time']

        elif strategy == Strategy.LEARNING:
            t = self.env.value['menu_time'] + self.env.value['learning_cost']

        elif strategy == Strategy.HOTKEY:
            t = self.env.value['hotkey_time']

        if success == False:
            t += self.env.value['menu_time'] + self.env.value['error_cost']
            if default_strategy  == Strategy.LEARNING : 
                t += self.env.value['learning_cost'] 
            
        return t

    ###########################
    def success(self, action):
        return True


    ###########################
    def time(self, action, success):
        return self.time_strategy(action.strategy, success)

    ###########################
    def has_RW_values( self ):
        return False

    ###########################
    def has_CK_values( self ):
        return False

    ###########################
    def has_CTRL_values( self ):
        return False

    ###########################
    def has_knowledge( self ) :
        return False

    ###########################
    def generate_step( self, cmd_id, date, action ):
        raise ValueError(" generate_step: method to implement ")
    
    ############################
    def update_model(self, step_result):
            raise ValueError(" update_model: method to implement ")


