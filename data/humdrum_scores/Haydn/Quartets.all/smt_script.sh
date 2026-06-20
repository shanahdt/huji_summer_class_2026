####Step 1: Find all rests in lower three voices.
grep 'r	r	r	r' *.metpos.metpos.metpos.solfa | grep -v 're' | grep -v 'r[ia]' | awk 'NF == 5'

####Step 2: OK, let's just look for rests in three lower voices.

grep '^r	r	r' *.metpos.metpos.metpos.solfa | grep -v 're' | grep -v 'r[ia]' | awk 'NF == 5'

####Woah nelly, that's a lot. Let's make it less greedy..

#####Let's talk about type 1 vs. type 2 errors. (Mike)

###PATTERN FILE:

^re.*(1|2)$
r       r       r       
=
so

