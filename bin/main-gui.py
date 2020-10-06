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



if __name__=="__main__":
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
    build_interface()  






