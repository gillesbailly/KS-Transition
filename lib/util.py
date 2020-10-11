import sys
import random
import numpy as np
import math
from builtins import object



#######################
def encode_cmd_s( cmd, s ) :
    return 3 * cmd + s


########################
def values_long_format(actions, values):
    res = [-1,-1,-1]
    for i in range( 0, len(actions)):
        res[ actions[i].strategy ] = values[i]
    return res

#########################
def zipfian(s, N):
    res = np.zeros(N)
    denum = 0
    for n in range(N):
        denum += 1/ ( (n+1)**s )

    for k in range(N):
        num = 1/( (k+1)**s)
        res [k] = num / denum 
    return res


########################
def soft_max(beta, vec):
    vec = vec * beta
    return np.exp( vec ) / np.sum( np.exp( vec ), axis=0)


def log_likelihood( prob_vec ):
    return np.sum( np.log2( prob_vec ) )

###################################
def strategies_from_technique( technique_name ):
    if technique_name == "disable":
        return [Strategy.HOTKEY, Strategy.LEARNING]
    else:
        return[Strategy.MENU, Strategy.HOTKEY, Strategy.LEARNING]

# ########################
# def soft_max_vec(beta, vec):
#     res = []
#     denum = 0
#     for v in vec:
#         denum += np.exp(beta * v)
#     for v in vec:
#         res.append( float( np.exp(beta*v) ) / float(denum) )

#     return res


#######################
def compound_soft_max(beta_1, vec_1, beta_2, vec_2):
    vec_1 = vec_1 * beta_1
    vec_2 = vec_2 * beta_2     
    return np.exp( vec_1 + vec_2 ) / np.sum( np.exp( vec_1 + vec_2 ), axis=0)

def extended_soft_max(beta_vec, value_vec):
    vec = np.zeros( len(value_vec[0]) )
    for i in range(0, len(value_vec)):
        vec += beta_vec[i] * value_vec[i]
    return np.exp( vec ) / np.sum( np.exp( vec ), axis = 0)





###########################
#   Command
###########################
class Command(object):
    
    def __init__(self, id=0, name="None", hotkey ="hk"):
        self.id     = id
        self.name   = name
        self.hotkey = hotkey


###########################
#       STEP RESULT       #
###########################
class StepResult(object):

    def __init__(self, cmd = -1, action = None, time = -1, success = -1, info_gain = -1):
        self.cmd     = cmd
        self.action  = action
        self.time    = time
        self.success = success


# ###########################
# #   FITTINGData
# ###########################
# class FittingData(object):
#     def __init__(self, model, user_id, technique_id, log_likelyhood, N, hotkey_count = -1):
#         self.model_name = model.name
#         self.model_params = model.get_param_value_str()
#         self.n_BIC_params = model.count_BIC_params()
#         self.user_id = user_id
#         self.technique_id = technique_id
#         self.log_likelyhood = round(log_likelyhood,2)
#         self.hotkey_count = hotkey_count
#         self.N = N

#     def bic(self) :
#         return round(- 2 * self.log_likelyhood + self.n_BIC_params * math.log(self.N) )



###########################
#                         #
#    SIMULATION RESULT    #
#                         #
###########################
class Simulation_Result( object ):
    def __init__( self, name = "" ):
        self.name           = name
        self.user_id        = -1
        self.technique_name = ""
        self.input          = None
        self.output         = None
        self.prob           = None
        self.whole_time     = 0


###########################
#                         #
#       MODEL RESULT      #
#                         #
###########################
class Model_Result( object ):

    ############################
    def __init__( self, name = "" ):
        self.name  = name
        self.user_id        = []
        self.log_likelihood = []
        self.prob           = []
        self.output         = []
        self.time           = []    #time of the simulation
        self.parameters     = []
        self.whole_time = 0

    ###################################
    def create( model_name, user_id_vec, debug = False) :
        model_result         = Model_Result( model_name )
        model_result.user_id = user_id_vec
        model_result.time    = [ 0 ] * len( user_id_vec )
        model_result.output  = [ None ] * len( user_id_vec) if debug else []
        model_result.prob    = [ None ] * len( user_id_vec) if debug else []
        model_result.parameters  = [ None ] * len( user_id_vec) 
        model_result.log_likelihood = [ 0 ] * len( user_id_vec )
        return model_result


###########################
#                         #
#       MODEL OUTPUT      #
#                         #
###########################
class Model_Output( object ):

    ##################################
    def __init__( self, n = 0 ):
        self.menu      = [ 0 ] * n
        self.hotkey    = [ 0 ] * n
        self.learning  = [ 0 ] * n

    ##################################
    def n( self ) :
        return len( self.action )


###########################
#                         #
#  MODEL OUTPUT DEBUG     #
#                         #
###########################
class Model_Output_Debug( Model_Output ):
    def __init__( self, n = 0 ):
        super().__init__( n )
        self.meta_info_1 = [ 0 ] * n
        self.meta_info_2 = [ 0 ] * n

