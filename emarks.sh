#!/bin/bash

# idea here is to copy calculated term mark to fin, then run this script to make the .csv file to submit

errecho(){ >&2 echo $*; }
die(){ errecho $*;	exit; }

test -f ./dot.sh || die cannot find ./dot.sh
source ./dot.sh

CLASS="CSC$COURSE$SESSION"
test -f "$CLASS"-classlist || die "CLASS is probably wrong, no file $CLASS-classlist"

USAGE="usage: $0 final-grades-file"

test "$#" -eq 1 || die $USAGE
FINAL_GRADES_FILE="$1"
test -f "$FINAL_GRADES_FILE" || die cannot stat final-grades-file $FINAL_GRADES_FILE

#the grade in the grades file we want to submit. I typically use fin/100
MARK=fin

test -f $FINAL_GRADES_FILE  || die "no file $FINAL_GRADES_FILE"

read -p "hit enter to prepare emarks .csv file to submit mark '$MARK' from grades file '$FINAL_GRADES_FILE': " junk

set -x
../../grades-bin/gsub -d -m $MARK $FINAL_GRADES_FILE > $CLASS-emarks.csv || die "gsub -d -m $MARK failed"

ls -l $CLASS-emarks.csv
