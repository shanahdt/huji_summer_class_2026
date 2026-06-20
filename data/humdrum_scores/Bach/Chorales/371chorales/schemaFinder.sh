rm -f /tmp/*.bass /tmp/*.soprano /tmp/outerVoices rm -f /tmp/concurrentSchema

for file in *.krn 
do 
	deg $file > /tmp/$file.deg
	extract -f 1,4 /tmp/$file.deg > /tmp/$file.outer
	cleave -i '**deg' -d '@' -o '**deg' /tmp/$file.outer > /tmp/$file.cleaved
	grep -v '=' /tmp/$file.cleaved | deg | grep -v '\.' | rid -GLId |
	sed 's/[XLJ\;]//g' | sed 's/\[//g' | sed 's/\]//g' | context -n 8 >> /tmp/$file.concurrentSchema
	# 
	# extract -f 4 $file | 
	# deg | grep -v "=" | grep -v "\." | rid -GLId | 
	# sed 's/[XLJ\;]//g' | sed 's/\[//g' | sed 's/\]//g' > /tmp/$file.soprano
done



sortcount -p /tmp/concurrentSchema > concurrentSchema1.txt
open concurrentSchema1.txt
