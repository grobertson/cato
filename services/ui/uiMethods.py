import sys
import traceback
import urllib
import json
import uiGlobals
import uiCommon
from catocommon import catocommon
import cloud
import settings

# unlike uiCommon, which is used for shared ui elements
# this is a methods class mapped to urls for web.py
# --- we CAN'T instantiate it - that's not how web.py works.
# (apparently it does the instantiation itself, or maybe not - it might just look into it.)
# it expects these classes to have GET and POST methods

# these are generic ui web methods, and stuff that's not enough to need it's own file.
class login:
    def GET(self):
        # visiting the login page kills the session
        uiGlobals.session.kill()
        
        qs = ""
        i = uiGlobals.web.input(msg=None)
        if i.msg:
            qs = "?msg=" + urllib.quote_plus(i.msg)
        raise uiGlobals.web.seeother('/static/login.html' + qs)

    def POST(self):
        try:
            # HERE WE WILL get the security policy and use it to test the various steps along the login process.
#            policy = settings.security()
#            print "@" + policy.LoginMessage
        

            # EVERY new HTTP request sets up the "request" in uiGlobals.
            # ALL functions chained from this HTTP request handler share that request
            uiGlobals.request = uiGlobals.Request(catocommon.new_conn())
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
            in_name = uiGlobals.web.input(username=None).username
            in_pwd = uiGlobals.web.input(password=None).password
    
            sql = "select user_id, user_password, full_name, user_role, email, status, failed_login_attempts, expiration_dt, force_change \
                from users where username='" + in_name + "'"
            
            row = uiGlobals.request.db.select_row_dict(sql)
            if not row:
                uiCommon.log("Invalid login attempt - [%s] not a valid user." % (in_name), 0)
                msg = "Invalid Username or Password."
                raise uiGlobals.web.seeother('/static/login.html?msg=' + urllib.quote_plus(msg))
    
            
            #alrighty, lets check the password
            # we do this by encrypting the form submission and comparing, 
            # NOT by decrypting it here.
            encpwd = catocommon.cato_encrypt(in_pwd)
            
            if row["user_password"] != encpwd:
                uiCommon.log("Invalid login attempt - [%s] bad password." % (in_name), 0)
                msg = "Invalid Username or Password."
                raise uiGlobals.web.seeother('/static/login.html?msg=' + urllib.quote_plus(msg))
                
            user_id = row["user_id"]
            
            #all good, put a few key things in the session
            user = {}
            user["user_id"] = user_id
            user["full_name"] = row["full_name"]
            user["role"] = row["user_role"]
            user["email"] = row["email"]
            user["ip_address"] = uiGlobals.web.ctx.ip
            uiCommon.SetSessionObject("user", user)
            #uiGlobals.session.user = user
            uiCommon.log("Login granted for: ", 4)
            uiCommon.log(uiGlobals.session.user, 4)
            # reset the user counters and last_login
            sql = "update users set failed_login_attempts=0, last_login_dt=now() where user_id='" + user_id + "'"
            if not uiGlobals.request.db.exec_db_noexcep(sql):
                uiCommon.log(uiGlobals.request.db.error, 0)
    
            #update the security log
            uiCommon.AddSecurityLog(uiGlobals.SecurityLogTypes.Security, 
                uiGlobals.SecurityLogActions.UserLogin, uiGlobals.CatoObjectTypes.User, "", 
                "Login from [" + uiGlobals.web.ctx.ip + "] granted.")
    
            uiCommon.log("Creating session...", 3)
                
            raise uiGlobals.web.seeother('/home')
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
        finally:
            if uiGlobals.request:
                if uiGlobals.request.db.conn.socket:
                    uiGlobals.request.db.close()
                uiCommon.log(uiGlobals.request.DumpMessages(), 0)

class logout:        
    def GET(self):
        i = uiGlobals.web.input(msg=None)
        msg = "User Logged out."
        if i.msg:
            msg = i.msg
        uiCommon.ForceLogout(msg)

