#!/bin/bash

# fetch a new classlist from CDF

die(){ echo $*;	exit; }

test -f ./dot.sh || die cannot find ./dot.sh
source ./dot.sh

test ! -z "$COURSE" || die COURSE env not found.. should be defined in ./dot.sh
test ! -z "$SESSION" || die SESSION env not found.. should be defined in ./dot.sh
test -d $GBIN || die no grades bin in $GBIN

CDF="CSC"$COURSE$SESSION
CLASSLIST=$CDF-classlist
EMPTY=$CDF-empty

test -f $CLASSLIST || die $0: cannot find class list $CLASSLIST

TMP=/tmp/CL$$
TMP_SORT=/tmp/CL-sorted$$

set -x
scp matz@cdf.utoronto.ca:/u/csc/instructors/classlists/$CDF $TMP || die scp failed
set -

#sort by utorid
sort --field-separator=, --key=3,3 --key=1,1 $TMP |  sed -e "s/,9/,09/" | sed -e "s/LEC //"  > $TMP_SORT || die sort $TMP failed

set -x
diff $TMP_SORT $CLASSLIST 
set -

echo too complicated\? try:
echo xdiff $TMP_SORT  $CLASSLIST

read -p "continue" JUNK

echo
echo utorids of drops:
echo

comm -13 $TMP_SORT  $CLASSLIST | cut -d, -f1

echo
echo lines from $EMPTY:
echo

comm -13 $TMP_SORT  $CLASSLIST | cut -d, -f1 | xargs -I % grep % $EMPTY

read -p "comm -13.. (drops)  >" junk
comm -13 $TMP_SORT  $CLASSLIST 
echo run drops.sh next to mark these student as having dropped
echo
read -p "comm -23.. (new students) ..  >" junk
comm -23 $TMP_SORT  $CLASSLIST 

read -p "added student lines in classlist formated as for empty grades file format >" junk
echo

comm -23 $TMP_SORT  $CLASSLIST \
	 | awk -F, '{printf "%s    %s%s,%s,%s,TAx,ROOM,%s,%s,%s\n", $2, $4,$5,$1,$3,$4,$5,$6}' \
	 | sed -e "s/LEC //" 

echo
echo copy/paste following into empty file
echo
read -p "look right? interrupt out now. enter to cp new classlist to $CLASSLIST  >" junk

bf=$(backfilename.sh $CLASSLIST)
mv $CLASSLIST $bf || die failed to backup $CLASSLIST
mv -i $TMP_SORT $CLASSLIST || die failed to mv $TMP_SORT $CLASSLIST 
echo backup saved in $bf
ls -l $bf

echo "if students were ADDED edit grades files by hand. else just run drops.sh"
echo xdiff $TMP_SORT  $CLASSLIST 



