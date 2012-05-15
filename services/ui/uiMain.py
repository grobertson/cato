#!/usr/bin/env python

import web
import os
import sys
import urllib
import pickle
import xml.etree.ElementTree as ET

base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
lib_path = os.path.join(base_path, "services", "lib")
sys.path.append(lib_path)
conf_path = os.path.join(base_path, "conf")
sys.path.append(conf_path)

# DON'T REMOVE these that Aptana shows as "unused".
# they are used, just in the URL mapping for web.py down below.
from catocommon import catocommon
from uiMethods import uiMethods
from uiMethods import logout
from uiMethods import login

from taskMethods import taskMethods
from cloudMethods import cloudMethods
from ecoMethods import ecoMethods

import uiCommon
import uiGlobals


def notfound():
    return web.notfound("Sorry, the page you were looking for was not found.")

class bypass:        
    def GET(self):
        return "This page isn't subject to the auth processor"

# the login announcement hits the Cloud Sidekick web site for a news snip
class announcement:        
    def GET(self):
        s = uiCommon.HTTPGetNoFail("http://community.cloudsidekick.com/login-page-announcement?utm_source=cato_app&utm_medium=loginpage&utm_campaign=app")
        if s:
            return s
        else:
            return ""


# the default page if no URI is given, just an information message
class index:        
    def GET(self):
        return render.home()

class home:        
    def GET(self):
        return render.home()

class settings:        
    def GET(self):
        return render.settings()

class taskManage:        
    def GET(self):
        return render.taskManage()

class taskEdit:        
    def GET(self):
        return render.taskEdit()

class taskRunLog:        
    def GET(self):
        return render_popup.taskRunLog()

class taskActivityLog:        
    def GET(self):
        return render.taskActivityLog()

class cloudAccountEdit:        
    def GET(self):
        return render.cloudAccountEdit()

class cloudEdit:        
    def GET(self):
        return render.cloudEdit()

class systemStatus:        
    def GET(self):
        return render.systemStatus()

class taskStatus:        
    def GET(self):
        return render.taskStatus()

#Authentication preprocessor

class ecoTemplateManage:        
    def GET(self):
        return render.ecoTemplateManage()

class ecoTemplateEdit:        
    def GET(self):
        return render.ecoTemplateEdit()

class ecosystemManage:        
    def GET(self):
        return render.ecosystemManage()

class ecosystemEdit:        
    def GET(self):
        return render.ecosystemEdit()

class upload:
    def GET(self):
        return """This endpoint only accepts POSTS from file_upload.html"""
    def POST(self):
        x = web.input(fupFile={}, ref_id="")
        if x:
            #print x # ref_id
            #web.debug(x['fupFile'].filename) # This is the filename
            #web.debug(x['fupFile'].value) # This is the file contents
            #web.debug(x['fupFile'].file.read()) # Or use a file(-like) object
            # raise web.seeother('/upload')
            
            ref_id = (x.ref_id if x.ref_id else "")
            filename = "temp/%s-%s.tmp" % (uiCommon.GetSessionUserID(), ref_id)
            fout = open(filename,'w') # creates the file where the uploaded file should be stored
            fout.write(x["fupFile"].file.read()) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.
            
            # all done, we loop back to the file_upload.html page, but this time include
            # a qq arg - the file name
            raise web.seeother("static/pages/file_upload.html?ref_id=%s&filename=%s" % (ref_id, filename))

class temp:
    """all we do for temp is deliver the file."""
    def GET(self, filename):
        try:
            f = open("temp/%s" % filename)
            if f:
                return f.read()
        except Exception, ex:
            return ex.__str__()
    
def auth_app_processor(handle):
    path = web.ctx.path
    
    if path == "/bypass":
        return handle()

    if path == "/announcement":
        return handle()

    if path != "/login" and not session.get('user', False):
        raise web.seeother('/login?msg=' + urllib.quote_plus("Session expired."))
    
    return handle()


