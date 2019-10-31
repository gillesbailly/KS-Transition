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
        with open(path, 'r') as csvFile:
            reader = csv.reader(csvFile, delimiter= ';')
            header = True
            for row in reader:
                if not header:
                    print("row: ", row)
                    self.value[ row[0] ] = float( row[2] ) if '.' in row[2] else int( row[2] )
                    min_  = float( row[3] ) if '.' in row[3] else int( row[3] )
                    max_  = float( row[4] ) if '.' in row[4] else int( row[4] )
                    self.range[ row[0] ] = [ min_, max_ ]
                    self.step[ row[0] ] = float( row[5] ) if '.' in row[5] else int( row[5] )
                    self.comment[ row[0] ] = row[6]
                else:
                    header = False



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


# class Environment(object):

#     ###################
#     def __init__(self, n_commands, n_selection, s_zipfian, error_cost):
#         self.reset(n_commands, n_selection, s_zipfian, error_cost)
        
#     ###################
#     # create the list of commands in the application
#     def create_command_list(self, nb):
#         l = np.zeros( nb, dtype=int )
#         for i in range(nb):
#             l[i] = int(i)
#         return l

#     ##################
#     def reset(self, n_commands, n_selection, s_zipfian, error_cost):
#         self.n_commands = n_commands
#         self.commands = self.create_command_list( self.n_commands )
#         self.n_selection = n_selection
#         self.s_zipfian = s_zipfian
#         self.error_cost = error_cost
#         self.cmd_seq = np.random.choice( self.commands, self.n_selection, p = zipfian( self.s_zipfian, len(self.commands) ))

#     def to_string(self, short=True):
#         res = "cmds:" + str(self.n_commands) + "; Sel: " + str(self.n_selection) + "; Zipf: " + str(self.s_zipfian) + "; Err: " + str(self.error_cost)
#         return res




##########################################
#                                        #
#             Model Interface            #
#                                        #
##########################################
class Model(object):

    def __init__(self, env):
        self.params = dict()
        self.params['n_strategy'] = 3
        #self.params = self.default_params

        self.env = env

    def reset(self):
    	pass
        
    def get_params(self):
        return self.params

    def set_params(self, params):
        self.params = params

    def n_strategy(self):
        return self.params['n_strategy']

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

    def select_action(self, cmd_id, date):
        raise ValueError(" method to implement")
        
    def initial_state(self):
        return 0

    def make_next_state(self, state, action):
        return state
    
    def initial_belief(self):
        return 0

    def generate_step(self, cmd_id, date, state, action):
        raise ValueError(" method to implement ")
    


