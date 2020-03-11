from alpha_beta_model_abstract import *
import math


################################################
#                                              #
#Implementation of the alpha/beta abstractclas #
#                                              #
################################################
class Alpha_Beta_Model(Alpha_Beta_Model_Abstract):

    
    def __init__(self, env, name):
        super().__init__(env, name)
        
  
    ###########################
    def update_model(self, step, _memory = None):
        memory = self.memory if _memory == None else _memory
        self.min_time = 0.4
        action = Action(step.cmd, step.action.strategy)
        a = action.to_string()
        cleaned_time = step.time if step.time < self.max_time else self.max_time
        reward = 1. - math.log(1+ cleaned_time - self.min_time) / math.log(1+ self.max_time - self.min_time)


        prev_RW_values = dict()
        if self.has_RW_values():
            for s in self.available_strategies :
                a_ctrl = Action(step.cmd, s).to_string()
                prev_RW_values[ a_ctrl ] =  memory.value[ 'RW' ][ a_ctrl ]

        if 'DECAY' in self.params.value.keys() :
            s = Strategy.HOTKEY
            decay = self.params.value['DECAY']
            for cmd in self.env.commands:
                if cmd != step.cmd and s != step.action.strategy:
                    a_cs = Action(cmd, s).to_string()
                    memory.value['RW'][ a_cs ] += decay * (0 -  memory.value['RW'][ a_cs ] )

        if 'IG_LEARNING' in self.params.value.keys() :
            alpha_IG_Learning = self.params.value['IG_LEARNING']
            if action.strategy == Strategy.LEARNING and step.success == True:
                a_ig = Action(step.cmd, Strategy.HOTKEY).to_string()
                memory.value[ 'RW' ][ a_ig ] +=  alpha_IG_Learning * (1. -  memory.value['RW'][ a_ig ] )    
                #print("IG: ", tmp, self.memory.value[ 'RW' ][ a_ig ],  )

        if 'IG_MENU' in self.params.value.keys() :
            alpha_IG_Menu = self.params.value['IG_MENU']
            if action.strategy == Strategy.MENU and step.success == True:
                a_ig = Action(step.cmd, Strategy.HOTKEY).to_string()
                memory.value[ 'RW' ][ a_ig ] +=  alpha_IG_Menu * (1. -  memory.value['RW'][ a_ig ] )   


        value_names = self.alpha.keys()
        for name in value_names:
            alpha = self.alpha[ name ]

            if name == 'RW' :       #Rescorla Wagner
                memory.value[ name ][ a ] += alpha * (reward -  memory.value[name][ a ] )    

            if name == "CK" :         # Choice Kernel
                #print("updaate CK")
                for s in self.available_strategies:
                    a_ck = Action(step.cmd, s).to_string()
                    a_t_k = 1. if action.strategy == s else 0.
                    memory.value[ name ][ a_ck ] +=  alpha * (a_t_k -  memory.value[ name ][ a_ck ] )

        #CTRL should be after all other modes
        if "CTRL" in value_names:
            gain = 0
            alpha = self.alpha["CTRL"]
            for s in self.available_strategies :
                a_ctrl = Action(step.cmd, s).to_string()
                gain += abs( memory.value[ 'RW' ][ a_ctrl ] - prev_RW_values[a_ctrl] )
            memory.value[ "CTRL" ][ a ] += alpha * (gain -  memory.value["CTRL"][ a ] )    


        # if name == "IG_OLD" :         # Informtion gain
        #     info_gain = step.information_gain 
        #     if info_gain <0  :
        #         info_gain = self.information_gain(step.cmd, step.action.strategy, step.success)

        #     self.memory.value[ name ][ a ] = info_gain
        #     self.memory.hotkey_knowledge[step.cmd ] += info_gain

        


    # ###########################
    # def information_gain(self, cmd, strategy, success):
    #     if not success:
    #         return 0
    #     elif strategy == Strategy.MENU:
    #         return 0
    #     else:
    #         alpha = self.alpha_from_name('IG')
    #         return alpha * (1. - self.memory.hotkey_knowledge[cmd] )


    # ###########################
    # def generate_step(self, cmd_id, date, action):
    #     result = StepResult()
    #     result.cmd = cmd_id
    #     result.action = action.copy() #probably false if it is not the correct cmd_iod
    #     result.success = (action.cmd == cmd_id)  #always correct
    #     result.time = self.time(action, result.success)
    #     result.information_gain = 0
    #     return result

                


