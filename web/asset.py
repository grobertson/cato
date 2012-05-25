"""
    THIS CLASS has it's own database connections.
    Why?  Because it isn't only used by the UI.
"""
import json
from catocommon import catocommon

class Assets(object): 
    rows = {}
        
    def __init__(self, sFilter=""):
        try:
            sWhereString = ""
            if sFilter:
                aSearchTerms = sFilter.split()
                for term in aSearchTerms:
                    if term:
                        sWhereString += " and (a.asset_name like '%%" + term + "%%' " \
                            "or a.port like '%%" + term + "%%' " \
                            "or a.address like '%%" + term + "%%' " \
                            "or a.db_name like '%%" + term + "%%' " \
                            "or a.asset_status like '%%" + term + "%%' " \
                            "or ac.username like '%%" + term + "%%') "
    
            sSQL = "select a.asset_id, a.asset_name, a.asset_status, a.address," \
                " case when ac.shared_or_local = 1 then 'Local - ' else 'Shared - ' end as shared_or_local," \
                " case when ac.domain <> '' then concat(ac.domain, cast(char(92) as char), ac.username) else ac.username end as credentials" \
                " from asset a" \
                " left outer join asset_credential ac on ac.credential_id = a.credential_id" \
                " where 1=1 " + sWhereString + " order by a.asset_name"

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

class Asset(object):
    ID = ""
    Name = ""
    Status = ""
    Port = ""
    DbName = ""
    Address = ""
    UserName = ""
    SharedOrLocal = ""
    CredentialID = ""
    Password = ""
    Domain = ""
    SharedCredName = ""
    SharedCredDesc = ""
    ConnString = ""

    def FromName(self, sAssetName):
        self.PopulateAsset(asset_name=sAssetName)
        
    def FromID(self, sAssetID):
        self.PopulateAsset(asset_id=sAssetID)

    def PopulateAsset(self, asset_id="", asset_name=""):
        """
            Note the absence of password or privileged_password in this method.
            We don't store passwords, even encrypted, in the object.
        """
        try:
            if not asset_id and not asset_name:
                raise Exception("Error building Asset object: ID or Name is required.");    
            
            sSQL = """select a.asset_id, a.asset_name, a.asset_status, a.port, a.db_name, a.conn_string,
                a.address, ac.username, ac.domain,
                ac.shared_cred_desc, ac.credential_name, a.credential_id,
                case when ac.shared_or_local = '0' then 'Shared' else 'Local' end as shared_or_local
                from asset a
                left outer join asset_credential ac on ac.credential_id = a.credential_id
                """
            
            if asset_id:
                sSQL += " where a.asset_id = '%s'""" % asset_id
            elif asset_name:
                sSQL += " where a.asset_name = '%s'""" % asset_name


            db = catocommon.new_conn()
            dr = db.select_row_dict(sSQL)
            
            if dr is not None:
                self.ID = dr["asset_id"]
                self.Name = dr["asset_name"]
                self.Status = dr["asset_status"]
                self.Port = ("" if not dr["port"] else str(dr["port"]))
                self.DbName = ("" if not dr["db_name"] else dr["db_name"])
                self.Address = ("" if not dr["address"] else dr["address"])
                self.UserName = ("" if not dr["username"] else dr["username"])
                self.SharedOrLocal = ("" if not dr["shared_or_local"] else dr["shared_or_local"])
                self.CredentialID = ("" if not dr["credential_id"] else dr["credential_id"])
                self.Domain = ("" if not dr["domain"] else dr["domain"])
                self.SharedCredName = ("" if not dr["credential_name"] else dr["credential_name"])
                self.SharedCredDesc = ("" if not dr["shared_cred_desc"] else dr["shared_cred_desc"])
                self.ConnString = ("" if not dr["conn_string"] else dr["conn_string"])
            else: 
                raise Exception("Unable to build Asset object. Either no Assets are defined, or no Asset by ID/Name could be found.")
        except Exception, ex:
            raise Exception(ex)
        finally:
            db.close()        

    def AsJSON(self):
        try:
            return json.dumps(self.__dict__)
        except Exception, ex:
            raise ex    

    @staticmethod
    def HasHistory(asset_id):
        """Returns True if the asset has historical data."""
        try:
            db = catocommon.new_conn()
            #  history in user_session.
            sql = "select count(*) from tv_task_instance where asset_id = '" + asset_id + "'"
            iResults = db.select_col_noexcep(sql)
            if db.error:
                raise Exception(db.error)
    
            if iResults:
                return True
    
            return False
        except Exception, ex:
            raise ex
        finally:
            if db: db.close()

    @staticmethod
    def DBCreateNew(sAssetName, sStatus, sDbName, sPort, sAddress, sConnString, sTagArray, sCredentialMode, credential=None):
        """
        Creates a new Asset.  Requires a credential object to be sent along.  If not provided, the 
        Asset is created with no credentials.
        """
        try:
            db = catocommon.new_conn()

            sAssetID = catocommon.NewGUID()

            if credential:
                c = Credential()
                c.FromDict(credential)
            
            
            sCredentialID = (c.ID if c.ID else "")



            #  there are three CredentialType's 
            #  1) 'selected' = user selected a different credential, just save the credential_id
            #  2) 'new' = user created a new shared or local credential
            #  3) 'existing' = same credential, just update the username,description ad password
            if sCredentialMode == "new":
                # if it's a local credential, the credential_name is the asset_id.
                # if it's shared, there will be a name.
                if c.Shared == "1":
                    c.Name = sAssetID

                result, msg = c.DBCreateNew()
                if not result:
                    return None, msg
