'''
------------------------------------------------------------------------------------------
This file contains string parsing utilities
------------------------------------------------------------------------------------------
'''

import functools
import time

#Create csv file titles with dates for better organization
def reduce_concat(x, sep=""):
    return functools.reduce(lambda x, y: str(x) + sep + str(y), x)

#"join" lists
def paste(*lists, sep=" ", collapse=None):
    result = map(lambda x: reduce_concat(x, sep=sep), zip(*lists))
    if collapse is not None:
        return reduce_concat(result, sep=collapse)
    return list(result)

#Function to replace various terms
def replace2(string, substitutions):

    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)

#Set items that aren't found in string search to 100000 so we can evaluate by less than so song title isn't obliterated
def infinite_neg(L):
    z = 0
    for i in L:
        if i == -1:
            i = i * -100000
            L[z] = i
        z += 1
    return L

def time_start():
    t1_start = time.perf_counter()
    t2_start = time.process_time()
    
    return (t1_start, t2_start)

def time_stop(t1, t2):
    t1_stop = time.perf_counter()
    t2_stop = time.process_time()
    duration = (t1_stop-t1)/60
    process_time = (t2_stop-t2/60)
    
    return (duration, process_time)