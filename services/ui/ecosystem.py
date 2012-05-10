"""
    THIS CLASS has it's own database connections.
    Why?  Because it isn't only used by the UI.
"""

import uiCommon
from catocommon import catocommon

class Ecotemplate(object):
    ID = uiCommon.NewGUID()
    Name = None
    Description = None
    StormFileType = None
    StormFile = None
    IncludeTasks = False #used for export to xml
    DBExists = None
    OnConflict = "cancel" #the default behavior for all conflicts is to cancel the operation
    Actions = {}

    #the default constructor (manual creation)
    def FromArgs(self, sName, sDescription):
        if not sName:
            raise Exception("Error building Ecotemplate: Name is required.")

        self.Name = sName
        self.Description = sDescription
        self.DBExists = self.dbExists()

    def FromID(self, sEcotemplateID, bIncludeActions = True):
        try:
            sSQL = "select ecotemplate_id, ecotemplate_name, ecotemplate_desc, storm_file_type, storm_file" \
                " from ecotemplate" \
                " where ecotemplate_id = '" + sEcotemplateID + "'"

            db = catocommon.new_conn()
            dr = db.select_row_dict(sSQL)
            if db.error:
                raise Exception("Ecotemplate Object: Unable to check for existing Name or ID. " + db.error)

            if dr is not None:
                self.DBExists = True
                self.ID = dr["ecotemplate_id"]
                self.Name = dr["ecotemplate_name"]
                self.Description = ("" if not dr["ecotemplate_desc"] else dr["ecotemplate_desc"])
                self.StormFileType = ("" if not dr["storm_file_type"] else dr["storm_file_type"])
                self.StormFile = ("" if not dr["storm_file"] else dr["storm_file"])
                
                if bIncludeActions:
                    # get a table of actions and loop the rows
                    sSQL = "select action_id, ecotemplate_id, action_name, action_desc, category, original_task_id, task_version, parameter_defaults, action_icon" \
                        " from ecotemplate_action" \
                        " where ecotemplate_id = '" + sEcotemplateID + "'"
    
                    dtActions = db.select_all_dict(sSQL)
                    if dtActions:
                        for drAction in dtActions:
                            ea = EcotemplateAction()
                            ea.FromRow(drAction, self)
                            if ea is not None:
                                self.Actions[ea.ID] = ea
            else: 
                raise Exception("Error building Ecotemplate object: " + db.error)
        except Exception, ex:
            raise ex
        finally:
            db.close()

    def AsJSON(self):
        try:
            sb = []
            sb.append("{")
            sb.append("\"%s\" : \"%s\"," % ("ID", self.ID))
            sb.append("\"%s\" : \"%s\"," % ("Name", self.Name))
            sb.append("\"%s\" : \"%s\"" % ("Description", uiCommon.packJSON(self.Description)))
            sb.append("}")
            return "".join(sb)
        except Exception, ex:
            raise ex


    def dbExists(self):
        try:
            # task_id is the PK, and task_name+version is a unique index.
            # so, we check the conflict property, and act accordingly
            sSQL = "select ecotemplate_id from ecotemplate" \
                " where ecotemplate_name = '" + self.Name + "'" \
                " or ecotemplate_id = '" + self.ID + "'"
            
            db = catocommon.new_conn()
            dr = db.select_row_dict(sSQL)
            if db.error:
                raise Exception("Ecotemplate Object: Unable to check for existing Name or ID. " + db.error)
            
            if dr is not None:
                if dr["ecotemplate_id"]:
                    # PAY ATTENTION! 
                    # if the template exists... it might have been by name, so...
                    # we're setting the ids to the same as the database so it's more accurate.
                    
                    self.ID = dr["ecotemplate_id"]
                    return True
                
            return False
        except Exception, ex:
            raise ex
        finally:
            db.close()

    def DBSave(self):
        try:
            if not self.Name or not self.ID:
                return False, "ID and Name are required Ecotemplate properties."

            db = catocommon.new_conn()

            if self.DBExists:
                # uh oh... this ecotemplate exists.  unless told to do so, we stop here.
                if self.OnConflict == "cancel":
                    return False, "Another Ecotemplate with that ID or Name exists.  [" + self.ID + "/" + self.Name + "]  Conflict directive set to 'cancel'. (Default is 'cancel' if omitted.)"
                else:
                    # ok, what are we supposed to do then?
                    if self.OnConflict == "replace":
                        # whack it all so we can re-insert
                        # but by name or ID?  which was the conflict?
                        
                        # no worries! the _DBExists function called when we created the object
                        # will have resolved any name/id issues.
                        
                        # if the ID existed it doesn't matter, we'll be plowing it anyway.
                        # by "plow" I mean drop and recreate the actions... the ecotemplate row will be UPDATED
                        sSQL = "update ecotemplate" \
                            " set ecotemplate_name = '" + self.Name + "'," \
                            " ecotemplate_desc = " + (" null" if not self.Description else " '" + uiCommon.TickSlash(self.Description + "'")) + "," \
                            " storm_file_type = " + (" null" if not self.StormFileType else " '" + self.StormFileType + "'") + "," \
                            " storm_file = " + (" null" if not self.StormFile else " '" + uiCommon.TickSlash(self.StormFile + "'")) + \
                            " where ecotemplate_id = '" + self.ID + "'"
                        if not db.tran_exec_noexcep(sSQL):
                            return False, db.error

                        sSQL = "delete from ecotemplate_action" \
                            " where ecotemplate_id = '" + self.ID + "'"
                        if not db.tran_exec_noexcep(sSQL):
                            return False, db.error
                    else:
                        # there is no default action... if the on_conflict didn't match we have a problem... bail.
                        return False, "There is an ID or Name conflict, and the on_conflict directive isn't a valid option. (replace/cancel)"
            else:
                # doesn't exist, we'll add it                
                sSQL = "insert into ecotemplate (ecotemplate_id, ecotemplate_name, ecotemplate_desc, storm_file_type, storm_file)" \
                    " values ('" + self.ID + "'," \
                        " '" + self.Name + "',"  + \
                        (" null" if not self.Description else " '" + uiCommon.TickSlash(self.Description) + "'") + "," + \
                        (" null" if not self.StormFileType else " '" + self.StormFileType + "'") + "," + \
                        (" null" if not self.StormFile else " '" + uiCommon.TickSlash(self.StormFile) + "'") + \
                        ")"
                if not db.tran_exec_noexcep(sSQL):
                    return False, db.error
                
            
            # create the actions
            # actions aren't referenced by id anywhere, so we'll just give them a new guid
            # to prevent any risk of PK issues.
            for ea in self.Actions.itervalues():
                sSQL = "insert into ecotemplate_action" \
                    " (action_id, ecotemplate_id, action_name, action_desc, category, action_icon, original_task_id, task_version, parameter_defaults)" \
                    " values (" \
                    " uuid()," \
                    " '" + self.ID + "'," \
                    " '" + uiCommon.TickSlash(ea.Name) + "'," + \
                    ("null" if not ea.Description else " '" + uiCommon.TickSlash(ea.Description) + "'") + "," + \
                    ("null" if not ea.Category else " '" + uiCommon.TickSlash(ea.Category) + "'") + "," \
                    " '" + ea.Icon + "'," \
                    " '" + ea.OriginalTaskID + "'," \
                    ("null" if not ea.TaskVersion else " '" + ea.TaskVersion + "'") + "," + \
                    ("null" if not ea.ParameterDefaultsXML else " '" + uiCommon.TickSlash(ea.ParameterDefaultsXML) + "'") + \
                    ")"
                
                if not db.tran_exec_noexcep(sSQL):
                    return False, db.error
                
                # now, does this action contain a <task> section?  If so, we'll branch off and do 
                # the create task logic.
                if ea.Task is not None:
                    result, msg = ea.Task.DBSave()
                    if not result:
                        # the task 'should' have rolled back on any errors, but in case it didn't.
                        db.tran_rollback()
                        return False, msg

                    # finally, don't forget to update the action with the new values if any
                    ea.OriginalTaskID = ea.Task.OriginalTaskID
                        
                    # we don't update the version if the action referenced the default (it was empty)
                    if ea.TaskVersion:
                        ea.TaskVersion = ea.Task.Version
            
            # yay!
            db.tran_commit()
            return True, None

        except Exception, ex:
            raise ex
        finally:
            db.close()

    def DBCopy(self, sNewName):
        try:
            et = Ecotemplate()
            if et is not None:
                # populate it
                et.Name = sNewName
                et.Description = self.Description
                et.StormFileType = self.StormFileType
                et.StormFile = self.StormFile
                et.Actions = self.Actions
                
                # we gave it a new name and id, recheck if it exists
                et.DBExists = et.dbExists()
                
                result, msg = et.DBSave()
                if not result:
                    return False, msg
            
                return True, ""
            
            return False, "Unable to create a new Ecotemplate."
        except Exception, ex:
            raise ex

class EcotemplateAction(object):
    ID = None
    Name = None
    Description = None
    Category = None
    OriginalTaskID = None
    TaskVersion = None
    Icon = None
    ParameterDefaultsXML = None
    Ecotemplate = None #pointer to our parent Template.

    # for export, we might want to tell the action to include the whole referenced task object
    # pretty rare, since for general use we don't wanna be lugging around a whole task.
    IncludeTask = False
    Task = None

    def FromRow(self, dr, et):
        try:
            self.Ecotemplate = et
            self.ID = dr["action_id"]
            self.Name = dr["action_name"]
            self.Description = dr["action_desc"]
            self.Category = dr["category"]
            self.OriginalTaskID = dr["original_task_id"]
            self.TaskVersion = str(dr["task_version"])
            self.Icon = dr["action_icon"]
            self.ParameterDefaultsXML = dr["parameter_defaults"]
        except Exception, ex:
            raise ex
        