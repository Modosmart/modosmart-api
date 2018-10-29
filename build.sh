#!/bin/bash
PROJECT_HOME=$(pwd)
# if [[ $(id -u) -ne 0 ]] ; then echo "Please run as root" ; exit 1 ; fi
function help {
	echo "Choose one of the following: {freeze|install}"
	exit 1
}

function freeze {
  pip freeze > requirements.txt
}

function install {
  pip install -r requirements.txt
}

if [ $# -eq 0 ]
then
	help
fi

for cmd in $@
do

case "$cmd" in

	freeze)
		freeze
	;;

	install)
		install
	;;

	*)
		help
	;;
esac

done
