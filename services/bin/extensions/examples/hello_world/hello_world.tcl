#!/usr/bin/env tclsh

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