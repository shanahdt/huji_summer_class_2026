###looping over every kern file.

for file in *.krn
	do
		#### creating a sequence of 1 4
	for part in $(seq 1 4) 
		do
			extract -f $part $file > $file.$part
			entropy=$(infot -s $file.$part |
				grep 'Average' | 
				awk '{print $6}')
			npvi=$(./npVI $file.$part)
			meter=$(grep '\*M.*/' $file.$part | awk '{print $1}')
		printf "$file\t $part\t $entropy\t $npvi\t $meter\n" 
	done 
done > kern_data

##loop over every harm file.
for nct in *.hrm
	do
		###loop over the voices with ncts labeled.
		for voice in $(seq 2 5)
		do
			### give counts of various ncts.
			sus=$(extract -f $voice $nct | grep -ch 'sus')
			lnt=$(extract -f $voice $nct | grep -ch 'lnt')
			unt=$(extract -f $voice $nct | grep -ch 'unt')
			ant=$(extract -f $voice $nct | grep -ch 'ant')
			printf "$nct\t $part\t $sus\t $lnt\t $unt\t $ant\n" 
		done
	done | grep -v 'all' > harm_data
	printf "file\tpart\tentropyt\npvi\tmeter\tfile\tpart\tsus\tlnt\tunt\tant\n" > my_data.tsv
	paste kern_data harm_data >> my_data.tsv
	rm -f *.[1-4]
	rm -f harm_data
	rm -f kern_data
