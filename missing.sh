#!/bin/bash

# print out the marks in a marks file that are "missing".. zero or blank.
# challenge is that gpr has no way of selecting blank marks

die(){ echo $*;	exit; }

GBIN=../../grades-bin

test ! -z "$1" || die usage: $0 marks file
test -f $1 || die $0: $1 not a marks file

test -d $GBIN || die no grades bin in $GBIN

mf=$1

$GBIN/glint $mf || die "failed to glint $mf"

test -f ./dot.sh || die cannot find ./dot.sh
source ./dot.sh

test ! -z "$COURSE" || die COURSE env not found.. should be defined in ./dot.sh
test ! -z "$SESSION" || die SESSION env not found.. should be defined in ./dot.sh


#^.........1..........2.........3.........4.........5
#^1........0..........0.........0.........0.........0
#0999054865    C4Qinyix             0101      MS        5         

PREFIX="CSC"$COURSE$SESSION

test -f $PREFIX || die $0: cannot find class list $PREFIX

TMP=/tmp/$mf$$

cp $mf $TMP
#$GBIN/gcopy -m $mf $TMP

#this sets the drop column for gonzo students
$GBIN/gupdatedrops -c 9 -L $PREFIX $TMP

# -d excludes drops
# -H no header
# -C no comment lines
# -W 10 sets the column width to 10.. except for student number, which is 15
# -T no statistics
# -M no titles or blank lines
#
#../grades-bin/gpr -d -H -T -M -C -W 10 $TMP | cut -c 15-25,35-37,45-46 | grep -v [1-9]$

$GBIN/gpr -d -H -T -M -C -W 10 $TMP | cut -c 15-25,66-69 | grep -v '[1-9]$'