###########################
#                         #
#        USER OUTPUT      #
#                         #
###########################
class User_Output( object ):

    ##################################
    def __init__( self, n = 0 ):
        self.time    = [0] * n
        self.success = [False] * n
        self.action  = [None] * n

    def n( self ) :
        return len( self.action )


###########################
#                         #
#      COMMAND INFOS      #
#                         #
###########################
class Command_Info( object ):

    ##################################
    def __init__( self ):
        self.id               = []
        self.name             = []
        self.frequency        = []
        self.start_transition = []
        self.stop_transition  = []



###########################
#                         #
#   EXPERIMENT OTHER      #
#                         #
###########################
class Experiment_Other( object ):

    ##################################
    def __init__( self ):
        self.block       = []
        self.block_trial = []
        self.encounter   = []
        self.method_id   = []
        self.method_name = []



###########################
#                         #
#        USER DATA        #
#                         #
###########################
class User_Data( object ):

    ##################################
    def __init__( self ):
        self.id = -1
        self.technique_id   = -1
        self.technique_name = "empty"
        self.command_info = Command_Info()
        self.output = User_Output()
        self.cmd = []

        self.other = Experiment_Other()

    ##################################
    def set( self, id, technique_id , technique_name ):
        self.id = id
        self.technique_name = technique_name
        self.technique_id = technique_id

    ##################################
    def trial_info( self, trial_id ):
        info = dict()
        if trial_id <0 or trial_id > len( self.cmd ) -1 :
            return info
        
        cmd_index = self.command_info.id.index( self.cmd[ trial_id ] )
        info["User id"]          = str( self.id )
        info["Technique"]        = self.technique_name
        info["Command"]          = str( self.cmd[ trial_id ] )
        info["Frequence" ]       = str( self.command_info.frequency[ cmd_index ] )
        info["Name"]             = self.command_info.name[ cmd_index ]
        info["Transition start"] = str( self.command_info.start_transition[ cmd_index ] )
        info["Transition stop"]  = str( self.command_info.stop_transition[ cmd_index ] )
        info["Time"]             = str( self.output.time[ trial_id ] )
        info["Success"]          = str( self.output.success[ trial_id ] )
        info["Strategy"]         = str( self.output.action[ trial_id ].strategy )
        info["Executed command"] = str( self.output.action[ trial_id ].cmd )
        info["block"]            = str( self.other.block[ trial_id ] )
        info["block trial"]      = str( self.other.block_trial[ trial_id ] )
        info["encounter"]        = str( self.other.encounter[ trial_id ] )
        info["method id"]        = str( self.other.method_id[ trial_id ] )
        info["method name"]      = str( self.other.method_name[ trial_id ] )
        return info
        




###########################
#                         #
#        FREEDOM          #
#                         #
###########################
class Freedom(object):
    FIXED = 0
    USER_FREE = 1
    TECHNIQUE_FREE = 2
    EXPERIMENT_FREE = 3

###########################
#                         #
#        Strategy         #
#                         #
###########################
class Strategy(object):
    MENU = 0
    HOTKEY = 1
    LEARNING = 2

class Strategy_Filter(Strategy):
    NONE = -1
    ALL = 10

###########################
#                         #
#          ACTION         #
#                         #
###########################
class Action():
#    def __init__(self, bin_number):
#        self.bin_number = bin_number

    def __init__(self, cmd, strategy):
        self.cmd = cmd
        self.strategy = strategy

    # def command(self):
    #     return self.cmd

    # def __eq__(self, other): 
    #     if not isinstance(other, Action):
    #         # don't attempt to compare against unrelated types
    #         return NotImplemented
    #     return self.cmd == other.cmd and self.strategy == other.strategy

    # def copy(self):
    #     return Action(self.cmd, self.strategy)

    # def print_action(self, short_print=False):
    #     if short_print:
    #         print("a: ", self.to_string(short_print))
    #     else:
    #         print("action: ", self.to_string())

    # def __repr__(self):
    #     return self.to_string()

    # def method_str(self):
    #     m = "menu"
    #     if self.strategy == Strategy.HOTKEY:
    #         m = "hotkey"
    #     return m

    # def strategy_str(self):
    #     s = "menu"
    #     if self.strategy == Strategy.HOTKEY:
    #         s = "hotkey"
    #     elif self.strategy == Strategy.LEARNING:
    #         s = "learning"
    #     return s

    # def to_string(self, short_print=False):
    #     s = "MENU"
    #     if self.strategy == Strategy.HOTKEY:
    #         s = "HOTKEY"
    #     elif self.strategy == Strategy.LEARNING:
    #         s = "LEARNING"
    #     if short_print:
    #         return str(self.cmd) + s[0]
    #     else:
    #         return str(self.cmd) + '_' + s





