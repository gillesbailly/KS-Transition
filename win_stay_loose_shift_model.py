import random
from util import *
from model_interface import *
import copy






#####################################
#                                   #
#   Random MODEL                    #
#   Users select randomly an action #
#   If error, users perform the correct menu action and got temporal penality for that ("error cost")
###############################
class Win_Stay_Loose_Shift_Model(Model):



    class Memory(Model):

        def __init__(self, env):
            self.strategy = dict()
            self.success = dict()
            for cmd in env.commands:
                self.strategy[ cmd ] = Strategy.MENU
                self.success[ cmd ] = True


        def update(self, action, success):
            self.strategy[ action.cmd ] = action.strategy
            self.success[ action.cmd ] = success



    def __init__(self, env):
        super().__init__("win_stay_loose_shift", env)
        self.memory = Win_Stay_Loose_Shift_Model.Memory(env)
        self.description = "The win-stay-lose-shift model is one of the simplest models that adapts its behavior according to feedback. Consistent with the name, the model repeats rewarded actions and switches away from unrewarded actions. In the noisy version of the model, the win-stay-lose-shift rule is applied probabilistically, such that the model applies the win-stay-lose-shift rule with probability 1 − eps, and chooses randomly with probability eps. "
        
        
    ##########################
    def select_action(self, cmd, date):
        actions = self.get_actions_from( cmd )
        eps = self.params.value['eps']

        if len(actions) == 2:
            prob = [1. - eps / 2., eps / 2. ] #menu win or hotkey loose
            print( self.memory.strategy[ cmd ], Strategy.MENU, self.memory.success[ cmd ] )

            if (self.memory.strategy[ cmd ] == Strategy.MENU) and (self.memory.success[ cmd ] == False):
                prob = [eps / 2., 1. - eps / 2. ] #menu loose

            if (self.memory.strategy[ cmd ] == Strategy.HOTKEY) and (self.memory.success[ cmd ] == True):
                prob = [eps / 2., 1. - eps / 2. ] #hotkey win
            print(prob)
            return np.random.choice( actions, 1, p=prob)[0]

        else:
            prob = [0,0,0]
            for a in actions:
                if (self.memory.strategy[ cmd ] == a.strategy):
                    if self.memory.success[ cmd ] == True:
                        prob[a.strategy] = 1. - eps / 3.
                    else:
                        prob[a.strategy] = eps / 3.
                else:
                    if self.memory.success[ cmd ] == True:
                        prob[a.strategy] = eps / 3.
                    else:
                        prob[a.strategy] = (1. - eps / 3.)/2.
        prob = np.array(prob)
        prob = prob / sum(prob)
        print(prob)
        return np.random.choice( actions, 1, p=prob)[0], prob  


    ###########################
    def generate_step(self, cmd_id, date, action):
        result = StepResult()
        result.cmd = cmd_id
        result.action = action.copy()
        result.success = (action.cmd == cmd_id)  #always correct
        result.time = self.time(action, result.success)
        return result


   ##########################
    def update_model(self, step):
        self.memory.update(step.action, step.success)


    #########################
    def reset(self):
        self.memory = Win_Stay_Loose_Shift_Model.Memory(self.env)

