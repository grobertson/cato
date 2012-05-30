#!/bin/bash
DEPLOY_DIR=/opt/cato
COMPONENT=3
SILENT=0
if [ ! -n "$1" ]
then
	read -p "Enter a target directory. (default: $DEPLOY_DIR): " dir
	if [ "$dir" != "" ]; then
		DEPLOY_DIR=$dir
	fi	
	echo ""
	echo "Components, 1 = web, 2 = services, 3 = all"
	read -p "Enter a component to install. (1,2,3; default: 3): " dir
	if [ "$dir" = "" ]; then
		COMPONENT=3
	else
		COMPONENT=$dir
	fi
else
	while getopts ":c:t:s" opt
	do
	    case "$opt" in
	      c)  COMPONENT="$OPTARG";;
	      s)  SILENT=1;;
	      t)  DEPLOY_DIR="$OPTARG";;
	      \?)               # unknown flag
		  echo >&2 \
		  "usage: $0 [-s] [-t targetpath] [-c component (1|2|3)]"
		  echo "        -s      silent operation" 
		  echo "        -t      path to install to" 
		  echo "        -c      1 = web, 2 = service, 3 = both"
		  exit 1;;
	    esac
	done
	shift `expr $OPTIND - 1`
fi
if [ $SILENT = 0 ]
then 
	echo "target = $DEPLOY_DIR, installing component = $COMPONENT, silent = $SILENT"
	echo "Installing to $DEPLOY_DIR ..."
fi

# common for all
if [ $SILENT = 0 ]
then 
	echo "Copying common files..."
fi

mkdir -p $DEPLOY_DIR
mkdir -p $DEPLOY_DIR/web
mkdir -p $DEPLOY_DIR/services
mkdir -p $DEPLOY_DIR/lib
mkdir -p $DEPLOY_DIR/logfiles
mkdir -p $DEPLOY_DIR/conf

rsync -aq conf/default.cato.conf $DEPLOY_DIR/conf
rsync -aq conf/setup_conf $DEPLOY_DIR/conf
rsync -aq conf/cloud_providers.xml $DEPLOY_DIR/conf
# rsync -aq lib/catocryptpy/* $DEPLOY_DIR/conf/catocryptpy
# rsync -aq lib/catocrypttcl/* $DEPLOY_DIR/conf/catocrypttcl
rsync -aq database/* $DEPLOY_DIR/conf/data

rsync -q NOTICE $DEPLOY_DIR/
rsync -q LICENSE $DEPLOY_DIR/

rsync -aq lib/* $DEPLOY_DIR/lib

if [ $SILENT = 0 ]
then 
	echo "Creating services link to conf dir..."
fi


# web
if [ "$COMPONENT" = "1" -o "$COMPONENT" = "3" ]
then

	if [ $SILENT = 0 ]
	then 
		echo "Copying web files..."
	fi

	# code
	rsync -aq web/static/* $DEPLOY_DIR/web/static
	rsync -aq web/extensions/* $DEPLOY_DIR/web/extensions
	rsync -aq web/templates/* $DEPLOY_DIR/web/templates

	# empty stuff
	#the temp directory
	mkdir -p $DEPLOY_DIR/web/temp
	#the cache directory
	mkdir -p $DEPLOY_DIR/web/datacache

	#explicit local files
	rsync -q web/*.py $DEPLOY_DIR/web/
	rsync -q web/*.xml $DEPLOY_DIR/web/

	if [ $SILENT = 0 ]
	then 
		echo "Creating web link to conf dir..."
	fi

	# ln -s $DEPLOY_DIR/conf $DEPLOY_DIR/web/conf
fi

#services
if [ "$COMPONENT" = "2" -o "$COMPONENT" = "3" ]
then

	if [ $SILENT = 0 ]
	then 
		echo "Copying services files..."
	fi

	rsync -aq services/*.sh $DEPLOY_DIR/services
	rsync -aq services/bin/* $DEPLOY_DIR/services/bin

	if [ $SILENT = 0 ]
	then 
		echo "Creating services link to conf dir..."
	fi

	# ln -s $DEPLOY_DIR/conf $DEPLOY_DIR/services/conf
fi

if [ $SILENT = 0 ]
then 
	echo "... Done"
fi








