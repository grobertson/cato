#!/usr/bin/env python

#########################################################################
# Copyright 2011 Cloud Sidekick
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#########################################################################


import os
import sys

base_path = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
lib_path = os.path.join(base_path, "lib")
sys.path.append(lib_path)

from catocommon import catocommon
import xml.etree.ElementTree as ET

db = catocommon.new_conn()

"""
    We're spinning through every single command in the task_step table, and reporting those that have 
    some sort of xml parsing error.
"""

print "Analyzing all Tasks ...\n"

sql = "select task_id, step_id, function_xml from task_step"
rows = db.select_all_dict(sql)

if rows:
    for row in rows:
        task_id = row["task_id"]
        step_id = row["step_id"]
        xml = row["function_xml"]
        
        if xml:
            try:
                xd = ET.fromstring(xml)
            except Exception, ex:
                print "\n\n"
                print "Task [%s], Step [%s], XML [%s]" % (task_id, step_id, xml)
                print ex.__str__()
        else:
            print " ERROR - step had no xml!"
    
    print "All Done!"
else:
    print "Nothing to do."


db.close()
