#!/bin/bash

test ! -z "$1" || die usuage: $0 cdf id

# probably want this to be fin after exams are marked
TERM_GRADES=term
#TERM_GRADES=fin

errecho(){ >&2 echo $*; }
die(){ errecho $*;	exit; }

test -f "$TERM_GRADES" || die cannot stat $TERM_GRADES

test -f ./dot.sh || die cannot find ./dot.sh
source ./dot.sh

test ! -z "$COURSE"  || die COURSE env not found.. should be defined in ./dot.sh
test ! -z "$SESSION" || die SESSION env not found.. should be defined in ./dot.sh
test ! -z "$YEAR"    || die YEAR env not found.. should be defined in ./dot.sh

GBIN=../../grades-bin
test -d $GBIN || die cannot stats $GBIN

CDF="CSC"$COURSE$SESSION
EMPTY=$CDF-empty

STUDENT_NO=$(grep $1 $EMPTY | awk '{print $1}')
test ! -z "$STUDENT_NO" || die no cdf id $1 in empty grade file?

echo print grades for student with number: $STUDENT_NO from grades file:
ls -l $TERM_GRADES
grep "$STUDENT_NO" "$EMPTY"
echo

if test -z "$STUDENT_NO"
then
	read -p "student number: " STUDENT_NO
fi

GBIN=../../grades-bin
test -d "$GBIN" || die cannot stat $GBIN

GSTATS_OPT="-d -W 7"

echo $GBIN/gstats $GSTATS_OPT -# $STUDENT_NO $TERM_GRADES
$GBIN/gstats $GSTATS_OPT -# $STUDENT_NO $TERM_GRADES

#make STUDENT_NO=$student_no onestat
