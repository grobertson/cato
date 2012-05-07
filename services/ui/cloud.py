"""
    THIS CLASS has it's own database connections.
    Why?  Because it isn't only used by the UI.
"""

import uiCommon
import uiGlobals
from catocommon import catocommon

class Cloud(object):
    IsUserDefined = True
    ID = None
    Name = None
    APIUrl = None
    APIProtocol = None
    Region = None
    Provider = None

    #the default constructor (manual creation)
    def FromArgs(self, p, bUserDefined, sID, sName, sAPIUrl, sAPIProtocol, sRegion):
        if not sID:
            raise Exception("Error building Cloud object: Cloud ID is required.")

        self.IsUserDefined = bUserDefined
        self.ID = sID
        self.Name = sName
        self.APIUrl = sAPIUrl
        self.APIProtocol = sAPIProtocol
        self.Region = sRegion
        self.Provider = p

    def FromID(self, sCloudID):
        try:
            if not sCloudID:
                raise Exception("Error building Cloud object: Cloud ID is required.")
            
            #search for the sCloudID in the CloudProvider Class -AND- the database
            cp = uiCommon.GetCloudProviders()
            if not cp:
                raise Exception("Error building Cloud object: Unable to GetCloudProviders.")
            #check the CloudProvider class first ... it *should be there unless something is wrong.
            for pname, p in cp.Providers.iteritems():
                for cname, c in p.Clouds.iteritems():
                    if c.ID == sCloudID:
                        self.IsUserDefined = c.IsUserDefined
                        self.ID = c.ID
                        self. Name = c.Name
                        self.APIUrl = c.APIUrl
                        self.APIProtocol = c.APIProtocol
                        self.Region = c.Region
                        self.Provider = c.Provider
                        
                        return
            
            #well, if we got here we have a problem... the ID provided wasn't found anywhere.
            #this should never happen, so bark about it.
            #raise Exception("Unable to build Cloud object. Either no Clouds are defined, or no Cloud with ID [" + sCloudID + "] could be found.")   
        except Exception, ex:
            raise ex

    def IsValidForCalls(self):
        if self.APIUrl and self.APIProtocol:
            return True
        return False

    def AsJSON(self):
        try:
            sb = []
            sb.append("{")
            sb.append("\"%s\" : \"%s\"," % ("ID", self.ID))
            sb.append("\"%s\" : \"%s\"," % ("Name", self.Name))
            sb.append("\"%s\" : \"%s\"," % ("Provider", self.Provider.Name))
            sb.append("\"%s\" : \"%s\"," % ("APIUrl", self.APIUrl))
            sb.append("\"%s\" : \"%s\"," % ("APIProtocol", self.APIProtocol))
            sb.append("\"%s\" : \"%s\"" % ("Region", self.Region))
            sb.append("}")
            return "".join(sb)
        except Exception, ex:
            raise ex

    #STATIC METHOD
    #creates this Cloud as a new record in the db
    #and returns the object
    @staticmethod
    def DBCreateNew(sCloudName, sProvider, sAPIUrl, sAPIProtocol):
        try:
            sSQL = ""
            sNewID = uiCommon.NewGUID()
            sSQL = "insert into clouds (cloud_id, cloud_name, provider, api_url, api_protocol)" \
                " values ('" + sNewID + "'," + "'" + sCloudName + "'," + "'" + sProvider + "'," + "'" + sAPIUrl + "'," + "'" + sAPIProtocol + "')"
            db = catocommon.new_conn()
            if not db.exec_db_noexcep(sSQL):
                if db.error == "key_violation":
                    return None, "A Cloud with that name already exists.  Please select another name."
                else:
                    return None, db.error
            db.close()
            
            #update the CloudProviders in the session
            cp = uiCommon.GetCloudProviders() #get the session object
            cp.Providers[sProvider].RefreshClouds() #find the proper Provider IN THE SESSION OBJECT and tell it to refresh it's clouds.
            uiCommon.UpdateCloudProviders(cp) #update the session
            
            #now it's inserted and in the session... lets get it back from the db as a complete object for confirmation.
            c = Cloud()
            c.FromID(sNewID)
            #yay!
            return c, None
        except Exception, ex:
            raise ex

    #INSTANCE METHOD
    #updates the current Cloud object to the db
    def DBUpdate(self):
        try:
            db = catocommon.new_conn()
            #of course we do nothing if this cloud was hardcoded in the xml
            #just return success, which should never happen since the user can't get to edit a hardcoded Cloud anyway.
            if not self.IsUserDefined:
                return True
            #what's the original name?
            sSQL = "select cloud_name from clouds where cloud_id = '" + self.ID + "'"
            sOriginalName = db.select_col_noexcep(sSQL)
            if not sOriginalName:
                if db.error:
                    raise Exception("Error getting original cloud name:" + db.error)
            
            sSQL = "update clouds set" + " cloud_name = '" + self.Name + "'," \
                " provider = '" + self.Provider.Name + "'," \
                " api_protocol = '" + self.APIProtocol + "'," \
                " api_url = '" + self.APIUrl + "'" \
                " where cloud_id = '" + self.ID + "'"
            if not db.exec_db_noexcep(sSQL):
                if db.error == "key_violation":
                    return None, "A Cloud with that name already exists.  Please select another name."
                else:
                    return None, db.error
            db.close()
            
            #update the CloudProviders in the session
            cp = uiCommon.GetCloudProviders() #get the session object
            cp.Providers[self.Provider.Name].RefreshClouds() #find the proper Provider IN THE SESSION OBJECT and tell it to refresh it's clouds.
            uiCommon.UpdateCloudProviders(cp) #update the session
            return True
        except Exception, ex:
            raise Exception(ex)


