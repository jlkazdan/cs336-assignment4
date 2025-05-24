import torch
import numpy as np
import regex as re
import torch.nn as nn
from collections import defaultdict
import ast 
import multiprocessing as mp
import concurrent.futures
import multiprocessing as mp
from multiprocessing import Pool  
import time
from multiprocessing import Process, Queue

def iterator():
    for i in range(1000):
        yield i

def producer(iterator, queue):
    for record in iterator:
        queue.put(record)

def print_it(f):
    for ele in f:
        print(ele)

def main():
    func = iterator()
    functions = [func for i in range(10)]
    queue = Queue(maxsize = 10)
    p = Process(target = producer, args = (queue))
    with Pool(10) as p:
        p.map(print_it, functions)

if __name__ == '__main__':
    main()
        

