timebase -t $1 $2 | metpos | hint -l | grep '[1|2]$' | grep -v '=' | rid -GLId | sortcount -p


           context -b '\(' -e '\)' -o '[=r]'