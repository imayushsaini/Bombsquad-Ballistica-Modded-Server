# Released under the MIT License. See LICENSE for details.
cmnds=["/add","/kick"]


def exec_cmd(cmnd,arg,client_id,pbid):
	if cmnd =="/kick":
		kick(arg[0])



# ==============

def kick(client_id):
	_ba.disconnectclient(client_id)
	# do something


def add():
	# do something

def end():
	#do something
