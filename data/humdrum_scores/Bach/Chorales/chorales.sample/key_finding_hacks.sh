for i in $1
do
	first_bass=$(rid -GLId $i | grep -A 1 '=1' | tail -1 | 
	cut -f 1 | sed 's/[0-9]//g' | sed 's/[;,\}]//g')
	last_bass=$(rid -GLId $i | grep -B 1 '==' | head -1 | 
	cut -f 1 | sed 's/[0-9]//g' | sed 's/[;,\}]//g')
	euclidean=$(keycor -e $i | sed 's/The.*://g')
	cor=$(keycor $i | sed 's/The.*://g')
	most_common=$(pc -x $i | 
	rid -GLId | tr -s '\t' '\n'  | grep -v '[\.=]' | sortcount | head -1)
 	printf "$first_bass\t$last_bass\t$most_common\t$euclidean\t$cor\n"
done