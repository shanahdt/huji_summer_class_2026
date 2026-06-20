echo "bass tenor alto soprano"
for file in *.krn
do
	for part in `seq 1 4`
	do
		#echo "writing $file.$part"
		extract -f $part $file | infot -s | grep 'Average' | awk '{print $6}' > $file.$part
	
	done
		paste $file.1 $file.2 $file.3 $file.4 #> $file.info
	# npvi=$(./nPVI $file)
# 	meter=$(grep '\*M.*/' $file | awk '{print $1}')
	# sus=$(grep -ch 'sus' $file)
	# lnt=$(grep -ch 'lnt' $file)
	# unt=$(grep -ch 'unt' $file)
	# ant=$(grep -ch 'ant' $file 	)
done
rm -f *.[1-4]
rm -f *.info