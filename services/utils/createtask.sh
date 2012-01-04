#!/bin/bash

# If you wanted to make an API call using shell scripting and curl, here's an example.
# Note: this file does NOT have an example of generating the SHA256 signature as utilities for doing that in shell script can vary.
# the example here doesn't actually work unless you plug in some code to generate your signature correctly
# or hardcode your timestamp and signature.
# but remember, the API requires a "timely" timestamp ... wait too long and your request will be rejected.

if [ "$1" == "" ]
then
   echo "Usage: createtask <task_xml_file>"
   exit
fi

infile=$1
tmpfile=infile.64

# remove any temp files
rm $tmpfile >/dev/null 2>&1

#base64 encode the input file into a temp file
base64 -i $infile -o $infile.tmp

# replace the +, / and = characters in the file, as they are invalid for an HTTP post.
awk '{ gsub(/\+/, "%2B"); gsub(/\//, "%2F"); gsub(/=/, "%3D"); print; }' $infile.tmp > $tmpfile

# write the scrubbed base64 task data into a file, in the HTTP form key=value format.
echo $(awk '{printf "TaskXML=%s",$1}' $tmpfile) > $tmpfile

# use curl to invoke the api call, and pass in the encoded data
curl "localhost:8088/pages/api.ashx?action=CreateTask&key=545b60a5-17e7-4fe0-b28f-7c4722c76544&timestamp=2011-12-20T13%3A58%3A14" --data @$tmpfile

# cleanup
rm $tmpfile >/dev/null 2>&1
rm $infile.tmp >/dev/null 2>&1

##the example here will require the proper creation of an SHA256 signature before 1.0.6 is released.
## we will be converting this script to TCL and using something like the following
## package require Tcl  8.2
## package require sha256  1.0.2
## ::sha2::hmac <password> <querystring>

## <password> is the password of the user making the API call.
## is the querystring from the ? to the end of the timestamp, NOT including the &signature= portion.

