"""
    All of the settings for the Cato modules.
"""
import json
from catocommon import catocommon

class settings(object):
    #initing the whole parent class gives you DICTIONARIES of every subclass
    def __init__(self):
        self.Security = self.security().__dict__
        
    def AsJSON(self):
        return json.dumps(self.__dict__)

    class security(object):
        """
            These settings are defaults if there are no values in the database.
        """
        PassMaxAge = 90 # how old can a password be?
        PassMaxAttempts = 3
        PassMaxLength = 32
        PassMinLength = 8
        PassComplexity = True # require 'complex' passwords (number and special character)
        PassAgeWarn = 15 # number of days before expiration to begin warning the user about password expiration
        PasswordHistory = 5 # The number of historical passwords to cache and prevent reuse.
        PassRequireInitialChange = True # require change on initial login?
        AutoLockReset = 5 # The number of minutes before failed password lockout expires
        LoginMessage = "" # The message that appears on the login screen
        AuthErrorMessage = "" # a customized message that appears when there are failed login attempts
        NewUserMessage = "" # the body of an email sent to new user accounts
        PageViewLogging = False # whether or not to log user-page access in the security log
        ReportViewLogging = False # whether or not to log user-report views in the security log
        AllowLogin = True # Is the system "up" and allowing users to log in?
        
        def __init__(self):
            try:
                sSQL = "select pass_max_age, pass_max_attempts, pass_max_length, pass_min_length, pass_age_warn_days," \
                        " auto_lock_reset, login_message, auth_error_message, pass_complexity, pass_require_initial_change, pass_history," \
                        " page_view_logging, report_view_logging, allow_login, new_user_email_message" \
                        " from login_security_settings" \
                        " where id = 1"
                
                db = catocommon.new_conn()
                row = db.select_row_dict(sSQL)
                if row:
                    self.PassMaxAge = row["pass_max_age"]
                    self.PassMaxAttempts = row["pass_max_attempts"]
                    self.PassMaxLength = row["pass_max_length"]
                    self.PassMinLength = row["pass_min_length"]
                    self.PassComplexity = catocommon.IsTrue(row["pass_complexity"])
                    self.PassAgeWarn = row["pass_age_warn_days"]
                    self.PasswordHistory = row["pass_history"]
                    self.PassRequireInitialChange = catocommon.IsTrue(row["pass_require_initial_change"])
                    self.AutoLockReset = row["auto_lock_reset"]
                    self.LoginMessage = row["login_message"]
                    self.AuthErrorMessage = row["auth_error_message"]
                    self.NewUserMessage = row["new_user_email_message"]
                    self.PageViewLogging = catocommon.IsTrue(row["page_view_logging"])
                    self.ReportViewLogging = catocommon.IsTrue(row["report_view_logging"])
                    self.AllowLogin = catocommon.IsTrue(row["allow_login"])
            except Exception, ex:
                raise Exception(ex)
            finally:
                db.close()
            
        def DBSave(self):
            try:
                sSQL = "update login_security_settings set" \
                    " pass_max_age='" + self.PassMaxAge + "'," \
                    " pass_max_attempts='" + self.PassMaxAttempts + "'," \
                    " pass_max_length='" + self.PassMaxLength + "'," \
                    " pass_min_length='" + self.PassMinLength + "'," \
                    " pass_complexity='" + ("1" if self.PassComplexity else "0") + "'," \
                    " pass_age_warn_days='" + self.PassAgeWarn + "'," \
                    " pass_history = '" + self.PasswordHistory + "'," \
                    " pass_require_initial_change='" + ("1" if self.PassRequireInitialChange else "0") + "'," \
                    " auto_lock_reset='" + self.AutoLockReset + "'," \
                    " login_message='" + self.LoginMessage.replace("'", "''") + "'," \
                    " auth_error_message='" + self.AuthErrorMessage.replace("'", "''").replace(";", "") + "'," \
                    " new_user_email_message='" + self.NewUserMessage.replace("'", "''").replace(";", "") + "'," \
                    " page_view_logging='" + ("1" if self.PageViewLogging else "0") + "'," \
                    " report_view_logging='" + ("1" if self.ReportViewLogging else "0") + "'," \
                    " allow_login='" + ("1" if self.AllowLogin else "0") + "'" \
                    " where id = 1"

                db = catocommon.new_conn()
                if not db.exec_db_noexcep(sSQL):
                    return False, db.error
            
                return True, ""
            except Exception, ex:
                raise Exception(ex)
            finally:
                db.close()

        def AsJSON(self):
            return json.dumps(self.__dict__)
