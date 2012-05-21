#!/usr/bin/env python

import os
import sys

base_path = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
lib_path = os.path.join(base_path, "lib")
sys.path.append(lib_path)

from catocommon import catocommon
import xml.etree.ElementTree as ET

db = catocommon.new_conn()

#if the containing field has the attribute input_type="text", it has not been updated.
# get the guid...
# get that step...
# massage as needed
# update the xml
# update the db
# remove the old step

def FixIt(xd, node):
    if node.get("input_type") is None:
        print "-- Action appears to be correct."
        return
    
    old_step = node.text
    print "fixing action ... "
    print " - referenced step is %s" % old_step
    
    sql = "select replace(function_xml, 'command_type=', 'name=') as function_xml from task_step where step_id = '%s'" % old_step
    embedded_xml = db.select_col_noexcep(sql)
    
    print " - referenced steps xml is \n%s" % embedded_xml
    
    if not embedded_xml:
        print " - Found no xml for the embedded command - it doesn't exist.  Emptying it..."
        node.clear()
    else:
        xNew = ET.fromstring(embedded_xml)
        if xNew is not None:
            # we remove the input_type attrib, that's how we knew it was old school
            # and empty it
            node.clear()
            node.append(xNew)
        else:
            print " - ERROR: embedded xml didn't parse."
        
        print " - success! New xml is \n%s" % ET.tostring(xd)

    print " - updating ..."
    sql = "update task_step set function_xml = '%s' where step_id = '%s'" % (ET.tostring(xd), this_step)
    if not db.exec_db_noexcep(sql):
        print db.error

    print " - removing old school step ..."
    sql = "delete from task_step where step_id = '%s'" % old_step
    if not db.exec_db_noexcep(sql):
        print db.error





sql = "select step_id, function_xml from task_step where function_name in ('if', 'exists', 'loop', 'while')"
#sql = "select step_id, function_xml from task_step where step_id = '18bdf372-c8b9-4a2c-bd1b-5fd7ad01e833'"
rows = db.select_all_dict(sql)

if rows:
    for row in rows:
        this_step = row["step_id"]
        print "analyzing step %s" % this_step
        
        if row["function_xml"]:
            xd = ET.fromstring(row["function_xml"])
            
            if xd is not None:
                # pass the xd and the node to a func
                # THE 'IF' COMMAND
                for node in xd.findall("tests/test/action"):
                    FixIt(xd, node)
                for node in xd.findall("else"):
                    FixIt(xd, node)

                # THE 'EXISTS' COMMAND
                for node in xd.findall("actions/positive_action"):
                    FixIt(xd, node)
                for node in xd.findall("actions/negative_action"):
                    FixIt(xd, node)
            
                # THE 'LOOP' and 'WHILE' COMMANDS
                node = xd.find("action")
                if node is not None:
                    FixIt(xd, node)
            
            else:
                "ERROR - couldn't parse this steps xml."
        else:
            print " ERROR - step had no xml!"
else:
    print "Nothing to do."


db.close()
