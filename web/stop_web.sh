#!/bin/bash

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
 
date
OS=`uname`
if [ "$OS" == "Darwin" ]; then
    ### this script does not work on the Mac yet. 
    echo "this script does not work on the Mac yet. Like to help?"
    exit 
fi
if [ -z "$CATO_HOME" ]; then

    EX_FILE=`readlink -f $0`
    EX_HOME=${EX_FILE%/*}
    CATO_HOME=${EX_HOME%/*}
    echo "CATO_HOME not set, assuming $CATO_HOME"
    export CATO_HOME
fi

# All other processes go here.  No process should be in both sections though.
FULL_PROCS[0]="$CATO_HOME/web/cato_admin_ui.py"

count=0
while [[ $count -lt ${#FULL_PROCS[*]} ]]; do
    PIDS=`ps -eafl | grep "${FULL_PROCS[$count]}" | grep -v "grep" | awk '{ print \$4 }'`

    if [ -z "$PIDS" ]; then
        echo "${FULL_PROCS[$count]} is not running"
    else
        for PID in $PIDS; do
            echo "Shutting down $i ($PID)"
            kill -9 $PID
        done
    fi 
        (( count += 1 ))
done
if [ "$1" = "leavecron" ]; then
	echo "Removing start_web.sh from crontab"
		crontab -l | grep -v start_web.sh > $CATO_HOME/conf/crontab.backup 2>/dev/null
		crontab -r 2>/dev/null
		crontab $CATO_HOME/conf/crontab.backup
		rm $CATO_HOME/conf/crontab.backup
	touch .shutdown
fi

echo "end"
exit
