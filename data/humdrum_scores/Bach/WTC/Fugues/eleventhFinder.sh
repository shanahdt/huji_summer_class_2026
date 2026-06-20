for file in *.krn
do
	extract -f 1 *.krn | mint > /tmp/$file
	grep 'P11' /tmp/$file
done
