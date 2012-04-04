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


