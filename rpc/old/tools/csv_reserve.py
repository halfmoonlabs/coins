#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
import csv
import requests
import json
import os
import binascii
from onename_register import register_name
from coinrpc.coinrpc import check_registration

from pymongo import Connection
con = Connection()
db = con['namecoin']
queue = db.queue

#-----------------------------------
def get_random_hex(size=10):
    #every byte of data is converted into the corresponding 2-digit hex representation
    return binascii.b2a_hex(os.urandom(size))

#-----------------------------------
def format_key_value(key, name=None):

    #need u/ for OneName usernames
    key = 'u/' + key.lower()

    value = {}

    value['status'] = "reserved"

    if name is not None and name != '' and name != ' ': 

        value["message"] = "This OneName username is reserved for " + name.lstrip(' ') 
        value["message"] += ". If this is you, please email reservations@onename.io to claim it for free."

    else:

        value["message"] = "This OneName username was parked to evade name squatting, but can be made available upon reasonable request"
        value["message"] += " at no charge. If you are interested in this name, please email reservations@onename.io with your twitter"
        value["message"] += " handle and why you would like this particular name."

    return key, value 


#-----------------------------------
#codes are only assigned to 'reserved' names
def assign_code(key):
    
    reply = queue.find_one({'key':key})    

    code = get_random_hex()
        
    if reply['activated'] is True:
    
        if not 'code' in reply:
            print "Creating code for: " + reply['key']
            reply['code'] = code 
            queue.save(reply)
        else: 
            pass
            #print reply['key'] + ',' + reply['code']
    else:
        print "Not activated: " + reply['key']

#-----------------------------------
def main_loop(key, name=None):

    key, value = format_key_value(key,name)

    reply = queue.find_one({'key':key})

    if check_registration(key) or reply is not None:
        print "already registered: " + key
        assign_code(key)
    else:
        #not in DB 
        print "not registered: " + key
        register_name(key,value)
    
#-----------------------------------
if __name__ == '__main__':

    with open('tools/data.csv') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            main_loop(row[0], row[1])

