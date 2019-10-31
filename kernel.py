import numpy as np
from util import *


###########################
#   History of command usage
###########################
class Command_history(object):

    def __init__(self, id):
        self.id = id
        self.date = []
        self.action = []
        self.time = []
        self.accuracy = []

    def add(self, date, _action , time, success):
        self.date.append(date)
        self.action.append(_action)
        self.time.append(time)
        self.accuracy.append( success )

    def reset(self):
        self.date = []
        self.action = []
        self.time = []
        self.accuracy = []

    def print(self):
        print( self.to_string() )

    def to_string(self):
        res = 'cmd ' + str(self.id) + ':'
        for i in range(len(self.date)):
            res += '[' + str(self.date[i]) + ', ' + self.action[i].to_string(True) + ', ' + str(self.time[i]) + ', ' + str(self.accuracy[i]) + ']'
        return res



###########################
#   Kernel
###########################
class Kernel(object):
    

    #########################
    def __init__(self, commands, params): #commands is a list of command ids
        self.cmd_history = dict()
        self.params = params
        for i in commands:
            self.cmd_history[i] = Command_history(i)


    ########################
    def update_command_history(self, cmd_id, date, action, time, success):
        hist = self.cmd_history[cmd_id]
        hist.add(date, action, time, success)
        self.cmd_history[cmd_id] = hist


    ########################
    def menu_knowledge(self, cmd_id):
    	return self.params['max_knowledge']


    ########################
    def prob(self, activation ):
        return 1 / (1 + np.exp(- (activation - self.params['tau']) / self.params['s'] ))


    ########################
    def menu_time(self, cmd_id, cur_date):
        a = self.menu_activation(cmd_id, cur_date)
        return self.params['F'] * np.exp(-a) + self.params['menu_time']


    ########################
    def hotkey_time(self, cmd_id, cur_date):
        a = self.hotkey_activation(cmd_id, cur_date)
        return self.params['F'] * np.exp(-a) + self.params['hotkey_time']


    ###############################################
    # activation is based on the work of anderson #
    ###############################################
    def menu_activation(self, cmd_id, cur_date):
        date = self.cmd_history[cmd_id].date
        action = self.cmd_history[cmd_id].action
        accuracy = self.cmd_history[cmd_id].accuracy
        
        sum = 0
        weight = 1
        for i in range( len(date)):
            strategy = action[i].strategy
            success = accuracy[i]
            if strategy == Strategy.MENU or strategy == Strategy.LEARNING:
                sum += success * (cur_date - date[i])**(-self.params['decay'])
        #print("len date: ", len(date), " menu activation: ", sum)
        return sum

    ###############################################
    # activation is based on the work of anderson #
    # plus a personal weight                      #
    ###############################################
    def hotkey_activation(self, cmd_id, cur_date):
        date = self.cmd_history[cmd_id].date
        action = self.cmd_history[cmd_id].action
        accuracy = self.cmd_history[cmd_id].accuracy
 
        sum = 0
        weight = 1
        for i in range( len(date)):
            strategy = action[i].strategy
            success = accuracy[i]
            if strategy == Strategy.MENU:
                weight =  self.params['implicit_knowledge']
            elif strategy == Strategy.LEARNING:
                weight =  self.params['explicit_knowledge']
            sum += success* weight * (cur_date - date[i])**(-self.params['decay'])
        return sum


    ########################
    def hotkey_knowledge(self, cmd_id, cur_date):
        a = self.hotkey_activation(cmd_id, cur_date)
        p = self.prob(a)
        if p > self.params['max_knowledge']:
            p = self.params['max_knowledge']
        return p

    
    ########################
    def knowledge(self, action, cur_date):
        if action.strategy == Strategy.HOTKEY:
            return self.hotkey_knowledge(action.cmd, cur_date)
        else:
            return self.menu_knowledge(action.cmd) #menu + learning


    ########################
    def print(self):
        for hist in self.cmd_history.values():
            hist.print()



# class CommandSequence(object):
    
#     def __init__(self, nb_commands, seq_length, prob_distribution):
#         self.sequence = np.random.choice(nb_commands, seq_length)
