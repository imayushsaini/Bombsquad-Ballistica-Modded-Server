
import ba,_ba
import datetime;
import os
# ct stores current time



path=_ba.env()['python_directory_user']
serverdata=os.path.join(path,"serverData" + os.sep)
class log(object):
	def __init__(self,msg,type='sys'):
		ct = datetime.datetime.now()
		msg=ct+msg

		if type=='chat':
			
			f=open(serverdata+"Chat Logs.log","a+")
			


		elif type=='playerjoin':
			f.open(serverdata+"joining.log","a+")
			

		elif type=='chatcmnd':
			f.open(serverdata+"cmndusage.log","a+")
			
		else:
			f=open(serverdata+"logs.log","a+")

		f.write(msg)
		f.close()






