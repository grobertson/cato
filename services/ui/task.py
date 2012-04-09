"""
SOME XML EXAMPLES
stuff = ET.fromstring(input)
lst = stuff.findall("users/user")
print len(lst)
for item in lst:
print item.attrib["x"]
item = lst[0]
ET.dump(item)
item.get("x")   # get works on attributes
item.find("id").text
item.find("id").tag
for user in stuff.getiterator('user') :
print "User" , user.attrib["x"]
ET.dump(user)
"""

import uuid
import xml.etree.ElementTree as ET
from catocommon import catocommon
import uiGlobals
import uiCommon

class Task(object):
	def __init__(self):
		self.ID = ""
		self.OriginalTaskID = ""
		self.Name = ""
		self.Code = ""
		self.Version = "1.000"
		self.Status = "Development"
		self.Description = ""
		self.DBExists = False
		self.OnConflict = "cancel" #the default behavior for all conflicts is to cancel the operation
		self.UseConnectorSystem = False
		self.IsDefaultVersion = False
		self.ConcurrentInstances = ""
		self.QueueDepth = ""
		self.ParameterXDoc = None
		#a task has a dictionary of codeblocks
		self.Codeblocks = {}

	#the default constructor (manual creation)
	def FromArgs(self, sName, sCode, sDesc):
		if not sName:
			raise Exception("Error building Task object: Name is required.")

		self.ID = str(uuid.uuid4())
		self.Name = sName
		self.Code = sCode
		self.Description = sDesc

	def FromXML(self, sTaskXML=""):
		if sTaskXML == "": return None
		
		xmlerr = "XML Error: Attribute not found."
		
		print "Creating Task object from XML"
		xTask = ET.fromstring(sTaskXML)
		
		#attributes of the <task> node
		self.ID = xTask.get("id", str(uuid.uuid4()))
		self.OriginalTaskID = self.ID
		self.Name = xTask.get("name", xmlerr)
		self.Code = xTask.get("code", xmlerr)
		self.OnConflict = xTask.get("code", "cancel") #cancel is the default action if on_conflict isn't specified
		
		# these, if not provided, have initial defaults
		self.Version = xTask.get("version", "1.000")
		self.Status = xTask.get("status", "Development")
		self.IsDefaultVersion = True
		self.ConcurrentInstances = xTask.get("concurrent_instances", "")
		self.QueueDepth = xTask.get("queue_depth", "")
		
		#text nodes in the <task> node
		_desc = xTask.find("description", xmlerr).text
		self.Description = _desc if _desc is not None else ""
		
		#CODEBLOCKS
		xCodeblocks = xTask.findall("codeblocks/codeblock")
		print "Number of Codeblocks: " + str(len(xCodeblocks))
		for xCB in xCodeblocks:
			newcb = Codeblock()
			newcb.FromXML(ET.tostring(xCB))
			self.Codeblocks[newcb.Name] = newcb

	def AsXML(self):
		root=ET.fromstring('<task />')
		
		root.set("id", self.ID)
		root.set("name", self.Name)
		root.set("code", self.Code)
		ET.SubElement(root, "description").text = self.Description
		
		#CODEBLOCKS
		xCodeblocks = ET.SubElement(root, "codeblocks") #add the codeblocks section
		
		#TODO!!! fix this to be for name, cb in self.Codeblocks!!!!
		for k in self.Codeblocks:
			#the dict can't unpack the object?
			#try it by reference
			cb = self.Codeblocks[k]
			#print cb.Name
			xCB = ET.SubElement(xCodeblocks, "codeblock") #add the codeblock
			xCB.set("name", cb.Name)
			
			#STEPS
			xSteps = ET.SubElement(xCB, "steps") #add the steps section
			
			for s in cb.Steps:
				stp = cb.Steps[s]
				#print stp
				xStep = ET.SubElement(xSteps, "step") #add the step
				xStep.set("id", stp.ID)
				xStep.set("codeblock", stp.Codeblock)
		
		return ET.tostring(root)

	
	def DBSave(self, db = None, bLocalTransaction = True):
		print "here we go"
		try:
			#if a db connection is passed, use it, else create one
			if db:
				bLocalTransaction = False
			else:
				db = catocommon.new_conn()

			if not self.Name or not self.ID:
				if bLocalTransaction:
					db.tran_rollback()
				return False, "ID and Name are required Task properties."

			if self.DBExists:
				#uh oh... this task exists.  unless told to do so, we stop here.
				if self.OnConflict == "cancel":
					sErr = "Another Task with that ID or Name/Version exists." \
						"[" + self.ID + "/" + self.Name + "/" + self.Version + "]" \
						"  Conflict directive set to 'cancel'. (Default is 'cancel' if omitted.)"
					if bLocalTransaction:
						db.tran_rollback()
					return False, sErr
				else:
					#ok, what are we supposed to do then?
					if self.OnConflict == "replace":
						"""					
						#whack it all so we can re-insert
						#but by name or ID?  which was the conflict?
						#no worries! the _DBExists function called when we created the object
						#will have resolved any name/id issues.
						#if the ID existed it doesn't matter, we'll be plowing it anyway.
						#by "plow" I mean drop and recreate the codeblocks and steps... the task row will be UPDATED
						oTrans.Command.CommandText = "delete from task_step_user_settings" \
							" where step_id in" \
							" (select step_id from task_step where task_id = '" + self.ID + "')"
						if not oTrans.ExecUpdate():
							return False, db.error
						oTrans.Command.CommandText = "delete from task_step where task_id = '" + self.ID + "'"
						if not oTrans.ExecUpdate():
							return False, db.error
						oTrans.Command.CommandText = "delete from task_codeblock where task_id = '" + self.ID + "'"
						if not oTrans.ExecUpdate():
							return False, db.error
						
						#update the task row
						oTrans.Command.CommandText = "update task set" \
							" version = '" + self.Version + "'," \
							" task_name = '" + ui.TickSlash(self.Name) + "'," \
							" task_code = '" + ui.TickSlash(self.Code) + "'," \
							" task_desc = '" + ui.TickSlash(self.Description) + "'," \
							" task_status = '" + self.Status + "'," \
							" default_version = '" + (1 if self.IsDefaultVersion else 0) + "'," \
							" concurrent_instances = '" + self.ConcurrentInstances + "'," \
							" queue_depth = '" + self.QueueDepth + "'," \
							" created_dt = now()," \
							" parameter_xml = " + ("'" + ui.TickSlash(ET.fromstring(self.ParameterXDoc)) + "'" if self.ParameterXDoc else "null") \
							" where task_id = '" + self.ID + "'"
						if not oTrans.ExecUpdate():
							return False, db.error
						#need to update this to work without session
						#ui.WriteObjectChangeLog(Globals.acObjectTypes.Task, this.ID, this.Name, "Task Updated");
						"""
					elif self.OnConflict == "minor":					
						"""						
						self.IncrementMinorVersion()
						self.DBExists = False
						self.ID = ui.NewGUID()
						self.IsDefaultVersion = False
						#insert the new version
						oTrans.Command.CommandText = "insert task" \
							" (task_id, original_task_id, version, default_version," \
							" task_name, task_code, task_desc, task_status, created_dt)" \
							" values " \
							" ('" + self._ID + "'," \
							" '" + self._OriginalTaskID + "'," \
							" " + self._Version + "," + " " \
							(1 if self._IsDefaultVersion else 0) + "," \
							" '" + ui.TickSlash(self._Name) + "'," \
							" '" + ui.TickSlash(self._Code) + "'," \
							" '" + ui.TickSlash(self._Description) + "'," \
							" '" + self._Status + "'," \
							" now())"
						if not oTrans.ExecUpdate():
							return False
						"""
					elif self.OnConflict == "major":
						"""
						self.IncrementMajorVersion()
						self.DBExists = False
						self.ID = ui.NewGUID()
						self.IsDefaultVersion = False
						#insert the new version
						oTrans.Command.CommandText = "insert task" \
							" (task_id, original_task_id, version, default_version," \
							" task_name, task_code, task_desc, task_status, created_dt)" \
							" values " \
							" ('" + self._ID + "'," \
							" '" + self._OriginalTaskID + "'," \
							" " + self._Version + "," \
							" " + (1 if self._IsDefaultVersion else 0) + "," \
							" '" + ui.TickSlash(self._Name) + "'," \
							" '" + ui.TickSlash(self._Code) + "'," \
							" '" + ui.TickSlash(self._Description) + "'," \
							" '" + self._Status + "'," \
							" now())"
						if not oTrans.ExecUpdate():
							return False
						"""
					else:
						#there is no default action... if the on_conflict didn't match we have a problem... bail.
						return False, "There is an ID or Name/Version conflict, and the on_conflict directive isn't a valid option. (replace/major/minor/cancel)"
			else:
				#the default action is to ADD the new task row... nothing
				sSQL = "insert task" \
					" (task_id, original_task_id, version, default_version," \
					" task_name, task_code, task_desc, task_status, created_dt)" \
					" values " + " ('" + self.ID + "'," \
					"'" + self.OriginalTaskID + "'," \
					" " + self.Version + "," \
					" 1," \
					" '" + uiCommon.TickSlash(self.Name) + "'," \
					" '" + uiCommon.TickSlash(self.Code) + "'," \
					" '" + uiCommon.TickSlash(self.Description) + "'," \
					" '" + self.Status + "'," \
					" now())"
				print sSQL
				if not db.tran_exec_noexcep(sSQL):
					print "failed"
					return False, db.error
				print "what?"
				# add security log
				print "logging"
				uiCommon.WriteObjectAddLog(uiGlobals.CatoObjectTypes.Task, self.ID, self.Name, "");

			"""
			#by the time we get here, there should for sure be a task row, either new or updated.				
			#now, codeblocks
			enumerator = self.Codeblocks.Values.GetEnumerator()
			while enumerator.MoveNext():
				c = enumerator.Current
				#PAY ATTENTION to crazy stuff here.
				#for exportability, embedded steps are held in codeblocks that don't really exist in the database
				# they are created on the task object when it's created from the db or xml.
				#BUT, when actually saving it, we don't wanna save these dummy codeblocks.
				#(having real dummy codeblocks in the db would freak out the command engine)
				#so ... if the codeblock name is a guid, we:
				#a) DO NOT insert it
				#b) any steps inside it are set to step_order=-1
				bIsBogusCodeblock = (ui.IsGUID(c.Name))
				if not bIsBogusCodeblock:
					oTrans.Command.CommandText = "insert task_codeblock (task_id, codeblock_name)" \
						" values ('" + self.ID + "', '" + c.Name + "')"
					if not oTrans.ExecUpdate():
						return False
				#and steps
				iStepOrder = 1
				enumerator = c.Steps.Values.GetEnumerator()
				while enumerator.MoveNext():
					s = enumerator.Current
					iStepOrder = (-1 if bIsBogusCodeblock else iStepOrder)
					oTrans.Command.CommandText = "insert into task_step (step_id, task_id, codeblock_name, step_order," \
						" commented, locked, output_parse_type, output_row_delimiter, output_column_delimiter," \
						" function_name, function_xml)" \
						" values (" + "'" + s.ID + "'," \
						"'" + s.Task.ID + "'," \
						("NULL" if str.IsNullOrEmpty(s.Codeblock) else "'" + s.Codeblock + "'") + "," \
						iStepOrder.ToString() + "," \
						"0,0," \
						s.OutputParseType.ToString() + "," \
						s.OutputRowDelimiter.ToString() + "," \
						s.OutputColumnDelimiter.ToString() + "," \
						"'" + s.FunctionName + "'," \
						"'" + ui.TickSlash(s.FunctionXML) + "'" \
						")"
					if not oTrans.ExecUpdate():
						return False
					iStepOrder += 1
			"""
			if bLocalTransaction:
				print "committing"
				db.tran_commit()
		except Exception, ex:
			return False, "Error updating the DB. " + ex.__str__()
		finally:
			return True, ""


class Codeblock(object):
	def __init__(self):
		self.Name = ""
		self.Steps = {}
		
	#a codeblock contains a dictionary collection of steps
	def FromXML(self, sCBXML=""):
		if sCBXML == "": return None
		xCB = ET.fromstring(sCBXML)
		
		self.Name = xCB.attrib["name"]
		
		#STEPS
		xSteps = xCB.findall("steps/step")
		print "Number of Steps in [" +self.Name + "]: " + str(len(xSteps))
		for xStep in xSteps:
			newstep = Step()
			newstep.FromXML(ET.tostring(xStep), self.Name)
			self.Steps[newstep.ID] = newstep



class Step(object):
	def __init__(self):
		self.ID = ""
		self.Codeblock = ""
		self.Order = 0
		self.Description = ""
		self.Commented = False
		self.Locked = False
		self.OutputParseType = 0

	def FromXML(self, sStepXML="", sCodeblockName=""):
		if sStepXML == "": return None
		if sCodeblockName == "": return None
		
		xStep = ET.fromstring(sStepXML)
		
		#attributes of the <step> node
		self.ID = xStep.get("id", str(uuid.uuid4()))
		self.Codeblock = sCodeblockName


