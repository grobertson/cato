import xml.etree.ElementTree as ET

# FunctionCategories IS a named dictionary of task command Category objects
# it's useful for spinning categories and functions hierarchically, as when building the command toolbox
class FunctionCategories(object):
    Categories = {}
    
    #method to load from the disk
    def Load(self, sFileName):
        try:
            xRoot = ET.parse(sFileName)
            if xRoot == None:
                #crash... we can't do anything if the XML is busted
                return False
            else:
                xCategories = xRoot.findall(".//category")
                print "Number of xCategories: " + str(len(xCategories))
                for xCategory in xCategories:
                    print "inxcat"
                    cat = self.BuildCategory(xCategory)
                    if cat != None:
                        print "in fc load - " + cat.Name
                        self.Categories[cat.Name] = cat
                        
                return True
        except Exception, ex:
            raise ex

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
            
            if xFunction.find("function"):
                func = xFunction.find("function")
                if func:
                    fn.TemplateXML = ET.tostring(func)
                    fn.TemplateXDoc = func

            cat.Functions[fn.Name] = fn
            print "in build cat - " + fn.Name

        return cat


class Category(object):
    def __init__(self):
        self.Name = None
        self.Label = None
        self.Description = None
        self.Icon = None
        # Category CONTAINS a dictionary of Function objects
        self.Functions = Functions()

#Functions is a class that derives from dict.
# it's just a dict of functions
class Functions(dict):
    def __init__(self):
        """Nothing here"""
    
    @staticmethod
    def WithCategories(fc):
        f = Functions()
        
        try:
            if not fc:
                #crash... we can't do anything if the XML is busted
                raise Exception ("Error: (Functions Class) Invalid or missing FunctionCategories Class.")
            else:
                for c_name, cat in fc.Categories.iteritems():
                    print c_name
                    for fn_name, fn in cat.Functions.iteritems():
                        print fn_name
                        f[fn.Name] = fn
        except Exception, ex:
            raise ex

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
