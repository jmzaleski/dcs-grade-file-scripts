#!/bin/bash


errecho(){ >&2 echo $*; }
die(){ errecho $*;	exit; }

test $# -eq 2 || die "usage: mark out_of"

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
out_of=$2

csv=$mark.csv

GBIN=../../grades-bin
CDF="CSC"$COURSE$SESSION
PREFIX=$CDF

TMP=/tmp/$mark-$$

cp $PREFIX-empty $TMP
$GBIN/gcopy -d -m $mark  $TMP $mark || die "failed to gcopy $mark from $mark to $TMP"
$GBIN/gupdatedrops -c 9 -L $PREFIX $TMP

ls -l $TMP

#BEGIN {printf "\"\",a2\r\n"; printf "\"\",5\r\n"}

HDR1='"\"\",'$mark'\r\n"'
HDR2='"\"\",'$out_of'\r\n"'

cat > /tmp/awk <<EOF
BEGIN {printf $HDR1; printf $HDR2}
      {printf "%s,%d\r\n", \$2,\$5}
EOF

$GBIN/gpr -d -H -T -M -C -W 10 $TMP | \
	tr -d _ | \
	tr '[:upper:]' '[:lower:]' | \
	awk -f /tmp/awk > $mark.csv

ls -l $mark.csv

# more #cut -c 15-25,30-56| more

#/rm-header.sh $TMP > /dev/null || die rm-header $TMP failed
#./rm-drop.sh $TMP > /dev/null || die rm-drop.sh $TMP failed

# squeeze out the multiple , left over from empy mark fields
#tr -s , < $TMP

# if grep 'T[123]$' $csv
# then
# 	echo maybe still need to do something about zero marks. perhaps in R
# 	echo could add grep -v into tr pipeline
# fi
