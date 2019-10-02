import sys
import random
import pandas as pd
import numpy as np
from builtins import object
from anytree import Node, RenderTree

from util import *


class TransitionModel:
    def __init__(self):
        self.sequence = []
        self.n_selection = 80
        self.n_commands = 3
        self.s_zipfian = 0
        self.learning_cost = 0.05
        self.menuParams = [0.2,0.6,1.12]   # power law of practice for menus
        self.hotkeyParams = [0.1,2,0.5] # power lawa of practice for hotkeys
        self.risk_aversion = 0.6  # below this threshold, users do not try to use hotkey: 1 user does not take risk; 0 user takes a lot of risk
        self.implicit_hotkey_knowledge_incr = 0.01
        self.explicit_hotkey_knowledge_incr = 0.2
        self.n_hotkey_knowledge = int(1. / self.implicit_hotkey_knowledge_incr )
        self.overreaction = 0.0

        self.eps = 0.0     #probability for exploit / explore
        self.horizon = 1
        self.discount = 1
        self.error_cost = 0.1  # the cost of an error (does not include the time for selectin the cmd again)


    def to_string(self):
        res = "Cue fixation Time: " + str(self.learning_cost)
        res += "\t Implicit: " + str(self.implicit_hotkey_knowledge_incr)
        res += "\t Explicit: " + str(self.explicit_hotkey_knowledge_incr)
        res += "\t Horizon: " + str(self.horizon)
        res += "\t Error_cost: " + str(self.error_cost)
        res += "\t overreaction: " + str(self.overreaction)


        return res

    ###############################
    #Power Law of Practice (PLP)
    def plp(self,params,p):
        return params[0] * np.exp(-params[1] * p ) + params[2]

    def plp_hotkey(self, p):
        return self.plp(self.hotkeyParams, p)

    def plp_menu(self, p):
        return self.plp(self.menuParams, p)


    def encode_action(self,belief, a, t):
        #k_h = belief.get_most_likely_kh() / self.n_hotkey_knowledge
        #res = "k_h:" + str(k_h) + ",a:" + str(a) + ",t:" + str(round(t,2))
        #return res
        return str(a) 

    def get_all_actions(self):
        return [Action(ActionType.MENU_C) , Action(ActionType.HOTKEY_C), Action(ActionType.MENU_LEARNING_C), Action(ActionType.MENU_E) , Action(ActionType.HOTKEY_E), Action(ActionType.MENU_LEARNING_E)]


    def get_correct_actions(self):
        return [Action(ActionType.MENU_C) , Action(ActionType.HOTKEY_C), Action(ActionType.MENU_LEARNING_C) ]


    def value_iteration(self, parent, depth, horizon, discount, debug_str):
        #print("VI depth: ", depth)
        if depth == (horizon+1):
            return 0

        belief = parent.belief
        k_h = belief.get_most_likely_kh() / self.n_hotkey_knowledge
        actions = self.get_correct_actions()
        
        v = 100000000
        a_min  = -1
        #print("START: ======================================= ", debug_str )
        for action in actions:
            a = action.bin_number
            
            #time = self.time_estimation(belief.n_h_c, belief.n_m_c, a)
            time = self.time_esperance(k_h, belief.k_m, belief.n_h_c, belief.n_m_c, a)

            next_belief = self.update_belief(belief, a, time, None)
            #print("time ", time)
            n = Node(self.encode_action(belief, a, time), parent= parent, a= a, time = time, belief = next_belief, value =0, a_min = -1)
            v_tmp = self.value_iteration(n, depth+1, horizon, discount, debug_str+ " " + str(a))
            if v_tmp == 0:
                n.parent=None
            if v > v_tmp:                
                v = v_tmp
                if v == 0:
                    a_min = -1
                else:
                    a_min = a
                    
                    #res += "\n " + debug_str +"->" +  str(a_min) + "(V:"+ str( round(v_tmp,3)) +")"
                    #res += "\n" + str_tmp
            
        parent.value = parent.time + discount * v
        parent.a_min = a_min
        parent.name = parent.name + ", v:"+ str(round(parent.value,2)) + ", a_min:"+ str(a_min)
        
        #    res += "\n " + debug_str +"->" +  str(a_min) + "(V:"+ str( round(parent.value,3)) +")"
        #    print(debug_str, " -> comparison:", round(parent.time,3), round(v,3) , round(parent.value,3), a_min )        
        #print("END =======================================")
        return parent.value

    

    # focu on the most likely state, rather than a probability distribution
    def select_action(self, belief, horizon, eps):
        actions = self.get_correct_actions()
        
        r = random.random()
        if r < self.eps:  #explore
            return random.choice( actions )

        root_node = Node("R-", belief = belief, time =0, a_min = -1)

        #discount = 1

        v = self.value_iteration(root_node, 0, horizon, self.discount, "r")
        #if root_node.a_min == 1:
            #print("belief k_h: ",  belief.get_most_likely_kh() / self.n_hotkey_knowledge )
        #print(" end select action: ", root_node.a_min)
        #exit(0)

        # for pre, fill, node in RenderTree(root_node):
        #     print("%s%s" % (pre, node.name))
        
        # if root_node.a_min == 1:
        #     exit(0)
        # # exit(0)

        return Action(root_node.a_min)


    def select_action_and_success(self, action, k_h, k_m):
        a = action.bin_number
        p_menu_correct = np.random.binomial(1, k_m)        #p_menu_correct == 0 or 1
        p_hotkey_correct = np.random.binomial(1, k_h)

        if a == ActionType.HOTKEY_C:
            if p_hotkey_correct == 0:  
                return Action(ActionType.HOTKEY_E)
            else:
                return Action(ActionType.HOTKEY_C)
            
        elif a == ActionType.MENU_C:
            if p_menu_correct == 0:  
                return Action(ActionType.MENU_E)
            else:
                return Action(ActionType.MENU_C)
            
        elif a == ActionType.MENU_LEARNING_C:
            if p_menu_correct == 0:  
                return Action(ActionType.MENU_LEARNING_E)
            else:
                return Action(ActionType.MENU_LEARNING_C)
        

    # the actions should only be correct in this method
    # k_h and k_m should be between 0 and 1
    def time_esperance(self, k_h, k_m, n_h_c, n_m_c, a ):
        time_c = self.time_estimation(n_h_c, n_m_c, a)
        time_e = self.time_estimation(n_h_c, n_m_c, a+3)
        knowledge = k_m
        if a == ActionType.HOTKEY_C:
            knowledge = k_h
        return time_c * knowledge + time_e * (1-knowledge)


    def time_estimation(self, n_hotkey_correct, n_menu_correct,  a):
        hotkey_time = self.plp_hotkey(n_hotkey_correct)                 #counter   n_hotkey
        menu_time = self.plp_menu(n_menu_correct)                       #counter   n_menu
        
        if a == ActionType.MENU_C:
            return menu_time
        
        elif a == ActionType.MENU_E:    
            return menu_time + menu_time + self.error_cost
            
        elif a == ActionType.MENU_LEARNING_C:
            return menu_time + self.learning_cost
        
        elif a == ActionType.MENU_LEARNING_E:
            return menu_time + self.learning_cost + menu_time + self.error_cost

        elif a == ActionType.HOTKEY_C:
            return hotkey_time 
            
        elif a == ActionType.HOTKEY_E:
            return hotkey_time + menu_time + self.error_cost
         
        else:
            print("time_error : error ->", a) 
            return -1
                 

    ''' return time and error (Correct:0; Error:1)'''
    def time(self, state, action):
        return self.time_estimation(state.n_h_c, state.n_m_c, action.bin_number)


    def is_terminal(self, state):
        return state.n_h_c + state.n_m_c + state.n_h_e + state.n_m_e  >= self.n_selection


    def initial_state(self):
        return State(k_h=0.0, k_m=0.97, n_h_c=0, n_m_c=0, n_h_e=0, n_m_e=0, k_f=0)


    def make_next_state(self, state, a):
        is_legal = True
        next_state = state.copy()

        if self.is_terminal( state) :
            is_legal = False
            return State(), is_legal

        if a == ActionType.MENU_C:
            next_state.k_h += self.implicit_hotkey_knowledge_incr
            next_state.n_m_c += 1 
            
        elif a == ActionType.HOTKEY_C:
            next_state.k_h += self.explicit_hotkey_knowledge_incr 
            next_state.n_h_c += 1

        elif a == ActionType.MENU_LEARNING_C:
            next_state.k_h += self.explicit_hotkey_knowledge_incr
            next_state.n_m_c += 1

        elif a == ActionType.MENU_E:
            #next_state.k_h += self.implicit_hotkey_knowledge_incr
            next_state.n_m_e += 1 
            
        elif a == ActionType.HOTKEY_E:
            next_state.k_h += 0 #NO LEARNING IF HOTKEY IS UNCORRECTLY EXECUTED!!!! 
            next_state.n_h_e += 1

        elif a == ActionType.MENU_LEARNING_E:
            next_state.k_h += self.explicit_hotkey_knowledge_incr
            next_state.n_m_e += 1

        else:
            print('make next state error in make_next_state')
        
        ''' we should maybe add noise here '''
        #print("make next state: ", next_state.k_h, self.implicit_hotkey_knowledge_incr, self.n_hotkey_knowledge, self.implicit_hotkey_knowledge_incr * (self.n_hotkey_knowledge-1) )

        if next_state.k_h > self.implicit_hotkey_knowledge_incr * (self.n_hotkey_knowledge-1):
            next_state.k_h = self.implicit_hotkey_knowledge_incr * (self.n_hotkey_knowledge-1)
        if next_state.k_h < 0:
            next_state.k_h = 0
        
        return next_state, is_legal


    def initial_belief(self):
        b_k_h = np.zeros(self.n_hotkey_knowledge)   # for each kh, probability that the agent thinks this is the knowledge.
        b_k_f = np.zeros(20)   # for each kf, probability that the agent thinks this is the length of the sequence
        b_k_h[0] = 1     # no believe no hotkey knowledge
        b_k_f[0] = 1     # expect a sequence length == 0
        return Belief(k_h= b_k_h, k_m=0.97, n_h_c = 0, n_m_c = 0, n_h_e = 0, n_m_e = 0, k_f=b_k_f)


    def update_belief(self, belief, a, time, history):
        k_h = belief.get_most_likely_kh() / self.n_hotkey_knowledge
        new_belief = belief.copy()

        if a == ActionType.MENU_C:
            k_h += self.implicit_hotkey_knowledge_incr
            new_belief.n_m_c += 1 
            
        elif a == ActionType.HOTKEY_C:
            k_h += self.explicit_hotkey_knowledge_incr + self.overreaction
            new_belief.n_h_c += 1

        elif a == ActionType.MENU_LEARNING_C:
            k_h += self.explicit_hotkey_knowledge_incr + self.overreaction
            new_belief.n_m_c += 1

        elif a == ActionType.MENU_E:
            k_h += self.implicit_hotkey_knowledge_incr
            new_belief.n_m_e += 1 
            
        elif a == ActionType.HOTKEY_E:
            k_h -= self.overreaction 
            new_belief.n_h_e += 1

        elif a == ActionType.MENU_LEARNING_E:
            k_h += 0
            new_belief.n_m_e += 1
        else:
            print('error in belief update', a)
        
        if k_h >  self.implicit_hotkey_knowledge_incr * (self.n_hotkey_knowledge -1):
            k_h = self.implicit_hotkey_knowledge_incr * (self.n_hotkey_knowledge -1)
        if k_h < 0:
            k_h = 0

        for i in range( len(belief.k_h) ):
            if( round(k_h * self.n_hotkey_knowledge) == i):
                new_belief.k_h[i] = 1
            else:
                new_belief.k_h[i] = 0

        return new_belief   


    


    def generate_step(self, state, action):
        is_legal = True
        if type(action) is int:
            action = HotkeyAction(action)

        result = StepResult()
        result.state = state
        result.next_state, is_legal = self.make_next_state(state, action.bin_number)
        result.action = action.copy()
        result.time = self.time(state, action)
        
        result.is_terminal = self.is_terminal(result.next_state)
        return result, is_legal


    def reset_simulation(self):
        pass


    def reset_episode(self):
        pass


    


