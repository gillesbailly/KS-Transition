from alpha_beta_model_abstract import *
import math



################################################
#                                              #
#Implementation of the alpha/beta abstractclas #
#                                              #
################################################
class ILHP_Model( Model ):

    class Memory():
        
        ###############################
        def __init__( self, command_ids ):            
            self.perseveration_value  = np.zeros(3 * len( command_ids ) )
            self.hotkey_knowledge     = np.zeros( len( command_ids ) ) #TOOD ???

        #############################
        def set_initial_perseveration_value(self, command_ids , value_0):
            for cmd in command_ids :
                for s in value_0 :
                    self.perseveration_value[ encode_cmd_s(cmd, s) ] = value_0[ s ]

    ###############################
    def __init__( self, env, name ):
        super().__init__(name, env)
        self.max_knowledge = 1.0
        self.command_ids = []
        
    ##########################
    def custom_reset_params(self) : 
        #print("custom reset params")
        self.decay          = self.params[ 'DECAY' ].value
        self.alpha_implicit = self.params[ 'ALPHA_IMPLICIT' ].value if 'ALPHA_IMPLICIT' in self.params else 0
        self.alpha_explicit = self.params[ 'ALPHA_EXPLICIT' ].value if 'ALPHA_EXPLICIT' in self.params else 0.5 #TODO
        self.perseveration  = self.params[ 'PERSEVERATION' ].value  if 'PERSEVERATION'  in self.params else -1
        self.horizon        = int( self.params[ 'HORIZON' ].value ) if 'HORIZON'        in self.params else 1
        self.beta           = self.params[ 'BETA' ].value
        self.discount       = self.params[ 'DISCOUNT' ].value
        self.menu_time      = self.params[ 'MENU_TIME' ].value
        self.hotkey_time    = self.params[ 'HOTKEY_TIME' ].value
        self.learning_cost  = self.params[ 'LEARNING_COST' ].value
        self.error_cost     = self.params[ 'ERROR_COST' ].value
        
        
        
    ########################## 
    def knowledge(self, cmd ) :
        return self.memory.hotkey_knowledge[ cmd ] 
  
    # ########################## 
    # def has_knowledge( self ) :
    #     return True   
  
    ###########################
    def update_model(self, step, _memory = None):
        memory = self.memory if _memory == None else _memory

        action = Action(step.cmd, step.action.strategy)

        # Decay
        for cmd in self.command_ids:
            memory.hotkey_knowledge[ cmd ] += self.decay * ( 0 - memory.hotkey_knowledge[ cmd ] )

        # Implicit / Explicit Learning
        if step.action.strategy == Strategy.MENU : #or step.success == False :
            memory.hotkey_knowledge[ step.cmd ]  += self.alpha_implicit * ( self.max_knowledge - memory.hotkey_knowledge[ step.cmd ] )
        else :
             memory.hotkey_knowledge[ step.cmd ] += self.alpha_explicit * ( self.max_knowledge - memory.hotkey_knowledge[ step.cmd ] )
        
        # Perseveration (similar to Choice Kernel CK )
        if self.perseveration >= 0 : 
            for s in self.available_strategies:
                a_t_k = 1. if step.action.strategy == s else 0.
                alpha_perseveration = 1.
                memory.perseveration_value[ encode_cmd_s(step.cmd, s) ] +=  alpha_perseveration * (a_t_k -  memory.perseveration_value[ encode_cmd_s(step.cmd, s) ] )
                

    ##########################
    def quick_update_memory(self, knowledge, strategy, success):
            new_knowledge = knowledge
            new_knowledge += self.decay * ( 0 - new_knowledge )
            if strategy == Strategy.MENU : #or success == False :
                new_knowledge += self.alpha_implicit * ( self.max_knowledge - new_knowledge )
            else :
                new_knowledge += self.alpha_explicit * ( self.max_knowledge - new_knowledge )
            return new_knowledge


    ##########################
    def default_strategy(self) :
        if not Strategy.MENU in self.available_strategies :
            return Strategy.LEARNING
        return Strategy.MENU
 

    ##########################
    def action_probs(self, cmd, date=0 ):
        
        if self.horizon == 0 :
            p = np.zeros( len( self.available_strategies ) )
            ds = self.default_strategy()
            index = self.available_strategies.index(ds)
            p[ index ] = 1.
            return p

        cur_knowledge = self.memory.hotkey_knowledge[ cmd ]
        value_vec = self.goal_values_recursive(cmd, cur_knowledge, self.horizon,[])
        reward_vec = 20 - value_vec #TODO What is this 20 (but I guess it is useless)
        Q_values = reward_vec 
        if self.perseveration >= 0 :
            Q_values = (1.- self.perseveration) * reward_vec + self.perseveration * self.perseveration_vec( cmd )

        return soft_max( self.beta, Q_values)

    ##########################
    def perseveration_vec(self, cmd ):
        #value_vec = np.zeros( len( self.available_strategies ) )
        return np.array ( [ self.memory.perseveration_value[ encode_cmd_s( cmd, s) ] for s in self.available_strategies ] )

        # for i, s in enumerate( self.available_strategies ):
        #     value_vec[ i ] = self.memory.perseveration[ encode_cmd_s( cmd, s ) ]
        # return value_vec



    ###########################
    def time(self, action, success):
        strategy = action.strategy
        t = 0
        if strategy == Strategy.MENU :
            t = self.menu_time
        elif strategy == Strategy.LEARNING:
            t = self.menu_time + self.learning_cost
        elif strategy == Strategy.HOTKEY:
            t = self.hotkey_time
        if success == False:
            t += self.menu_time + self.error_cost
            if self.default_strategy()  == Strategy.LEARNING : 
                t += self.learning_cost
        return t

    #########################
    def success(self,action):
        res = [True, False]
        probs = [ self.max_knowledge, 1. - self.max_knowledge ]
        if action.strategy == Strategy.HOTKEY :
            k = self.memory.hotkey_knowledge[ action.cmd ]
            probs = [ k,  1. - k ]
        return self.choice(res, probs)
        

    ##########################
    def relevant_strategies(self, horizon, history) :
        s_vec = self.available_strategies.copy()
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

                k = cur_knowledge if s_vec[i] == Strategy.HOTKEY else self.max_knowledge
                t = time_correct * k + time_error * (1.-k)
                gv = gv_correct * k + gv_error * (1. - k)
                #print("h=", horizon, "s: ", s_vec[i], "k:",k, time_correct, time_error, t, "gv:", gv )
                gv_all[i] = t + self.discount * gv
            else:
                t = time_correct
                gv = gv_correct
                gv_all[i] = t + self.discount * gv

        return gv_all if horizon == self.horizon else np.amin(gv_all)



    #########################
    def reset( self, command_ids, available_strategies ):
        self.custom_reset_params()
        self.command_ids = command_ids
        self.set_available_strategies( available_strategies )
        self.memory = ILHP_Model.Memory( command_ids )
        initial_values = [ 0 ] * len( available_strategies )
        self.memory.set_initial_perseveration_value( command_ids, initial_values )
            
        



        



