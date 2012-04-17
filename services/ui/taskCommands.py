import xml.etree.ElementTree as ET
from uiCommon import log

# FunctionCategories contains a list of all Category objects, 
# as well as a dictionary of function objects.
# it's useful for spinning categories and functions hierarchically, as when building the command toolbox
class FunctionCategories(object):
    Categories = [] # all the categories - NOTE that categories contain a list of their own functions
    Functions = {} # a dictionary of ALL FUNCTIONS - for when you need to look up a function directly by name without recursing categories
    
    #method to load from the disk
    def Load(self, sFileName):
        try:
            xRoot = ET.parse(sFileName)
            if xRoot == None:
                #crash... we can't do anything if the XML is busted
                return False
            else:
                xCategories = xRoot.findall(".//category")
                for xCategory in xCategories:
                    cat = self.BuildCategory(xCategory)
                    if cat != None:
                        self.Categories.append(cat)
                        
                return True
        except Exception, ex:
            raise ex

    # append extension files to the class
    def Append(self, sFileName):
        try:
            log("Parsing extension file " + sFileName, 4)
            xRoot = ET.parse(sFileName)
            if xRoot == None:
                #crash... we can't do anything if the XML is busted
                return False
            else:
                xCategories = xRoot.findall(".//category")
                for xCategory in xCategories:
                    cat = self.BuildCategory(xCategory)
                    if cat != None:
                        log("Parsing extension category = " + cat.Name, 4)
                        self.Categories.append(cat)
                        
                return True
        except Exception, ex:
            # appending does not throw an exception, just a warning in the log
            log("WARNING: Error parsing extension command file [" + sFileName + "]. " + ex.__str__(), 0)

    def BuildCategory(self, xCategory):
        #not crashing... just skipping
        if not xCategory.get("name", None):
            return None
        
        #ok, minimal data is intact... proceed...
        cat = Category()
        cat.Name =  xCategory.get("name")
        cat.Label = xCategory.get("label", cat.Name)
        cat.Description = xCategory.get("description", "")
        cat.Icon = xCategory.get("icon", "")

        # load up this category with it's functions
        for xFunction in xCategory.findall("commands/command"):
            #not crashing... just skipping
            if not xCategory.get("name", None):
                return None

            # ok, minimal data is intact... proceed...
            fn = Function(cat)
            fn.Name = xFunction.get("name")
            fn.Label = xFunction.get("label", fn.Name)
            fn.Description = xFunction.get("description", "")
            fn.Help = xFunction.get("help", "")
            fn.Icon = xFunction.get("icon", "")
            
            func = xFunction.find("function")
            if func is not None:
                fn.TemplateXML = ET.tostring(func)
                fn.TemplateXDoc = func

            cat.Functions.append(fn)
            
            # while we're here, it's a good place to append this funcion to the 
            # complete dict on this class
            self.Functions[fn.Name] = fn

        return cat


class Category(object):
    def __init__(self):
        self.Name = None
        self.Label = None
        self.Description = None
        self.Icon = None
        # Category CONTAINS a list of Function objects
        self.Functions = []

class Function(object):
    def __init__(self, cat):
        self.Name = None
        self.Label = None
        self.Description = None
        self.Help = None
        self.Icon = None
        self.Category = cat #Function has a parent Category
        self.TemplateXML = None
        self.TemplateXDoc = None