def SetTaskCommands():
    try:
        from taskCommands import FunctionCategories
        #we load two classes here...
        #first, the category/function hierarchy
        cats = FunctionCategories()
        bCoreSuccess = cats.Load("task_commands.xml")
        if not bCoreSuccess:
            raise Exception("Critical: Unable to read/parse task_commands.xml.")

        #try to append any extension files
        #this will read all the xml files in /extensions
        #and append to sErr if it failed, but not crash or die.
        for root, subdirs, files in os.walk("extensions"):
            for f in files:
                ext = os.path.splitext(f)[-1]
                if ext == ".xml":
                    fullpath = os.path.join(root, f)
                    if not cats.Append(fullpath):
                        uiCommon.log("WARNING: Unable to load extension command xml file [" + fullpath + "].", 0)

        #put the categories list in the session...
        #uiGlobals.session.function_categories = cats.Categories
        #then the dict of all functions for fastest lookups
        #uiGlobals.session.functions = cats.Functions

        # was told not to put big objects in the session, so since this can actually be shared by all users,
        # lets try saving a pickle
        # it will get created every time a user logs in, but can be read by all.
        f = open("datacache/_categories.pickle", 'wb')
        pickle.dump(cats, f, pickle.HIGHEST_PROTOCOL)
        f.close()
        
        #rebuild the cache html files
        CacheTaskCommands()

        return True
    except Exception, ex:
        uiCommon.log("Unable to load Task Commands XML." + ex.__str__(), 0)

def CacheTaskCommands():
    #creates the html cache file
    try:
        sCatHTML = ""
        sFunHTML = ""

        # so, we will use the FunctionCategories class in the session that was loaded at login, and build the list items for the commands tab.
        cats = uiCommon.GetTaskFunctionCategories()
        if not cats:
            print "Error: Task Function Categories class is not in the datacache."
        else:
            for cat in cats:
                sCatHTML += "<li class=\"ui-widget-content ui-corner-all command_item category\""
                sCatHTML += " id=\"cat_" + cat.Name + "\""
                sCatHTML += " name=\"" + cat.Name + "\">"
                sCatHTML += "<div>"
                sCatHTML += "<img class=\"category_icon\" src=\"" + cat.Icon + "\" alt=\"\" />"
                sCatHTML += "<span>" + cat.Label + "</span>"
                sCatHTML += "</div>"
                sCatHTML += "<div id=\"help_text_" + cat.Name + "\" class=\"hidden\">"
                sCatHTML += cat.Description
                sCatHTML += "</div>"
                sCatHTML += "</li>"
                
                sFunHTML += "<div class=\"functions hidden\" id=\"cat_" + cat.Name + "_functions\">"
                # now, let's work out the functions.
                # we can just draw them all... they are hidden and will display on the client as clicked
                for fn in cat.Functions:
                    sFunHTML += "<div class=\"ui-widget-content ui-corner-all command_item function\""
                    sFunHTML += " id=\"fn_" + fn.Name + "\""
                    sFunHTML += " name=\"" + fn.Name + "\">"
                    sFunHTML += "<img class=\"function_icon\" src=\"" + fn.Icon + "\" alt=\"\" />"
                    sFunHTML += "<span>" + fn.Label + "</span>"
                    sFunHTML += "<div id=\"help_text_" + fn.Name + "\" class=\"hidden\">"
                    sFunHTML += fn.Description
                    sFunHTML += "</div>"
                    sFunHTML += "</div>"

                sFunHTML += "</div>"

        with open("static/_categories.html", 'w') as f_out:
            if not f_out:
                print "ERROR: unable to create static/_categories.html."
            f_out.write(sCatHTML)

        with open("static/_functions.html", 'w') as f_out:
            if not f_out:
                print "ERROR: unable to create static/_functions.html."
            f_out.write(sFunHTML)

    except Exception, ex:
        uiCommon.log(ex.__str__(), 0)

