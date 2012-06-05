#!/bin/bash
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
