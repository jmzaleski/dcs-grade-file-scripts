#!/bin/bash

die(){ echo $*;	exit; }

test ! -z "$1" || die usage: $0 cdf id

test -f ./dot.sh || die cannot find ./dot.sh
source ./dot.sh

test ! -z "$COURSE" || die COURSE env not found.. should be defined in ./dot.sh
test ! -z "$SESSION" || die SESSION env not found.. should be defined in ./dot.sh

CLASS="CSC"$COURSE$SESSION
LIST=$CLASS-empty

test -f $CLASS || die cannot open $CLASS

grep -i $* $CLASS > /dev/null 2>&1 || die failed to find any hits for $*

num_lines=$(grep -i $* $CLASS | wc -l)
#echo "$num_lines"

if test "$num_lines" -gt 1
then
	grep -i $* $CLASS
	die matched more than one line.
fi

line=$(grep -i $* $CLASS)
#echo line: $line 

cdf_id=$(echo $line | cut -d' ' -f1)


if test -f tutorial-0101-1 
then
	tutorial_line=$(grep $cdf_id tutorial-*101-*)
	tutorial_section=$(echo $tutorial_line | cut -d':' -f1)
	tutorial_tutor=$(echo $tutorial_line | cut -d',' -f4)
else
	echo did you run split-tutorial.sh? no file tutorial-0101-1
	tutorial_tutor="$(grep $cdf_id $LIST| cut -d, -f3)"
	tutorial_section="$(grep $cdf_id $LIST| cut -d, -f2)"
    ##|| die did you run split-tutorial.sh? no file tutorial-0101-1
fi

echo TA: $tutorial_tutor
echo SECTION: $tutorial_section 
echo EMAIL: $(grep $cdf_id $CLASS | cut -d\) -f2)

to_paste="$(grep $cdf_id $CLASS)) $tutorial_section $tutorial_tutor"

echo hit enter to paste to clipboard:
echo '``'$to_paste"''"
read -p '> ' junk
echo $to_paste | pbcopy
