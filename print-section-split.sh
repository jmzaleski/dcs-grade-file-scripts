for section in 0101 5101
do
	for split in aa ab ac
	do
		echo $section $split $(head -1 tutorial-$section-$split | cut -d, -f2) -  $(tail -1 tutorial-$section-$split | cut -d, -f2)
	done
done
