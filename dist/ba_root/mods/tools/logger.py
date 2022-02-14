
import ba,_ba
import datetime;
import os
import threading
# ct stores current time

import setting
settings = setting.get_settings_data()

if settings['discordbot']["enable"]:
	from tools import discordbot


path=_ba.env()['python_directory_user']
serverdata=os.path.join(path,"serverData" + os.sep)
chats=[]
joinlog=[]
cmndlog=[]
misclogs=[]

def log(msg,mtype='sys'):
	global chats,joinlog,cmndlog,misclogs

	if settings['discordbot']["enable"]:
		m=msg.replace('||','|')
		discordbot.push_log("***"+mtype+":***"+m)

	ct=datetime.datetime.now()
	msg=str(ct)+": "+msg +"\n"
	if mtype=='chat':
		chats.append(msg)
		if len(chats) >10:
			dumplogs(chats,"chat").start()
			chats=[]
	elif mtype=="playerjoin":
		joinlog.append(msg)
		if len(joinlog)>3:
			dumplogs(joinlog,"joinlog").start()
			joinlog=[]
	elif mtype=='chatcmd':
		cmndlog.append(msg)
		if len(cmndlog)>3:
			dumplogs(cmndlog,"cmndlog").start()
			cmndlog=[]

	else:
		misclogs.append(msg)
		if len(misclogs)>5:
			dumplogs(misclogs,"sys").start()
			misclogs=[]


class dumplogs(threading.Thread):
	def __init__(self,msg,mtype='sys'):
		threading.Thread.__init__(self)
		self.msg=msg
		self.type=mtype

	def run(self):


		if self.type=='chat':
			
			f=open(serverdata+"Chat Logs.log","a+")
			


		elif self.type=='joinlog':
			f=open(serverdata+"joining.log","a+")
			

		elif self.type=='cmndlog':
			f=open(serverdata+"cmndusage.log","a+")
			
		else:
			f=open(serverdata+"logs.log","a+")
		for m in self.msg:
			f.write(m)
		f.close()






