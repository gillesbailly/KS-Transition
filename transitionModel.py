import sys
import random
import pandas as pd
import numpy as np
from builtins import object
from  anytree import Node, RenderTree
import copy
from util import *
from kernel import *
from model_interface import *


class TransitionModel(Model):
    def __init__(self, env):
        super().__init__(env)
        self.env = env
        self.params['n_strategy'] = 3                    # if == 2 actions {Menu; Hotkey}; == 3 actions: {Menu; Hotkey; Learning}
        self.params['menu_time'] = 1.12                    # menu selection time (seconds)
        self.params['hotkey_time'] = 0.5                    # hotkey selection time (seconds)
        self.params['learning_cost'] = 0.2                # additional temporal cost when learning keyboard shortcuts in the menu 
        
        self.params['risk_aversion'] = 0.6
        self.params['implicit_knowledge'] = 0.3
        self.params['explicit_knowledge'] = 1
        self.params['eps'] = 0.0
        self.params['horizon'] = 2
        self.params['discount'] = 1
        self.params['over_reaction'] = 0.0
        self.params['decay'] = 0.5
        self.params['F'] = 0.4
        self.params['tau'] = 2
        self.params['s'] = 0.4
        self.params['max_knowledge'] = 0.95 
        
        self.kernel = Kernel(self.env.commands, self.params )
        #self.n_hotkey_knowledge = int(1. / self.implicit_hotkey_knowledge_incr )
        

    def time_estimation(self, action, date, kernel):
        knowledge = kernel.knowledge(action, date)
        time_correct = self.time(action, date, kernel, success = True)
        time_error = self.time(action, date, kernel, success = False)
        return knowledge * time + (1-knowledge) * time_error


    def time(self, action, cur_date, kernel, success = True):
        s = action.strategy
        t = 0
        if s == Strategy.MENU:
            t = kernel.menu_time(action.cmd, cur_date)
        elif s == Strategy.LEARNING:
            t = kernel.menu_time(action.cmd, cur_date) + self.params['learning_cost']
        elif s == Strategy.HOTKEY:
            t = kernel.hotkey_time(action.cmd, cur_date)

        if success == False:
            t += kernel.menu_time(action.cmd, cur_date) + self.env.error_cost
        return t


    ########################################
    def select_action(self, cmd_id, date):
        kernel = copy.deepcopy(self.kernel)
        root_node = Node("R-", cmd= cmd_id, date = date, kernel = kernel, time =0, a_min = -1)
        v = self.value_iteration(root_node, date, 0, "r")
        print(root_node.name)
        return root_node.a_min


    ########################################
    def value_iteration(self, parent, date, depth, debug_str):
        #print("VI depth: ", depth)
        if depth == ( self.params['horizon'] + 1 ):
            return 0

        actions = self.get_actions_from( parent.cmd )
        v = 100000000
        a_min  = -1

        for a in actions:
            knowledge = parent.kernel.knowledge(a, date)
            success = True
            time_correct = self.time(a, date, parent.kernel, success)
            kernel_correct = copy.deepcopy(parent.kernel)
            kernel_correct.update_command_history(parent.cmd, date, a, time_correct, success)
            n_correct = Node(a.to_string(True)+'_C', parent = parent, cmd = parent.cmd, a = a, date = date, kernel = kernel_correct, time = time_correct, value = 0, a_min = -1 )
            v_correct = self.value_iteration(n_correct, date+1, depth+1, debug_str + " " + a.to_string(True)+ '_C')

            success = False
            time_error = self.time(a, date, parent.kernel, success = False)
            kernel_error = copy.deepcopy(parent.kernel)
            kernel_error.update_command_history(parent.cmd, date, a, time_error, success)
            n_error = Node(a.to_string(True)+'_E', parent = parent, cmd = parent.cmd, a = a, date = date, kernel = kernel_error, time = time_error, value = 0, a_min = -1 )
            v_error = self.value_iteration(n_error, date+1, depth+1, debug_str + " " + a.to_string(True) + '_E')

            v_tmp = v_correct * knowledge + v_error * (1. - knowledge)

            if v_tmp == 0:
                n_correct.parent=None
            if v > v_tmp:                
                v = v_tmp
                if v == 0:
                    a_min = -1
                else:
                    a_min = a
                    
                    #res += "\n " + debug_str +"->" +  str(a_min) + "(V:"+ str( round(v_tmp,3)) +")"
                    #res += "\n" + str_tmp
            
        parent.value = parent.time + self.params['discount'] * v
        parent.a_min = a_min
        parent.name = parent.name + ", v:"+ str(round(parent.value,2)) + ", a_min:"+ str(a_min)
        
        return parent.value

        

    ##################################
    def generate_step(self, cmd_id, date, state, action):        
        result = StepResult()
        result.cmd = cmd_id
        result.state = state
        result.action = action.copy()

        result.success = 1
        knowledge = self.kernel.knowledge(result.action, date)
        r = random.random()
        if r > knowledge:
            result.success = 0

        result.time = self.time(action, date, self.kernel, result.success)
        
        is_legal = True
        self.kernel.update_command_history(cmd_id, date, result.action, result.time, result.success)
        return result, is_legal


    ################################
    def reset(self):
        self.kernel = Kernel(self.env.commands, self.params)
        


