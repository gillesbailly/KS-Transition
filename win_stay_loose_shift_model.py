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

        def __init__(self, env, default_strategy):
            self.strategy = dict()
            self.success = dict()
            for cmd in env.commands:
                self.strategy[ cmd ] = default_strategy
                self.success[ cmd ] = True


    #########################
    def __init__(self, env):
        super().__init__("win_stay_loose_shift", env)
        self.description = "The win-stay-lose-shift model is one of the simplest models that adapts its behavior according to feedback. Consistent with the name, the model repeats rewarded actions and switches away from unrewarded actions. In the noisy version of the model, the win-stay-lose-shift rule is applied probabilistically, such that the model applies the win-stay-lose-shift rule with probability 1 − eps, and chooses randomly with probability eps. "
        self.reset(self.available_strategies)
    

    ##########################
    def action_probs(self, cmd, date):
       
        eps = self.params.value['eps']
        actions = self.get_actions_from( cmd )
        n = len(actions)
        probs = np.zeros( n )
        print("actions:  ", actions)
        for i in range(0, n) :
            a = actions[i]
            if (self.memory.strategy[ cmd ] == a.strategy):
                if self.memory.success[ cmd ] == True:
                    probs[i] = (1. - eps)  + eps / float(n)
                else:
                    probs[i] = eps / float(n)
            else:
                if self.memory.success[ cmd ] == True:
                    probs[i] = eps / float(n)
                else:
                    probs[i] = (1. - eps) / (float(n) - 1. ) + eps / float(n)
        return probs

        # if len(actions) == 2:
        #     probs = [1. - eps / 2., eps / 2. ] #menu win or hotkey loose
            
        #     if (self.memory.strategy[ cmd ] == Strategy.MENU) and (self.memory.success[ cmd ] == False):
        #         probs = [eps / 2., 1. - eps / 2. ] #menu loose

        #     if (self.memory.strategy[ cmd ] == Strategy.HOTKEY) and (self.memory.success[ cmd ] == True):
        #         probs = [eps / 2., 1. - eps / 2. ] #hotkey win
        #     #print(prob)
        #     return probs

        # else:
        #     probs = [0,0,0]
        #     for a in actions:
        #         if (self.memory.strategy[ cmd ] == a.strategy):
        #             if self.memory.success[ cmd ] == True:
        #                 probs[a.strategy] = 1. - eps / 3.
        #             else:
        #                 probs[a.strategy] = eps / 3.
        #         else:
        #             if self.memory.success[ cmd ] == True:
        #                 probs[a.strategy] = eps / 3.
        #             else:
        #                 probs[a.strategy] = (1. - eps / 3.)/2.
        # probs = np.array(probs)
        # probs = probs / sum(probs)
        # return probs



    ###########################
    def generate_step(self, cmd_id, date, action):
        result = StepResult()
        result.cmd = cmd_id
        result.action = action.copy()
        result.success = (action.cmd == cmd_id)  #always correct
        result.time = self.time(action, result.success)
        return result


    ##########################
    def update_action_success(self, action, success):
            self.memory.strategy[ action.cmd ] = action.strategy
            self.memory.success[ action.cmd ] = success


   ##########################
    def update_model(self, step):
        self.update_action_success(step.action, step.success)


    def default_strategy(self, available_strategies):
        s = Strategy.MENU
        if not (s in self.available_strategies):
            s = Strategy.LEARNING
            if not (s in self.available_strategies):
                s = Strategy.HOTKEY
        return s

    ##########################
    def reset(self, available_strategies):
        self.set_available_strategies( available_strategies )
        self.memory = Win_Stay_Loose_Shift_Model.Memory(self.env, self.default_strategy(self.available_strategies) )

