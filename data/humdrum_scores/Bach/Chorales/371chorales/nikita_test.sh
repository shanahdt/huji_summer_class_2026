for chorale in *.krn
do
	harmonic_entropy=$(sonority $chorale | infot -s | grep 'Average' | awk '{print $6}')
	Average_nPVI=$(nPVI $chorale)
	root_position=$(sonority -i $chorale | grep -v '[=X\*]' | rid -GLId | sortcount -p | grep '0$' | awk '{print $1}')
	meter=$(grep '\*M' $chorale | grep -v 'MM' | awk '{print $1}' | sed 's/\*M//g' | tr '\n' ' ' | sed 's/ //g')
	rhythm_entropy=$(dur -x $chorale | rid -GLId | grep -v '^=' | tr '\t' '_' | infot -s | grep 'Average' | awk '{print $6}')

	printf "$harmonic_entropy,$Average_nPVI,$root_position,$meter,$rhythm_entropy\n"
done
