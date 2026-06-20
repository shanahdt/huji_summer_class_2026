for file in *.krn
do
hint $file | rid -GLId | 
grep -v = | grep -v '^-' | 
infot -s | grep redund | 
awk 'BEGIN{FS="\t"}{print $2}'
done