# DOESN'T HAPPEN ON AN add
#            elif sCredentialMode == "existing":
#                result, msg = c.DBUpdate()
#                if not result:
#                    return None, msg
            else:
                #  user selected a shared credential
                #  remove the local credential if one exists
                sSQL = """delete from asset_credential
                    where shared_or_local = 1
                    and credential_id in (select credential_id from asset where asset_id = '%s')""" % sAssetID
                if not db.exec_db_noexcep(sSQL):
                    return False, db.error


            sSQL = "insert into asset" \
            " (asset_id, asset_name, asset_status, address, conn_string, db_name, port, credential_id)" \
            " values (" \
            "'" + sAssetID + "'," \
            "'" + sAssetName + "'," \
            "'" + sStatus + "'," \
            "'" + sAddress + "'," \
            "'" + sConnString + "'," \
            "'" + sDbName + "'," + \
            ("NULL" if sPort == "" else "'" + sPort + "'") + "," \
            "'" + sCredentialID + "'" \
            ")"
            if not db.tran_exec_noexcep(sSQL):
                if db.error == "key_violation":
                    return None, "Asset Name '" + sAssetName + "' already in use, choose another."
                else: 
                    return None, db.error

            #region "tags"
            #  remove the existing tags
            sSQL = "delete from object_tags where object_id = '" + sAssetID + "'"
            if not db.tran_exec_noexcep(sSQL):
                raise Exception(db.error)

            
            # at some point around here we'll figure out the credentials thing
                    

            db.tran_commit()

            # if we can't create tags we don't actually fail...
            for tag in sTagArray:
                sql = "insert object_tags (object_type, object_id, tag_name) values (2, '%s','%s')" % (sAssetID, tag)
                if not db.exec_db_noexcep(sql):
                    print "Error creating Groups for new user %s." % sAssetID
            
            # now it's inserted... lets get it back from the db as a complete object for confirmation.
            a = Asset()
            a.FromID(sAssetID)
    
            return a, None

        except Exception, ex:
            raise ex


