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
from catocryptpy import catocryptpy
from catodb import catodb
from uiMethods import uiMethods

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

class login:
    def GET(self):
        qs = ""
        i = web.input(msg=None)
        if i.msg:
            qs = "?msg=" + urllib.quote(i.msg)
        raise web.seeother('/static/login.html' + qs)

    def POST(self):
        in_name = web.input(username=None).username
        in_pwd = web.input(password=None).password
        
        db = catocommon.new_conn()

        sql = "select user_id, user_password, full_name, user_role, email, status, failed_login_attempts, expiration_dt, force_change \
            from users where username='" + in_name + "'"
        
        row = db.select_row(sql)
        if not row:
            server.output("Invalid login attempt - [%s] not a valid user." % (in_name))
            msg = "Invalid Username or Password."
            raise web.seeother('/static/login.html?msg=' + urllib.quote(msg))

        
        #alrighty, lets check the password
        # we do this by encrypting the form submission and comparing, 
        # NOT by decrypting it here.
        encpwd = catocommon.cato_encrypt(in_pwd)
        
        if row[1] != encpwd:
            server.output("Invalid login attempt - [%s] bad password." % (in_name))
            msg = "Invalid Username or Password."
            raise web.seeother('/static/login.html?msg=' + urllib.quote(msg))
            
        user_id = row[0]
        
        #all good, put a few key things in the session
        user = {}
        user["user_id"] = user_id
        user["full_name"] = row[2]
        user["role"] = row[3]
        user["email"] = row[4]
        user["ip_address"] = web.ctx.ip
        session.user = user
        
        # reset the user counters and last_login
        sql = "update users set failed_login_attempts=0, last_login_dt=now() where user_id='" + user_id + "'"
        if not db.try_exec_db(sql):
            print db.error

        #update the security log
        uiCommon.AddSecurityLog(db, user_id, uiGlobals.SecurityLogTypes.Security, 
            uiGlobals.SecurityLogActions.UserLogin, uiGlobals.CatoObjectTypes.User, "", 
            "Login from [" + web.ctx.ip + "] granted.")

        db.close()


        #put the site.master.xml in the session here
        # this is a significant boost to performance
        x = ET.parse("site.master.xml")
        if x:
            session.site_master_xml = x
        else:
            raise Error("Critical: Unable to read/parse site.master.xml.")

        
        raise web.seeother('/home')

class logout:        
    def GET(self):
        i = web.input(msg=None)
        msg = "User Logged out."
        if i.msg:
            msg = i.msg
        uiCommon.ForceLogout(msg)

class home:        
    def GET(self):
        return render.home()

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
        '/login', 'login',
        '/logout', 'logout',
        '/home', 'home',
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
    
    app.run()
