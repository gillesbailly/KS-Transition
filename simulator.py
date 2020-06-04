import sys
import os.path
from experiment import *
import csv
import numpy as np
from util import *
from math import *
import pandas as pd
import time
import copy
from scipy.optimize import *
import datetime

##########################################
# how to deal with q0?
# it is technique dependent
# how to deal wiht errors...

##########################################
#                                        #
#             Simulator                  #
#                                        #
##########################################
class Simulator(object):


    ###################
    def __init__(self, environment):
        self.name = "Simulator"
        self.env = environment
        self.ignore_count = 0


    ###################################
    def save(self, filename, sims):
        with open(filename, mode='w') as log_file:
            writer = csv.writer(log_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            header = ['model', 'param', 'sim', 'episode', 'trial', 'n_selection', 'stimulus', 'occ', 'cmd', 'strategy', 'method', 'time', 'success']
            writer.writerow( header)
    
            for i in range( len(sims) ):
                h = sims[i]
                n_selection = len(h.command_sequence)
                episode = h.episode_id
                occ = dict()
                for cmd in h.commands:
                    occ[cmd] = 0
                for j in range( n_selection ):
                    stimulus = h.command_sequence[j]
                    strategy = h.action[j].strategy_str()
                    method = h.action[j].method_str()

                    occ[ stimulus ] = occ[ stimulus ] + 1
                    row = [h.model_name, h.params, i, episode, j + 1, n_selection, stimulus, occ[ stimulus ],  h.cmd[j], strategy, method, h.time[j], h.success[j] ]
                    writer.writerow(row)


    ###################################
    #
    # Test model against empirical data
    # 
    ###################################
    def test_model(self, model, filename, raw, _filter):
        experiment = Experiment( filename, self.env.value['n_strategy'], raw, _filter )
        sims = self.test_model_data(model, experiment)
        return sims


        
    ###################################
    def test_model_data(self,model, experiment):
        sims = []
        #print("debug experiment data: ", len(experiment.data) )
        for d in experiment.data:
            data = copy.deepcopy(d)
            self.env.update_from_empirical_data( copy.copy(data.commands), copy.copy(data.cmd), 3 )
            available_strategies = self.strategies_from_technique( data.technique_name )
            model.reset( available_strategies )
            log_likelyhood = 0
            data.model_name = model.name
            data.params = model.get_param_value_str()
            #print("debug env cmd seq: ", len(self.env.cmd_seq) )
            #print( data.user_action )
            for date in range( 0, len(self.env.cmd_seq) ):
                cmd = self.env.cmd_seq[date]

                #result from the model
                action, prob_vec = model.select_action( cmd, date ) #action correct
                res = model.generate_step(cmd, date, action)
                a_vec = model.get_actions_from( cmd )
                probs = values_long_format(a_vec, prob_vec)

                data.update_history_short( action, probs, res.time, res.success )
                if model.has_RW_values():
                    data.rw_vec.append( values_long_format(a_vec, model.values( 'RW', cmd, date )) )

                if model.has_CK_values():
                    data.ck_vec.append( values_long_format(a_vec, model.values('CK', cmd, date )) )
                #if model.has_CTRL_values():
                #    history.ck_vec.append( values_long_format(a_vec, model.values('CTRL', cmd, date )) )

                if model.has_knowledge() :
                    data.knowledge.append( model.knowledge( cmd ) )

                # model against empirical data
                user_action = Action(cmd,data.user_action[date].strategy)
                user_action_prob = prob_vec[ a_vec.index(user_action) ]
                user_step = StepResult(cmd, user_action,  data.user_time[date], data.user_success[date])
                
                data.user_action_prob.append( user_action_prob)
                if user_action_prob == 0:
                    user_action_prob = 0.00000001

                log_likelyhood += log2(user_action_prob)

                #update the model with empirical data
                model.update_model( user_step )
                
            data.fd  = FittingData( model, data.user_id, data.technique_id, log_likelyhood, len(self.env.cmd_seq),  data.get_hotkey_count() )
            sims.append(data)
        return sims        




    ###################################
    # run the model on n_episode
    # do not change the values of the parameters
    ###################################
    def run(self, model, n_episode):
        #print('\n========================= run simulation =====================')
        #print("model: ", model)
        sims = []

        for i in range(n_episode):
            self.env.update()
            history = History()
            history.set_commands( self.env.commands, self.env.cmd_seq, None, None)
            history.set_model( model.name, model.get_param_value_str() )
            history.episode_id = i
            model.reset( [Strategy.MENU, Strategy.HOTKEY, Strategy.LEARNING ] )
            
            for date in range( 0, len(self.env.cmd_seq) ):
                cmd = self.env.cmd_seq[date]
                a_vec = model.get_actions_from( cmd )
                action, prob_vec = model.select_action( cmd, date) #action correct
                res = model.generate_step(cmd, date, action)
                model.update_model(res)
                history.update_history_long(res.cmd, res.action, prob_vec, res.time, res.success)
                if model.has_RW_values():
                    history.rw_vec.append( values_long_format(a_vec, model.values( 'RW', cmd, date )) )

                if model.has_CK_values():
                    history.ck_vec.append( values_long_format(a_vec, model.values('CK', cmd, date )) )

                if model.has_CTRL_values():
                    history.ck_vec.append( values_long_format(a_vec, model.values('CTRL', cmd, date )) )

                    

            sims.append( history )
        return sims


    def simple_simulate(self, model, data) :
        data.set_model( model.name, model.get_param_value_str() )
        self.env.update_from_empirical_data(data.commands, data.cmd, 3 )
        available_strategies = self.strategies_from_technique( data.technique_name )
        model.reset( available_strategies )

        for date in range( 0, len(self.env.cmd_seq) ):
            cmd = self.env.cmd_seq[date]
            #a_vec = model.get_actions_from( cmd )
            a_vec = model.get_actions_from( cmd )
            action, prob_vec = model.select_action( cmd, date) #action correct
            res = model.generate_step(cmd, date, action)
            model.update_model(res)
            data.update_history_long(res.cmd, res.action, prob_vec, res.time, res.success)
            if model.has_RW_values():
                data.rw_vec.append( values_long_format(a_vec, model.values( 'RW', cmd, date )) )

            if model.has_CK_values():
                data.ck_vec.append( values_long_format(a_vec, model.values('CK', cmd, date )) )

            if model.has_CTRL_values():
                data.ck_vec.append( values_long_format(a_vec, model.values('CTRL', cmd, date )) )

            if model.has_knowledge() :
                    data.knowledge.append( model.knowledge( cmd ) )

        return data



















    ###################################
    # explore model
    # this method is recursive.
    # 
    ###################################
    def explore(self, model, params, n_episode):
        if len(params) == 0:
            return []

        params_saved = copy.deepcopy( model.params )
        res = []
        p = params[0]
        print("p: ", params[0])
        a_info = model.params.get_info(p)

        for v in np.arange(a_info[1], a_info[2], a_info[3]):    #1 min, 2. max, 3. step
            model.params.value[p] = v
            sims = []
            if len(params) == 1:
                sims = self.run( model, n_episode)
            else:
                sublist = params[1: len(params) ]
                sims = self.explore(model, sublist, n_episode)
            res = res + sims
            #print("explore: ",  len(res) )

        model.params = params_saved
        return res



    def parse_params(self, params):
        name_vec = []
        value_vec = []
        param_vec = params.split(',')
        for p in param_vec:
            d = p.split(':')
            name_vec.append( d[0] )
            value_vec.append( d[1] )
        return name_vec, value_vec


    ###################################
    def save_loglikelyhood(self, filename, sims, overwrite = False):
        mode = 'w' if overwrite else 'a'
        exist = os.path.exists(filename)

        with open(filename, mode= mode ) as log_file:
            writer = csv.writer(log_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            if not exist or mode == 'w':
                header = ['model_name', 'user_id', 'hotkey_count', 'technique_id', 'log_likelyhood', 'n_params', 'N', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10']
                writer.writerow( header)
    
            for d in sims:
                name_vec, value_vec = self.parse_params( d.model_params )
                n_params = len( value_vec)
                for i in range( n_params, 10 ):  # fill with null values
                    value_vec.append(-1)
                row = [d.model_name, d.user_id, d.hotkey_count, d.technique_id, d.log_likelyhood, d.n_BIC_params, d.N] + value_vec
                writer.writerow(row)


    def is_tested_parameter(self, params, df_log_model):
        name_vec, value_vec = self.parse_params( params )
        n_params = len( value_vec)
        for i in range( n_params, 10 ):  # fill with null values
            value_vec.append(-1)
        #print(df_log_model.p1)
        #print(value_vec)

        res = df_log_model[ (df_log_model.p1 == float(value_vec[0])) & (df_log_model.p2 == float(value_vec[1]) ) & (df_log_model.p3 == float(value_vec[2]) )& (df_log_model.p4 == float(value_vec[3])) & (df_log_model.p5 == float(value_vec[4])) & (df_log_model.p6 == float(value_vec[5])) & (df_log_model.p7 == float(value_vec[6])) & (df_log_model.p8 == float(value_vec[7])) & (df_log_model.p9 == float(value_vec[8])) & (df_log_model.p10 == float(value_vec[9]))] 
        #print("---------------------- res: ", res, len(res.user_id))
        return len(res.user_id) == 0


    ###################################
    def explore_model_and_parameter_space(self, model_vec, experiment, overwrite= True):
        res = []

        for model in model_vec :
            self.ignore_count = 0
            df_log_model = None if overwrite else pd.read_csv('./likelyhood/log_' + model.name + '.csv', delimiter=';')

            start = time.time()
            params = list( model.get_params().value.keys() )
            sims = self.explore_parameter_space(model, params, experiment, overwrite, df_log_model)
            end = time.time()
            print("explore the model: ", model.name, " in ",  end - start)
            print("------------- ANALYSIS ---------------")
            file_name = './likelyhood/log_' + model.name + '.csv'
            self.save_loglikelyhood(file_name, sims, overwrite)
            print("we ignore ", self.ignore_count, " parameter estimations")
            res += sims
        return res


    ###################################
    def optimize_models(self, model_vec, experiment, target, fixed_params ):
        user_group = []
        if target == "all" :
            user_group = np.arange(43)
        elif target == "traditional":
            user_group = np.arange(0,43,3)
        elif target == "audio" :
            user_group = np.arange(1,43,3)
        elif target == "disable" :
            user_group = np.arange(2,43,3)
        else :
            user_group.append( int(target) )

        #filter only useful experiment data
        experiment_data =[]
        for d in experiment.data :
            if d.user_id in user_group :
                experiment_data.append( d )


        
        for model in model_vec :    
            self.start = time.time()
            param_name_vec = copy.copy( list( model.get_params().value.keys() ) )
            #param_value_vec = copy.copy( list( model.get_params().value.values() ) )
            #param_0_vec = [0.05, 0.1, 7, 2, 0.4]
            #bnds = ((0,1), (0,1), (0,12), (1.5,2.5), (0,1))
            bnds = []
            for name in param_name_vec :
                info = model.params.get_info(name)  #1 min, 2. max, 3. step
                bnds.append( [info[1], info[2] ] )
            print(param_name_vec, bnds)
            #exit(0)
            

            # for key in fixed_params :
            #     index = param_name_vec.index(key)
            #     del param_name_vec[ index ]
            #     del param_value_vec[ index ]
  

            #print(param_name_vec, param_value_vec, bnds)
            #np.zeros( len(param_name_vec) )
            
            #print( param_name_vec )
            #res = self.optimize_model(model, param_0_vec, experiment)
            #options = dict()
            #options['maxiter'] = 1
            self.minll = 10000000
            res = differential_evolution(self.model_fit, bounds = bnds, args = (param_name_vec, model, experiment_data, fixed_params) )
            #res = minimize(self.model_fit, param_value_vec, args = (param_name_vec, model, experiment_data, fixed_params), method='L-BFGS-B', bounds =bnds, options={'maxiter': 6, 'disp':0, 'eps':0.05})
                        

            res_x = res.x
            ll = res.fun
            print(res)
            #res_x = [0.05, 0.2, 7, 0.4]
            #ll = -1000
            self.end = time.time()

            print("optmize the model: ", model.name, " in ",  self.end - self.start)
            # param_res = []
            # for i in range( 0, len(res_x) ) :
            #     name = param_name_vec[ i ]
            #     v = res_x[ i ]
            #     if name == 'KM' :
            #         v = v / 10.
            #     if name == 'HORIZON' :
            #         v = int(v) 
            #     param_res.append( round(v,3) )

            # for key in fixed_params :
            #     param_res.append( fixed_params[key] )
            #     param_name_vec.append( key )
            # print(fixed_params, param_name_vec)
            file_name = './likelyhood/optimisation/log_' + model.name + '_' + target + '.csv'
            self.save_optimized_loglikelyhood(file_name, model, target, ll, param_name_vec, res.x )
            #print(res)


    ###################################
    def save_optimized_loglikelyhood(self, filename, model, target, likelyhood, param_names, param_values, overwrite = False):
        mode = 'w' if overwrite else 'a'
        exist = os.path.exists(filename)

        with open(filename, mode= mode ) as log_file:
            writer = csv.writer(log_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            if not exist or mode == 'w':
                header = ['date', 'model_name', 'target', 'log_likelyhood', 'n_params' ] + param_names
                writer.writerow( header)
            
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d %H:%M:%S")
            row = [date_str, model.name, target, likelyhood, len(param_names) ]
            for i in param_values :
                row.append ( str(round(i, 4) ) ) 

            writer.writerow(row)


    ##################################
    def model_fit(self, param_value, param_name, model, experiment_data, fixed_params):
        # for i in range(0, len(param_name) ) :
        #     name = param_name[i]
        #     if name == "HORIZON" :
        #         value = int( param_value[i] )
        #     elif name == "KM":
        #         value = param_value[i] / 10.
        #     else:
        #         value = param_value[i] 
        #     model.params.value[ name ] = value
        #     for key in fixed_params :
        #         model.params.value[key] = fixed_params[ key ]
        
        for i in range(0, len(param_name) ) :
             name = param_name[i]
             value = param_value[i]
             model.params.value[ name ] = value


        if model.name == 'trans' or 'TRANS' in model.name :
            i_KM = param_name.index('KM')
            i_KL = param_name.index('KL')
            if param_value[ i_KM ] > param_value[ i_KL ] :
                #print("km > kl")
                return 1000000

        sims = self.fast_test_model( model, experiment_data )
        log_likelyhood = 0
        
        for d in sims:
            log_likelyhood += d.log_likelyhood
        log_likelyhood / len( sims )
        if self.minll >= - log_likelyhood :
            self.minll = - log_likelyhood
            print( time.time() - self.start, ": best p &ll  ", param_value, ": ", log_likelyhood)
        #else :
        #    print( time.time() - self.start, ": p &ll  ", param_value, ": ", log_likelyhood)
            
        return - log_likelyhood

            


    ###################################
    def explore_parameter_space(self, model, param_vec, experiment, overwrite, df_log_model):
        if len(param_vec) == 0:
            return []

        param_vec_saved = copy.deepcopy( model.params )
        res = []
        #print("explore_parameter_space: ", param_vec)
        param_name = param_vec[0]
        #print("param: ", param_name)
        param_info = model.params.get_info(param_name)

        for value in np.arange(param_info[1], param_info[2] + param_info[3], param_info[3]):    #1 min, 2. max, 3. step
            model.params.value[param_name] = value
            sims = []
            if len(param_vec) == 1:
                execute = overwrite
                if not execute :
                    execute = self.is_tested_parameter(model.get_param_value_str(), df_log_model)

                if execute:
                    start = time.time()
                    sims = self.fast_test_model(model, experiment)
                    end = time.time()
                    print("wip: ", model.name, model.get_param_value_str(), end-start)
                else:
                    self.ignore_count+=1

            else:
                sub_param_vec = param_vec[ 1: len(param_vec) ]
                sims = self.explore_parameter_space(model, sub_param_vec, experiment, overwrite, df_log_model)
            res = res + sims
            

        model.params = param_vec_saved
        return res

    ###################################
    def strategies_from_technique(self, technique_name):
        #print(technique_name)
        if technique_name == "disable":
            return [Strategy.HOTKEY, Strategy.LEARNING]
        else:
            return[Strategy.MENU, Strategy.HOTKEY, Strategy.LEARNING]     

    

    ###################################
    def fast_test_model(self,model, experiment_data):
        sims = []
        max_user_id = 43
        #print("length: ", len(experiment_data) )
        for data in experiment_data:
            if data.user_id < max_user_id:
                #print("user:", data.user_id)
                self.env.update_from_empirical_data(data.commands, data.cmd, 3 )
                available_strategies = self.strategies_from_technique( data.technique_name )
                model.reset( available_strategies )
                log_likelyhood = 0
                for date in range( 0, len(self.env.cmd_seq) ):
                    cmd = self.env.cmd_seq[date]

                    # model against empirical data
                    user_step = StepResult(cmd, Action(cmd, data.user_action[date].strategy),  data.user_time[date], data.user_success[date])
                    user_action_prob = model.prob_from_action( user_step.action, date)
                
                    
                    if user_action_prob == 0:
                        user_action_prob = 0.000001
                    log_likelyhood += log2(user_action_prob)
                    #print(model.name, user_action_prob, log_likelyhood)
                    #update the model with empirical data
                    model.update_model( user_step )
 
                fd = FittingData( model, data.user_id, data.technique_id, log_likelyhood, len(self.env.cmd_seq),  data.get_hotkey_count() )
                sims.append( fd )
        return sims       



