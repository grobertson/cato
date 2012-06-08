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

package require mysqltcl
package require tdom
set ::CATO_HOME [file dirname [file dirname [file normalize $argv0]]]
source $::CATO_HOME/services/bin/common.tcl
read_config
proc connect {} {
    puts "Connecting to $::CONNECT_SERVER $::CONNECT_DB $::CONNECT_PORT, user $::CONNECT_USER"
    if {[catch {set ::CONN [::mysql::connect -user $::CONNECT_USER -password $::CONNECT_PASSWORD -host $::CONNECT_SERVER -db $::CONNECT_DB -port $::CONNECT_PORT -multiresult 1 -multistatement 1]} errMsg]} {
        puts "Could not connect to the database. Error message -> $errMsg"
        puts "Exiting..."
        exit
    }
}
proc parse {task_id step_id x} {
	set xmldoc [dom parse -simple $x]
    set root [$xmldoc documentElement]
    set new_xml [$root asXML -indent none]
    $root delete
    $xmldoc delete
    set new_xml [::mysql::escape $new_xml]
    #puts $new_xml
    set sql "update task_step set function_xml = '$new_xml' where task_id = '$task_id' and step_id = '$step_id'"
    #set sql "insert into task_step_test2 (task_id, step_id, function_xml) values ('$task_id','$step_id','$new_xml')"
    ::mysql::exec $::CONN $sql
}
connect
set sql "select task_id, step_id, function_xml from task_step"
puts $sql
set  rows [::mysql::sel $::CONN $sql -list]
foreach row $rows {
    parse [lindex $row 0] [lindex $row 1] [lindex $row 2]
}
