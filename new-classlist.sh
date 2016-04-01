#!/bin/bash

# print out the marks in a marks file that are "missing".. zero or blank.
# challenge is that gpr has no way of selecting blank marks

die(){ echo $*;	exit; }

GBIN=../../grades-bin

test -d $GBIN || die no grades bin in $GBIN

test -f ./dot.sh || die cannot find ./dot.sh
source ./dot.sh

test ! -z "$COURSE" || die COURSE env not found.. should be defined in ./dot.sh
test ! -z "$SESSION" || die SESSION env not found.. should be defined in ./dot.sh

CLASSLIST="CSC"$COURSE$SESSION
test -f $CLASSLIST || die $0: cannot find class list $CLASSLIST

TMP=/tmp/CL$$
TMP_SORT=/tmp/CL-sorted$$

# scp matz@cdf.utoronto.ca:/u/csc/instructors/classlists/$CDF $TMP_CLASSLIST
# ugh. what i call a classlist they call an emaillist
#
set -x
scp matz@cdf.utoronto.ca:/u/csc/instructors/emaillists/$CLASSLIST $TMP || die scp failed
set -

sort $TMP > $TMP_SORT || die sort $TMP failed

set -x
diff $CLASSLIST $TMP_SORT 
set -

read -p "look right? interrupt out now. enter to cp new classlist to $CLASSLIST  >" junk
bf=$(backfilename.sh $CLASSLIST)
mv $CLASSLIST $bf || die failed to backup $CLASSLIST
mv $TMP_SORT $CLASSLIST || die failed to mv $TMP_SORT $CLASSLIST 
ls -l $bf
echo backup saved in $bf
echo "if students were ADDED edit grades files by hand. else just run drops.sh"



