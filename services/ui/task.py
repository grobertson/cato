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

"""
    THIS CLASS has it's own database connections.
    Why?  Because it isn't only used by the UI.
"""

import traceback
import uuid
import xml.etree.ElementTree as ET
from catocommon import catocommon
import uiCommon
from datetime import datetime

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
        self.NumberOfApprovedVersions = 0
        #a task has a dictionary of codeblocks
        self.Codeblocks = {}

    #the default constructor (manual creation)
    def FromArgs(self, sName, sCode, sDesc):
        if not sName:
            raise Exception("Error building Task object: Name is required.")

        self.ID = str(uuid.uuid4())
        self.OriginalTaskID = self.ID
        self.Name = sName
        self.Code = sCode
        self.Description = sDesc

    #constructor - from the database by ID
    @staticmethod
    def FromID(sTaskID, bIncludeUserSettings = False):
        sErr = ""
        try:
            t = Task()
            
            db = catocommon.new_conn()

            sSQL = "select task_id, original_task_id, task_name, task_code, task_status, version, default_version," \
                    " task_desc, use_connector_system, concurrent_instances, queue_depth, parameter_xml" \
                    " from task" \
                    " where task_id = '" + sTaskID + "'"

            dr = db.select_row_dict(sSQL)

            if dr:
                sErr = t.PopulateTask(dr, bIncludeUserSettings)

            if t.ID:
                return t, ""
            else:
                return None, sErr
            
        except Exception, ex:
            raise ex

    """@staticmethod
    def FromOTIDVersion(self, sOriginalTaskID, sVersion):
        try:
            dc = dataAccess()
            sVersionClause = ""
            if str.IsNullOrEmpty(sVersion):
                sVersionClause = " and default_version = 1"
            else:
                sVersionClause = " and version = '" + sVersion + "'"
            sSQL = "select task_id, original_task_id, task_name, task_code, task_status, version, default_version," + " task_desc, use_connector_system, concurrent_instances, queue_depth, parameter_xml" + " from task" + " where original_task_id = '" + sOriginalTaskID + "'" + sVersionClause
            dr = None
            if not dc.sqlGetDataRow(, sSQL, ):
                return 
            if dr != None:
                self.PopulateTask(dr, False, )
        except Exception, ex:
            raise ex"""

    def FromXML(self, sTaskXML=""):
        if sTaskXML == "": return None
        
        xmlerr = "XML Error: Attribute not found."
        
        uiCommon.log("Creating Task object from XML", 3)
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
        uiCommon.log("Number of Codeblocks: " + str(len(xCodeblocks)), 4)
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
            xCB = ET.SubElement(xCodeblocks, "codeblock") #add the codeblock
            xCB.set("name", cb.Name)
            
            #STEPS
            xSteps = ET.SubElement(xCB, "steps") #add the steps section
            
            for s in cb.Steps:
                stp = cb.Steps[s]
                xStep = ET.SubElement(xSteps, "step") #add the step
                xStep.set("id", stp.ID)
                xStep.set("codeblock", stp.Codeblock)
        
        return ET.tostring(root)

    def AsJSON(self):
        try:
            sb = []
            sb.append("{")
            sb.append("\"%s\" : \"%s\"," % ("ID", self.ID))
            sb.append("\"%s\" : \"%s\"," % ("Name", self.Name))
            sb.append("\"%s\" : \"%s\"," % ("Code", self.Code))
            sb.append("\"%s\" : \"%s\"," % ("Version", self.Version))
            sb.append("\"%s\" : \"%s\"," % ("Status", self.Status))
            sb.append("\"%s\" : \"%s\"," % ("OriginalTaskID", self.OriginalTaskID))
            sb.append("\"%s\" : \"%s\"," % ("IsDefaultVersion", self.IsDefaultVersion))
            sb.append("\"%s\" : \"%s\"," % ("Description", self.Description))
            sb.append("\"%s\" : \"%s\"," % ("ConcurrentInstances", self.ConcurrentInstances))
            sb.append("\"%s\" : \"%s\"," % ("QueueDepth", self.QueueDepth))
            sb.append("\"%s\" : \"%s\"," % ("NumberOfApprovedVersions", self.NumberOfApprovedVersions))
            sb.append("\"%s\" : \"%s\"" % ("UseConnectorSystem", self.UseConnectorSystem))
            sb.append("}")
            return "".join(sb)
        except Exception, ex:
            raise ex

    def DBSave(self, db = None, bLocalTransaction = True):
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
                            " ('" + self.ID + "'," \
                            " '" + self.OriginalTaskID + "'," \
                            " " + self.Version + "," + " " \
                            (1 if self.IsDefaultVersion else 0) + "," \
                            " '" + ui.TickSlash(self.Name) + "'," \
                            " '" + ui.TickSlash(self.Code) + "'," \
                            " '" + ui.TickSlash(self.Description) + "'," \
                            " '" + self.Status + "'," \
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
                            " ('" + self.ID + "'," \
                            " '" + self.OriginalTaskID + "'," \
                            " " + self.Version + "," \
                            " " + (1 if self.IsDefaultVersion else 0) + "," \
                            " '" + ui.TickSlash(self.Name) + "'," \
                            " '" + ui.TickSlash(self.Code) + "'," \
                            " '" + ui.TickSlash(self.Description) + "'," \
                            " '" + self.Status + "'," \
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
                if not db.tran_exec_noexcep(sSQL):
                    return False, db.error

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
                        iStepOrder + "," \
                        "0,0," \
                        s.OutputParseType + "," \
                        s.OutputRowDelimiter + "," \
                        s.OutputColumnDelimiter + "," \
                        "'" + s.FunctionName + "'," \
                        "'" + ui.TickSlash(s.FunctionXML) + "'" \
                        ")"
                    if not oTrans.ExecUpdate():
                        return False
                    iStepOrder += 1
            """
            if bLocalTransaction:
                db.tran_commit()
        except Exception, ex:
            return False, "Error updating the DB. " + ex.str__()
        finally:
            return True, ""

    def Copy(self, iMode, sNewTaskName, sNewTaskCode):
        #iMode 0=new task, 1=new major version, 2=new minor version
        try:
            sSourceTaskID = self.ID
            #NOTE: this routine is not very object-aware.  It works and was copied in here
            #so it can live with other relevant code.
            #may update it later to be more object friendly
            sErr = ""
            sSQL = ""
            sNewTaskID = uiCommon.NewGUID()
            iIsDefault = 0
            sTaskName = ""
            sOTID = ""

            #do it all in a transaction
            db = catocommon.new_conn()

            #figure out the new name and selected version
            sTaskName = self.Name
            sOTID = self.OriginalTaskID

            #figure out te new version
            if iMode == 0:
                #figure out the new name and selected version
                sSQL = "select count(*) from task where task_name = '" + sNewTaskName + "'"
                iExists = db.select_col_noexcep(sSQL)
                if db.error:
                    raise Exception("Unable to check name conflicts for  [" + sNewTaskName + "]." + db.error)
                sTaskName = (sNewTaskName + " (" + str(datetime.now()) + ")" if iExists > 0 else sNewTaskName)

                iIsDefault = 1
                self.Version = "1.000"
                sOTID = sNewTaskID
            elif iMode == 1:
                self.IncrementMajorVersion()
            elif iMode == 2:
                self.IncrementMinorVersion()
            else: #a iMode is required
                raise Exception("A mode required for this copy operation.")

            #if we are versioning, AND there are not yet any 'Approved' versions,
            #we set this new version to be the default
            #(that way it's the one that you get taken to when you pick it from a list)
            if iMode > 0:
                sSQL = "select case when count(*) = 0 then 1 else 0 end" \
                    " from task where original_task_id = '" + sOTID + "'" \
                    " and task_status = 'Approved'"
                iExists = db.select_col_noexcep(sSQL)
                if db.error:
                    db.tran_rollback()
                    raise Exception(db.error)

            #string sTaskName = (iExists > 0 ? sNewTaskName + " (" + DateTime.Now + ")" : sNewTaskName);
            #drop the temp tables.
            sSQL = "drop temporary table if exists _copy_task"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)
            sSQL = "drop temporary table if exists _step_ids"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)
            sSQL = "drop temporary table if exists _copy_task_codeblock"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)
            sSQL = "drop temporary table if exists _copy_task_step"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)

            #start copying
            sSQL = "create temporary table _copy_task select * from task where task_id = '" + self.ID + "'"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)

            #update the task_id
            sSQL = "update _copy_task set" \
                " task_id = '" + sNewTaskID + "'," \
                " original_task_id = '" + sOTID + "'," \
                " version = '" + str(self.Version) + "'," \
                " task_name = '" + sTaskName + "'," \
                " task_code = '" + sNewTaskCode + "'," \
                " default_version = " + str(iIsDefault) + "," \
                " task_status = 'Development'," \
                " created_dt = now()"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)

            #codeblocks
            sSQL = "create temporary table _copy_task_codeblock" \
                " select '" + sNewTaskID + "' as task_id, codeblock_name" \
                " from task_codeblock where task_id = '" + self.ID + "'"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)

            #USING TEMPORARY TABLES... need a place to hold step ids while we manipulate them
            sSQL = "create temporary table _step_ids" \
                " select distinct step_id, uuid() as newstep_id" \
                " from task_step where task_id = '" + self.ID + "'"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)

            #steps temp table
            sSQL = "create temporary table _copy_task_step" \
                " select step_id, '" + sNewTaskID + "' as task_id, codeblock_name, step_order, commented," \
                " locked, function_name, function_xml, step_desc, output_parse_type, output_row_delimiter," \
                " output_column_delimiter, variable_xml" \
                " from task_step where task_id = '" + self.ID + "'"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)

            #update the step id
            sSQL = "update _copy_task_step a, _step_ids b" \
                " set a.step_id = b.newstep_id" \
                " where a.step_id = b.step_id"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)

            #update steps with codeblocks that reference a step (embedded steps)
            sSQL = "update _copy_task_step a, _step_ids b" \
                " set a.codeblock_name = b.newstep_id" \
                " where b.step_id = a.codeblock_name"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)

            #spin the steps and update any embedded step id's in the commands
            sSQL = "select step_id, newstep_id from _step_ids"
            dtStepIDs = db.select_all_dict(sSQL)
            if db.error:
                raise Exception("Unable to get step ids." + db.error)

            for drStepIDs in dtStepIDs:
                sSQL = "update _copy_task_step" \
                    " set function_xml = replace(lower(function_xml)," \
                    " '" + drStepIDs["step_id"].lower() + "'," \
                    " '" + drStepIDs["newstep_id"] + "')" \
                    " where function_name in ('if','loop','exists','while')"
                if not db.tran_exec_noexcep(sSQL):
                    raise Exception(db.error)

            #finally, put the temp steps table in the real steps table
            sSQL = "insert into task select * from _copy_task"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)
            sSQL = "insert into task_codeblock select * from _copy_task_codeblock"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)
            sSQL = "insert into task_step select * from _copy_task_step"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)

            #finally, if we versioned up and we set this one as the new default_version,
            #we need to unset the other row
            if iMode > 0 and iIsDefault == 1:
                sSQL = "update task set default_version = 0 where original_task_id = '" + sOTID + "' and task_id <> '" + sNewTaskID + "'"
                if not db.tran_exec_noexcep(sSQL):
                    raise Exception(db.error)

            db.tran_commit()

            return sNewTaskID
        except Exception, ex:
            raise ex
        finally:
            db.close()

    def PopulateTask(self, dr, IncludeUserSettings):
        try:
            #of course it exists...
            self.DBExists = True

            self.ID = dr["task_id"]
            self.Name = dr["task_name"]
            self.Code = dr["task_code"]
            self.Version = dr["version"]
            self.Status = dr["task_status"]
            self.OriginalTaskID = dr["original_task_id"]
            self.IsDefaultVersion = (True if dr["default_version"] == "1" else False)
            self.Description = (dr["task_desc"] if dr["task_desc"] else "")
            self.ConcurrentInstances = (dr["concurrent_instances"] if dr["concurrent_instances"] else "")
            self.QueueDepth = (dr["queue_depth"] if dr["queue_depth"] else "")
            self.UseConnectorSystem = (True if dr["use_connector_system"] == 1 else False)
            
            #parameters
            if dr["parameter_xml"]:
                xParameters = ET.fromstring(dr["parameter_xml"])
                if xParameters is not None:
                    self.ParameterXDoc = xParameters
            # 
            # * ok, this is important.
            # * there are some rules for the process of 'Approving' a task and other things.
            # * so, we'll need to know some count information
            # 
            db = catocommon.new_conn()
            
            sSQL = "select count(*) from task" \
                " where original_task_id = '" + self.OriginalTaskID + "'" \
                " and task_status = 'Approved'"
            iCount = db.select_col_noexcep(sSQL)
            if db.error:
                return "Error counting Approved versions:" + db.error
            self.NumberOfApprovedVersions = iCount

            sSQL = "select count(*) from task where original_task_id = '" + self.OriginalTaskID + "'"
            iCount = db.select_col_noexcep(sSQL)
            if db.error:
                return "Error counting Approved versions:" + db.error
            self.NumberOfOtherVersions = iCount

            #now, the fun stuff
            #1 get all the codeblocks and populate that dictionary
            #2 then get all the steps... ALL the steps in one sql
            #..... and while spinning them put them in the appropriate codeblock
            #GET THE CODEBLOCKS
            sSQL = "select codeblock_name from task_codeblock where task_id = '" + self.ID + "' order by codeblock_name"
            dtCB = db.select_all_dict(sSQL)
            if dtCB:
                for drCB in dtCB:
                    cb = Codeblock(drCB["codeblock_name"])
                    self.Codeblocks[cb.Name] = cb
            else:
                #uh oh... there are no codeblocks!
                #since all tasks require a MAIN codeblock... if it's missing,
                #we can just repair it right here.
                sSQL = "insert task_codeblock (task_id, codeblock_name) values ('" + self.ID + "', 'MAIN')"
                if not db.exec_db_noexcep(sSQL):
                    return db.error
                self.Codeblocks["MAIN"] = Codeblock("MAIN")

            #GET THE STEPS
            #we need the userID to get the user settings in some cases
            if IncludeUserSettings:
                sUserID = uiCommon.GetSessionUserID()
                #NOTE: it may seem like sorting will be an issue, but it shouldn't.
                #sorting ALL the steps by their order here will ensure they get added to their respective 
                # codeblocks in the right order.
                sSQL = "select s.step_id, s.step_order, s.step_desc, s.function_name, s.function_xml, s.commented, s.locked, codeblock_name," \
                    " s.output_parse_type, s.output_row_delimiter, s.output_column_delimiter, s.variable_xml," \
                    " us.visible, us.breakpoint, us.skip, us.button" \
                    " from task_step s" \
                    " left outer join task_step_user_settings us on us.user_id = '" + sUserID + "' and s.step_id = us.step_id" \
                    " where s.task_id = '" + self.ID + "'" \
                    " order by s.step_order"
            else:
                sSQL = "select s.step_id, s.step_order, s.step_desc, s.function_name, s.function_xml, s.commented, s.locked, codeblock_name," \
                    " s.output_parse_type, s.output_row_delimiter, s.output_column_delimiter, s.variable_xml," \
                    " 0 as visible, 0 as breakpoint, 0 as skip, '' as button" \
                    " from task_step s" \
                    " where s.task_id = '" + self.ID + "'" \
                    " order by s.step_order"

            dtSteps = db.select_all_dict(sSQL)
            if dtSteps:
                for drSteps in dtSteps:
                    oStep = Step.FromRow(drSteps, self)
                    # the steps dictionary for each codeblock uses the ORDER, not the STEP ID, as the key
                    # this way, we can order the dictionary.
                    
                    # maybe this should just be a list?
                    if oStep:
                        #a 'REAL' codeblock will be in this collection
                        # (the codeblock of an embedded step is not a 'real' codeblock, rather a pointer to another step
                        if self.Codeblocks.has_key(oStep.Codeblock):
                            self.Codeblocks[oStep.Codeblock].Steps[oStep.Order] = oStep
                            #print self.Codeblocks[oStep.Codeblock].Steps
                        else:
                            #so, what do we do if we found a step that's not in a 'real' codeblock?
                            #well, the gui will take care of drawing those embedded steps...
                            #but we have a problem with export, version up, etc.
                            #these steps can't be orphans!
                            #so, we'll go ahead and create codeblocks for them.
                            #this is terrible, but part of the problem with this embedded stuff.
                            #we'll tweak the gui so GUID named codeblocks don't show.
                            self.Codeblocks[oStep.Codeblock] = Codeblock(oStep.Codeblock)
                            self.Codeblocks[oStep.Codeblock].Steps[oStep.Order] = oStep
            #maybe one day we'll do the full recusrive loading of all embedded steps here
            # but not today... it's a big deal and we need to let these changes settle down first.
            
        except Exception, ex:
            raise ex
        finally:
            db.close()

class Codeblock(object):
    def __init__(self, sName):
        self.Name = sName
        self.Steps = {}
        
    #a codeblock contains a dictionary collection of steps
    def FromXML(self, sCBXML=""):
        if sCBXML == "": return None
        xCB = ET.fromstring(sCBXML)
        
        self.Name = xCB.attrib["name"]
        
        #STEPS
        xSteps = xCB.findall("steps/step")
        uiCommon.log("Number of Steps in [" +self.Name + "]: " + str(len(xSteps)), 4)
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
        self.OutputRowDelimiter = 0
        self.OutputColumnDelimiter = 0
        self.FunctionXML = None
        self.FunctionXDoc = None
        self.VariableXML = None
        self.VariableXDoc = None
        self.FunctionName = ""
        self.UserSettings = StepUserSettings()
        # this property isn't added by the "Populate" methods - but can be added manually.
        # this is because of xml import/export - where the function details aren't required.
        # but they are in the UI when drawing steps.
        self.Function = None 
        # Very rarely does a single Step object have an associated parent Task.
        # usually, we're working on steps within the context of already knowing the Task.
        # but if it's needed, it will have been explicitly populated.
        self.Task = None
        
        # if an error occured parsing, this step will be invalid
        # this property notes that
        self.IsValid = True
        
    def FromXML(self, sStepXML="", sCodeblockName=""):
        if sStepXML == "": return None
        if sCodeblockName == "": return None
        
        xStep = ET.fromstring(sStepXML)
        
        #attributes of the <step> node
        self.ID = xStep.get("id", str(uuid.uuid4()))
        self.Codeblock = sCodeblockName

    @staticmethod
    def FromRow(dr, task):
        s = Step()
        s.PopulateStep(dr, task)
        return s
        
    @staticmethod
    def ByIDWithSettings(sStepID, sUserID):
        """
        Gets a single step object, including user settings.  Does NOT have an associated parent Task object.
        This is called by the AddStep methods, and other functions *on* the task page where we don't need
        the associated task object
        """
        try:
            """                string sSQL = "select t.task_name, t.version," +
                        " s.step_id, s.task_id, s.step_order, s.codeblock_name, s.step_desc, s.function_name, s.function_xml, s.commented, s.locked," +
                        " s.output_parse_type, s.output_row_delimiter, s.output_column_delimiter, s.variable_xml" +
                        " from task_step s" +
                        " join task t on s.task_id = t.task_id" +
                        " where s.step_id = '" + sStepID + "' limit 1";
            """
            sSQL = "select s.step_id, s.step_order, s.step_desc, s.function_name, s.function_xml, s.commented, s.locked, s.codeblock_name," \
                " s.output_parse_type, s.output_row_delimiter, s.output_column_delimiter, s.variable_xml," \
                " us.visible, us.breakpoint, us.skip, us.button" \
                " from task_step s" \
                " left outer join task_step_user_settings us on us.user_id = '" + sUserID + "' and s.step_id = us.step_id" \
                " where s.step_id = '" + sStepID + "' limit 1"
            db = catocommon.new_conn()
            row = db.select_row_dict(sSQL)
            if row:
                oStep = Step.FromRow(row, None)
                return oStep

            if db.error:
                uiCommon.log("Error getting Step by ID: " + db.error, 2)
            
            return None
        except Exception, ex:
            raise ex
        finally:
            db.close()
        
    def PopulateStep(self, dr, oTask):
        try:
            self.ID = dr["step_id"]
            self.Codeblock = ("" if not dr["codeblock_name"] else dr["codeblock_name"])
            self.Order = dr["step_order"]
            self.Description = ("" if not dr["step_desc"] else dr["step_desc"])
            self.Commented = (True if dr["commented"] == "1" else False)
            self.Locked = (True if dr["locked"] == "1" else False)
            self.OutputParseType = dr["output_parse_type"]
            self.OutputRowDelimiter = dr["output_row_delimiter"]
            self.OutputColumnDelimiter = dr["output_column_delimiter"]
            self.FunctionXML = ("" if not dr["function_xml"] else dr["function_xml"])
            self.VariableXML = ("" if not dr["variable_xml"] else dr["variable_xml"])
            #once parsed, it's cleaner.  update the object with the cleaner xml
            if self.FunctionXML:
                try:
                    self.FunctionXDoc = ET.fromstring(self.FunctionXML)
                except Exception:
                    self.IsValid = False
                    print "CRITICAL: Unable to parse function xml in step [%s]." % self.ID
                    print traceback.format_exc()    
            if self.VariableXML:
                try:
                    self.VariableXDoc = ET.fromstring(self.VariableXML)
                except Exception:
                    self.IsValid = False
                    print "CRITICAL: Unable to parse variable xml in step [%s]." % self.ID
                    print traceback.format_exc()    

            #this.Function = Function.GetFunctionByName(dr["function_name"]);
            self.FunctionName = dr["function_name"]

            # user settings, if available
            if dr["button"] is not None:
                self.UserSettings.Button = dr["button"]
            if dr["skip"] is not None:
                self.UserSettings.Skip = (True if dr["skip"] == 1 else False)
            if dr["visible"] is not None:
                self.UserSettings.Visible = (True if dr["visible"] == 1 else False)
            
            #NOTE!! :oTask can possibly be null, in lots of cases where we are just getting a step and don't know the task.
            #if it's null, it will not populate the parent object.
            #this happens all over the place in the HTMLTemplates stuff, and we don't need the extra overhead of the same task
            #object being created hundreds of times.
            if oTask:
                self.Task = oTask
            else:
                #NOTE HACK TODO - this is bad and wrong
                #we shouldn't assume the datarow was a join to the task table... but in a few places it was.
                #so we're populating some stuff here.
                #the right approach is to create a full Task object from the ID, but we need to analyze
                #how it's working, so we don't create a bunch more database hits.
                #I THINK THIS is only happening on GetSingleStep and taskStepVarsEdit, but double check.
                self.Task = Task()
                if dr.has_key("task_id"):
                    self.Task.ID = dr["task_id"]
                if dr.has_key("task_name"):
                    self.Task.Name = dr["task_name"]
                if dr.has_key("version"):
                    self.Task.Version = dr["version"]
            return self
        except Exception, ex:
            raise ex
        
class StepUserSettings(object):
    def __init__(self):
        self.Visible = True
        self.Breakpoint= False
        self.Skip = False
        self.Button = ""


