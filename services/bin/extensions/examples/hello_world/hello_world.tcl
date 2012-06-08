#!/usr/bin/env tclsh

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


proc hello_world { command } {
	#the proc_name variable must be set - it is used by the logging functions
	set proc_name hello_world

	# the $command variable is always an XML document.  We use tdom to read it.
	# but have a couple of utility functions to help.
	
	#get the xml document as a DOM.  Assigns the global $::ROOT to the document root.
	get_xml_root $command
	
	# selectNodes is a tdom function that will pull out a node from the xml
	set msg_txt [$::ROOT selectNodes string(message)]

	# the replace_variables_all function will parse a string, and replace any [[vars]] with the proper values.
	set message [replace_variables_all $msg_txt]
	
	# release the DOM object
	del_xml_root
	
	#the insert_audit function writes output to both the log file and the log table.
	# the global var $::STEP_ID is the id of the current step.
	insert_audit $::STEP_ID  "" $message ""
}