def CacheMenu():
    #put the site.master.xml in the session here
    # this is a significant boost to performance
    xRoot = ET.parse("site.master.xml")
    if not xRoot:
        raise Exception("Critical: Unable to read/parse site.master.xml.")
        
    xMenus = xRoot.findall("mainmenu/menu") 

    sHTML = ""
    for xMenu in xMenus:
        sLabel = xMenu.get("label", "No Label Defined")
        sHref = (" href=\"" + xMenu.get("href", "") + "\"" if xMenu.get("href") else "")
        sOnClick = (" onclick=\"" + xMenu.get("onclick", "") + "\"" if xMenu.get("onclick") else "")
        sIcon = ("<img src=\"" + xMenu.get("icon", "") + "\" alt=\"\" />" if xMenu.get("icon") else "")
        sTarget = xMenu.get("target", "")
        sClass = xMenu.get("class", "")
        
        sHTML += "<li class=\"" + sClass + "\" style=\"cursor: pointer;\">"
        sHTML += "<a"
        sHTML += sOnClick
        sHTML += sHref
        sHTML += sTarget
        sHTML += ">"
        sHTML += sIcon
        sHTML += sLabel
        sHTML += "</a>"
        
        xItems = xMenu.findall("item")
        if str(len(xItems)) > 0:
            sHTML += "<ul>"
            for xItem in xItems:
                sLabel = xItem.get("label", "No Label Defined")
                sHref = (" href=\"" + xItem.get("href", "") + "\"" if xItem.get("href") else "")
                sOnClick = (" onclick=\"" + xItem.get("onclick", "") + "\"" if xItem.get("onclick") else "")
                sIcon = ("<img src=\"" + xItem.get("icon", "") + "\" alt=\"\" />" if xItem.get("icon") else "")
                sTarget = xItem.get("target", "")
                sClass = xItem.get("class", "")

                sHTML += "<li class=\"ui-widget-header " + sClass + "\" style=\"cursor: pointer;\">"
                sHTML += "<a"
                sHTML += sOnClick 
                sHTML += sHref 
                sHTML += sTarget 
                sHTML += ">"
                sHTML += sIcon
                sHTML += sLabel
                sHTML += "</a>"
                sHTML += "</li>"
            sHTML += "</ul>"
            
        #wrap up the outer menu
        sHTML += "</li>"
    
    with open("static/_menu.html", 'w') as f_out:
        if not f_out:
            print "ERROR: unable to create static/_menu.html."
        f_out.write(sHTML)


"""
    Main Startup
"""



if __name__ == "__main__":
    #this is a service, which has a db connection.
    # but we're not gonna use that for gui calls - we'll make our own when needed.
    server = catocommon.CatoService("web_api")
    server.startup()

    if len(sys.argv) < 2:
        config = catocommon.read_config()
        if "web_port" in config:
            port=config["web_port"]
            sys.argv.append(port)

    urls = (
        '/', 'index',
        '/uiMethods/(.*)', 'uiMethods',
        '/cloudMethods/(.*)', 'cloudMethods',
        '/taskMethods/(.*)', 'taskMethods',
        '/ecoMethods/(.*)', 'ecoMethods',
        '/login', 'login',
        '/logout', 'logout',
        '/home', 'home',
        '/cloudEdit', 'cloudEdit',
        '/cloudAccountEdit', 'cloudAccountEdit',
        '/taskEdit', 'taskEdit',
        '/taskRunLog', 'taskRunLog',
        '/taskActivityLog', 'taskActivityLog',
        '/taskManage', 'taskManage',
        '/systemStatus', 'systemStatus',
        '/taskStatus', 'taskStatus',
        '/ecoTemplateEdit', 'ecoTemplateEdit',
        '/ecoTemplateManage', 'ecoTemplateManage',
        '/ecosystemManage', 'ecosystemManage',
        '/ecosystemEdit', 'ecosystemEdit',
        '/announcement', 'announcement',
        '/upload', 'upload',
        '/settings', 'settings',
        '/temp/(.*)', 'temp',
        '/bypass', 'bypass'
    )


    render = web.template.render('templates', base='base')
    render_popup = web.template.render('templates', base='popup')
    render_plain = web.template.render('templates')
    
    app = web.application(urls, globals(), autoreload=True)
    session = web.session.Session(app, web.session.DiskStore('sessions'))
    app.add_processor(auth_app_processor)
    app.notfound = notfound
    
    uiGlobals.web = web
    uiGlobals.session = session
    uiGlobals.server = server
    
    # the debug level (0-4 with 0 being 'none' and 4 being 'verbose')    
    uiGlobals.debuglevel = 4 # change as needed for debugging
    
    # setting this to True seems to show a lot more detail in UI exceptions
    web.config.debug = False
    
    # we need to build some static html here...
    # caching in the session is a bad idea, and this stuff very very rarely changes.
    # so, when the service is started it will update the files, and the ui 
    # will simply pull in the files when requested.
    
    # put the task commands in a pickle for our lookups
    # and cache the html in a flat file
    uiCommon.log("Generating static html...", 3)
    SetTaskCommands()
    CacheMenu()
        
    
    app.run()