"""
CUT THIS DOWN to just be an update function
        def static SaveAsset(object[] oAsset):
            #  check the # of elements in the array
            if oAsset.__LENGTH != 19) return "Incorrect number of Asset Properties:" + oAsset.__LENGT:

            sAssetID = oAsset[0]
            sAssetName = oAsset[1].replace("'", "''")
            sDbName = oAsset[2].replace("'", "''")
            sPort = oAsset[3]
            sConnectionType = oAsset[4]
            sIsConnection = "0" #  oAsset[5]

            sAddress = oAsset[5].replace("'", "''")
            #  mode is edit or add
            sMode = oAsset[6]
            sCredentialID = oAsset[7]
            sCredUsername = oAsset[8].replace("'", "''")
            sCredPassword = oAsset[9].replace("'", "''")
            sShared = oAsset[10]
            sCredentialName = oAsset[11].replace("'", "''")
            sCredentialDescr = oAsset[12].replace("'", "''")
            sDomain = oAsset[13].replace("'", "''")
            sCredentialType = oAsset[14]

            sAssetStatus = oAsset[15]
            sPrivilegedPassword = oAsset[16]
            sTagArray = oAsset[17]

            sConnString = oAsset[18].replace("'", "''")

            #  for logging
            sOriginalAssetName = ""
            sOriginalPort = ""
            sOriginalDbName = ""
            sOriginalAddress = ""
            sOriginalConnectionType = ""
            sOriginalUserName = ""
            sOriginalConnString = ""
            sOriginalCredentialID = ""
            sOriginalAssetStatus = ""

            sSql = null
            sErr = null


            # if we are editing get the original values
            # this is getting original values for logging purposes
            if sMode == "edit":
                sSql = "select a.asset_name, a.asset_status, a.port, a.db_name, a.address, a.db_name, a.connection_type, a.conn_string, ac.username, a.credential_id," \
                    " case when a.is_connection_system = '1' then 'Yes' else 'No' end as is_connection_system " \
                    " from asset a " + 
                    " left outer join asset_credential ac on ac.credential_id = a.credential_id " \
                    " where a.asset_id = '" + sAssetID + "'"

                if !dc.sqlGetDataRow(0000BYREF_ARG0000dr, sSql, 0000BYREF_ARG0000sErr:
                    uiCommon.log(self.db.error)
                else:
                    if dr is not None:
                        sOriginalAssetName = dr["asset_name"]
                        sOriginalPort = ("" if object.ReferenceEqualsdr["port"], DBNull.Value else dr["port"])
                        sOriginalDbName = ("" if object.ReferenceEqualsdr["db_name"], DBNull.Value else dr["db_name"])
                        sOriginalAddress = ("" if object.ReferenceEqualsdr["address"], DBNull.Value else dr["address"])
                        sOriginalConnectionType = ("" if object.ReferenceEqualsdr["connection_type"], DBNull.Value else dr["connection_type"])
                        sOriginalUserName = ("" if object.ReferenceEqualsdr["username"], DBNull.Value else dr["username"])
                        sOriginalConnString = ("" if object.ReferenceEqualsdr["conn_string"], DBNull.Value else dr["conn_string"])
                        sOriginalCredentialID = ("" if object.ReferenceEqualsdr["credential_id"], DBNull.Value else dr["credential_id"])
                        sOriginalAssetStatus = dr["asset_status"]
            
            # NOTE NOTE NOTE!
            # the following is a catch 22.
            # if we're adding a new asset, we will need to figure out the credential first so we can save the credential id on the asset
            # but if it's a new local credential, it gets the asset id as it's name.
            # so.........
            # if it's a new asset, go ahead and get the new guid for it here so the credential add will work.
            if sMode == "add":
                sAssetID = uiCommon.NewGUID()
            # and move on...
            
            
            
            #  there are three CredentialType's 
            #  1) 'selected' = user selected a different credential, just save the credential_id
            #  2) 'new' = user created a new shared or local credential
            #  3) 'existing' = same credential, just update the username,description ad password
            sPriviledgedPasswordUpdate = null
            if sCredentialType == "new":
                if sPrivilegedPassword.__LENGTH == 0:
                    sPriviledgedPasswordUpdate = "NULL"
                else:
                    sPriviledgedPasswordUpdate = "'" + catocommon.cato_encrypt(sPrivilegedPassword) + "'"

                # if it's a local credential, the credential_name is the asset_id.
                # if it's shared, there will be a name.
                if sShared == "1":
                    sCredentialName = sAssetID
                    
                    # whack and add - easiest way to avoid conflicts
                    sSql = "delete from asset_credential where credential_name = '" + sCredentialName + "' and shared_or_local = '1'"
                    if !dc.sqlExecuteUpdate(sSql, 0000BYREF_ARG0000sErr:
                        uiCommon.log(self.db.error)
                
                # now we're clear to add
                sCredentialID = "'" + uiCommon.NewGUID() + "'"
                sSql = "insert into asset_credential " \
                    "(credential_id,credential_name,username,password,domain,shared_or_local,shared_cred_desc,privileged_password) " \
                        "values (" + sCredentialID + ",'" + sCredentialName + "','" + sCredUsername + "','" + catocommon.cato_encrypt(sCredPassword) + "','" + sDomain + "','" + sShared + "','" + sCredentialDescr + "'," + sPriviledgedPasswordUpdate + ")"
                if !dc.sqlExecuteUpdate(sSql, 0000BYREF_ARG0000sErr:
                    if sErr == "key_violation":
                        uiCommon.log("A Credential with that name already exists.  Please select another name.")
                    else: 
                        uiCommon.log(self.db.error)
                
                #  add security log
                uiCommon.WriteObjectAddLog(uiGlobals.CatoObjectTypes.Credential, sCredentialID, sCredentialName, "")
                

            elif sCredentialType == "existing":
                sCredentialID = "'" + sCredentialID + "'"
                #  bugzilla 1126 if the password has not changed leave it as is.
                sPasswordUpdate = null
                if sCredPassword == "($%#d@x!&":
                    #  password has not been touched
                    sPasswordUpdate = ""
                else:
                    #  updated password
                    sPasswordUpdate = ",password = '" + catocommon.cato_encrypt(sCredPassword) + "'"

                #  bugzilla 1260
                #  same for privileged_password

                if sPrivilegedPassword == "($%#d@x!&":
                    #  password has not been touched
                    sPriviledgedPasswordUpdate = ""
                else:
                    #  updated password
                    #  bugzilla 1352 priviledged password can be blank, so if it is, set it to null
                    if sPrivilegedPassword.__LENGTH == 0:
                        sPriviledgedPasswordUpdate = ",privileged_password = null"
                    else:
                        sPriviledgedPasswordUpdate = ",privileged_password = '" + catocommon.cato_encrypt(sPrivilegedPassword) + "'"

                sSql = "update asset_credential " \
                        "set username = '" + sCredUsername + "'" + sPasswordUpdate + sPriviledgedPasswordUpdate + ",domain = '" + sDomain + "'," \
                        "shared_or_local = '" + sShared + "',shared_cred_desc = '" + sCredentialDescr + "'" \
                        "where credential_id = " + sCredentialID
                if !dc.sqlExecuteUpdate(sSql, 0000BYREF_ARG0000sErr:
                    uiCommon.log(self.db.error)

                #  add security log
                uiCommon.WriteObjectPropertyChangeLog(uiGlobals.CatoObjectTypes.Asset, sAssetID, sAssetName.strip().replace("'", "''") + "Changed credential", sOriginalUserName, sCredUsername)

            else:
                #  user selected a shared credential
                #  remove the local credential if one exists

                if sOriginalCredentialID.__LENGTH > 0:
                    sSql = "delete from asset_credential where credential_id = '" + sOriginalCredentialID + "' and shared_or_local = '1'"
                    if !dc.sqlExecuteUpdate(sSql, 0000BYREF_ARG0000sErr:
                        uiCommon.log(self.db.error)

                    #  add security log
                    uiCommon.WriteObjectDeleteLog(uiGlobals.CatoObjectTypes.Asset, sAssetID, sAssetName.strip().replace("'", "''"), "Credential deleted" + sOriginalCredentialID + " " + sOriginalUserName)


                sCredentialID = "'" + sCredentialID + "'"



            #  checks that cant be done on the client side
            #  is the name unique?
            sInuse = ""

            if sMode == "edit":
                sSql = "select asset_id from asset where asset_name = '" + sAssetName.strip() + "' and asset_id <> '" + sAssetID + "' limit 1"
            else:
                sSql = "select asset_id from asset where asset_name = '" + sAssetName.strip() + "' limit 1"

            00000 = self.db.select_col_noexcep(sSQL)
            if self.db.error:
                uiCommon.log(self.db.error)
            else:
                if sInuse:
                    return "Asset Name '" + sAssetName + "' already in use, choose another." + sAssetID

            try:

                if sMode == "edit":
                    sSql = "update asset set asset_name = '" + sAssetName + "'," \
                        " asset_status = '" + sAssetStatus + "'," \
                        " address = '" + sAddress + "'" + "," \
                        " conn_string = '" + sConnString + "'" + "," \
                        " db_name = '" + sDbName + "'," \
                        " port = " + ("NULL" if sPort == "" else "'" + sPort + "'") + "," \
                        " connection_type = '" + sConnectionType + "'," \
                        " is_connection_system = '" + (1 if sIsConnection == "Yes" else 0) + "'," \
                        " credential_id = " + sCredentialID \
                        " where asset_id = '" + sAssetID + "'"

                    sSQL = sSql
                    if not self.db.tran_exec_noexcep(sSQL):
                        uiCommon.log(self.db.error)

                else:
                    sSql = "insert into asset (asset_id,asset_name,asset_status,address,conn_string,db_name,port,connection_type,is_connection_system,credential_id)" \
                    " values (" \
                    "'" + sAssetID + "'," \
                    "'" + sAssetName + "'," \
                    "'" + sAssetStatus + "'," \
                    "'" + sAddress + "'," \
                    "'" + sConnString + "'," \
                    "'" + sDbName + "'," \
                    ("NULL" if sPort == "" else "'" + sPort + "'") + "," \
                    "'" + sConnectionType + "'," \
                    "'0'," \
                    sCredentialID + ")"

                    sSQL = sSql
                    if not self.db.tran_exec_noexcep(sSQL):
                        uiCommon.log(self.db.error)

                #region "tags"
                #  remove the existing tags
                sSql = "delete from object_tags where object_id = '" + sAssetID + "'"
                sSQL = sSql
                if not self.db.tran_exec_noexcep(sSQL):
                    uiCommon.log(self.db.error)

                #  add user groups, if there are any
                if sTagArray.__LENGTH > 0:
                    ArrayList aTags = new ArrayList(sTagArray.split(','))
### CHECK NEXT LINE for type declarations !!!
                    for sTagName in aTags:
                        sSql = "insert object_tags (object_id, object_type, tag_name)" \
                            " values ('" + sAssetID + "', 2, '" + sTagName + "')"
                        sSQL = sSql
                        if not self.db.tran_exec_noexcep(sSQL):
                            uiCommon.log(self.db.error)
                #endregion

                self.db.tran_commit()

            except Exception:

                uiCommon.log(traceback.format_exc())


"""

