#!/usr/bin/env tclsh

proc bash_example { command } {
	#the proc_name variable must be set - it is used by the logging functions
	set proc_name bash_example

	insert_audit $::STEP_ID  "" "Firing up bash..." ""

	#there are two options here:
	#1) parse the function xml here, and send values on the command line call -or-
	#2) save the whole xml to a file, or encode it, and pick it up in the target script.
	
	#let's do an example of #1 - we'll pull the "arg" xml node out of the command
	# (see the hello_world example, or the extension documentation, for details on these built-in functions)
	get_xml_root $command
	set arg_val [replace_variables_all [$::ROOT selectNodes string(arg)]]
	del_xml_root

	#we're setting the output variable in case the exec had anything on stdout
	set output [exec extensions/examples/bash_example/bash_example.sh $arg_val]

	#display the stdout from the exec call
	insert_audit $::STEP_ID  "" $output ""
}