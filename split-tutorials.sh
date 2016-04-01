#!/opt/local/bin/bash 
# bloody hell!! os/x bash is v3 and doesn't do associative arrays!!

# shell script to split a class into tutorials
# AFTER the grades files have been initialized

die(){ echo $*;	exit; }

TUTORIAL_STEM="tutorial"

source ./dot.sh

# class list from CDF
CDF="CSC"$COURSE"H1F"

#set -x
BFN=$CDF-base.txt

test -f $BFN || die missing $BFN. Did you run init-grades ?

# use paste to create a CSV file with stud no, cdfid, email
#temp file containing student no, cdfid

awk '{printf "%s,%s\n", $1,$2}' $BFN | paste -d, -  $BFN-section > sections
SECTIONS="0101 5101"

for i in $SECTIONS
do
	grep $i'$' sections > section-$i.csv
done	

wc -l section*.csv

LINES=28
echo TODO: WARNING LINES to split hardcoded to $LINES
echo NB: $LINES '* 3 = ' $(expr $LINES \* 3)

read -p '..enter LINES (default '$LINES'):' read_lines

echo $read_lines

LINES=${$read_lines-$LINES}

read -p 'continue to split tutorials? LINES='$LINES'..interrupt to bail..' read_lines

#now break up into tutorial sized chunks
#TODO: automate the line count. no time now

for i in $SECTIONS
do
	split -l $LINES section-$i.csv "$TUTORIAL_STEM"-$i-
	wc -l "$TUTORIAL_STEM"-"$i"-*
done	

wc -l "$TUTORIAL_STEM"-0101-* "$TUTORIAL_STEM"-5101-*

read -p 'rename split files? ..interrupt to bail..' JUNK

set -
for sec in $SECTIONS
do
	ix=1
	for f in "$TUTORIAL_STEM"-"$sec"-*
	do
		dest="$TUTORIAL_STEM"-"$sec"-$ix
		mv $f $dest
		ix=$(expr $ix + 1)
	done
	ls -l "$TUTORIAL_STEM"-"$sec"-*
done	

read -p 'add TA email? ..interrupt to bail..' JUNK


# see csc300-ta-2015f

# from: aliciagrubb@gmail.com OR
# from: amgrubb@cs.toronto.edu> OR
# from: seanpollock93@gmail.com OR
# from: yiren.zheng@mail.utoronto.ca  OR 
# from: michael.sabet@gmail.com  OR 

# 0101 wed 5-6
# 5101 wed 6-7
# this from our own housekeeping at beginning of term
# Wed 5-6pm -  BA1200 Alicia / BA2159 Michael / BA3008 Sean
# Wed 6-7pm - BA1200 Alicia / SS2128 Michael / UC65 Yiren

declare -A TAxx
TAxx=(
	["0101-1"]="amgrubb@cs.toronto.edu"
	["0101-2"]="michael.sabet@gmail.com"
	["0101-3"]="seanpollock93@gmail.com"
    ["5101-1"]="amgrubb@cs.toronto.edu"
	["5101-2"]="michael.sabet@gmail.com"
	["5101-3"]="yiren.zheng@mail.utoronto.ca"
   )

#echo "${!TAxx[@]}"

for tutorial in ${!TAxx[@]}
do
	tutor=${TAxx["$tutorial"]} || die cannot find key $tutorial
	fn="$TUTORIAL_STEM"-"$tutorial"
	test -f $fn || die cannot find $fn
	ls -l $fn
	sed  -e 's/$/,'$tutor'/' $fn > $fn.ta
	mv $fn.ta $fn
	head -1 $fn
done


