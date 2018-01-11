# coding=utf-8


import sys  
sys.path.append("..")
import time
import string
import random


def id_generator(size=17, chars=string.ascii_uppercase + string.digits):
    r_id = ''.join(random.choice(chars) for _ in range(size))
    return '888%s' % str(r_id)