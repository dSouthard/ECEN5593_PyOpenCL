
# coding: utf-8

# In[1]:

import matplotlib.pyplot as plt
import pyopencl as cl
import numpy as np
import time
get_ipython().magic(u'matplotlib inline')


# In[4]:

# Get opencl devices:
plat = cl.get_platforms()
devices = plat[0].get_devices()
#print "My GPU:",devices[0]
print "My CPU:",devices[0]

# Create contexts for my devices
#ctx_gpu = cl.Context([devices[0]])
#ctx_cpu = cl.Context([devices[1]])

#print ctx_gpu
#print ctx_cpu


# In[5]:

# OpenCL vector addition function
def opencl_vectorAdd(a, b, ctx):

    queue = cl.CommandQueue(ctx) # create a queue to schedule the kernel to run on the device

    # Create memory buffers
    mf = cl.mem_flags
    a_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a)
    b_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b)
    dest_buf = cl.Buffer(ctx, mf.WRITE_ONLY, b.nbytes)

    # OpenCL code 
    prg = cl.Program(ctx, """
        __kernel void vectorAdd(__global float *output,
                                __global const float *in_A,
                                __global const float *in_B)
        {
            int id = get_global_id(0);        // get global thread ID
            output[id] = in_A[id] + in_B[id]; // perform vector adition
        }
        """).build()

    result = np.empty_like(a) # place to store the result
    prg.vectorAdd(queue, a.shape, None, dest_buf, a_buf, b_buf).wait() # do the vector add
    cl.enqueue_copy(queue, result, dest_buf) # copy the results from buffer into result
    #print "\nresult",result    
    return result


# In[6]:

# Python vector addition function
def py_vectorAdd(vec_a, vec_b):
    vec_c = np.zeros(len(vec_a))
    if len(vec_a) != len(vec_b):
        print "Vector A is not the same size as vector B."
        print "Vector A has length", len(vec_a),
        print "while vector B has length", len(vec_b)
    else:
        for i in range(len(vec_c)):
            vec_c[i] = vec_a[i] + vec_b[i]
    return vec_c


# In[8]:

# Test 
a = np.arange(0,55,5).astype(np.float32)
b = np.arange(0,55,5).astype(np.float32)
print "Vector A:\n", a, "\nVector B:\n", b, "\nResults:"
print py_vectorAdd(a,b)
print opencl_vectorAdd(a, b, cl.Context([devices[0]]))
#print opencl_vectorAdd(a, b, cl.Context([devices[1]]))


# In[13]:

# Execution time comparisons:

ex_time = np.zeros(3)

sz = 100000000
a = np.random.rand(sz).astype(np.float32)
b = np.random.rand(sz).astype(np.float32)

start = time.time()
py_vectorAdd(a,b)
end = time.time()
ex_time[0] = end - start

print "\nTime taken for python vector_add:\n {0} seconds".format(ex_time[0])

#start = time.time()
#opencl_vectorAdd(a, b, ctx=ctx_gpu)
#end = time.time()
#print "Time taken for OpenCL GPU vector_add: {0} seconds".format(end - start)

#start = time.time()
#opencl_vectorAdd(a, b, ctx=ctx_cpu)
#end = time.time()
#print "Time taken for OpenCL CPU vector_add: {0} seconds".format(end - start)

for dev in range(len(devices)):
    start = time.time()
    opencl_vectorAdd(a, b, cl.Context([devices[dev]]))
    end = time.time()
    ex_time[dev+1] = end - start
    print "Time taken for OpenCL vector_add on:", str(devices[dev]).split('\'')[1], "\n {0} seconds".format(ex_time[dev+1])


# In[15]:

# Plot the data:
names = ['Python', 'OpenCL CPU']#, 'OpenCL GPU']
ax = plt.subplot(111)

plt.xlabel('Device')
plt.ylabel('Execution time (s)')
plt.title('Execution time for Vector Add')
plt.grid(True)
bins = map(lambda x: x-0.5/2,range(1,len(ex_time)+1))
ax.bar(bins,ex_time,0.5)
ax.set_xticks(map(lambda x: x, range(1,len(ex_time)+1)))
ax.set_xticklabels(names,rotation=45, rotation_mode="anchor", ha="right")
plt.show()

# Plot the data to compare CPU to GPU (if there is also a GPU):

#ax = plt.subplot(111)
#plt.xlabel('Device')
#plt.ylabel('Execution time (s)')
#plt.title('Execution time (CPU vs GPU)')
#plt.grid(True)
#bins = map(lambda x: x-0.5/2,range(1,len(ex_time[1:3])+1))
#ax.bar(bins,ex_time[1:3],0.5)
#ax.set_xticks(map(lambda x: x, range(1,len(ex_time[1:3])+1)))
#ax.set_xticklabels(names[1:3],rotation=45, rotation_mode="anchor", ha="right")
#plt.show()


# In[ ]:



