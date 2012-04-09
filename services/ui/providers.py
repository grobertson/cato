import xml.etree.ElementTree as ET
import cloud
from catocommon import catocommon

class CloudProviders(object):
    Providers = {}
    #CloudProviders is a dictionary of Provider objects
    #the constructor requires an ET Document
    def __init__(self, xRoot):
        try:
            if not xRoot:
                raise Exception("Error: Invalid or missing Cloud Providers XML.")
            else:
                xProviders = xRoot.findall("providers/provider")
                for xProvider in xProviders:
                    p_name = xProvider.get("name", None)

                    if p_name == None:
                        raise Exception("Cloud Providers XML: All Providers must have the 'name' attribute.")
                    
                    test_product = xProvider.get("test_product", None)
                    test_object = xProvider.get("test_object", None)
                    user_defined_clouds = xProvider.get("user_defined_clouds", True)
                    user_defined_clouds = (False if user_defined_clouds == "false" else True)
                     
                    pv = Provider(p_name, test_product, test_object, user_defined_clouds)
                    xClouds = xProvider.findall("clouds/cloud")
                    #if this provider has hardcoded clouds... get them
                    for xCloud in xClouds:
                        if xCloud.get("id", None) == None:
                            raise Exception("Cloud Providers XML: All Clouds must have the 'id' attribute.")
                        if xCloud.get("name", None) == None:
                            raise Exception("Cloud Providers XML: All Clouds must have the 'name' attribute.")
                        if xCloud.get("api_url", None) == None:
                            raise Exception("Cloud Providers XML: All Clouds must have the 'api_url' attribute.")
                        if xCloud.get("api_protocol", None) == None:
                            raise Exception("Cloud Providers XML: All Clouds must have the 'api_protocol' attribute.")
                        #region is an optional attribute
                        sRegion = xCloud.get("region", "")
                            
                        #print ET.tostring(xCloud)
                        c = cloud.Cloud()
                        c.FromArgs(pv, False, xCloud.get("id", None), xCloud.get("name", None), xCloud.get("api_url", None), xCloud.get("api_protocol", None), sRegion)
                        if c.ID:
                            pv.Clouds[c.ID] = c

                    #Let's also add any clouds that may be in the database...
                    #IF the "user_defined_clouds" flag is set.
                    if pv.UserDefinedClouds:
                        sSQL = "select cloud_id, cloud_name, api_url, api_protocol from clouds where provider = '" + pv.Name + "' order by cloud_name"
                        db = catocommon.new_conn()
                        dt = db.select_all(sSQL)
                        db.close()
                        if dt:
                            for dr in dt:
                                c = cloud.Cloud()
                                c.FromArgs(pv, True, dr[0], dr[1], dr[2], dr[3], "")
                                if c:
                                    pv.Clouds[c.ID] = c
                        else:
                            raise Exception("Error building Cloud object: ")
                
                    #get the cloudobjecttypes for this provider.                    
                    xProducts = xProvider.findall("products/product")
                    for xProduct in xProducts:
                        p_name = xProduct.get("name", None)

                        if p_name == None:
                            raise Exception("Cloud Providers XML: All Products must have the 'name' attribute.")
    
                        p = Product(pv)
                        p.Name = xProduct.get("name", None)
                        #use the name for the label if it doesn't exist.
                        p.Label = xProduct.get("label", p_name)
                        p.APIUrlPrefix = xProduct.get("api_url_prefix", None)
                        p.APIUri = xProduct.get("api_uri", None)
                        p.APIVersion = xProduct.get("api_version", None)
                        
                        #the product contains object type definitions
                        xTypes = xProduct.findall("object_types/type")
                        for xType in xTypes:
                            if xType.get("id", None) == None:
                                raise Exception("Cloud Providers XML: All Object Types must have the 'id' attribute.")
                            if xType.get("label", None) == None:
                                raise Exception("Cloud Providers XML: All Object Types must have the 'label' attribute.")

                            cot = CloudObjectType(p)
                            cot.ID = xType.get("id")
                            cot.Label = xType.get("label")
                            cot.APICall = xType.get("api_call", None)
                            cot.APIRequestGroupFilter = xType.get("request_group_filter", None)
                            cot.APIRequestRecordFilter = xType.get("request_record_filter", None)
                            cot.XMLRecordXPath = xType.get("xml_record_xpath", None)
                            
                            #the type contains property definitions
                            xProperties = xType.findall("property")
                            for xProperty in xProperties:
                                # name="ImageId" label="" xpath="imageId" id_field="1" has_icon="0" short_list="1" sort_order="1"
                                if xProperty.get("name", None) == None:
                                    raise Exception("Cloud Providers XML: All Object Type Properties must have the 'name' attribute.")
                                
                                cotp = CloudObjectTypeProperty(cot)
                                cotp.Name = xProperty.get("name")
                                cotp.XPath = xProperty.get("xpath", None)
                                cotp.Label = xProperty.get("label", None)
                                cotp.SortOrder = xProperty.get("sort_order", None)
                                cotp.IsID = (True if xProperty.get("id_field", False) == "1" else False)
                                cotp.HasIcon = (True if xProperty.get("has_icon") == "1" else False)
                                cotp.ShortList = (True if xProperty.get("short_list") == "1" else False)
                                cotp.ValueIsXML = (True if xProperty.get("value_is_xml") == "1" else False)
                                
                                cot.Properties.append(cotp)
                            p.CloudObjectTypes[cot.ID] = cot
                        pv.Products[p.Name] = p
                    self.Providers[pv.Name] = pv

        except Exception, ex:
            raise ex

class Provider(object):
    Name = None
    TestProduct = None
    TestObject = None
    UserDefinedClouds = None
    Clouds = {}
    Products = {}
    
    def __init__(self, sName, sTestProduct, sTestObject, bUserDefinedClouds):
        self.Name = sName
        self.TestProduct = sTestProduct
        self.TestObject = sTestObject
        self.UserDefinedClouds = bUserDefinedClouds

    #get it by ID from the session
    def GetFromSession(self, sProvider):
        try:
            #get the provider record from the CloudProviders object in the session
            cp = uiCommon.GetCloudProviders()
            if cp == None:
                raise Exception("Error building Provider object: Unable to GetCloudProviders.")
            if cp.ContainsKey(sProvider):
                return cp[sProvider]
            else:
                raise Exception("Provider [" + sProvider + "] does not exist in the cloud_providers.xml file.")
        except Exception, ex:
            raise ex
            

        def GetObjectTypeByName(self, sObjectType):
            for p in self.Products:
                try:
                    cot = p.CloudObjectTypes[sObjectType]
                    if cot:
                        return cot
                except Exception, ex:
                    """"""
                    #don't crash while it's iterating, it may find it in the next object.
                    #don't worry, we'll return null if it doesn't find anything.
                        
            return None
    
    
class Product(object):
    ParentProvider = None
    Name = None
    Label = None
    APIUrlPrefix = None
    APIUri = None
    APIVersion = None
    #Product CONTAINS a named dictionary of CloudObjectTypes;
    CloudObjectTypes = {}
    
    #constructor
    def __init__(self, parent):
        self.ParentProvider = parent

    def IsValidForCalls(self):
        if self.Name:
            return True
        return False
    
class CloudObjectType(object):
    ParentProduct = None
    ID = None
    Label = None
    APICall = None
    APIRequestGroupFilter = None
    APIRequestRecordFilter = None
    XMLRecordXPath = None
    Properties = [] #!!! This is a list, not a dictionary

    #constructor
    def __init__(self, parent):
        self.ParentProduct = parent

    def IsValidForCalls(self):
        if self.XMLRecordXPath and self.ID:
            return True
        return False
    
class CloudObjectTypeProperty:
    ParentObjectType = None
    Name = None
    Label = None
    XPath = None
    SortOrder = None
    HasIcon = None
    IsID = None
    ShortList = None
    ValueIsXML = None
    
    #constructor
    def __init__(self, parent):
        self.ParentObjectType = parent
