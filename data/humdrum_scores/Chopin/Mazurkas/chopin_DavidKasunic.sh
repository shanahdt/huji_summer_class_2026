####This is a function. It is created here, and is "called" below. 
keys(){
###get all major [non-accidental] keys
grep -h '\*[A-G]:' *.krn | sort | uniq -c | sort -n >> keys

###get all minor [non-accidental] keys
grep -h '\*[a-g]:' *.krn | sort | uniq -c | sort -n >> keys

####get all flat major keys 
grep -h '\*[A-G]\-:' *.krn | sort | uniq -c | sort -n >> keys

####get all flat minor keys 
grep -h '\*[a-g]\-:' *.krn | sort | uniq -c | sort -n >> keys

###get all sharp major keys
grep -h '\*[A-G]\#:' *.krn | sort | uniq -c | sort -n >> keys

###get all sharp minor keys
grep -h '\*[a-g]\#:' *.krn | sort | uniq -c | sort -n >> keys
}

####Types of inversions in the Mazurkas by numbers
inversions(){
sonority -i *.krn | rid -GLId | grep -v '=' | grep -v '*' | grep -v 'rest' | grep -v X | sort | uniq -c | sort -n >> inversions
} >> inversions

###Redundancy for all of Mazurkas.
sonority -i *.krn | rid -GLId | grep -v '=' | grep -v '*' | grep -v 'rest' | grep -v X | infot -s >> redund

###Look for harmonic intervals. 
hint *.krn | grep -v '=' | grep -v '\*' | rid -GLId | grep -v '^-' | sort | uniq -c | sort -nr >> harmonicIntervals

###Melodic intervals with the mazurkas look to be a little messy. this data needs to be cleaned up.

sed 's/\*MM//g'
keys
inversions




