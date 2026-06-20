####Find a Bach Chorale in F, with a wonky Db.

file=$(grep -l 'D\-' $(grep -l 'k\[b\-\]' *.krn))
echo "phil's chord was in" $file 
