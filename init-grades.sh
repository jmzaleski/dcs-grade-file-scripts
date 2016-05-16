#!/bin/bash 

# shell script to kick off grades file for a class.
# get the crummy text file from CDF and wack it into being a grades file

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

test ! -z "$COURSE" || die COURSE env not found.. should be defined in ./dot.sh
test ! -z "$SESSION" || die SESSION env not found.. should be defined in ./dot.sh

# class list from CDF
CDF="CSC"$COURSE$SESSION
HDR="csc"$COURSE"-header.txt"

test -f $HDR || die cannot stat $HDR

TMP2=/tmp/$CDF$$
TMP_CLASSLIST=/tmp/$CDF"-classlist"$$

AWK_SCRIPT=/tmp/AWK$$

# "base" file contains student number and cdf id with funky blanks as grades program likes
BODY_BASE=$CDF-base.txt

#"grades" file has header above base"
EMPTY=$CDF-empty

#just the emails in cdf id sorted order
EMAILS=$CDF-email

ssh matz@cdf.utoronto.ca test -f /u/csc/instructors/emaillists/$CDF \
      || die cdf cannot stat: /u/csc/instructors/emaillists/$CDF

type backfilename.sh > /dev/null || die $0 depends on backfilename.sh, which is a matz personal script

#echo SKIP: scp matz@cdf.utoronto.ca:/u/csc/instructors/emaillists/$CDF .

set -e

read -p "backup  $CDF ? >" JUNK
#exit $(isyes "$JUNK")

# if isyes "$JUNK"
# then
# 	test -f $CDF && cp  $CDF $(backfilename.sh $CDF)
# 	test -f $CDF-classlist && cp $CDF-classlist $(backfilename.sh $CDF-classlist)
# fi

BACKUP="$CDF $CDF-classlist $EMPTY $CDF-5char-cdfid $BODY_BASE $CDF-ID-cdfuserid-map.txt"

if isyes "$JUNK"
then
	for file in $BACKUP
	do
		bf=$(backfilename.sh $file)
		test -f $file && cp -p $file $bf
		ls -l $bf
	done
fi

/bin/rm -f $BODY_BASE $EMPTY $EMAILS

scp matz@cdf.utoronto.ca:/u/csc/instructors/emaillists/$CDF $TMP2
scp matz@cdf.utoronto.ca:/u/csc/instructors/classlists/$CDF $TMP_CLASSLIST

# email file has nasty format with email following (
# example line:
#c2liangx  999943511 (Liang, Xin Yi) xinyi.liang@mail.utoronto.ca

# -classlist has section in $4
# c1dongxi  999220542 LEC 5101 Dong             Xiaochuan

# sort them both by CDF id, 
#
sort $TMP2 > $CDF                          #this one has email column
sort $TMP_CLASSLIST > $CDF-classlist       #this one has section

# weird caveat is that glint thinks name must be longer than 5 chars?? pad a few with _
#

set -x
echo cdf userids that are shorter than 5 chars..
awk 'length($1) <= 5 {print $1}' $CDF > $CDF-5char-cdfid

# base won't expand the $ if you quote the EOF in 'EOF'
cat <<'EOF' > $AWK_SCRIPT
#base grades file is student ID, cdf id
length($1)<5  {print $2"    "$1"__"; next }
                  {print $2"    "$1}
EOF

# just the lecture section..
awk '{print $4}' $CDF-classlist > $BODY_BASE-section

# cdfid, student num, with magic grades file blanks for key fields
awk -f $AWK_SCRIPT $CDF > /tmp/$BODY_BASE$$ || die $AWK_SCRIPT blows it

# add column for lecture section.. note (temporary) blank char separator for sort
# sort it, first by section id, then by cdfid, then change blank sep to comma.
# futz section blank sep away, add TA field..
awk -f $AWK_SCRIPT $CDF \
	| paste -d' ' - $BODY_BASE-section \
	| sort --key=3,3 --key=2.2  \
	| sed -e 's/ 0101/,0101,TA1/' \
	> $BODY_BASE 

#	| sed -e 's/ 5101/,5101,TA1,/' \

#shouldn't be any of these
awk 'length($1) <= 5 {print $1}' $BODY_BASE || die we should have fixed short cdf ids

#but the lecture section id column should be comma separated..

cat $HDR $BODY_BASE > "$EMPTY"

../../grades-bin/glint "$EMPTY"

#create a student number to CDF id map file (for quiz marking python script)
tr -s '[:blank:]' < $BODY_BASE | tr [:blank:] , > $CDF-ID-cdfuserid-map.txt

#make an email list in cdf id order
sort $CDF | sed -e 's/(.*)//'  | awk '{print $3}' > $EMAILS

ls -ltr $HDR $CDF $CDF-ID-cdfuserid-map.txt $BODY_BASE $EMPTY $EMAILS

read -p 'continue to tutorials? interrupt to bail..' JUNK

# use paste to create a CSV file with stud no, cdfid, email
#temp file containing student no, cdfid

awk '{printf "%s,%s\n", $1,$2}' $BODY_BASE | paste -d, -  $BODY_BASE-section > sections

grep '0101$' sections > section-0101.csv
grep '5101$' sections > section-5101.csv


#now break up into tutorial sized chunks
#TODO: automate the line count. no time now
LINES=29
wc -l section*.csv

echo TODO: WARNING LINES to split hardcoded to $LINES
read -p "interrupt to bail before split' JUNK
split -l $LINES section-0101.csv tutorial-0101-
split -l $LINES section-5101.csv tutorial-5101-




