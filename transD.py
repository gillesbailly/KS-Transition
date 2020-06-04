from alpha_beta_model_abstract import *
import math

DISCOUNT = 0.9

################################################
#                                              #
#Implementation of the alpha/beta abstractclas #
#                                              #
################################################
class TransD(Alpha_Beta_Model_Abstract):

    
    def __init__(self, env, name):
        super().__init__(env, name)
        self.max_knowledge = 1.0
     

    ########################## 
    def knowledge(self, cmd ) :
        return self.memory.hotkey_knowledge[ cmd ]   
  

    ########################## 
    def has_knowledge( self ) :
        return True   
  

    ###########################
    def update_model(self, step, _memory = None):
        memory = self.memory if _memory == None else _memory

        action = Action(step.cmd, step.action.strategy)
        
        ################
        #   update K   #
        ################
        decay = self.params.value['DECAY']
        for cmd in self.env.commands:
            memory.hotkey_knowledge[ cmd ] += decay * ( 0 - memory.hotkey_knowledge[ cmd ] )

        km = self.params.value['KM']
        kl = self.params.value['KL']
        if step.action.strategy == Strategy.MENU or step.success == False :
            memory.hotkey_knowledge[ step.cmd ] += km * ( self.max_knowledge - memory.hotkey_knowledge[ step.cmd ] )
        else :
             memory.hotkey_knowledge[ step.cmd ] += kl * ( self.max_knowledge - memory.hotkey_knowledge[ step.cmd ] )
        #elif step.action.strategy == Strategy.LEARNING and step.success:
        #    memory.hotkey_knowledge[ step.cmd ] += kl * ( self.max_knowledge - memory.hotkey_knowledge[ step.cmd ] )
        
        #elif step.action.strategy == Strategy.HOTKEY and step.success :
        #    memory.hotkey_knowledge[ step.cmd ] += kl * ( self.max_knowledge - memory.hotkey_knowledge[ step.cmd ] )
    
        ################
        #   update CK  #
        ################
        if 'CK' in self.params.value : 
            for s in self.available_strategies:
                a_ck = Action(step.cmd, s).to_string()
                a_t_k = 1. if step.action.strategy == s else 0.
                alpha_ck = 1
                memory.value[ 'CK' ][ a_ck ] +=  alpha_ck * (a_t_k -  memory.value[ 'CK' ][ a_ck ] )


    ##########################
    def default_strategy(self) :
        if not Strategy.MENU in self.available_strategies :
            return Strategy.LEARNING
        else :
            return Strategy.MENU
 

    ##########################
    def action_probs(self, cmd, date):
        horizon = int( self.params.value['HORIZON'] )
        if horizon == 0 :
            p = np.zeros( len( self.available_strategies ) )
            ds = self.default_strategy()
            index =self.available_strategies.index(ds)
            p[ index ] = 1.
            return p

        value_vec = self.goal_values_recursive(cmd, self.memory, horizon,[])
        reward_vec = 20 - value_vec #TODO What is this 20 (but I guess it is useless)
        #Q_values = reward_vec 
        W = self.params.value['W_CK'] if 'W_CK' in self.params.value else 0
        Q_values = (1.- W) * reward_vec + W * self.values( 'CK', cmd, -1 )
        return soft_max( self.params.value['B'], Q_values)

    def success(self,action):
        res = [True, False]
        probs = [self.max_knowledge, 1-self.max_knowledge]
        if action.strategy==Strategy.HOTKEY :
            k = self.memory.hotkey_knowledge[ action.cmd ]
            probs = [ k, (1-k) ]
        return self.choice(res, probs)
        

    ##########################
    def relevant_strategies(self, horizon, history) :
        s_vec = copy.copy(self.available_strategies)
        if len(history) == 0 :
            return s_vec

        if horizon <= 1 and Strategy.LEARNING in self.available_strategies :
            if not Strategy.LEARNING == self.default_strategy() :
                s_vec.remove( Strategy.LEARNING )
        
        if history[-1] == Strategy.HOTKEY : #once you choose HOTKEY -> use use HOTKEY
            s_vec = [Strategy.HOTKEY]
        
        if history[-1] == Strategy.LEARNING and Strategy.MENU in self.available_strategies:
            s_vec.remove( Strategy.MENU )

        return s_vec

    ##########################
    def goal_values_recursive(self, cmd, memory, horizon, history) :
        s_vec = self.available_strategies
        gv_all = np.zeros( len(s_vec) )
        horizon_param = int( self.params.value['HORIZON'] ) #for optimization method which potentially generate horizon as a float

        if horizon == 0:
            #print("h=", horizon, " return gv_all: ", gv_all)
            return gv_all if horizon == horizon_param else 0

        #s_vec = self.available_strategies
        s_vec = self.relevant_strategies(horizon, history)


        gv_all = np.zeros( len(s_vec) )
        #print('========== h', history, 's_vec', s_vec)
        for i in range (0, len(s_vec) ) :
            local_history = copy.copy( history )
            #print('error', s_vec, i, local_history)
            local_history.append( s_vec[ i ] )
            a = Action(cmd, s_vec[i])
            #print('h=',horizon, '--->', s_vec, ' ', s_vec[i], '----------- k:', memory.hotkey_knowledge[cmd], 'history', history, 'local_history:', local_history)
            new_memory_correct = copy.deepcopy(memory) 
            time_correct = self.time_strategy(s_vec[i] , success = True)
            step = StepResult(cmd, a, time = time_correct, success = True )
            self.update_model(step, new_memory_correct)
            gv_correct = self.goal_values_recursive(cmd, new_memory_correct, horizon - 1, local_history)
            #print("h=", horizon, "s: ", s_vec[i],  "correct gv: ", gv_correct)
            #print('---')
            new_memory_error = copy.deepcopy( memory )
            time_error = self.time_strategy(s_vec[i], success = False)
            step = StepResult(cmd, a, time = time_error, success = False )
            self.update_model(step, new_memory_error)
            gv_error = self.goal_values_recursive(cmd, new_memory_error, horizon - 1, local_history)
            #print("h=", horizon, "s: ", s_vec[i]," error gv: ", gv_error)

            k = memory.hotkey_knowledge[cmd] if s_vec[i] == Strategy.HOTKEY else self.max_knowledge
            t = time_correct * k + time_error * (1.-k)
            gv = gv_correct * k + gv_error * (1. - k)
            #print("h=", horizon, "s: ", s_vec[i], "k:",k, time_correct, time_error, t, "gv:", gv )

            gv_all[i] = t + DISCOUNT * gv

        return gv_all if horizon == horizon_param else np.amin(gv_all)



    #########################
    def custom_reset_memory(self, available_strategies):
        if 'K0' in self.params.value: 
            for cmd in self.env.commands:
                self.memory.hotkey_knowledge[ cmd ] = self.params.value['K0']
        
        if 'CK' in self.params.value :
            name = 'CK'
            self.memory.value[ name ] = dict()
            self.memory.set_initial_value( self.env, name, self.value_0(available_strategies, name) )



        



