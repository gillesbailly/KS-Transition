from util import *
import copy
import csv



##########################################
#                                        #
#             Parameters                 #
#                                        #
##########################################
class Parameters(object):
    


    #######################
    def __init__(self, path):
        self.value = dict()
        self.range = dict()
        self.step = dict()
        self.comment = dict()
        self.load(path)

    #######################
    def load(self, path):
        if not path:
            return
        with open(path, 'r') as csvFile:
            reader = csv.reader(csvFile, delimiter= ';')
            header = True
            for row in reader:
                if not header:
                    self.value[ row[0] ] = float( row[2] ) if '.' in row[2] else int( row[2] )
                    min_  = float( row[3] ) if '.' in row[3] else int( row[3] )
                    max_  = float( row[4] ) if '.' in row[4] else int( row[4] )
                    self.range[ row[0] ] = [ min_, max_ ]
                    self.step[ row[0] ] = float( row[5] ) if '.' in row[5] else int( row[5] )
                    self.comment[ row[0] ] = row[6]
                else:
                    header = False

    #######################
    def merge_with(self, params):
        self.value.update( params.value )
        self.range.update( params.range )
        self.step.update( params.step )
        self.comment.update( params.comment )
        
    def get_info( self, name ):
        return [self.value[name], self.range[name][0], self.range[name][1], self.step[name], self.comment[name] ]

    def values_str( self ):
        res = ''
        first = True
        for key, value in self.value.items():
            if first:
                first = False
            else:
                res += ','
            res += key + ':' + str(value)

        return res


    #####################
    def update(self):
        pass

##########################################
#                                        #
#             Environment (context)      #
#                                        #
##########################################
class Environment(Parameters):
    def __init__(self, path):
        super().__init__(path)
        self.commands = self.create_command_list( self.value['n_commands'] )
        self.cmd_seq = np.random.choice( self.commands, self.value['n_selection'], p = zipfian( self.value['s_zipfian'] , len(self.commands) ))

    ###################
    # create the list of commands in the application
    def create_command_list(self, nb):
        l = np.zeros( nb, dtype=int )
        for i in range(nb):
            l[i] = int(i)
        return l

    def update(self):
        self.commands = self.create_command_list( self.value['n_commands'] )
        self.cmd_seq = np.random.choice( self.commands, self.value['n_selection'], p = zipfian( self.value['s_zipfian'] , len(self.commands) ))





##########################################
#                                        #
#             Model Interface            #
#                                        #
##########################################
class Model(object):

    def __init__(self, name, env):
        self.env = env
        self.name = name
        self.description = 'Model description is empty'
        path = './parameters/'
        ext = '_model.csv'
        self.params = Parameters(path + self.name + ext)
        

    def reset(self):
    	pass
        
    def get_params(self):
        return self.params

    def get_param_value_str(self):
        return self.params.values_str()

    def set_params(self, params):
        self.params = params

    def n_strategy(self):
        return self.env.value['n_strategy']

    def get_all_actions(self):
        res =[]
        for cmd in self.env.commands:
            res.append( Action(cmd, Strategy.MENU) )
            res.append( Action(cmd, Strategy.HOTKEY) )
            if self.n_strategy() == 3:
                res.append( Action(cmd, Strategy.LEARNING) )
        return res

    def get_actions_from(self, cmd_id):
        if self.n_strategy() == 3:
            return [Action(cmd_id, Strategy.MENU), Action(cmd_id, Strategy.HOTKEY), Action(cmd_id, Strategy.LEARNING)]
        else:
            return [Action(cmd_id, Strategy.MENU), Action(cmd_id, Strategy.HOTKEY)]

    ##########################
    # should return an action and the prob for each action
    def select_action(self, cmd, date):
         actions = self.get_actions_from( cmd )
         prob = self.action_probs(cmd, date)
         return np.random.choice( actions, 1, p=prob)[0], prob  
    

    ###########################
    def prob_from_action(self, a, date):
        action_vec = self.get_actions_from( a.cmd )
        prob = self.action_probs(a.cmd, date)
        for i in range(0, len(action_vec)):
            action = action_vec[i]
            if action.cmd == a.cmd and action.strategy == a.strategy:
                return prob[i]
        raise ValueError("The action has not been found....", a, action_vec)
        return -1

    def action_probs(self, cmd, date):
        raise ValueError(" method to implement")

    def initial_state(self):
        return 0

    def make_next_state(self, state, action):
        return state
    
    def initial_belief(self):
        return 0


    ###########################
    def time(self, action, success):
        s = action.strategy
        t = 0
        if s == Strategy.MENU:
            t = self.env.value['menu_time']
        elif s == Strategy.LEARNING:
            t = self.env.value['menu_time'] + self.env.value['learning_cost']
        elif s == Strategy.HOTKEY:
            t = self.env.value['hotkey_time']

        if success == False:
            t += self.env.value['menu_time'] + self.env.value['error_cost']
        return t


    ###########################
    def generate_prob_step(self, cmd_id, date, action_prob):
        action_vec = self.get_actions_from(cmd_id)
        res = StepResult()
        res.time = 0
        res.success = 0
        for i in range( len(action_prob) ):
            action = action_vec[i]
            prob = action_prob[i]
            step = generate_step(cmd_id, date, action)
            res.time += step.time * prob
            res.success += step.success * prob



    ###########################
    def has_q_values(self):
        return False

    ###########################
    def generate_step(self, cmd_id, date, action):
        raise ValueError(" generate_step: method to implement ")
    
    ############################
    def update_model(self, step_result):
            raise ValueError(" update_model: method to implement ")


