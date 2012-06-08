#!/usr/bin/env tclsh

# Copyright 2012 Cloud Sidekick
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  
#     http:# www.apache.org/licenses/LICENSE-2.0
#  
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

proc read_file { command } {
	#the proc_name variable must be set - it is used by the logging functions
	set proc_name hello_world

	# the $command variable is always an XML document.  We use tdom to read it.
	# but have a couple of utility functions to help.
	
	#get the xml document as a DOM.  Assigns the global $::ROOT to the document root.
	get_xml_root $command
	
	set filename [$::ROOT selectNodes string(filename)]
	set start [$::ROOT selectNodes string(start)]
	set num_chars [$::ROOT selectNodes string(num_chars)]
	
	# release the DOM object
	del_xml_root
	
	if {[catch {set fp [open $filename]} err_msg]} {
		error_out "File read error:\012$err_msg" 2204
	}
	if {"$start" > ""} {
		incr $start -1
	} else {
		set start 0
	}	
	seek $fp $start
	if {"$num_chars" > ""} {
		set output_buffer [read $fp $num_chars]
	} else {
		set output_buffer [read $fp]
	}
	close $fp

	insert_audit $::STEP_ID  "" "read file $output_buffer" ""

	if {[lindex $::step_arr($::STEP_ID) 4] > 0} {
		process_buffer $output_buffer
	}

}