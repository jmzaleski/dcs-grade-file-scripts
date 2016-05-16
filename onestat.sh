#!/bin/bash

test ! -z "$1" || die usuage: $0 cdf id

errecho(){ >&2 echo $*; }
die(){ errecho $*;	exit; }
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

echo -n print stats for student:
grep $1 $CDF 

if test -z "$STUDENT_NO"
then
	read -p "student number: " STUDENT_NO
fi

GBIN=../../grades-bin
test -d "$GBIN" || die cannot stat $GBIN

GSTATS_OPT="-d -W 7"
TERM_GRADES=$CDF-term

test -f "$TERM_GRADES" || die cannot stat $TERM_GRADES

$GBIN/gstats $GSTATS_OPT -# $STUDENT_NO $TERM_GRADES

#make STUDENT_NO=$student_no onestat
