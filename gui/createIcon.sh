#! /bin/sh
if [ "$2" != "" ] ; then
  on=$2
else
  b=`echo $1 | sed 's/\.[^.]*$//'`
  on=b.ico
fi
convert $1 -define icon:auto-resize="256,128,96,64,48,32,16" $on