"""
    THIS CLASS has it's own database connections.
    Why?  Because it isn't only used by the UI.
"""

import uiCommon
from catocommon import catocommon

class Ecotemplate(object):
    ID = None
    Name = None
    Description = None
    StormFileType = None
    StormFile = None
    IncludeTasks = False #used for export to xml
    DBExists = None;
    OnConflict = "cancel" #the default behavior for all conflicts is to cancel the operation
    Actions = {}

    #the default constructor (manual creation)
    def FromArgs(self, sName, sDescription):
        if not sName:
            raise Exception("Error building Ecotemplate: Name is required.")

        self.ID = uiCommon.NewGUID()
        self.Name = sName
        self.Description = sDescription
        self.DBExists = self.dbExists()

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

            print self.DBExists
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
                print "inserting"
                # doesn't exist, we'll add it                
                sSQL = "insert into ecotemplate (ecotemplate_id, ecotemplate_name, ecotemplate_desc, storm_file_type, storm_file)" \
                    " values ('" + self.ID + "'," \
                        " '" + self.Name + "',"  + \
                        (" null" if not self.Description else " '" + uiCommon.TickSlash(self.Description) + "'") + "," + \
                        (" null" if not self.StormFileType else " '" + self.StormFileType + "'") + "," + \
                        (" null" if not self.StormFile else " '" + uiCommon.TickSlash(self.StormFile) + "'") + \
                        ")"
                print sSQL
                if not db.tran_exec_noexcep(sSQL):
                    return False, db.error
                
#                # uiCommon.WriteObjectAddLog(acObjectTypes.Ecosystem, this.ID, this.Name, "Ecotemplate created.")
#            
#            # create the actions
#            # actions aren't referenced by id anywhere, so we'll just give them a new guid
#            # to prevent any risk of PK issues.
#### CHECK NEXT LINE for type declarations !!!
#for EcotemplateAction ea in self.Actions.Values:
#                sSQL = "insert into ecotemplate_action" + 
#                    " (action_id, ecotemplate_id, action_name, action_desc, category, action_icon, original_task_id, task_version, parameter_defaults)" \
#                    " values (" \
#                    " uuid()," + 
#                    " '" + self.ID + "'," + 
#                    " '" + uiCommon.TickSlash(ea.Name) + "'," + 
#                    ("null" if not ea.Description) else " '" + uiCommon.TickSlash(ea.Description + "'") + "," + 
#                    ("null" if not ea.Category) else " '" + uiCommon.TickSlash(ea.Category + "'") + "," + 
#                    " '" + ea.Icon + "'," + 
#                    " '" + ea.OriginalTaskID + "'," + 
#                    ("null" if not ea.TaskVersion) else " '" + ea.TaskVersion + "'") + "," + 
#                    ("null" if not ea.ParameterDefaultsXML) else " '" + uiCommon.TickSlash(ea.ParameterDefaultsXML + "'") + \
#                    ")"
#                
#                if not uiGlobals.request.db.tran_exec_noexcep(sSQL):
#                    return false
#                
#                # now, does this action contain a <task> section?  If so, we'll branch off and do 
#                # the create task logic.
#                if ea.Task is not None):
#                    if !ea.Task.DBSave(0000BYREF_ARG0000sErr, oTrans):
#                        # the task 'should' have rolled back on any errors, but in case it didn't.
#try:                                 uiGlobals.request.db.tran_rollback()
#                            return false
#} catch (Exception)                         else:
#                        if sErr):
#try:                                     uiGlobals.request.db.tran_rollback()
#                                return false
#} catch (Exception)                                     
#                        # finally, don't forget to update the action with the new values if any
#                        ea.OriginalTaskID = ea.Task.OriginalTaskID
#                        
#                        # we don't update the version if the action referenced the default (it was empty)
#                        if  (ea.TaskVersion))
#                            ea.TaskVersion = ea.Task.Version
            
            # yay!
            db.tran_commit()
            return True, None

        except Exception, ex:
            raise ex
        finally:
            db.close()