class Credentials(object): 
    rows = {}
        
    def __init__(self, sFilter=""):
        try:
            sWhereString = ""
            if sFilter:
                aSearchTerms = sFilter.split()
                for term in aSearchTerms:
                    if term:
                        sWhereString += " and (credential_name like '%%" + term + "%%' " \
                            "or username like '%%" + term + "%%' " \
                            "or domain like '%%" + term + "%%' " \
                            "or shared_cred_desc like '%%" + term + "%%') "
    
            sSQL = "select credential_id, credential_name, username, domain, shared_cred_desc" \
                " from asset_credential" \
                " where shared_or_local = 0 " + sWhereString + " order by credential_name"

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

class Credential(object):
    ID = None
    Username = None
    Password = None
    Shared = None
    Name = None
    Description = None
    Domain = None
    PrivilegedPassword = None
    
    def __init__(self):
        self.ID = catocommon.NewGUID()
        
    def FromArgs(self, sID, sName, sDesc, sUsername, sPassword, sShared, sDomain, sPrivPassword):
        self.ID = sID
        self.Name = sName
        self.Description = sDesc
        self.Username = sUsername
        self.Password = sPassword
        self.Shared = sShared
        self.Domain = sDomain
        self.PrivilegedPassword = sPrivPassword

        # if created by args, it may or may not have an ID.
        # but it needs one.
        if not self.ID:
            self.ID = catocommon.NewGUID()

    def FromDict(self, cred):
        try:
            for k, v in cred.items():
                setattr(self, k, v)
                
            # if created by args, it may or may not have an ID.
            # but it needs one.
            if not self.ID:
                self.ID = catocommon.NewGUID()
        except Exception, ex:
            raise ex

    def DBCreateNew(self):
        try:
            db = catocommon.new_conn()

            sPriviledgedPasswordUpdate = ""
            if self.PrivilegedPassword:
                sPriviledgedPasswordUpdate = "NULL"
            else:
                sPriviledgedPasswordUpdate = "'" + catocommon.cato_encrypt(self.PrivilegedPassword) + "'"

            # if it's a local credential, the credential_name is the asset_id.
            # if it's shared, there will be a name.
            if self.Shared == "1":
                # whack and add - easiest way to avoid conflicts
                sSQL = "delete from asset_credential where credential_name = '%s' and shared_or_local = '1'" % self.Name
                if not db.exec_db_noexcep(sSQL):
                    return False, db.error
            
            sSQL = "insert into asset_credential " \
                "(credential_id, credential_name, username, password, domain, shared_or_local, shared_cred_desc, privileged_password) " \
                "values ('" + self.ID + "','" + self.Name + "','" + self.Username + "','" + catocommon.cato_encrypt(self.Password) + "','" \
                + self.Domain + "','" + self.Shared + "','" + self.Description + "'," + sPriviledgedPasswordUpdate + ")"
            if not db.exec_db_noexcep(sSQL):
                if db.error == "key_violation":
                    return False, "A Credential with that name already exists.  Please select another name."
                else: 
                    return False, db.error
            
            #  add security log
            # need to move this function to catocommon
            # uiCommon.WriteObjectAddLog(uiGlobals.CatoObjectTypes.Credential, sCredentialID, sCredentialName, "")
            return True, None
        except Exception, ex:
            raise ex
        finally:
            db.close()
                

    def DBDelete(self):
        try:
            db = catocommon.new_conn()

            sSQL = "delete from asset_credential where credential_id = '%s'" % self.ID
            if not db.exec_db_noexcep(sSQL):
                return False, db.error

            #  add security log
            #uiCommon.WriteObjectDeleteLog(uiGlobals.CatoObjectTypes.Asset, sAssetID, sAssetName.strip().replace("'", "''"), "Credential deleted" + sOriginalCredentialID + " " + sOriginalUserName)

            return True, None
        except Exception, ex:
            raise ex
        finally:
            db.close()
                
    def DBUpdate(self):
        try:
            db = catocommon.new_conn()

            # if the password has not changed leave it as is.
            sPasswordUpdate = ""
            if self.Password and self.Password != "~!@@!~":
                sPasswordUpdate = ", password = '" + catocommon.cato_encrypt(self.Password) + "'"

            #  same for privileged_password
            sPriviledgedPasswordUpdate = ""
            if self.PrivilegedPassword != "~!@@!~":
                #  updated password
                #  priviledged password can be blank, so if it is, set it to null
                if self.PrivilegedPassword:
                    sPriviledgedPasswordUpdate = ", privileged_password = null"
                else:
                    sPriviledgedPasswordUpdate = ", privileged_password = '" + catocommon.cato_encrypt(self.PrivilegedPassword) + "'"

            sSQL = "update asset_credential " \
                "set username = '" + self.Username + "'," \
                "domain = '" + self.Domain + "'," \
                "shared_or_local = '" + self.Shared + "'," \
                "shared_cred_desc = '" + self.Description + "'" \
                + sPasswordUpdate + sPriviledgedPasswordUpdate + \
                "where credential_id = '" + self.ID + "'"
            if not db.exec_db_noexcep(sSQL):
                return False, db.error

#                #  add security log
#                uiCommon.WriteObjectPropertyChangeLog(uiGlobals.CatoObjectTypes.Asset, sAssetID, sAssetName.strip().replace("'", "''") + "Changed credential", sOriginalUserName, sCredUsername)

            return True, None
        except Exception, ex:
            raise ex
        finally:
            db.close()

