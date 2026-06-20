###this script loops through all kern files, and 
###looks at the most common melodic transition in a given voice (here the bass)
### and creates a key variable. It then prints the file name, the key, and the
### most used interval.

for file in *.krn
do
	###most used interval
	top_interval=$(extractx -f 1 $file | deg -a | rid -GLId | grep -v '[=\.r>]' | context -n 2 | sortcount -p | head -1)
	###key of the piece
	key=$(grep '\*.*:' $file | awk '{print $1}')
	###print everything out nicely.
	printf "$file\t$key\t$top_interval\n"
	
done



