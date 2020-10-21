import sys
import time as TIME
import numpy as np
import timeit
sys.path.append("./GUI/")
sys.path.append("./lib/")
sys.path.append("./plugins/")
sys.path.append("./plugins/loader/")
sys.path.append("./plugins/export/")
sys.path.append("./plugins/model/")


print(" read packages")
import os.path
from win import *



# def bootstrap_ci(df, repetitions = 1000, alpha = 0.05, random_state=None): 

    
#     mean_diffs = []
#     for i in range(repetitions):
#         bootstrap_sample = df.sample(n = bootstrap_sample_size, replace = True, random_state = random_state)
#         mean_diff = df.mean().iloc[1,0] - bootstrap_sample.mean().iloc[0,0]
#         mean_diffs.append(mean_diff)
# # confidence interval
#     left = np.percentile(mean_diffs, alpha/2*100)
#     right = np.percentile(mean_diffs, 100-alpha/2*100)
# # point estimate
#     point_est = df.mean().iloc[1,0] - df.groupby(classes).mean().iloc[0,0]
#     print('Point estimate of difference between means:', round(point_est,2))
#     print((1-alpha)*100,'%','confidence interval for the difference between means:', (round(left,2), round(right,2)))


#########################
def bootstrap_ci( population, size=0.75, n_replicates=1000 ):
    n = int( len(population) * size )
    replicates = np.zeros( (n_replicates, n) )
    for i in range( n_replicates ):
        replicates[i,:] = np.random.choice(population, size= n, replace = True)
    mean_replicates = np.mean( replicates, axis=1 )
    return np.percentile( mean_replicates, [2.5, 97.5] )


if __name__=="__main__":

    population = np.array( [1,1,1,1,1,1,2,3,4,5,6,7,8,9,50, 100,200])
    #population = np.array( [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
    print("population: ", np.mean(population), np.percentile(population, [2.5, 97.5] ) )
    print(" 95 percent bootstrap CI:", np.mean( population ), bootstrap_ci( population ) )

#    print( "population: ", population )
#    print( "samples : ", samples )
    #bootstrap_ci( population, repetitions = 10)
    # take 1k 'samples' from the larger population
    #samples = population[:3]
    #print( "samples: ", samples )

    #print(bs.bootstrap(samples, stat_func=bs_stats.mean))
    #print(bs.bootstrap(samples, stat_func=bs_stats.std))



    # original = np.array( [0,5,2,3,4,5] )
    # mycopy = np.copy( original )
    # mycopy = np.delete(mycopy, 1)
    # print("===================", original, mycopy)

    # original = [0,5,2,3,4,5]
    # mycopy = original[:]
    # mycopy.remove(3)
    # original.remove(0)
    # print("===================", original, mycopy)

    #my_vec = [10] * 1000
    # start = TIME.time()
    # my_vec_res = copy.copy( my_vec)
    # stop = TIME.time()
    # print("copy time:", stop-start )

    # start = TIME.time()
    # my_vec_res = [ s for s in my_vec ]
    # stop = TIME.time()
    # print("[] time:", stop-start )

    # start = TIME.time()
    #timeit.timeit('"-".join(str(n) for n in range(100))', number=10000)
    #print( timeit.timeit( stmt='my_vec_res = my_vec[:]' , setup='my_vec = [10] * 10000', number=10000) )
    # stop = TIME.time()
    # print("slice (pas copy) time:", stop-start )

    # start = TIME.time()
    #print( timeit.timeit( stmt='my_vec_res = my_vec.copy()', setup='my_vec = [10] * 10000', number=10000) )
    #print( timeit.timeit( stmt='my_vec_res = copy.copy(my_vec)', setup='import copy; my_vec = [10] * 10000', number=10000) )
    # stop = TIME.time()
    # print("array.copy time:", stop-start )


    # start = TIME.time()
    # my_vec_res = np.copy(my_vec)
    # stop = TIME.time()
    # print("np.copy time:", stop-start )

    # my_vec = np.array( [10]* 1000 )
    # start = TIME.time()
    # my_vec_res = np.copy(my_vec)
    # stop = TIME.time()
    # print("np.copy sur un np time:", stop-start )



    #print("coucou main")
    # my_vec = np.array( [1,2,3,4,5] )
    # print(my_vec)
    # print( my_vec * 5)
    # a = np.zeros(0)
    # b = np.zeros(0, dtype=int)
    # c = np.empty(5)
    # d = np.empty(5, dtype=int)
    # e = np.array([])
    # f = np.array([], dtype=int)
    # print( a, b, c, d, e, f )
    # a = np.append( a, int(3) )
    # b = np.append( b, 3)
    # c = np.append( c, 3)
    # d = np.append( d, 3)
    # e = np.append( e, 3)
    # f = np.append( f, 3)
    
    # print( a, b, c, d, e, f )
    # print(None)
    # a = np.array([1,2,3,4,5])
    # b = 3
    # print( np.setdiff1d(a,b) )
    build_interface()  






