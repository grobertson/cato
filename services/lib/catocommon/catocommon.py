import os.path
from catocryptpy import catocryptpy
import pymysql
import time
from catodb import catodb

def read_config():

	home = "."
	filename = os.path.join(home, "conf", "cato.conf")		
	if not os.path.isfile(filename):
		msg = "The configuration file "+ filename +" does not exist."
		raise Exception(msg)
	try:
		fp = open(filename, 'r')
	except IOError as (errno, strerror):
		msg = "Error opening file " + filename +" "+ format(errno, strerror)
		raise IOError(msg)
	
	key_vals = {}
	contents = fp.read().splitlines()
	enc_key = ""
	enc_pass = ""
	for line in contents:
		line = line.strip()
		if len(line) > 0 and not line.startswith("#"):
			row = line.split()
			key = row[0].lower()
			if len(row) > 1:
				value = row[1]
			else:
				value = ""
			if key == "key":
				enc_key = value
			elif key == "password":
				enc_pass = value
			else:
				key_vals[key] = value
	un_key = catocryptpy.decrypt_string(enc_key,"")
	key_vals["key"] = un_key
	un_pass = catocryptpy.decrypt_string(enc_pass,un_key)
	key_vals["password"] = un_pass
		
	return key_vals

class CatoService:
        def __init__(self, process_name):
		self.host_domain = os.getlogin() +'@'+ os.uname()[1]
		self.host = os.uname()[1]
		self.platform = os.uname()[0]
		self.user = os.getlogin()
		self.my_pid = os.getpid()
		self.delay = 3
		self.loop = 10
		self.mode = "on"
		self.master = 1
		self.process_name = process_name
		self.initialize_logfile()

	def initialize_logfile(self):
		home = "."
		self.logfile_name = os.path.join(home, "logfiles", self.process_name.lower()+".log")

	def output(self,*args):
		output_string = time.strftime("%Y-%m-%d %H:%M:%S ") + "".join(str(s) for s in args) + "\n"
		print output_string 
		fp = open(self.logfile_name, 'a')
		fp.write(output_string)
		fp.close


	def check_registration(self):

		# Get the node number
		sql = "select id from tv_application_registry where app_name = '"+self.process_name+ \
			"' and app_instance = '"+self.host_domain+"'"

		result = self.db.select_col(sql)
		if not result:
			self.output(self.process_name +" has not been registered, registering...")
			self.register_app()
			result = self.db.select_col(sql)
			self.instance_id = result
		else:
			self.output(self.process_name +" has already been registered, updating...")
			self.instance_id = result
			self.output("application instance = %d" % self.instance_id)
			self.db.exec_db("""update application_registry set hostname = %s, userid = %s,
				 pid = %s, platform = %s where id = %s""", 
				(self.host_domain, self.user, str(self.my_pid), self.platform,
				 self.instance_id))

	def register_app(self):
		self.output("Registering application...")

		sql = "insert into application_registry (app_name, app_instance, master, logfile_name, " \
			"hostname, userid, pid, platform) values ('"+self.process_name+ \
			"', '"+self.host_domain+"',1, '"+self.process_name.lower()+".log', \
			'"+self.host+"', '"+self.user+"',"+str(self.my_pid)+",'"+self.platform+"')"
		self.db.exec_db(sql)
		self.output("Application registered.")

	def update_heartbeat(self):
		sql = "update application_registry set heartbeat = now() where id = %s"
		self.db.exec_db(sql,(self.instance_id))
	
	def startup(self):
		self.output("####################################### Starting up ", self.process_name, 
				" #######################################")
		config = read_config()
		self.db = catodb.Db()
		conn = self.db.connect_db(server=config["server"], port=config["port"], user=config["user"], 
						password=config["password"], database=config["database"])
		self.check_registration()
		self.update_heartbeat()


	def end(self):
		self.db.close()