class uiMethods:
    #the GET and POST methods here are hooked by web.py.
    #whatever method is requested, that function is called.
    def GET(self, method):
        try:
            # EVERY new HTTP request sets up the "request" in uiGlobals.
            # ALL functions chained from this HTTP request handler share that request
            uiGlobals.request = uiGlobals.Request(catocommon.new_conn())
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            methodToCall = getattr(self, method)
            result = methodToCall()
            return result
        except Exception as ex:
            raise ex
        finally:
            if uiGlobals.request:
                if uiGlobals.request.db.conn.socket:
                    uiGlobals.request.db.close()
                uiCommon.log(uiGlobals.request.DumpMessages(), 0)

    def POST(self, method):
        try:
            # EVERY new HTTP request sets up the "request" in uiGlobals.
            # ALL functions chained from this HTTP request handler share that request
            uiGlobals.request = uiGlobals.Request(catocommon.new_conn())
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            methodToCall = getattr(self, method)
            result = methodToCall()
            return result
        except Exception as ex:
            raise ex
        finally:
            if uiGlobals.request:
                if uiGlobals.request.db.conn.socket:
                    uiGlobals.request.db.close()
                uiCommon.log(uiGlobals.request.DumpMessages(), 0)

    def wmGetCloudAccountsForHeader(self):
        try:
            sSelected = uiCommon.GetCookie("selected_cloud_account")

            sHTML = ""
            ca = cloud.CloudAccounts("")
            if ca.rows:
                for row in ca.rows:
                    # if sSelected is empty, set the default in the cookie.
                    sSelectClause = ""
                    if not sSelected:
                        if row["is_default"] == "Yes":
                            uiCommon.SetCookie("selected_cloud_account", row["account_id"])
                    else:
                        sSelectClause = ("selected=\"selected\"" if sSelected == row["account_id"] else "")
                        
                    sHTML +=  "<option value=\"%s\" provider=\"%s\" %s>%s (%s)</option>" % (row["account_id"], row["provider"], sSelectClause, row["account_name"], row["provider"])

                return sHTML
            
            #should not get here if all is well
            return "<option>ERROR</option>"
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmUpdateHeartbeat(self):
        uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
        #NOTE: this needs all the kick and warn stuff
        uid = uiCommon.GetSessionUserID()
        ip = uiCommon.GetSessionObject("user", "ip_address")
        
        if uid and ip:
            sSQL = "update user_session set heartbeat = now() where user_id = '" + uid + "' \
                and address = '" + ip + "'"
            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
        return ""
    
    def wmGetSystemStatus(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            sProcessHTML = ""
            sSQL = "select app_instance as Instance," \
                " app_name as Component," \
                " heartbeat as Heartbeat," \
                " case master when 1 then 'Yes' else 'No' end as Enabled," \
                " timestampdiff(MINUTE, heartbeat, now()) as mslr," \
                " load_value as LoadValue, platform, hostname" \
                " from application_registry " \
                " order by component, master desc"
            rows = uiGlobals.request.db.select_all(sSQL)
            for dr in rows:
                sProcessHTML += "<tr>" \
                    "<td>" + str((dr[0] if dr[0] else "")) + "</td>" \
                    "<td>" + str((dr[1] if dr[1] else "")) + "</td>" \
                    "<td>" + str((dr[2] if dr[2] else "")) + "</td>" \
                    "<td>" + str((dr[3] if dr[3] else "")) + "</td>" \
                    "<td>" + str((dr[4] if dr[4] else "")) + "</td>" \
                    "<td>" + str((dr[5] if dr[5] else "")) + "</td>" \
                    "</tr>"

            sUserHTML = ""
            sSQL = "select u.full_name, us.login_dt, us.heartbeat as last_update, us.address," \
                " case when us.kick = 0 then 'Active' when us.kick = 1 then 'Warning' " \
                " when us.kick = 2 then 'Kicking' when us.kick = 3 then 'Inactive' end as 'kick' " \
                " from user_session us join users u on u.user_id = us.user_id " \
                " where timestampdiff(MINUTE,us.heartbeat, now()) < 10" \
                " order by us.heartbeat desc"
            rows = uiGlobals.request.db.select_all(sSQL)
            for dr in rows:
                sUserHTML += "<tr>" \
                    "<td>" + str((dr[0] if dr[0] else "")) + "</td>" \
                    "<td>" + str((dr[1] if dr[1] else "")) + "</td>" \
                    "<td>" + str((dr[2] if dr[2] else "")) + "</td>" \
                    "<td>" + str((dr[3] if dr[3] else "")) + "</td>" \
                    "<td>" + str((dr[4] if dr[4] else "")) + "</td>" \
                    "</tr>"
                    
            sMessageHTML = ""
            sSQL = "select msg_to, msg_subject," \
                " case status when 0 then 'Queued' when 1 then 'Error' when 2 then 'Success' end as status," \
                " error_message," \
                " convert(date_time_entered, CHAR(20)) as entered_dt, convert(date_time_completed, CHAR(20)) as completed_dt" \
                " from message" \
                " order by msg_id desc limit 100"
            rows = uiGlobals.request.db.select_all(sSQL)
            for dr in rows:
                sMessageHTML += "<tr>" \
                    "<td>" + str((dr[0] if dr[0] else "")) + "</td>" \
                    "<td>" + str((dr[1] if dr[1] else "")) + "</td>" \
                    "<td>" + str((dr[2] if dr[2] else "")) + "</td>" \
                    "<td>" + str((dr[3] if dr[3] else "")) + "</td>" \
                    "<td>" + str((dr[4] if dr[4] else "")) + "<br />" + str((dr[5] if dr[5] else "")) + "</td>" \
                    "</tr>"
                    
            
            return "{ \"processes\" : \"%s\", \"users\" : \"%s\", \"messages\" : \"%s\" }" % (sProcessHTML, sUserHTML, sMessageHTML)

        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmGetLog(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
            
            sObjectID = uiCommon.getAjaxArg("sObjectID")
            sObjectType = uiCommon.getAjaxArg("sObjectType")
            sSearch = uiCommon.getAjaxArg("sSearch")
            sRecords = uiCommon.getAjaxArg("sRecords", "100")
            sFrom = uiCommon.getAjaxArg("sFrom", "")
            sTo = uiCommon.getAjaxArg("sTo", "")
            
            sWhereString = "(1=1)"
            if sObjectID:
                sWhereString += " and usl.object_id = '" + sObjectID + "'"

            if sObjectType:
                if sObjectType > "0": # but a 0 object type means we want everything
                    sWhereString += " and usl.object_type = '" + sObjectType + "'"
           
            if not sObjectID and not sObjectType: # no arguments passed means we want a security log
                sWhereString += " and usl.log_type = 'Security'"

            sDateSearchString = ""
            sTextSearch = ""
            
            if sSearch:
                sTextSearch += " and (usl.log_dt like '%%" + sSearch.replace("'", "''") + "%%' " \
                    "or u.full_name like '%%" + sSearch.replace("'", "''") + "%%' " \
                    "or usl.log_msg like '%%" + sSearch.replace("'", "''") + "%%') "
            
            if sFrom:
                sDateSearchString += " and usl.log_dt >= str_to_date('" + sFrom + "', '%%m/%%d/%%Y')"
            if sTo:
                sDateSearchString += " and usl.log_dt <= str_to_date('" + sTo + "', '%%m/%%d/%%Y')"
                
            sSQL = "select usl.log_msg as log_msg," \
                " convert(usl.log_dt, CHAR(20)) as log_dt, u.full_name" \
                " from user_security_log usl" \
                " join users u on u.user_id = usl.user_id" \
                " where " + sWhereString + sDateSearchString + sTextSearch + \
                " order by usl.log_id desc" \
                " limit " + (sRecords if sRecords else "100")
                
            sLog = ""
            rows = uiGlobals.request.db.select_all_dict(sSQL)
            if uiGlobals.request.db.error:
                return "{ \"error\" : \"Unable to get log. %s\" }" % (uiGlobals.request.db.error)
            if rows:
                i = 1
                sb = []
                for row in rows:
                    sb.append("[")
                    sb.append("\"%s\", " % (row["log_dt"]))
                    sb.append("\"%s\", " % (uiCommon.packJSON(row["full_name"])))
                    sb.append("\"%s\"" % (uiCommon.packJSON(row["log_msg"])))
                    sb.append("]")
                
                    #the last one doesn't get a trailing comma
                    if i < len(rows):
                        sb.append(",")
                        
                    i += 1
    
                sLog =  "".join(sb)

            return "{ \"log\" : [ %s ] }" % (sLog)

        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmGetDatabaseTime(self):
        sNow = uiGlobals.request.db.select_col_noexcep("select now()")
        if uiGlobals.request.db.error:
            return uiGlobals.request.db.error
        
        if sNow:
            return str(sNow)
        else:
            return "Unable to get system time."
        
    def wmGetActionPlans(self):
        sTaskID = uiCommon.getAjaxArg("sTaskID")
        sActionID = uiCommon.getAjaxArg("sActionID")
        sEcosystemID = uiCommon.getAjaxArg("sEcosystemID")
        try:
            sHTML = ""

            sSQL = "select plan_id, date_format(ap.run_on_dt, '%%m/%%d/%%Y %%H:%%i') as run_on_dt, ap.source, ap.action_id, ap.ecosystem_id," \
                " ea.action_name, e.ecosystem_name, ap.source, ap.schedule_id" \
                " from action_plan ap" \
                " left outer join ecotemplate_action ea on ap.action_id = ea.action_id" \
                " left outer join ecosystem e on ap.ecosystem_id = e.ecosystem_id" \
                " where ap.task_id = '" + sTaskID + "'" + \
                (" and ap.action_id = '" + sActionID + "'" if sActionID else "") + \
                (" and ap.ecosystem_id = '" + sEcosystemID + "'" if sEcosystemID else "") + \
                " order by ap.run_on_dt"
            dt = uiGlobals.request.db.select_all_dict(sSQL)
            if uiGlobals.request.db.error:
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
            else:
                if dt:
                    for dr in dt:
                        sHTML += " <div class=\"ui-widget-content ui-corner-all pointer clearfloat action_plan\"" \
                            " id=\"ap_" + str(dr["plan_id"]) + "\"" \
                            " plan_id=\"" + str(dr["plan_id"]) + "\"" \
                            " eco_id=\"" + dr["ecosystem_id"] + "\"" \
                            " run_on=\"" + str(dr["run_on_dt"]) + "\"" \
                            " source=\"" + dr["source"] + "\"" \
                            " schedule_id=\"" + str(dr["schedule_id"]) + "\"" \
                        ">"
                        sHTML += " <div class=\"floatleft action_plan_name\">"
    
                        # an icon denotes if it's manual or scheduled
                        if dr["source"] == "schedule":
                            sHTML += "<span class=\"floatleft ui-icon ui-icon-calculator\" title=\"Scheduled\"></span>"
                        else:
                            sHTML += "<span class=\"floatleft ui-icon ui-icon-document\" title=\"Run Later\"></span>"
    
                        sHTML += dr["run_on_dt"]
    
                        # show the action and ecosystem if it's in the results but NOT passed in
                        # that means we are looking at this from a TASK
                        if not sActionID:
                            if dr["ecosystem_name"]:
                                sHTML += " " + dr["ecosystem_name"]
    
                            if dr["action_name"]:
                                sHTML += " (" + dr["action_name"] + ")"
                        sHTML += " </div>"
    
                        sHTML += " <div class=\"floatright\">"
                        sHTML += "<span class=\"ui-icon ui-icon-trash action_plan_remove_btn\" title=\"Delete Plan\"></span>"
                        sHTML += " </div>"
    
    
                        sHTML += " </div>"

            return sHTML

        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmGetActionSchedules(self):
        sTaskID = uiCommon.getAjaxArg("sTaskID")
        sActionID = uiCommon.getAjaxArg("sActionID")
        sEcosystemID = uiCommon.getAjaxArg("sEcosystemID")
        try:
            sHTML = ""

            sSQL = "select s.schedule_id, s.label, s.descr, e.ecosystem_name, a.action_name" \
                " from action_schedule s" \
                " left outer join ecotemplate_action a on s.action_id = a.action_id" \
                " left outer join ecosystem e on s.ecosystem_id = e.ecosystem_id" \
                " where s.task_id = '" + sTaskID + "'" + \
                (" and e.ecosystem_id = '" +sEcosystemID + "'" if sEcosystemID else "")
            dt = uiGlobals.request.db.select_all_dict(sSQL)
            if uiGlobals.request.db.error:
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
            else:
                if dt:
                    for dr in dt:
                        sToolTip = ""
                        # show the action and ecosystem if it's in the results but NOT passed in
                        # that means we are looking at this from a TASK
                        if not sActionID:
                            sToolTip += "Ecosystem: " + (dr["ecosystem_name"] if dr["ecosystem_name"] else "None") + "<br />"
        
                            if dr["action_name"]:
                                sToolTip += "Action: " + dr["action_name"] + "<br />"
        
                        sToolTip += (dr["descr"] if dr["descr"] else "")
        
                        # draw it
                        sHTML += " <div class=\"ui-widget-content ui-corner-all pointer clearfloat action_schedule\"" \
                            " id=\"as_" + dr["schedule_id"] + "\"" \
                        ">"
                        sHTML += " <div class=\"floatleft schedule_name\">"
        
                        sHTML += "<span class=\"floatleft ui-icon ui-icon-calculator schedule_tip\" title=\"" + sToolTip + "\"></span>"
        
                        sHTML += (dr["schedule_id"] if not dr["label"] else dr["label"])
        
                        sHTML += " </div>"
        
                        sHTML += " <div class=\"floatright\">"
                        sHTML += "<span class=\"ui-icon ui-icon-trash schedule_remove_btn\" title=\"Delete Schedule\"></span>"
                        sHTML += " </div>"
        
        
                        sHTML += " </div>"

            return sHTML

        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmGetRecurringPlan(self):
        sScheduleID = uiCommon.getAjaxArg("sScheduleID")
        # tracing this backwards, if the action_plan table has a row marked "schedule" but no schedule_id, problem.
        if not sScheduleID:
            uiGlobals.request.Messages.append("Unable to retrieve Reccuring Plan - schedule id argument not provided.")
        
        sb = []

        # now we know the details, go get the timetable for that specific schedule
        sSQL = "select schedule_id, months, days, hours, minutes, days_or_weeks, label" \
            " from action_schedule" \
            " where schedule_id = '" + sScheduleID + "'"
        dt = uiGlobals.request.db.select_all_dict(sSQL)
        if uiGlobals.request.db.error:
            uiGlobals.request.Messages.append(uiGlobals.request.db.error)

        if dt:
            for dr in dt:
                sMo = dr["months"]
                sDa = dr["days"]
                sHo = dr["hours"]
                sMi = dr["minutes"]
                sDW = dr["days_or_weeks"]
                sDesc = (dr["schedule_id"] if not dr["label"] else dr["label"])
    
                sb.append("{")
                sb.append("\"sDescription\" : \"%s\"," % sDesc)
                sb.append("\"sMonths\" : \"%s\"," % sMo)
                sb.append("\"sDays\" : \"%s\"," % sDa)
                sb.append("\"sHours\" : \"%s\"," % sHo)
                sb.append("\"sMinutes\" : \"%s\"," % sMi)
                sb.append("\"sDaysOrWeeks\" : \"%s\"" % sDW)
                sb.append("}")
        else:
            uiGlobals.request.Messages.append("Unable to find details for Recurring Action Plan. " + uiGlobals.request.db.error + " ScheduleID [" + sScheduleID + "]")

        return "".join(sb)
    
    def wmDeleteSchedule(self):
        try:
            sScheduleID = uiCommon.getAjaxArg("sScheduleID")
    
            if not sScheduleID:
                uiGlobals.request.Messages.append("Missing Schedule ID.")
                return "Missing Schedule ID."
    
            sSQL = "delete from action_plan where schedule_id = '" + sScheduleID + "'"
            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)

            sSQL = "delete from action_schedule where schedule_id = '" + sScheduleID + "'"
            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
    
            #  if we made it here, so save the logs
            uiCommon.WriteObjectDeleteLog(uiGlobals.CatoObjectTypes.EcoTemplate, "", "", "Schedule [" + sScheduleID + "] deleted.")
    
            return ""
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmDeleteActionPlan(self):
        try:
            iPlanID = uiCommon.getAjaxArg("iPlanID")
    
            if iPlanID < 1:
                uiGlobals.request.Messages.append("Missing Action Plan ID.")
                return "Missing Action Plan ID."
    
            sSQL = "delete from action_plan where plan_id = " + iPlanID

            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)

            #  if we made it here, so save the logs
            uiCommon.WriteObjectDeleteLog(uiGlobals.CatoObjectTypes.EcoTemplate, "", "", "Action Plan [" + iPlanID + "] deleted.")
    
            return ""
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
    
    def wmRunLater(self):
        try:
            sTaskID = uiCommon.getAjaxArg("sTaskID")
            sActionID = uiCommon.getAjaxArg("sActionID")
            sEcosystemID = uiCommon.getAjaxArg("sEcosystemID")
            sRunOn = uiCommon.getAjaxArg("sRunOn")
            sParameterXML = uiCommon.getAjaxArg("sParameterXML")
            iDebugLevel = uiCommon.getAjaxArg("iDebugLevel")
            sAccountID = uiCommon.getAjaxArg("sAccountID")
            
            if not sTaskID or not sRunOn:
                uiGlobals.request.Messages.append("Missing Action Plan date or Task ID.")

            # we encoded this in javascript before the ajax call.
            # the safest way to unencode it is to use the same javascript lib.
            # (sometimes the javascript and .net libs don't translate exactly, google it.)
            sParameterXML = uiCommon.unpackJSON(sParameterXML)
            
            # we gotta peek into the XML and encrypt any newly keyed values
            sParameterXML = uiCommon.PrepareAndEncryptParameterXML(sParameterXML);          

            sSQL = "insert into action_plan (task_id, action_id, ecosystem_id, account_id," \
                " run_on_dt, parameter_xml, debug_level, source)" \
                " values (" \
                " '" + sTaskID + "'," + \
                (" '" + sActionID + "'" if sActionID else "''") + "," + \
                (" '" + sEcosystemID + "'" if sEcosystemID else "''") + "," + \
                (" '" + sAccountID + "'" if sAccountID else "''") + "," \
                " str_to_date('" + sRunOn + "', '%%m/%%d/%%Y %%H:%%i')," + \
                (" '" + uiCommon.TickSlash(sParameterXML) + "'" if sParameterXML else "null") + "," + \
                (iDebugLevel if iDebugLevel > "-1" else "null") + "," \
                " 'manual'" \
                ")"

            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmRunRepeatedly(self):
        try:
            sTaskID = uiCommon.getAjaxArg("sTaskID")
            sActionID = uiCommon.getAjaxArg("sActionID")
            sEcosystemID = uiCommon.getAjaxArg("sEcosystemID")
            sMonths = uiCommon.getAjaxArg("sMonths")
            sDays = uiCommon.getAjaxArg("sDays")
            sHours = uiCommon.getAjaxArg("sHours")
            sMinutes = uiCommon.getAjaxArg("sMinutes")
            sDaysOrWeeks = uiCommon.getAjaxArg("sDaysOrWeeks")
            sParameterXML = uiCommon.getAjaxArg("sParameterXML")
            iDebugLevel = uiCommon.getAjaxArg("iDebugLevel")
            sAccountID = uiCommon.getAjaxArg("sAccountID")
            
            if not sTaskID or not sMonths or not sDays or not sHours or not sMinutes or not sDaysOrWeeks:
                uiGlobals.request.Messages.append("Missing or invalid Schedule timing or Task ID.")

            # we encoded this in javascript before the ajax call.
            # the safest way to unencode it is to use the same javascript lib.
            # (sometimes the javascript and .net libs don't translate exactly, google it.)
            sParameterXML = uiCommon.unpackJSON(sParameterXML)
            
            # we gotta peek into the XML and encrypt any newly keyed values
            sParameterXML = uiCommon.PrepareAndEncryptParameterXML(sParameterXML);                

            # figure out a label and a description
            sDesc = ""
            sLabel, sDesc = uiCommon.GenerateScheduleLabel(sMonths, sDays, sHours, sMinutes, sDaysOrWeeks)

            sSQL = "insert into action_schedule (schedule_id, task_id, action_id, ecosystem_id, account_id," \
                " months, days, hours, minutes, days_or_weeks, label, descr, parameter_xml, debug_level)" \
                   " values (" \
                " '" + uiCommon.NewGUID() + "'," \
                " '" + sTaskID + "'," \
                + (" '" + sActionID + "'" if sActionID else "''") + "," \
                + (" '" + sEcosystemID + "'" if sEcosystemID else "''") + "," \
                + (" '" + sAccountID + "'" if sAccountID else "''") + "," \
                " '" + sMonths + "'," \
                " '" + sDays + "'," \
                " '" + sHours + "'," \
                " '" + sMinutes + "'," \
                " '" + sDaysOrWeeks + "'," \
                + (" '" + sLabel + "'" if sLabel else "null") + "," \
                + (" '" + sDesc + "'" if sDesc else "null") + "," \
                + (" '" + uiCommon.TickSlash(sParameterXML) + "'" if sParameterXML else "null") + "," \
                + (iDebugLevel if iDebugLevel > "-1" else "null") + \
                ")"

            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmSavePlan(self):
        try:
            iPlanID = uiCommon.getAjaxArg("iPlanID")
            sParameterXML = uiCommon.getAjaxArg("sParameterXML")
            iDebugLevel = uiCommon.getAjaxArg("iDebugLevel")
            """
             * JUST AS A REMINDER:
             * There is no parameter 'merging' happening here.  This is a Plan ...
             *   it has ALL the parameters it needs to pass to the CE.
             * 
             * """
    
            if not iPlanID:
                uiGlobals.request.Messages.append("Missing Action Plan ID.")

            # we encoded this in javascript before the ajax call.
            # the safest way to unencode it is to use the same javascript lib.
            # (sometimes the javascript and .net libs don't translate exactly, google it.)
            sParameterXML = uiCommon.unpackJSON(sParameterXML)
            
            # we gotta peek into the XML and encrypt any newly keyed values
            sParameterXML = uiCommon.PrepareAndEncryptParameterXML(sParameterXML);                

            sSQL = "update action_plan" \
                " set parameter_xml = " + ("'" + uiCommon.TickSlash(sParameterXML) + "'" if sParameterXML else "null") + "," \
                " debug_level = " + (iDebugLevel if iDebugLevel > -1 else "null") + \
                " where plan_id = " + iPlanID

            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())


    def wmSaveSchedule(self):
        sScheduleID = uiCommon.getAjaxArg("sScheduleID")
        sMonths = uiCommon.getAjaxArg("sMonths")
        sDays = uiCommon.getAjaxArg("sDays")
        sHours = uiCommon.getAjaxArg("sHours")
        sMinutes = uiCommon.getAjaxArg("sMinutes")
        sDaysOrWeeks = uiCommon.getAjaxArg("sDaysOrWeeks")
        sParameterXML = uiCommon.getAjaxArg("sParameterXML")
        iDebugLevel = uiCommon.getAjaxArg("iDebugLevel")
        """
         * JUST AS A REMINDER:
         * There is no parameter 'merging' happening here.  This is a Scheduled Plan ...
         *   it has ALL the parameters it needs to pass to the CE.
         * 
         * """

        try:
            if not sScheduleID or not sMonths or not sDays or not sHours or not sMinutes or not sDaysOrWeeks:
                uiGlobals.request.Messages.append("Missing Schedule ID or invalid timetable.")

            # we encoded this in javascript before the ajax call.
            # the safest way to unencode it is to use the same javascript lib.
            # (sometimes the javascript and .net libs don't translate exactly, google it.)
            sParameterXML = uiCommon.unpackJSON(sParameterXML)
            
            # we gotta peek into the XML and encrypt any newly keyed values
            sParameterXML = uiCommon.PrepareAndEncryptParameterXML(sParameterXML);                

            # whack all plans for this schedule, it's been changed
            sSQL = "delete from action_plan where schedule_id = '" + sScheduleID + "'"
            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)


            # figure out a label
            sLabel, sDesc = uiCommon.GenerateScheduleLabel(sMonths, sDays, sHours, sMinutes, sDaysOrWeeks)

            sSQL = "update action_schedule set" \
                " months = '" + sMonths + "'," \
                " days = '" + sDays + "'," \
                " hours = '" + sHours + "'," \
                " minutes = '" + sMinutes + "'," \
                " days_or_weeks = '" + sDaysOrWeeks + "'," \
                " label = " + ("'" + sLabel + "'" if sLabel else "null") + "," \
                " descr = " + ("'" + sDesc + "'" if sDesc else "null") + "," \
                " parameter_xml = " + ("'" + uiCommon.TickSlash(sParameterXML) + "'" if sParameterXML else "null") + "," \
                " debug_level = " + (iDebugLevel if iDebugLevel > -1 else "null") + \
                " where schedule_id = '" + sScheduleID + "'"

            if not uiGlobals.request.db.exec_db_noexcep(sSQL):
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())

    def wmGetSettings(self):
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name
        
            s = settings.settings()
            if s:
                return s.AsJSON()
            
            #should not get here if all is well
            return "{'result':'fail','error':'Error getting settings.'}"
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    def wmSaveSettings(self):
        """
            In this method, the values come from the browser in a jQuery serialized array of name/value pairs.
        """
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name

            sType = uiCommon.getAjaxArg("sType")
            sValues = uiCommon.getAjaxArg("sValues")
        
            # sweet, use getattr to actually get the class we want!
            objname = getattr(settings.settings, sType.lower())
            obj = objname()
            if obj:
                # spin the sValues array and set the appropriate properties.
                # setattr is so awesome
                for pair in sValues:
                    setattr(obj, pair["name"], pair["value"])
                    # print  "setting %s to %s" % (pair["name"], pair["value"])
                # of course all of our settings classes must have a DBSave method
                result, msg = obj.DBSave()
                
                if result:
                    uiCommon.AddSecurityLog(uiGlobals.SecurityLogTypes.Security, 
                        uiGlobals.SecurityLogActions.ConfigChange, uiGlobals.CatoObjectTypes.NA, "", 
                        "%s settings changed." % sType.capitalize())
                    
                    return "{'result':'success'}"
                else:
                    return "{'result':'fail','error':'%s'}" % msg
            
            #should not get here if all is well
            return "{'result':'fail','error':'Error saving settings - no type provided.'}"
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

    def wmGetMyAccount(self):
        try:
            user_id = uiCommon.GetSessionUserID()

            sSQL = """select full_name, username, authentication_type, email, 
                ifnull(security_question, '') as security_question, 
                ifnull(security_answer, '') as security_question
                from users
                where user_id = '%s'""" % user_id
            dr = uiGlobals.request.db.select_row_dict(sSQL)
            if uiGlobals.request.db.error:
                uiGlobals.request.Messages.append(uiGlobals.request.db.error)
                raise uiGlobals.request.db.error
            else:
                # here's the deal - we aren't even returning the 'local' settings if the type is ldap.
                if dr["authentication_type"] == "local":
                    return json.dumps(dr)
                else:
                    d = {"full_name":dr["full_name"], "username": dr["username"], "email":dr["email"], "type":dr["authentication_type"]}
                    return json.dumps(d)

        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            
    def wmSaveMyAccount(self):
        """
            In this method, the values come from the browser in a jQuery serialized array of name/value pairs.
        """
        try:
            uiGlobals.request.Function = __name__ + "." + sys._getframe().f_code.co_name

            user_id = uiCommon.GetSessionUserID()
            sValues = uiCommon.getAjaxArg("sValues")
        
            sql_bits = []
            for pair in sValues:
                # but to prevent sql injection, only build a sql from values we accept
                if pair["name"] == "my_email":
                    sql_bits.append("email = '%s'" %  uiCommon.TickSlash(pair["value"]))
                if pair["name"] == "my_question":
                    sql_bits.append("security_question = '%s'" % uiCommon.TickSlash(pair["value"]))
                if pair["name"] == "my_answer":
                    if pair["value"]:
                        sql_bits.append("security_answer = '%s'" % catocommon.cato_encrypt(pair["value"]))

                # only do the password if it was provided
                if pair["name"] == "my_password":
                    if pair["value"]:
                        sql_bits.append("user_password = '%s'" % catocommon.cato_encrypt(pair["value"]))

            sql = "update users set %s where user_id = '%s'" % (",".join(sql_bits), user_id)

            if not uiGlobals.request.db.exec_db_noexcep(sql):
                uiCommon.log(uiGlobals.request.db.error, 0)
                return uiGlobals.request.db.error

            uiCommon.WriteObjectChangeLog(uiGlobals.CatoObjectTypes.User, user_id, user_id, "My Account settings updated.")
                
            return ""
        except Exception:
            uiGlobals.request.Messages.append(traceback.format_exc())
            return traceback.format_exc()

            