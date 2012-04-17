#!/usr/bin/env python

import web
import os
import sys
import urllib
import xml.etree.ElementTree as ET

base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
lib_path = os.path.join(base_path, "services", "lib")
sys.path.append(lib_path)

from catocommon import catocommon
from uiMethods import uiMethods
from uiMethods import logout
from uiMethods import login

from taskMethods import taskMethods
from cloudMethods import cloudMethods

import uiCommon
import uiGlobals


def notfound():
    return web.notfound("Sorry, the page you were looking for was not found.")

class bypass:        
    def GET(self):
        return "This page isn't subkect to the auth processor"

# the default page if no URI is given, just an information message
class index:        
    def GET(self):
        return render.home()

class home:        
    def GET(self):
        return render.home()

class taskManage:        
    def GET(self):
        return render.taskManage()

class taskEdit:        
    def GET(self):
        return render.taskEdit()

class cloudEdit:        
    def GET(self):
        return render.cloudEdit()

class systemStatus:        
    def GET(self):
        return render.systemStatus()

#Authentication preprocessor
def auth_app_processor(handle):
    path = web.ctx.path
    
    if path == "/bypass":
        return handle()

    if path != "/login" and not session.get('user', False):
        raise web.seeother('/login?msg=' + urllib.quote("Session expired."))
    
    return handle()

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
        '/login', 'login',
        '/logout', 'logout',
        '/home', 'home',
        '/cloudEdit', 'cloudEdit',
        '/taskEdit', 'taskEdit',
        '/taskManage', 'taskManage',
        '/systemStatus', 'systemStatus',
        '/bypass', 'bypass'
    )


    render = web.template.render('templates', base='base')
    render_plain = web.template.render('templates')
    
    app = web.application(urls, globals(), autoreload=True)
    session = web.session.Session(app, web.session.DiskStore('sessions'))
    app.add_processor(auth_app_processor)
    app.notfound = notfound
    
    uiGlobals.web = web
    uiGlobals.session = session
    uiGlobals.server = server
    
    # the debug level (0-4 with 0 being 'none' and 4 being 'verbose')    
    uiGlobals.debuglevel = 3 # change as needed for debugging
    
    # setting this to True seems to show a lot more detail in UI exceptions
    web.config.debug = False
    
    app.run()