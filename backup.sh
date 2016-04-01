#!/bin/bash

errecho(){ >&2 echo $*; }
die(){ errecho $*;	exit; }

isyes(){
	prompt="$1 ? [yY]>" 
	read -p "$prompt" JUNK
	if test -z "$JUNK"; then
		return 1
	fi
	case $JUNK in
	[yY]*)
		return 0
		;;
	*)
		return 1
    esac
}

test -f ./dot.sh || die cannot find ./dot.sh
source ./dot.sh

test ! -z "$COURSE" || die COURSE env not found.. should be defined in ./dot.sh
test ! -z "$SESSION" || die SESSION env not found.. should be defined in ./dot.sh
test ! -z "$YEAR" || die YEAR env not found.. should be defined in ./dot.sh

# class list from CDF
#HDR="csc"$COURSE"-header.txt"

DEST=~/doc/skule/instruct/backups/"CSC"$COURSE$SESSION-$YEAR
SRC=~/Dropbox/CSC/$COURSE 

test -d $SRC || die "cannot stat SRC $SRC"
test -d $DEST || die "cannot stat DEST $DEST"

mkdir -p $DEST

if test ! -d "$1"
then
	workspace=$SRC
else
	workspace=$1
fi

#DIR
d=`basename $workspace`

destdir=`date +$DEST-%h%d`

#stupid bloody trailing / (or would make a directory called $SRC-backup/$SRC

VERB="--progress -v"

LOCAL_BACKUP=$DEST/$d-backup
RSYNC_EXCLUDE='--exclude=video/ --exclude=previous-years/'
RSYNC_CMD1="rsync $RSYNC_EXCLUDE  -a --delete $VERB $SRC/ $LOCAL_BACKUP"

######################### always run local incremental backup #############


isyes "about to run $RSYNC_CMD1" 

echo '---------------------------------'
echo running $RSYNC_CMD1
eval $RSYNC_CMD1
echo returned $?
echo '---------------------------------'

echo; 

du -sh $workspace
du -sh $LOCAL_BACKUP

echo

###################### local full ################################3

if test -d $destdir
then
	for i in a b c d e f g h i j k l m n o p q r s t u v w x y z
	do
		if test ! -d $destdir.$i
		then
			destdir=$destdir.$i
			#remote_destdir=$remote_destdir.$i
			break
		else
			echo $destdir.$i exists already, moving on..
		fi
	done
fi

#assertion, more or less..
if test -f $destdir
then
    echo $0: Oh no, bug in script $destdir already exists. exit without copy
    exit 2
fi



RSYNC_CMD="rsync $RSYNC_EXCLUDE -a $VERB $workspace/ $destdir"


######################### optionally run local full  backup #############

cmd="$RSYNC_CMD $RSYNC_EXCLUDE_SAVE_SPACE"

echo about to run: $cmd
echo return to continue..

read  -t 30 -p '> ' junk ############# block on read ##########
echo running..
eval $cmd

du -sh $workspace
du -sh $destdir

echo dest look right?

echo
echo 'two rsync commands run to backup:'
echo
echo $RSYNC_CMD1
echo
echo $cmd


