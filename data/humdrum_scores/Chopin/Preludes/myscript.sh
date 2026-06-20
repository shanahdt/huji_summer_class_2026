for file in *.krn
do
	number=$(grep 'OTL' $file | awk 'BEGIN{FS="\:"}{print $2}' | awk '{print $7, $8}')
	tempo=$(grep 'MM' $file | 
	sed 's/\*MM//g' | 
	awk '{if ($1 > 60){print $1} else {print "toooooooooo slow"}}' | head -1)
echo "The tempo of $number is $tempo"
done

