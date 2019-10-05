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

    def add(self, date, _action , time):
        self.date.append(date)
        self.action.append(_action)
        self.time.append(time)
        self.accuracy.append( self.id == _action.command() )

    def reset(self):
        self.date = []
        self.action = []

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
    
    def __init__(self, commands): #commands is a list of command ids
        self.cmd_history = dict()
        for i in commands:
            self.cmd_history[i] = Command_history(i)

    def update_command_history(self, cmd_id, date, action, time):
        hist = self.cmd_history[cmd_id]
        hist.add(date, action, time)
        self.cmd_history[cmd_id] = hist

    def menu_knowledge(self, cmd_id):
    	return 0.95

    def hotkey_knowledge(self, cmd_id):
    	return 0

    def print(self):
        for hist in self.cmd_history.values():
            hist.print()






class CommandSequence(object):
    
    def __init__(self, nb_commands, seq_length, prob_distribution):
        self.sequence = np.random.choice(nb_commands, seq_length)
