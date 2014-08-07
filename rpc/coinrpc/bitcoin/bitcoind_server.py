#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------
# Copyright 2014 Halfmoon Labs, Inc.
# All Rights Reserved
#-----------------------

from bitcoinrpc.authproxy import AuthServiceProxy

from commontools import log, error_reply

#---------------------------------------
class BitcoindServer(object):

	#-----------------------------------
	def __init__(self, server, port, user, passwd, use_https=True, passphrase=None):
		
		self.passphrase = passphrase
		self.server = server 

		#self.bitcoind = bitcoinrpc.connect_to_remote(user, passwd, 
		#								host=server, port=port, 
		#								use_https=use_https)

		self.bitcoind = AuthServiceProxy("https://" + user + ':' + passwd + '@' + server + ':' + port)

	#-----------------------------------
	def blocks(self):
		reply = {}
		info = self.bitcoind.getinfo()
		reply['blocks'] = info['blocks']
		return reply


	#-----------------------------------
	#helper function
	def unlock_wallet(self, timeout = 120):

		info = self.bitcoind.walletpassphrase(self.passphrase, timeout)
		return info             #info will be True or False


	#-----------------------------------
	def sendtoaddress(self, bitcoinaddress, amount):
	
		try:
			status = self.bitcoind.sendtoaddress(bitcoinaddress, float(amount))
			return status 
		except Exception as e:
			return error_reply(str(e))

	#-----------------------------------
	def validateaddress(self, bitcoinaddress):
	
		try:
			status = self.bitcoind.validateaddress(bitcoinaddress)
			return status
		except Exception as e:
			return error_reply(str(e))

	#-----------------------------------
	def importprivkey(self, bitcoinprivkey, label='', rescan=False):
	
		try:
			if rescan is True: 
				status = self.bitcoind.importprivkey(bitcoinprivkey, label, 'true')
			else:
				status = self.bitcoind.importprivkey(bitcoinprivkey, label, 'false') 
			return status
		except Exception as e:
			return error_reply(str(e))

	#-----------------------------------
	def sendtousername(username, bitcoin_amount):

		#Step 1:get the bitcoin address using onename.io API call
		url = "http://onename.io/" + username + ".json"
		r = requests.get(url)
		data = r.json()
		
		try:
			bitcoin_address = data['bitcoin']['address']
		except:
			bitcoin_address = ""

		reply = {} 

		#Step 2: send bitcoins, using bitcoind to that address  
		if bitcoin_address != "":
		
			if self.unlock_wallet():

				#send the bitcoins...
				tx = self.sendtoaddress(bitcoin_address, float(bitcoin_amount))
				reply['status']=200
				reply['tx'] = tx
				return reply

		return error_reply("couldn't send BTC")
