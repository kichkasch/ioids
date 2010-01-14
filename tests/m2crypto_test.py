#!/usr/bin/python

from M2Crypto import DSA

dsainstance = DSA.gen_params(512)

print dsainstance
