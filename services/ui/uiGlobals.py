#this globals are set on init, and anything that imports this file
# has access to these objects
web = None
session = None
#this db references an open connection used by many functions
#don't use it all the time - some functions that need transactions, etc should get
# their own connections.
dbconn = None

# "server" is the running web service
server = None

# the debug level (0-4 with 0 being 'none' and 4 being 'verbose')
debuglevel = 2 #defaults to 2

ConnectionTypes = ["ssh - ec2", "ssh", "telnet", "mysql", "oracle", "sqlserver", "sybase", "informix"]
    
class SecurityLogTypes(object):
    Object = "Object"
    Security = "Security"
    Usage = "Usage"
    Other = "Other"
    
class SecurityLogActions(object):
    UserLogin = "UserLogin"
    UserLogout = "UserLogout"
    UserLoginAttempt = "UserLoginAttempt"
    UserPasswordChange = "UserPasswordChange"
    UserSessionDrop = "UserSessionDrop"
    SystemLicenseException = "SystemLicenseException"
    
    ObjectAdd = "ObjectAdd"
    ObjectModify = "ObjectModify"
    ObjectDelete = "ObjectDelete"
    ObjectView = "ObjectView"
    ObjectCopy = "ObjectCopy"
    
    PageView = "PageView"
    ReportView = "ReportView"
    
    APIInterface = "APIInterface"
    
    Other = "Other"
    ConfigChange = "ConfigChange"

class CatoObjectTypes(object):
    NA = 0
    User = 1
    Asset = 2
    Task = 3
    Schedule = 4
    Registry = 6
    MessageTemplate = 18
    Parameter = 34
    Credential = 35
    Domain = 36
    CloudAccount = 40
    Cloud = 41
    Ecosystem = 50
    EcoTemplate = 51
            