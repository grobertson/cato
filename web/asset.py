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
