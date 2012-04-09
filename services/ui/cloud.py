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
            
            uiCommon.WriteObjectAddLog(db, uiGlobals.CatoObjectTypes.Cloud, sNewID, sCloudName, "Cloud Created")
            
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
            
            uiCommon.WriteObjectPropertyChangeLog(db, uiGlobals.CatoObjectTypes.Cloud, self.ID, self.Name, sOriginalName, self.Name)
            
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
    
    def Fill(self, sFilter):
        sWhereString = ""
        if sFilter:
            aSearchTerms = sFilter.split()
            for term in aSearchTerms:
                if term:
                    sWhereString += " and (account_name like '%%" + term + "%%' " \
                        "or account_number like '%%" + term + "%%' " \
                        "or provider like '%%" + term + "%%' " \
                        "or login_id like '%%" + term + "%%') "

        sSQL = "select account_id, account_name, account_number, provider, login_id, auto_manage_security," \
            " case is_default when 1 then 'Yes' else 'No' end as is_default," \
            " (select count(*) from ecosystem where account_id = cloud_account.account_id) as has_ecosystems" \
            " from cloud_account" \
            " where 1=1 " + sWhereString + " order by is_default desc, account_name"
        
        db = catocommon.new_conn()
        self.DataTable = db.select_all(sSQL)
        db.close()

    def AsJSON(self):
        try:
            i = 1
            sb = []
            sb.append("[")
            for row in self.DataTable:
                sb.append("{")
                sb.append("\"%s\" : \"%s\"," % ("ID", row[0]))
                sb.append("\"%s\" : \"%s\"" % ("Name", row[1]))
                sb.append("}")
            
                #the last one doesn't get a trailing comma
                print str(i) + " : " + str(len(self.DataTable))
                if i < len(self.DataTable):
                    sb.append(",")
                    
                i += 1

            sb.append("]")
            return "".join(sb)
        except Exception, ex:
            raise ex
