from alpha_beta_model_abstract import *
import math


################################################
#                                              #
#Implementation of the alpha/beta abstractclas #
#                                              #
################################################
class Trans(Alpha_Beta_Model_Abstract):

    
    def __init__(self, env, name):
        super().__init__(env, name)
        self.max_knowledge = 0.97
        
  
    ###########################
    def update_model(self, step, _memory = None):
        memory = self.memory if _memory == None else _memory

        action = Action(step.cmd, step.action.strategy)
        
        ################
        #   update K   #
        ################
        km = self.params.value['KM']
        kl = self.params.value['KL']
        if step.action.strategy == Strategy.MENU :
            memory.hotkey_knowledge[ step.cmd ] += km * ( self.max_knowledge - memory.hotkey_knowledge[ step.cmd ] )
        
        elif step.action.strategy == Strategy.LEARNING :
            memory.hotkey_knowledge[ step.cmd ] += kl * ( self.max_knowledge - memory.hotkey_knowledge[ step.cmd ] )
        
        elif step.action.strategy == Strategy.HOTKEY and step.success :
            memory.hotkey_knowledge[ step.cmd ] += kl * ( self.max_knowledge - memory.hotkey_knowledge[ step.cmd ] )
        

 
    ##########################
    def action_probs(self, cmd, date):
        value_vec = self.goal_values_recursive(cmd, self.memory, self.params.value['HORIZON'])
        reward_vec = 20 - value_vec

        return soft_max( self.params.value['B'], reward_vec)

    def success(self,action):
        res = [True, False]
        probs = [self.max_knowledge, 1-self.max_knowledge]
        if action.strategy==Strategy.HOTKEY :
            k = self.memory.hotkey_knowledge[ action.cmd ]
            probs = [ k, (1-k) ]
        return self.choice(res, probs)
        

    ##########################
    def goal_values_recursive(self, cmd, memory, horizon) :
        s_vec = self.available_strategies
        gv_all = np.zeros( len(s_vec) )

        if horizon == 0:
            return gv_all if horizon == self.params.value['HORIZON'] else 0

        s_vec = self.available_strategies
        gv_all = np.zeros( len(s_vec) )

        for i in range (0, len(s_vec) ) :
            a = Action(cmd, s_vec[i])
            
            new_memory = copy.deepcopy(memory) 
            time_correct = self.time_strategy(s_vec[i] , success = True)
            step = StepResult(cmd, a, time = time_correct, success = True )
            self.update_model(step, new_memory)
            gv_correct = self.goal_values_recursive(cmd, new_memory, horizon - 1)

            time_error = self.time_strategy(s_vec[i], success = False)
            new_memory = copy.deepcopy( memory )
            step = StepResult(cmd, a, time = time_error, success = False )
            self.update_model(step, new_memory)
            gv_error = self.goal_values_recursive(cmd, new_memory, horizon - 1)

            k = memory.hotkey_knowledge[cmd] if s_vec[i] == Strategy.HOTKEY else 0.95
            t = time_correct * k + time_error * (1.-k)
            gv = gv_correct * k + gv_error * (1. - k)
            gv_all[i] = t + self.params.value['DISCOUNT'] * gv

        return gv_all if horizon == self.params.value['HORIZON'] else np.amax(gv_all)



    



