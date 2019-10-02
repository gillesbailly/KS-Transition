import sys
import random
import numpy as np
from builtins import object



def zipfian(s, N):
    res = np.zeros(N)
    denum = 0
    for n in range(N):
        denum += 1/ ( (n+1)**s )

    for k in range(N):
        num = 1/( (k+1)**s)
        res [k] = num / denum 
    return res

###########################
#   STEP RESULT
###########################
class StepResult(object):
    def __init__(self):
        self.state = None
        self.next_state = None
        self.action = None
        self.time = -1
        self.is_terminal = False


###########################
#   HISTORY
###########################
class History(object):
    def __init__(self):
        self.state = []
        self.next_state = []
        self.action = []
        self.time = []
        self.belief = []
        self.next_belief = []

    def update_history(self, s, n_s, a, t, b, n_b):
        self.state.append( s )
        self.next_state.append (n_s)
        self.action.append( a )
        self.time.append(t)
        self.belief.append(b)
        self.next_belief.append(n_b)



###########################
#   BELIEF
# k_h and k_f are distributions of probabilities over the different states
###########################

class Belief(object):
    def __init__(self, k_h, k_m, n_h_c, n_m_c, n_h_e, n_m_e, k_f):
        self.k_h = k_h
        self.k_m = k_m
        self.n_h_c = n_h_c
        self.n_m_c = n_m_c
        self.n_h_e = n_h_e
        self.n_m_e = n_m_e
        self.k_f = k_f


    def copy(self):
        new_k_h = self.k_h.copy()
        new_k_f = self.k_f.copy()
        return Belief(new_k_h, self.k_m, self.n_h_c, self.n_m_c, self.n_h_e, self.n_m_e, new_k_f)

    def get_most_likely_kh(self):
        return np.argmax( np.array(self.k_h) )




########################################################
# MENU_C: Correct Menu selection
# HOTKEY_C: Correct Hotkey selection
# MENU_LEARNING_C: Correct Menu selection where users learn keyboard shortcut cue
# MENU_E: Uncorrect Menu selection
# HOTKEY_C: Uncorrect Hotkey selection
# MENU_LEARNING_C: Uncorrect Menu selection where users learn keyboard shortcut cue
##########################################################
class ActionType(object):
    MENU_C = 0
    HOTKEY_C = 1
    MENU_LEARNING_C = 2
    MENU_E = 3
    HOTKEY_E = 4
    MENU_LEARNING_E = 5



###########################
#   ACTION
###########################
class Action(object):
    def __init__(self, bin_number):
        self.bin_number = bin_number

    def copy(self):
        return Action(self.bin_number)

    def print_action(self, short_print=False):
        if short_print:
            print("a: ", self.to_string(short_print))
        else:
            print("action: ", self.to_string(short_print))

    def to_string(self, short_print=False):
        long_name  = ["MENUc", "HOTKEYc", "MENU_LEARNINGc", "MENUe", "HOTKEYe", "MENU_LEARNINGe"]
        short_name = ["Mc", "Hc", "MLc", "Me", "He", "MLe"]
        if short_print:
            return short_name[self.bin_number]
        else:
            return long_name[self.bin_number]


###########################
#   STATE
###########################
class State(object):
    """
    Knowledge has four features [M, H, n_menu, n_hotkey]
    M is knowledge of menu has a single value: 0.95
    H is knowledge of the hotkey [0,1]
    n_menu is the number of previous selection with the menu
    n_hotkey is the number of previous selection with the hotkey

    n_menu and n_hotkey are observable

    we were thinking introducing an additional feauture Occ as the length the sequence.
    """
    #todo initial kh depends on the number of levels of hotkey knowledge
    def __init__(self, k_h=0.0, k_m=0.97, n_h_c = 0, n_m_c = 0, n_h_e = 0, n_m_e = 0, k_f=0 ):
        self.k_h = k_h
        self.k_m = k_m
        self.n_h_c = n_h_c
        self.n_m_c = n_m_c
        self.n_h_e = n_h_e
        self.n_m_e = n_m_e
        
        self.k_f = k_f

    def __eq__(self, other):
        return self.k_h == other.k_h and self.k_m == other.k_m and self.n_h_c == other.n_h_c and self.n_m_c == other.n_m_c and self.n_h_e == other.n_h_e and self.n_m_e == other.n_m_e

    def print_knowledge(self):
        print( self.to_string() )

    def to_string(self):
        return '(' + str(self.k_h) + ',' + str(self.k_m) + ']-' + '[' + str(self.n_h_c)+ ',' +  str(self.n_m_c) + ',' + str(self.n_h_e) + ',' +  str(self.n_m_e) + ']'

#        return '(' + str( self.kf ) + ', ' + str( self.kh ) +  ', ' + str( self.km ) + ')'

    def copy(self):
        return State(self.k_h, self.k_m, self.n_h_c, self.n_m_c, self.n_h_e, self.n_m_e )

    def as_list(self):
        return [self.k_h, self.k_m, self.n_h_c, self.n_m_c, self.n_h_e, self.n_m_e]


