#!/bin/bash

PROGNAME=${0##*/}
PROGVERSION=0.0.1 

usage()
{
  cat << EO
        Usage: $PROGNAME [options]

        Program Nextion Display with updated Firmware

        Options:
EO
  cat <<EO | column -s\& -t

        -h|--help & show this output
        -v|--version & show version information
	-t|--turnaround & program display content upside down
EO
}


SHORTOPTS="hvt"
LONGOPTS="help,version,turnaround"

ARGS=$(getopt -s bash --options $SHORTOPTS  \
  --longoptions $LONGOPTS --name $PROGNAME -- "$@" )

eval set -- "$ARGS"

while true; do
   case $1 in
      -h|--help)
         usage
         exit 0
         ;;
      -v|--version)
         echo "$PROGVERSION"
         ;;
      -t|--turnaround)
#         shift
        echo "Programming rotated version into display" 
	sudo systemctl stop unipagernextion.service
	../Nextion/nextion.py ../Nextion/NX4024T032_270deg.tft
	sleep 10
	sudo systemctl start unipagernextion.service
	exit 0
         ;;
      --)
         shift
         break
         ;;
      *)
         shift
         break
         ;;
   esac
   shift
done
echo "Programming normal version into display"
sudo systemctl stop unipagernextion.service
../Nextion/nextion.py ../Nextion/NX4024T032.tft
sleep 10
sudo systemctl start unipagernextion.service
