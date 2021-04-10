#!/bin/sh

helpFunction()
{
   echo "AI MAS Client - 2021 DTU - Group 28 Final Project"
   echo ""
   echo "Usage: $0 -m level -t time out -s speed"
   echo "\t-m level to be executed. Relative path from ROOT/levels/"
   echo "\t-t server timeout"
   echo "\t-s server action replay speed"
   echo "\t-h display this message"
   echo ""
   exit 1
}

while getopts "m:t:s:h:" opt
do
   case "$opt" in
      m ) level="$OPTARG" ;;
      t ) timeout="$OPTARG" ;;
      s ) speed="$OPTARG" ;;
      h ) helpFunction ;;
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
echo "###########################"
echo ""
echo "...Starting application..."
echo ""
echo "###########################"
echo ""

echo "java -jar server.jar -l "levels/$level" -c \"python bin/main.py\" -g -s $speed -t $timeout"
echo ""

java -jar server.jar -l "levels/$level" -c "python bin/main.py" -g -s $speed -t $timeout
