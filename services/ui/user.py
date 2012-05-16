"""
    THIS CLASS has it's own database connections.
    Why?  Because it isn't only used by the UI.
"""
import json
from catocommon import catocommon

class Users(object): 
    rows = {}
        
    def __init__(self, sFilter=""):
        try:
            sWhereString = ""
            if sFilter:
                aSearchTerms = sFilter.split()
                for term in aSearchTerms:
                    if term:
                        sWhereString += " and (u.full_name like '%%" + term + "%%' " \
                            "or u.user_role like '%%" + term + "%%' " \
                            "or u.username like '%%" + term + "%%' " \
                            "or u.status like '%%" + term + "%%' " \
                            "or u.last_login_dt like '%%" + term + "%%') "
    
            sSQL = "select u.user_id, u.username, u.full_name, u.last_login_dt, u.email," \
                " case when u.status = '1' then 'Enabled' when u.status = '-1' then 'Locked'" \
                " when u.status = '0' then 'Disabled' end as status," \
                " u.authentication_type, u.user_role as role" \
                " from users u" \
                " where u.status <> 86 " + sWhereString + " order by u.full_name"
            
            db = catocommon.new_conn()
            self.rows = db.select_all_dict(sSQL)
        except Exception, ex:
            raise Exception(ex)
        finally:
            db.close()

    def AsJSON(self):
        try:
            return json.dumps(self.rows)
        except Exception, ex:
            raise ex

class User(object):
    ID = ""
    FullName = ""
    Status = ""
    LoginID = ""
    Role = ""
    LastLoginDT = ""
    AuthenticationType = ""
    ExpirationDT = ""
    SecurityQuestion = ""
    FailedLoginAttempts = 0
    ForceChange = False
    Email = ""
    SettingsXML = ""
    
    def FromName(self, sUsername):
        self.PopulateUser(login_id=sUsername)
        
    def FromID(self, sUserID):
        self.PopulateUser(user_id=sUserID)

    def PopulateUser(self, user_id="", login_id=""):
        """
            Note the absence of password or security_answer in this method.  There are specialized 
            methods for testing passwords, etc.
        """
        try:
            if not user_id and not login_id:
                raise Exception("Error building User object: User ID or Login is required.");    
            
            sSQL = """select u.user_id, u.username, u.full_name, u.status, u.last_login_dt,
                u.failed_login_attempts, u.email ,u.authentication_type,
                u.security_question, u.force_change, u.settings_xml,
                u.user_role, u.expiration_dt
                from users u"""
            
            if user_id:
                sSQL += " where u.user_id = '%s'""" % user_id
            elif login_id:
                sSQL += " where u.username = '%s'""" % login_id


            db = catocommon.new_conn()
            dr = db.select_row_dict(sSQL)
            
            if dr is not None:
                self.ID = dr["user_id"]
                self.FullName = dr["full_name"]
                self.LoginID = dr["username"]
                self.Status = dr["status"]
                self.Role = dr["user_role"]
                self.AuthenticationType = dr["authentication_type"]
                self.LastLoginDT = ("" if not dr["last_login_dt"] else str(dr["last_login_dt"]))
                self.ExpirationDT = ("" if not dr["expiration_dt"] else str(dr["expiration_dt"]))
                self.SecurityQuestion = ("" if not dr["security_question"] else dr["security_question"])
                self.FailedLoginAttempts = (0 if not dr["failed_login_attempts"] else dr["failed_login_attempts"])
                self.ForceChange = (True if dr["force_change"] == 1 else False)
                self.Email = ("" if not dr["email"] else dr["email"])
                self.SettingsXML = ("" if not dr["settings_xml"] else dr["settings_xml"])

            else: 
                raise Exception("Unable to build User object. Either no Users are defined, or no User with ID [" + user_id + "] could be found.")
        except Exception, ex:
            raise Exception(ex)
        finally:
            db.close()        

    def AsJSON(self):
        try:
            return json.dumps(self.__dict__)
        except Exception, ex:
            raise ex

    def Authenticate(self, login_id, password):
        try:
            # alrighty, lets check the password
            # we do this by encrypting the form submission and comparing, 
            # NOT by decrypting it here.
            sql = "select user_password from users where username='%s'" % login_id
            db = catocommon.new_conn()
            db_pwd = db.select_col_noexcep(sql)
            
            encpwd = catocommon.cato_encrypt(password)
            
            if db_pwd != encpwd:
                print "Invalid login attempt - [%s] bad password." % (login_id)
                return False

            self.PopulateUser(login_id=login_id)
            # TODO:
            # Check Expiration
            # Check failed login attempts against the security policy
            # Check for "locked" or "disabled" status
            # throw back pretty codes for each case, so the login page dialogs can react accordingly



            # reset the user counters and last_login
