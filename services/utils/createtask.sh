#!/bin/bash

if [ "$1" == "" ]
then
   echo "Usage: createtask <task_xml_file>"
   exit
fi

infile=$1
tmpfile=infile.64

rm $tmpfile >/dev/null 2>&1

base64 -i $infile -o $infile.tmp

awk '{ gsub(/\+/, "%2B"); gsub(/\//, "%2F"); gsub(/=/, "%3D"); print; }' $infile.tmp > $tmpfile

echo $(awk '{printf "TaskXML=%s",$1}' $tmpfile) > $tmpfile

curl "localhost:8088/pages/api.ashx?action=CreateTask&key=12-34-56-78-90" --data @$tmpfile

rm $tmpfile >/dev/null 2>&1
rm $infile.tmp >/dev/null 2>&1

##the example here will require the proper creation of an SHA256 signature before 1.0.6 is released.
## we will be converting this script to TCL and using something like the following
## package require Tcl  8.2
## package require sha256  1.0.2
## ::sha2::hmac <password> <querystring>

## <password> is the password of the user making the API call.
## is the querystring from the ? to the end of the timestamp, NOT including the &signature= portion.

