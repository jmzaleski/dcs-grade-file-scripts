#!/bin/bash
# #### assumes that the CLASSLIST has been updated already and we just want to mark drops in a marks file

die(){ echo $*;	exit; }

GBIN=../../grades-bin
test -d $GBIN || die no grades bin in $GBIN

test ! -z "$1" || die usage: $0 marks file '#assumes classlist updated already, perhaps using new-classlist.sh'
test -f $1 || die $0: $1 not a marks file

set -x

mf=$1

test -f ./dot.sh || die cannot find ./dot.sh
source ./dot.sh

test ! -z "$COURSE" || die COURSE env not found.. should be defined in ./dot.sh
test ! -z "$SESSION" || die SESSION env not found.. should be defined in ./dot.sh
CLASSLIST="CSC"$COURSE$SESSION
test -f $CLASSLIST || die $0: cannot find class list $CLASSLIST

#### assumes that the classlist has been updated already

#this is where we we'll mangle marks file
TMP_MF=/tmp/$(basename $mf)$$

TMP_CL=/tmp/cl$$
#will cut student numbers out of class list and put them in file of their own. hence in column 0
cut -d, -f2 $CLASSLIST > $TMP_CL

cp $mf $TMP_MF

# -c 0 tells it to look for student numbers at left margin.. which makes sense given cut command above
# more problematic is -9 vs -10
# http://www.cdf.toronto.edu/~clarke/grade/lineapps/gupdatedrops.shtml suggests we use -9
CMD="$GBIN/gupdatedrops -c 0 -L $TMP_CL"

#this sets the drop column for gonzo students

$CMD $TMP_MF || die "failed to run $CMD $TMP_MF"

diff $mf $TMP_MF
set -

echo
echo NOTE gupdate drops rewrites 9 digit student numbers as 10, hence diff hard useless
echo reasonable hack is to s/^9/09/ in grades file beforehand
echo if too complicated try:
echo xdiff $mf $TMP_MF
read -p "look right? interrupt out now. enter to apply same drops to $mf  >" junk


bf=$(backfilename.sh $mf)
cp $mf $bf
ls -l $bf
echo backup saved in $bf

$CMD $mf