# Note: this is not a container for CloudAccount objects - it's just a rowset from the database
# with an AsJSON method.
# why? Because the CloudAccount objects contain a full set of Provider information - stuff
# we don't need for list pages and dropdowns.
class CloudAccounts(object): 
    DataTable = None
    
    def Fill(self, sFilter="", sProvider=""):
        sWhereString = ""
        if sFilter:
            aSearchTerms = sFilter.split()
            for term in aSearchTerms:
                if term:
                    sWhereString += " and (account_name like '%%" + term + "%%' " \
                        "or account_number like '%%" + term + "%%' " \
                        "or provider like '%%" + term + "%%' " \
                        "or login_id like '%%" + term + "%%') "

        # if a sProvider arg is passed, we explicitly limit to this provider
        if sProvider:
            sWhereString += " and provider = '%s'" % sProvider
            
        sSQL = "select account_id, account_name, account_number, provider, login_id, auto_manage_security," \
            " case is_default when 1 then 'Yes' else 'No' end as is_default," \
            " (select count(*) from ecosystem where account_id = cloud_account.account_id) as has_ecosystems" \
            " from cloud_account" \
            " where 1=1 " + sWhereString + " order by is_default desc, account_name"
        
        db = catocommon.new_conn()
        self.DataTable = db.select_all_dict(sSQL)
        db.close()

    def AsJSON(self):
        try:
            i = 1
            sb = []
            sb.append("[")
            for row in self.DataTable:
                sb.append("{")
                sb.append("\"%s\" : \"%s\"," % ("ID", row["account_id"]))
                sb.append("\"%s\" : \"%s\"" % ("Name", row["account_name"]))
                sb.append("}")
            
                #the last one doesn't get a trailing comma
                if i < len(self.DataTable):
                    sb.append(",")
                    
                i += 1

            sb.append("]")
            return "".join(sb)
        except Exception, ex:
            raise ex

class CloudAccount(object):
    ID = None
    Name = None
    AccountNumber = None
    LoginID = None
    LoginPassword = None
    IsDefault = None
    Provider = None

    def FromID(self, sAccountID):
        try:
            if not sAccountID:
                raise Exception("Error building Cloud Account object: Cloud Account ID is required.");    
            
            sSQL = "select account_name, account_number, provider, login_id, login_password, is_default" \
                " from cloud_account" \
                " where account_id = '" + sAccountID + "'"

            db = catocommon.new_conn()
            dr = db.select_row_dict(sSQL)
            db.close()
            
            if dr is not None:
                self.ID = sAccountID
                self.Name = dr["account_name"]
                self.AccountNumber = ("" if not dr["account_number"] else dr["account_number"])
                self.LoginID = ("" if not dr["login_id"] else dr["login_id"])
                self.LoginPassword = ("" if not dr["login_password"] else catocommon.cato_decrypt(dr["login_password"]))
                self.IsDefault = (True if dr["is_default"] == 1 else False)
                
                # find a provider object
                cp = uiCommon.GetCloudProviders()
                if not cp:
                    raise Exception("Error building Cloud Account object: Unable to GetCloudProviders.")
                    return

                #check the CloudProvider class first ... it *should be there unless something is wrong.
                if cp.Providers.has_key(dr["provider"]):
                    self.Provider = cp.Providers[dr["provider"]]
                else:
                    raise Exception("Provider [" + dr["provider"] + "] does not exist in the cloud_providers session xml.")

            else: 
                raise Exception("Unable to build Cloud Account object. Either no Cloud Accounts are defined, or no Account with ID [" + sAccountID + "] could be found.")
        except Exception, ex:
            raise Exception(ex)

    def IsValidForCalls(self):
        if self.LoginID and self.LoginPassword:
            return True
        return False

    def AsJSON(self):
        try:
            sb = []
            sb.append("{")
            sb.append("\"%s\" : \"%s\"," % ("ID", self.ID))
            sb.append("\"%s\" : \"%s\"," % ("Name", self.Name))
            sb.append("\"%s\" : \"%s\"," % ("Provider", self.Provider.Name))
            sb.append("\"%s\" : \"%s\"," % ("AccountNumber", self.AccountNumber))
            sb.append("\"%s\" : \"%s\"," % ("LoginID", self.LoginID))
            sb.append("\"%s\" : \"%s\"," % ("LoginPassword", self.LoginPassword))
            sb.append("\"%s\" : \"%s\"," % ("IsDefault", self.IsDefault))
            
            # the clouds hooked to this account
            sb.append("\"Clouds\" : {")
            lst = []
            for cname, c in self.Provider.Clouds.iteritems():
                #stick em all in a list for now
                s = "\"%s\" : %s" % (c.ID, c.AsJSON())
                lst.append(s)
            #join the list using commas!
            sb.append(",".join(lst))

            sb.append("}")

            
            sb.append("}")
            return "".join(sb)
        except Exception, ex:
            raise ex

