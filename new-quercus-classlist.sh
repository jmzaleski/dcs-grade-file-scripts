#!/bin/bash

# fetch a new classlist from CDF

die(){ echo $*;	exit; }

test -f ./dot.sh || die cannot find ./dot.sh
source ./dot.sh

test ! -z "$COURSE" || die COURSE env not found.. should be defined in ./dot.sh
test ! -z "$SESSION" || die SESSION env not found.. should be defined in ./dot.sh
test -d $GBIN || die no grades bin in $GBIN

# oops CDF is now a misnomer for this variable
CDF="CSC"$COURSE$SESSION
QCLASSLIST=$CDF-quercus.csv

#test -f $QCLASSLIST || die $0: cannot find class list $QCLASSLIST

# this file contains the freshly exported and downloaded quercus grades
QFRESH=/tmp/CL$$

# this file is the fresh export sorted
FRESH_SORT=/tmp/CL-sorted$$

# the pre-existing quercus file sorted
QCLASSLIST_SORT=/tmp/q-CL$$

set -x
ls -ltr ~/Downloads/*Grades-CSC$COURSE*.csv | tail -5
set -

echo

NEWEST=$(ls -tr ~/Downloads/*Grades-CSC$COURSE*.csv | tail -1)
ls -l $NEWEST
echo guessing that newest quercus export file is $NEWEST

read -p "hit return to use grades file exported from quercus: $NEWEST >" JUNK

#sort by utorid
SORT="sort --field-separator=,  --key=1,1"
# cut out the columns we need -- we don't need grades, just the student ID fields
# Doh, nasty workaround. The name column header is just "name"
# but the name column has a comma in it "zaleski, mathew", so cut commands are different:

CUT="cut -d, -f1-4,6-7"
CUT2="cut -d, -f1-5,7-8"

set -x
cp $NEWEST $QFRESH || die failed to copy $NEWEST $QFRESH
#head -1 $QFRESH
#head -n 1 $QFRESH # | $CUT 

# whew. do CUT command on first line, cut2 on remaining. skip line 2
(head -n 1 $QFRESH | $CUT && tail -n +3 $QFRESH | $SORT | $CUT2)  > $FRESH_SORT || die sort $QFRESH failed
#head -1 $FRESH_SORT
set -

if test ! -f $QCLASSLIST
then
	echo $0: cannot find class list $QCLASSLIST creating one..	
	read -p "hit enter to run: /bin/cp -i $FRESH_SORT $QCLASSLIST >" JUNK
	/bin/cp -i $FRESH_SORT $QCLASSLIST
	echo fresh class list created from quercus download..
	ls -l $QCLASSLIST
	exit
fi	

(head -n 1 $QCLASSLIST && tail -n +4 $QCLASSLIST | $SORT ) | $CUT  > $QCLASSLIST_SORT || die sort $QCLASSLIST failed

echo -n num drops
# comm old new
comm -13 $FRESH_SORT $QCLASSLIST_SORT  | wc -l
echo -n num adds
comm -23 $FRESH_SORT $QCLASSLIST_SORT | wc -l

echo to investigate following do:
echo xdiff $FRESH_SORT $QCLASSLIST_SORT

read -p 'comm downloaded class list' junk

echo drops:
echo  '---------------------'
comm -13 $FRESH_SORT $QCLASSLIST_SORT
echo '---------------------'
echo adds:
comm -23 $FRESH_SORT $QCLASSLIST_SORT
echo '---------------------'

echo to investigate following do:
echo xdiff $FRESH_SORT $$QCLASSLIST_SORT

read -p 'diff previous and newly downloaded class list' junk

set -x
diff $FRESH_SORT $QCLASSLIST_SORT
set -

echo too complicated\? try:
echo xdiff $FRESH_SORT $QCLASSLIST_SORT

read -p "continue to utorid's" JUNK
echo
echo utorids of drops:
echo
comm -13 $FRESH_SORT $QCLASSLIST_SORT | cut -d, -f5

echo
read -p "comm -23.. (utorid of new students) ..  >" junk
comm -23 $FRESH_SORT $QCLASSLIST_SORT | cut -d, -f5

read -p "last chance before scribbling on $QCLASSLIST:" junk

bf=$(backfilename.sh $QCLASSLIST)
mv $QCLASSLIST $bf || die failed to backup $QCLASSLIST
set -x
mv -i $NEWEST $QCLASSLIST || die failed to mv $FRESH_SORT $QCLASSLIST 
set -
echo backup saved in $bf
ls -l $bf

echo 
echo to undo what just happened:
echo cp $bf $QCLASSLIST

echo 
echo to investigate what happened:
echo xdiff $bf  $QCLASSLIST
echo



