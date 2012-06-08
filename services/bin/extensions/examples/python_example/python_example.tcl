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


proc python_example { command } {
	#the proc_name variable must be set - it is used by the logging functions
	set proc_name python_example

	insert_audit $::STEP_ID  "" "Firing up Python..." ""

	#there are two options here:
	#1) parse the function xml here, and send values on the command line call -or-
	#2) save the whole xml to a file, or encode it, and pick it up in the target script.
	
	#let's do an example of #1 - we'll pull the "arg" xml node out of the command
	# (see the hello_world example, or the extension documentation, for details on these built-in functions)
	get_xml_root $command
	set arg_val [replace_variables_all [$::ROOT selectNodes string(arg)]]
	del_xml_root

	#we're setting the output variable in case the exec had anything on stdout
	set output [exec python extensions/examples/python_example/python_example.py $arg_val]

	#display the stdout from the exec call
	insert_audit $::STEP_ID  "" $output ""
}