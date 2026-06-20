
for file in *.krn
    do
    # cello=$(extract -f 1 $file | deg -a | infot -s | grep Average | awk '{print $6}')
    # viola=$(extract -f 2 $file | deg -a | infot -s | grep Average | awk '{print $6}')
    # violin2=$(extract -f 3 $file | deg -a | infot -s | grep Average | awk '{print $6}')
    # violin1=$(extract -f 3 $file | deg -a | infot -s | grep Average | awk '{print $6}')
    year=$(grep 'ODT' $file)
    printf "$year\n"
    done
