######There is more motion between 3 and 4 in the major mode than in the minor mode.
######THere is less motion between 2 and 3 in the major mode than in the minor mode.
######There is less motion between 5 and 6 in the major mode than in the minor mode.

#######This Script finds mi to fa and me to fa and puts them in separate files, depending on if it was found in a major or minor key.

for file in *.krn
do
	if grep -q '\*[A-G]:' $file ; then
		solfa $file | grep -v '^=' | context -n 2 | sed 's/[0-9]//g' | sed 's/[{}]//g' | sed 's/^\.//' | rid -GLId | grep 'so la' >> Major ###sol la###
	elif grep -q '\*[a-g]:' $file ; then
	 	solfa $file | grep -v '^=' | context -n 2 | sed 's/[0-9]//g' | sed 's/[{}]//g' | sed 's/^\.//' | rid -GLId | grep 'so le' >> Minor  ###sol le###
	else echo "Found no instances"
	fi
	
done
		
