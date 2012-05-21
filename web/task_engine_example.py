#!/usr/bin/env python

import sys
import os
import xml.etree.ElementTree as ET

base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
lib_path = os.path.join(base_path, "services", "lib")
sys.path.append(lib_path)

import task

import te_globals

def ProcessStep(step):
    print "executing step [%d, %s]" % (step.Order, step.ID)

    command_type = step.FunctionName
    if not command_type:
        print "ERROR: unable to continue - could not resolve command type for step [%s]" % step.ID
        sys.exit()

    # here's how we unpack the Function Xml Document (which is an ElementTree object
    # we'll pass this "xd" reference into any of the specific functions.
    xd = step.FunctionXDoc
    if xd is None:
        print "ERROR: this step doesn't have function xml."
        sys.exit()


    # this will be the big case routine to call functions based on the command type.
    # you pass in the elementtree document, and each function knows which specific nodes it expects
    if command_type == "codeblock":
        print "a 'codeblock' call..."
        # a codeblock command just forks to a new codeblock
        codeblock_to_call = xd.findtext("codeblock", None)
        print codeblock_to_call
        if codeblock_to_call:
            ProcessCodeblock(codeblock_to_call)
        else:
            "uh oh ... I couldn't find the 'codeblock' property in this steps command xml."
    elif command_type == "cmd_line":
        print "would execute 'cmd_line'"
    elif command_type == "new_connection":
        print "would execute 'new_connection'"
        from te_new_connection import connect
        connect(step)
        print te_globals.connections #now the connection we set in te_new_connection is available everywhere!
        
    else:
        print "oops, I don't know how to handle [%s]" % command_type
    
               
def ProcessCodeblock(codeblock_name):
    cb = t.Codeblocks[codeblock_name]
    if cb:
        print "in Codelock [%s]" % codeblock_name
        if cb.Steps:
            # steps are stored in a dictionary, which isn't sorted.
            # no worries, we'll sort it here
            for order, step in sorted(cb.Steps.iteritems()):
                ProcessStep(step)
    else:
        "ummm... I couldn't find the codeblock [%s]" % codeblock_name

if __name__ == "__main__":
    
    # get the task by ID
    task_id = "b185734c-4ff0-4d55-83ee-80c6e043bffa"
    
    t, sErr = task.Task.FromID(task_id)
    if sErr:
        print sErr
    if t:
        if t.ID:
            print "Processing Task [%s]" % (t.Name)
            # now we get the MAIN codeblocks and loop the steps,
            # starting with main of course
            ProcessCodeblock("MAIN")
