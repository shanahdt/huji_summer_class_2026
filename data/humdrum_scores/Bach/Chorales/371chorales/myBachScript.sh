########This is my test script. May,2015.

extract -f 4 $1 | midi | rid -GLId | awk 'BEGIN{FS="/"}{print $2}' | 
sed 's/\-//g' | grep '^[0-9]' | sort | uniq | tail -1
