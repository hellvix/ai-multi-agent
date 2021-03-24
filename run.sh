#!/bin/sh

helpFunction()
{
   echo "AI MAS Client - 2021 DTU Final Project"
   echo ""
   echo "Usage: $0 -m level -t time out -s speed"
   echo "\t-m level found inside ROOT/levels/"
   echo "\t-t server timeout"
   echo "\t-s action replay speed"
   echo "\t-h display this message"
   echo ""
   exit 1
}

while getopts "m:h:" opt
do
   case "$opt" in
      m ) level="$OPTARG" ;;
      t ) timeout="$OPTARG" ;;
      s ) speed="$OPTARG" ;;
      ? ) helpFunction ;;
   esac
done

if [ -z "$level" ]
then
   level="MAPF00.lvl"
   echo "- No level specified. Using default:" $level;
   
fi

if [ -z "$timeout" ]
then
   timeout=18000
   echo "- No timeout gispecifiedven. Using default:" $timeout;
   
fi

if [ -z "$speed" ]
then
   speed=150
   echo "- No speed specified. Using default:" $speed;
   
fi

echo ""
echo "Starting application..."
echo ""
java -jar server.jar -l levels/$level -c "python bin/main.py" -g -s $speed -t $timeout