#            sql = "update users set failed_login_attempts=0, last_login_dt=now() where user_id='%s'" % self.ID
#            if not db.exec_db_noexcep(sql):
#                print db.error
        
            return True
        except Exception, ex:
            raise Exception(ex)
            return False
        finally:
            db.close()        

    #STATIC METHOD
    #creates this Cloud as a new record in the db
    #and returns the object
#    @staticmethod
#    def DBCreateNew(sAccountName, sAccountNumber, sProvider, sLoginID, sLoginPassword, sIsDefault):
#        try:
#            db = catocommon.new_conn()
#
#            # if there are no rows yet, make this one the default even if the box isn't checked.
#            if sIsDefault == "0":
#                iExists = -1
#                
#                sSQL = "select count(*) as cnt from cloud_account"
#                iExists = db.select_col_noexcep(sSQL)
#                if iExists == None:
#                    if db.error:
#                        db.tran_rollback()
#                        return None, "Unable to count Cloud Accounts: " + db.error
#                
#                if iExists == 0:
#                    sIsDefault = "1"
#
#            sNewID = catocommon.NewGUID()
#            sPW = (catocommon.cato_encrypt(sLoginPassword) if sLoginPassword else "")
#            
#            sSQL = "insert into cloud_account" \
#                " (account_id, account_name, account_number, provider, is_default, login_id, login_password, auto_manage_security)" \
#                " values ('" + sNewID + "'," \
#                "'" + sAccountName + "'," \
#                "'" + sAccountNumber + "'," \
#                "'" + sProvider + "'," \
#                "'" + sIsDefault + "'," \
#                "'" + sLoginID + "'," \
#                "'" + sPW + "'," \
#                "0)"
#            
#            if not db.tran_exec_noexcep(sSQL):
#                if db.error == "key_violation":
#                    sErr = "A Cloud Account with that name already exists.  Please select another name."
#                    return None, sErr
#                else: 
#                    return None, db.error
#            
#            # if "default" was selected, unset all the others
#            if sIsDefault == "1":
#                sSQL = "update cloud_account set is_default = 0 where account_id <> '" + sNewID + "'"
#                if not db.tran_exec_noexcep(sSQL):
#                    raise Exception(db.error)
#
#            db.tran_commit()
#            
#            # now it's inserted... lets get it back from the db as a complete object for confirmation.
#            ca = CloudAccount()
#            ca.FromID(sNewID)
#
#            # yay!
#            return ca, None
#        except Exception, ex:
#            raise ex
#        finally:
#            db.close()

    def DBUpdate(self):
        try:
            db = catocommon.new_conn()
            
            #  only update the passwword if it has changed
            # a password is required, so an empty value does NOT update!
            sNewPassword = ""
            if self.LoginPassword:
                sNewPassword = (", password = '" + catocommon.cato_encrypt(self.Password) + "'" if self.Password else "")

            sSQL = "update cloud_account set" \
                    " account_name = '" + self.Name + "'," \
                    " account_number = '" + self.AccountNumber + "'," \
                    " provider = '" + self.Provider.Name + "'," \
                    " is_default = '" + ("1" if self.IsDefault else "0") + "'," \
                    " auto_manage_security = 0," \
                    " login_id = '" + self.LoginID + "'" + \
                    sNewPassword + \
                    " where account_id = '" + self.ID + "'"
            
            if not db.exec_db_noexcep(sSQL):
                if db.error == "key_violation":
                    sErr = "A Cloud Account with that name already exists.  Please select another name."
                    return False, sErr
                else: 
                    return False, db.error
            
            # if "default" was selected, unset all the others
            if self.IsDefault:
                sSQL = "update cloud_account set is_default = 0 where account_id <> '" + self.ID + "'"
                # not worth failing... we'll just end up with two defaults.
                db.exec_db_noexcep(sSQL)

            return True, None
        except Exception, ex:
            raise ex
        finally:
            db.close()
