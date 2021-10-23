# -*- coding: utf-8 -*-
# coding: utf-8

# ba_meta require api 6
import ba,_ba
import json

# for flask app ==================
import os
import flask

from flask import request , jsonify
import _thread



stats=[{},[],{"cpu":0,"ram":0}]

class livestats(object):
	def __init__(self):
		self.timer=ba.Timer(5,ba.Call(self.getinfo),timetype=ba.TimeType.REAL,repeat=True)

	def getinfo(self):
		liveplayer={}
		global stats
		for i in _ba.get_game_roster():
			id=json.loads(i['spec_string'])["n"]
			try:
				liveplayer[id]={'name': i['players'][0]['name_full'],
								'clientid':i['client_id']}
			except:
				liveplayer[id]-{'name': "<in-lobby>", 'clientid':i['client_id']}
		stats[0] = liveplayer
		stats[1] = _ba.get_chat_messages()
		# stats[2]["cpu"]= p.cpu_percent()
		# stats[2]["ram"]=p.virtual_memory().percent
		

livestats()

#========= flask app ============
os.environ['FLASK_APP']='bombsquadflaskapp.py'
os.environ['FLASK_ENV']= 'development'

app = flask.Flask(_name_)
app.config["DEBUG"]=False   

@app.route("/",methods=['GET'])
def home():
	return "any message here"

@app.route('/live',methods=['GET'])
def livestat():
	return jsonify(stats)

# ba_meta export plugin
class HeySmoothy(ba.Plugin):
    def __init__(self):
    	flask=_thread.start_new_thread(app.run,("0,0,0,0",80,False))

    	print("flask service")