ls *.krn >> /tmp/list

for file in *.krn
do 
	sonority $file | grep -v '=' | infot -s | grep -i $1 

done | awk '{print $NF}' >> /tmp/numbers

assemble /tmp/list /tmp/numbers > data.txt
rm /tmp/list /tmp/numbers
open data.txt
