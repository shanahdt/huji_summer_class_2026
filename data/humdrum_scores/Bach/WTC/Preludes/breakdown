####make everything a scale degree
deg -a *.krn | 

###get rid of comments
rid -GLId | 
##get rid of barlines and rests
grep -v '=' | grep -v 'r' | 
#### turn tabs into newlines, get rid of null data tokens, turn spaces into newlines, and get a total percentage.
tr -s '\t' '\n' | grep -v '\.' | tr -s ' ' '\n' | sortcount -p

