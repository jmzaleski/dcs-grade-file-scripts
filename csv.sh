#!/bin/bash
errecho(){ >&2 echo $*; }
die(){ errecho $*;	exit; }

isyes(){
	JUNK=$1
	if test -z "$JUNK"
	then
		return 1
	else
		case $JUNK in
		[yY]*)
			return 0
			;;
		*)
			return 1
	 esac
fi
}

test -f ./dot.sh || die cannot find ./dot.sh
source ./dot.sh

test ! -z "$COURSE"  || die COURSE env not found.. should be defined in ./dot.sh
test ! -z "$SESSION" || die SESSION env not found.. should be defined in ./dot.sh
test ! -z "$YEAR"    || die YEAR env not found.. should be defined in ./dot.sh

test ! -z "$1" || die usage: $0 marks file

mark=$1
csv=$mark.csv

GBIN=../../grades-bin
CDF="CSC"$COURSE$SESSION
PREFIX=$CDF

TMP=/tmp/$mark-$$
TERM=out/$PREFIX-term 

##why copy the marks out of the term file?? why not out of the marks file directly

cp $PREFIX-empty $TMP
$GBIN/gcopy -d -m $mark  $TMP $mark || die "failed to gcopy $mark from $mark to $TERM"

#ls -l $TMP

./rm-header.sh $TMP > /dev/null || die rm-header $TMP failed
./rm-drop.sh $TMP > /dev/null || die rm-drop.sh $TMP failed

# squeeze out the multiple , left over from empy mark fields
tr -s , < $TMP

# if grep 'T[123]$' $csv
# then
# 	echo maybe still need to do something about zero marks. perhaps in R
# 	echo could add grep -v into tr pipeline
# fi
