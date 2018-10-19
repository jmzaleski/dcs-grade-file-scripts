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
CLASSLIST=$CDF-quercus.csv

test -f $CLASSLIST || die $0: cannot find class list $CLASSLIST

TMP=/tmp/CL$$
Q_TMP_SORT=/tmp/q-CL$$
TMP_SORT=/tmp/CL-sorted$$

ls -ltr ~/Downloads/*Grades-CSC$COURSE*.csv
NEWEST=$(ls -tr ~/Downloads/*Grades-CSC$COURSE*.csv | tail -1)

read -p "export grades file from quercus to ~/Downloads $NEWEST" JUNK

#sort by utorid
# nevermind section
SORT="sort --field-separator=,  --key=1,1"
CUT="cut -d, -f1-5"

set -x
cp $NEWEST $TMP || die failed to copy $NEWEST $TMP
$SORT $CLASSLIST | $CUT  > $Q_TMP_SORT || die sort $CLASSLIST failed
$SORT $TMP       | $CUT  > $TMP_SORT || die sort $TMP failed
set -

echo -n num drops
comm -13 $TMP_SORT  $Q_TMP_SORT | wc -l
echo -n num adds
comm -23 $TMP_SORT  $Q_TMP_SORT | wc -l

echo to investigate following do:
echo xdiff $TMP_SORT $Q_TMP_SORT

read -p 'comm downloaded class list' junk

echo drops:
echo  '---------------------'
comm -13 $TMP_SORT  $Q_TMP_SORT
echo '---------------------'
echo adds:
comm -23 $TMP_SORT  $Q_TMP_SORT
echo '---------------------'

echo to investigate following do:
echo xdiff $TMP_SORT $$Q_TMP_SORT

read -p 'diff previous and newly downloaded class list' junk

set -x
diff $TMP_SORT $Q_TMP_SORT
set -

echo too complicated\? try:
echo xdiff $TMP_SORT  $Q_TMP_SORT

read -p "continue to utorid's" JUNK
echo
echo utorids of drops:
echo
comm -13 $TMP_SORT  $Q_TMP_SORT | cut -d, -f5

echo
read -p "comm -23.. (utorid of new students) ..  >" junk
comm -23 $TMP_SORT  $Q_TMP_SORT | cut -d, -f5

read -p "last chance before scribbling on $CLASSLIST:" junk

bf=$(backfilename.sh $CLASSLIST)
mv $CLASSLIST $bf || die failed to backup $CLASSLIST
set -x
mv -i $NEWEST $CLASSLIST || die failed to mv $TMP_SORT $CLASSLIST 
set -
echo backup saved in $bf
ls -l $bf

echo 
echo to undo what just happened:
echo cp $bf $CLASSLIST

echo 
echo to investigate what happened:
echo xdiff $bf  $CLASSLIST
echo



