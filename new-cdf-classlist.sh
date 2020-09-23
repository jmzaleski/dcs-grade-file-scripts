#!/bin/bash

# fetch a new classlist from CDF

die(){ echo $*;	exit; }

test -f ./dot.sh || die cannot find ./dot.sh
source ./dot.sh

test ! -z "$COURSE" || die COURSE env not found.. should be defined in ./dot.sh
test ! -z "$SESSION" || die SESSION env not found.. should be defined in ./dot.sh
test -d $GBIN || die no grades bin in $GBIN

CDF="CSC"$COURSE$SESSION
CLASSLIST=$CDF-cdf.csv
TMP=/tmp/CL$$
TMP_SORT=/tmp/CL-sorted$$

set -x
scp matz@cdf.utoronto.ca:/u/csc/instructors/classlists/$CDF $TMP || die scp failed
set -

# sort by 
sort --field-separator=,  --key=1,1 $TMP \
	 | sed -e 's/,LEC /,/' \
	 | sed -e 's/,99/,099/' \
	 > $TMP_SORT || die sort $TMP failed

if test ! -f $CLASSLIST
then 
	echo $0: cannot find class list $CLASSLIST creating one..
	ls -l $TMP_SORT
	echo following prompt is from cp -i interrupt to not copy
	read -p "hit enter to run: /bin/cp -i $TMP_SORT $CLASSLIST >" JUNK
	/bin/cp -i $TMP_SORT $CLASSLIST
	echo fresh class list created from CDF
	ls -l $CLASSLIST
	exit
fi

echo -n num drops
# comm new old
comm -13 $TMP_SORT  $CLASSLIST | wc -l
echo -n num adds
comm -23 $TMP_SORT  $CLASSLIST | wc -l

echo drops:
comm -13 $TMP_SORT  $CLASSLIST
echo adds:
comm -23 $TMP_SORT  $CLASSLIST

read -p 'diff previous and newly downloaded class list:' junk

set -x
diff $TMP_SORT $CLASSLIST 
set -

echo diff too complicated\? try:
echo xdiff $TMP_SORT  $CLASSLIST

read -p "continue" JUNK
echo
echo utorids of drops:
echo
comm -13 $TMP_SORT  $CLASSLIST | cut -d, -f1

read -p "comm -13.. (drops)  >" junk
comm -13 $TMP_SORT  $CLASSLIST 

echo
read -p "comm -23.. (utorid of new students) ..  >" junk
comm -23 $TMP_SORT  $CLASSLIST 

bf=$(backfilename.sh $CLASSLIST)
mv $CLASSLIST $bf || die failed to backup $CLASSLIST
mv -i $TMP_SORT $CLASSLIST || die failed to mv $TMP_SORT $CLASSLIST 
echo backup saved in $bf
ls -l $bf

echo
echo xdiff $TMP_SORT  $CLASSLIST
echo

cat <<EOF
now wrangle google doc view:
1. go to cdf workbook, rename first sheet (maybe append -N?)
2. import the .csv this script wrote as new sheet in this workbook
3. move the sheet to leftmost
4. hide old sheet to save confusion
EOF
