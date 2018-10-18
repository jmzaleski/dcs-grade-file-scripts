#!/bin/bash

die(){ echo $*;	exit; }

test ! -z "$1" || die usage: $0 cdf id

test -f ./dot.sh || die cannot find ./dot.sh
source ./dot.sh

test ! -z "$COURSE" || die COURSE env not found.. should be defined in ./dot.sh
test ! -z "$SESSION" || die SESSION env not found.. should be defined in ./dot.sh

CDF="CSC"$COURSE$SESSION

CLASS=$CDF-cdf.csv

test -f $CLASS || die cannot open $CLASS

LIST="$CDF-empty"
TAFILE=TA
TMP=/tmp/em$$
cat > $TMP < /dev/null

#echo args: $* 
for i in $*
do
	grep -i $i $CLASS > /dev/null || die failed to find any hits for $i

	num_lines=$(grep -i $i $CLASS | wc -l)
	#echo "$num_lines"

	if test "$num_lines" -gt 1 
	then
		grep -i $i $CLASS
		die $i matched more than one line.
	else
		grep -i $i $CLASS | cut -d, -f6 >> $TMP
		#grep -i $i $LIST
	fi
done

concat=''
for i in $(cat $TMP)
do
	concat="$i, $concat"
done

echo
echo
echo $concat
echo
echo

read -p 'hit enter to paste to clipboard:' junk
echo $concat | pbcopy


