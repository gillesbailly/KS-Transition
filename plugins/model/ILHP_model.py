#from alpha_beta_model_abstract import *
#import math
from model_interface import *


################################################
#                                              #
#Implementation of the alpha/beta abstractclas #
#                                              #
################################################
class ILHP_Model( Model ):

    class Memory():
        
        ###############################
        def __init__( self, n_commands, n_strategies ):            
            self.perseveration_value  = np.zeros( (n_commands, n_strategies) )
            self.hotkey_knowledge     = np.zeros( n_commands ) #TOOD ???


    ###############################
    def __init__( self, variant_name = '' ):
        super().__init__( 'ILHP', variant_name )
        self.max_knowledge = 1.0
        #self.default_strategy = Strategy.MENU
        #self.present_strategies = np.array( [1,1,1]) #[MENU, HOKEY, LEARNING]
        
    ##########################
    def custom_reset_params(self) : 
        #print("custom reset params")

        self.decay          = self.params.target_value( 'DECAY' )
        self.alpha_implicit = self.params.target_value( 'ALPHA_IMPLICIT' )
        alpha_explicit_diff = self.params.target_value( 'ALPHA_EXPLICIT_DIFF' )
        self.alpha_explicit = self.alpha_implicit + alpha_explicit_diff
        self.perseveration  = self.params.target_value( 'PERSEVERATION' )
        self.horizon        = int( self.params.target_value( 'HORIZON' ) )
        self.beta           = self.params.target_value( 'BETA' )
        self.discount       = self.params.target_value(  'DISCOUNT' )
        self.s_time         = [ self.params.target_value( 'MENU_TIME' ), self.params.target_value( 'HOTKEY_TIME' ), self.params.target_value( 'MENU_TIME' ) + self.params.target_value( 'LEARNING_COST' ) ]
        self.error_cost     = self.params.target_value( 'ERROR_COST' )
        self.time_penalty = self.s_time[ self.default_strategy ] + self.error_cost
        
        
        
    ########################## 
    def knowledge(self, cmd ) :
        return self.memory.hotkey_knowledge[ cmd ] 
  
   
    ###########################
    def update_model(self, step, _memory = None):
        memory = self.memory if _memory == None else _memory

        # Decay 
        memory.hotkey_knowledge += self.decay * ( 0 - memory.hotkey_knowledge )

        # Implicit / Explicit Learning
        if step.action.strategy == Strategy.MENU : #or step.success == False :
            memory.hotkey_knowledge[ step.cmd ] += self.alpha_implicit * ( self.max_knowledge - memory.hotkey_knowledge[ step.cmd ] )
        else :
            memory.hotkey_knowledge[ step.cmd ] += self.alpha_explicit * ( self.max_knowledge - memory.hotkey_knowledge[ step.cmd ] )
        
        # Perseveration (similar to Choice Kernel CK )
        if self.perseveration > 0 :
            a_t_k = np.zeros(3)
            a_t_k[ step.action.strategy ] = 1
            memory.perseveration_value[ step.cmd ] += (a_t_k -  memory.perseveration_value[ step.cmd ] )
        

    ##########################
    def quick_update_memory(self, knowledge, strategy, success):
            new_knowledge = knowledge + self.decay * ( 0 - knowledge )
            if strategy == Strategy.MENU : #or success == False :
                new_knowledge += self.alpha_implicit * ( self.max_knowledge - new_knowledge )
            else :
                new_knowledge += self.alpha_explicit * ( self.max_knowledge - new_knowledge )
            return new_knowledge


    ##########################
    # def default_strategy_long(self) :
    #     if not Strategy.MENU in self.available_strategies :
    #         return Strategy.LEARNING
    #     return Strategy.MENU
 

    ##########################
    def action_probs(self, cmd ):
        
        if self.horizon == 0 :
            p = np.zeros( 3 )
            p[ self.default_strategy ] = 1. #valid even if technique == disable
            return p

        cur_knowledge = self.memory.hotkey_knowledge[ cmd ]
        value_vec = self.goal_values_recursive(cmd, cur_knowledge, self.horizon,[])
        reward_vec = 20 - value_vec #TODO What is this 20 (but I guess it is useless)
        #Q_values = reward_vec
        
        #ensure the Q_value vector has a length  == 3
        Q_values = np.zeros(3)
        for s, r in zip( self.available_strategies, reward_vec ):
            Q_values[ s ] = r

        if self.perseveration > 0 :
            Q_values = (1.- self.perseveration) * Q_values + self.perseveration * self.perseveration_vec( cmd )

        return soft_max3( self.beta, Q_values, self.present_strategies )

    ##########################
    def perseveration_vec( self, cmd ):
        #value_vec = np.zeros( len( self.available_strategies ) )
        #return np.array ( [ self.memory.perseveration_value[ cmd ][ s ] for s in self.available_strategies ] )
        return self.memory.perseveration_value[ cmd ]

        # for i, s in enumerate( self.available_strategies ):
        #     value_vec[ i ] = self.memory.perseveration[ encode_cmd_s( cmd, s ) ]
        # return value_vec



    ###########################
    def time(self, action, success):
        return self.s_time[ action.strategy ] + (1-success) * self.time_penalty
        # t = self.s_time[ action.strategy ]
        # if success == False :
        #     t += self.s_time[ self.default_strategy ] + self.error_cost 
        # return t

    #########################
    def success(self,action):
        res = [True, False]
        probs = [ self.max_knowledge, 1. - self.max_knowledge ]
        if action.strategy == Strategy.HOTKEY :
            k = self.memory.hotkey_knowledge[ action.cmd ]
            probs = [ k,  1. - k ]
        return self.choice(res, probs)
        

    ##########################
    # we assume that we have eihter 3 strategies (menu, hotkey, learning) 
    # for Traditional and Audio or 2 strategies (Learning and hotkey) for Disable
    def relevant_strategies(self, horizon, history) :  
        if len(history) == 0 :
            return self.available_strategies.copy()
        
        if history[-1] == Strategy.HOTKEY : #once you choose HOTKEY -> use use HOTKEY
            return [Strategy.HOTKEY]
        
        s_vec = self.available_strategies.copy()
        if horizon <= 1 and not Strategy.LEARNING == self.default_strategy :
            s_vec = np.setdiff1d( s_vec, Strategy.LEARNING, assume_unique= True )
        
        if history[-1] == Strategy.LEARNING and Strategy.MENU in self.available_strategies:
            s_vec = np.setdiff1d( s_vec, Strategy.MENU, assume_unique= True )

        return s_vec

    ##########################
    def goal_values_recursive(self, cmd, cur_knowledge, horizon, history) :
        s_vec = self.available_strategies
        gv_all = np.zeros( len(s_vec) )

        if horizon == 0:
            #print("h=", horizon, " return gv_all: ", gv_all)
            return gv_all if horizon == self.horizon else 0

        #s_vec = self.available_strategies
        s_vec = self.relevant_strategies(horizon, history)


        gv_all = np.zeros( len(s_vec) )
        #print('========== h', history, 's_vec', s_vec)
        for i in range (0, len(s_vec) ) :
            local_history = history.copy()
            #print('error', s_vec, i, local_history)
            local_history.append( s_vec[ i ] )
            a = Action(cmd, s_vec[i])
            #print('h=',horizon, '--->', s_vec, ' ', s_vec[i], '----------- k:', memory.hotkey_knowledge[cmd], 'history', history, 'local_history:', local_history)
            #new_memory_correct = copy.deepcopy(memory)
            
            time_correct = self.time( a , success = True)
            #step = StepResult(cmd, a, time = time_correct, success = True )
            #self.update_model(step, new_memory_correct)
            new_correct_knowledge  = self.quick_update_memory(cur_knowledge, s_vec[i], True)
            gv_correct = self.goal_values_recursive(cmd, new_correct_knowledge, horizon - 1, local_history)
            #print("h=", horizon, "s: ", s_vec[i],  "correct gv: ", gv_correct)
            #print('---')
            
            if s_vec[i] == Strategy.HOTKEY :

                #new_memory_error = copy.deepcopy( memory )
                time_error = self.time(a, success = False)
                #step = StepResult(cmd, a, time = time_error, success = False )
                #self.update_model(step, new_memory_error)
                new_error_knowledge  = self.quick_update_memory(cur_knowledge, s_vec[i], False)
                gv_error = self.goal_values_recursive(cmd, new_error_knowledge, horizon - 1, local_history)
                #print("h=", horizon, "s: ", s_vec[i]," error gv: ", gv_error)

                k  = cur_knowledge if s_vec[i] == Strategy.HOTKEY else self.max_knowledge
                t  = time_correct * k + time_error * (1.-k)
                gv = gv_correct   * k + gv_error * (1. - k)
                #print("h=", horizon, "s: ", s_vec[i], "k:",k, time_correct, time_error, t, "gv:", gv )
                gv_all[i] = t + self.discount * gv
            else:
                t = time_correct
                gv = gv_correct
                gv_all[i] = t + self.discount * gv

        return gv_all if horizon == self.horizon else np.amin(gv_all)

    ###########################
    def meta_info_1( self, cmd ):
        return self.memory.hotkey_knowledge[ cmd ]

    ###########################
    def meta_info_2( self, cmd ):
        return 0

    #########################
    def reset( self, command_ids, available_strategies ):
        self.command_ids = command_ids
        self.set_available_strategies( available_strategies )
        #self.default_strategy = self.default_strategy_long()
        self.custom_reset_params()
        self.memory = ILHP_Model.Memory( len(command_ids), 3 )
            
        



        



