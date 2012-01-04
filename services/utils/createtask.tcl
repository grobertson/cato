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

package require base64
package require sha256  1.0.2
package require tdom
package require http
#package require tls
#::http::register https 443 ::tls::socket

# This script will create a task using a well formed task XML document as input.

set ::API_URL [lindex [split [lindex $::argv 0]] 0]
set ::TASK_XML_FILE [lindex [split [lindex $::argv 1]] 0]
set ::KEY [lindex [split [lindex $::argv 2]] 0]
set ::PASSWORD [lindex [split [lindex $::argv 3]] 0]
set ::SILENT [lindex [split [lindex $::argv 4]] 0]
set ::RESULT ""

proc output {args} {
	if {"$::SILENT" != "-silent"} {
		set output_string [lindex $args 0]
		#puts "\n[clock format [clock seconds] -format "%Y-%m-%d %H:%M:%S"] :: $output_string"
		puts "$output_string"
		flush stdout
	}
}

# this proc does an HTTP POST to the specified URL, and sends the encoded task xml as form data
proc http_get {url task_xml_encoded} {
	# if you wanted to do a GET instead it would look like this, get is a lot pickier about what's in the querystring... specifically newlines.
	# catch {set token [::http::geturl $url -timeout [expr 10 * 1000]]} error_code
	
	#but this is big data and it has newlines... so we're using POST
	set query "TaskXML=$task_xml_encoded"
	catch {set token [::http::geturl $url -timeout [expr 60 * 1000] -query $query]} error_code
	
	if {[string match "::http::*" $error_code] == 0} {
		set output_buffer "<error>$error_code</error>"
		#output "\n\nHTTP Error:\n$error_code" 1
	} else {
		if {"[::http::status $token]" != "ok" || [::http::ncode $token] != 200} {
			set output_buffer "<error>HTTP Error: [::http::status $token] [::http::code $token] [::http::data $token]</error>"
			error $output_buffer 2011
		
		} else {
			set output_buffer [::http::data $token]
			#output $output_buffer 1
		}
		
	}
	if {[info exists token] == 1} {
		::http::cleanup $token 
	}

	set ::RESULT $output_buffer
}

# this proc reads a file into a variable
proc read_file {filename} {
	#output "will try to read $filename"
	
	if {[catch {set fp [open $filename]} err_msg]} {
		error "File read error:\012$err_msg" 2204
	}

	seek $fp 0
	set ::TASK_XML [read $fp]
	close $fp

	#output "$task_xml"
}

#############
# MAIN CODE #
#############

output "Cato CreateTask Utility\n"

# do not continue unless we have all the required arguments
if {"$::API_URL" == "" || "$::TASK_XML_FILE" == "" || "$::KEY" == "" || "$::PASSWORD" == ""} {
	output "Usage:\n createtask.tcl <url> <task_xml_filename> <key> <password>\n\nExample:\n createtask.tcl localhost my_task.xml 545b60a5-17e7-4fe0-b28f-7c4722c76544 foo"
	exit
}

# a little useful information
output "Using the API at: $::API_URL"
output "Task Input File: $::TASK_XML_FILE"
output "API Key: $::KEY"

# read the specified XML file
read_file $::TASK_XML_FILE

# we can't proceed if the file was empty or there was a problem reading it.
if {"$::TASK_XML" == ""} {
	error "$::TASK_XML_FILE did not contain any data."
}

# TODO: this could load the xml file into a dom object and validate it if we want to get fancy...
# but the API will validate it too, so for now we won't bother.

# the Task XML must be prepared before sending over HTTP.
# first, base64 encode it
set task_xml_encoded [base64::encode $::TASK_XML]

# then, replace occurences of http reserved characters in the base64 encoding, 
# because a base64 string can include three invalid HTTP chars (+, / and =).
# + becomes %2B
# / becomes %2F
# = becomes %3D
set task_xml_encoded  [string map {= %3D / %2F + %2B} $task_xml_encoded]
#output $task_xml_64

# timestamp must be this exact format, in UTC time, and with the dashes URL encoded
# 2011-12-20T13%3A58%3A14
set timestamp [string map {: %3A} [clock format [clock seconds] -format "%Y-%m-%dT%H:%M:%S" -gmt true]]
#output "Timestamp: $timestamp"

set string_to_sign "action=CreateTask&key=$::KEY&timestamp=$timestamp"
#output "String to sign: $string_to_sign"

set signature [::sha2::hmac $::PASSWORD $string_to_sign]
#output "Signature: $signature"

# build the URL we will connect to
set url "http://$::API_URL/pages/api.ashx?$string_to_sign&signature=$signature"

output "\n\nConnecting using: $url"

# and do the connection
http_get $url $task_xml_encoded

# process the results
#output $::RESULT

# the output buffer will be xml
# so... load the XML into a dom and return either the error OR the created task_id
regsub -all "&" $::RESULT "&amp;" ::RESULT
set xmldoc [dom parse $::RESULT]
set root [$xmldoc documentElement]

# now, if it was successful we will have a task_id node.
# the fastest way to do this is to assume success, check for that node, and display the error if it wasn't there.
set task_id [$root selectNodes string(//task_id)]
output "TID: $task_id"
if {"$task_id" == ""} {
	set ::SILENT ""
	output $::RESULT
} else {
	# if the silent flag is set, output only the task_id
	if {"$::SILENT" == "-silent"} {
		puts $task_id
	} else {
		output "Successfully created task_id $task_id"
	}
}

#TODO: if a flag was set, go ahead and RUN this task.
# we can just call the RunTask.tcl file


# if you wanted to reuse these dom objects, they need to be explicitly unset
# but in this example we're done, so... no need
# $xmldoc delete
# $root delete
# unset root xmldoc


# and we're done
exit


