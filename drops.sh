#!/bin/bash
# #### assumes that the CLASSLIST has been updated already and we just want to mark drops in a marks file

die(){ echo $*;	exit; }

GBIN=../../grades-bin
test -d $GBIN || die no grades bin in $GBIN

test ! -z "$1" || die usage: $0 marks file
test -f $1 || die $0: $1 not a marks file

mf=$1

test -f ./dot.sh || die cannot find ./dot.sh
source ./dot.sh

test ! -z "$COURSE" || die COURSE env not found.. should be defined in ./dot.sh
test ! -z "$SESSION" || die SESSION env not found.. should be defined in ./dot.sh
CLASSLIST="CSC"$COURSE$SESSION
test -f $CLASSLIST || die $0: cannot find class list $CLASSLIST

#### assumes that the classlist has been updated already

TMP_MF=/tmp/$mf$$

cp $mf $TMP_MF

# -c 9 something about 9 vs 10 digit student numbers
# since our students are currently a mixture,
# using -c 10 will ignore the leading 1 of the 10 digit numbers..
# which is okay, I guess.
# more annoying is that the gupdatedrops rewrites the grades file with 10 digit numbers.
#
CMD="$GBIN/gupdatedrops -c 9 -L $CLASSLIST"

#this sets the drop column for gonzo students
$CMD $TMP_MF || die "failed to run $CMD $TMP_MF"

set -x
diff -w $TMP_MF $mf
set -

read -p "look right? interrupt out now. enter to apply same drops to $mf  >" junk
bf=$(backfilename.sh $mf)
cp $mf $bf
ls -l $bf
echo backup saved in $bf

$CMD $mf

