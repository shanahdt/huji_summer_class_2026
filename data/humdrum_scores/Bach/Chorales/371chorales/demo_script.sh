#### our code

### cluster some bach basslines.

for file in *.bass
    do  

    entropy=$(infot -s $file | grep "Average information" | awk '{print $6}')
    npvi=$(npvi $file)
    rests=$(census -k $file | grep "rests")
    printf "$file, $entropy, $npvi, $rests\n"
    done    