import uiCommon

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
            cp = uiCommon.GetCloudProviders();
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
            #raise Exception("Unable to build Cloud object. Either no Clouds are defined, or no Cloud with ID [" + sCloudID + "] could be found.");    
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

"""    #CLASS METHOD
    #creates this Cloud as a new record in the db
    #and returns the object
    def DBCreateNew(sCloudName, sProvider, sAPIUrl, sAPIProtocol, sErr):
        try:
            dc = dataAccess()
            ui = acUI.acUI()
            sSQL = ""
            sNewID = ui.NewGUID()
            sSQL = "insert into clouds (cloud_id, cloud_name, provider, api_url, api_protocol)" + " values ('" + sNewID + "'," + "'" + sCloudName + "'," + "'" + sProvider + "'," + "'" + sAPIUrl + "'," + "'" + sAPIProtocol + "')"
            if not dc.sqlExecuteUpdate(sSQL, ):
                if sErr == "key_violation":
                    sErr = "A Cloud with that name already exists.  Please select another name."
                    return None
                else:
                    raise Exception(sErr)
            ui.WriteObjectAddLog(Globals.acObjectTypes.Cloud, sNewID, sCloudName, "Cloud Created")
            #update the CloudProviders in the session
            cp = ui.GetCloudProviders() #get the session object
            cp[sProvider].RefreshClouds() #find the proper Provider IN THE SESSION OBJECT and tell it to refresh it's clouds.
            ui.UpdateCloudProviders(cp) #update the session
            #now it's inserted... lets get it back from the db as a complete object for confirmation.
            c = Cloud(sNewID)
            #yay!
            return c
        except Exception, ex:
            raise Exception(ex.Message)


    DBCreateNew = staticmethod(DBCreateNew)

    #INSTANCE METHOD
    #updates the current Cloud object to the db
    def DBUpdate(self, sErr):
        try:
            ui = acUI.acUI()
            dc = dataAccess()
            sSQL = ""
            #of course we do nothing if this cloud was hardcoded in the xml
            #just return success, which should never happen since the user can't get to edit a hardcoded Cloud anyway.
            if not self._IsUserDefined:
                return True
            #what's the original name?
            sOriginalName = ""
            sSQL = "select cloud_name from clouds where cloud_id = '" + self._ID + "'"
            if not dc.sqlGetSingleString(, sSQL, ):
                raise Exception("Error getting original cloud name:" + sErr)
            sSQL = "update clouds set" + " cloud_name = '" + self._Name + "'," + " provider = '" + self._Provider.Name + "'," + " api_protocol = '" + self._APIProtocol + "'," + " api_url = '" + self._APIUrl + "'" + " where cloud_id = '" + self._ID + "'"
            if not dc.sqlExecuteUpdate(sSQL, ):
                if sErr == "key_violation":
                    sErr = "A Cloud with that name already exists.  Please select another name."
                    return False
                else:
                    raise Exception(sErr)
            ui.WriteObjectChangeLog(Globals.acObjectTypes.Cloud, self._ID, self._Name, sOriginalName, self._Name)
            #update the CloudProviders in the session
            cp = ui.GetCloudProviders() #get the session object
            cp[self._Provider.Name].RefreshClouds() #find the proper Provider IN THE SESSION OBJECT and tell it to refresh it's clouds.
            ui.UpdateCloudProviders(cp) #update the session
            return True
        except Exception, ex:
            raise Exception(ex.Message)
"""