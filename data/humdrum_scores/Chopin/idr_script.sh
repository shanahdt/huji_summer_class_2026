for file in $1
do 
	awk '{for(i=1;i<=NF;i++)if($i ~ /P1/)x++;print x;x=0}' $1> p1.tmp 
	awk '{for(i=1;i<=NF;i++)if($i ~ /m3/)x++;print x;x=0}' $1> m3.tmp
	awk '{for(i=1;i<=NF;i++)if($i ~ /M3/)x++;print x;x=0}' $1> maj3.tmp
	awk '{for(i=1;i<=NF;i++)if($i ~ /P[45]/)x++;print x;x=0}' $1 > p45.tmp
	awk '{for(i=1;i<=NF;i++)if($i ~ /m2/)x++;print x;x=0}' $1> m2.tmp
	awk '{for(i=1;i<=NF;i++)if($i ~ /M2/)x++;print x;x=0}' $1> maj2.tmp
	awk '{for(i=1;i<=NF;i++)if($i ~ /A4/)x++;print x;x=0}' $1 > tt.tmp
	awk '{for(i=1;i<=NF;i++)if($i ~ /d5/)x++;print x;x=0}' $1 > tt1.tmp
	assemble tt.tmp tt1.tmp | awk '{$1 + $2}' > tt2.tmp
	##### something is happening here.
	awk '{for(i=1;i<=NF;i++)if($i !~ /P1|m3|M3|P4|P5|m2|M2|A4|d5/)x++;print x;x=0}' $1 > diss.tmp
done

assemble p1.tmp m3.tmp maj3.tmp p45.tmp m2.tmp maj2.tmp tt2.tmp diss.tmp > mod_icv.tmp

awk '{FS="\t"}{print $1+$2+$3+$4+$5+$6+$7+$8}' mod_icv.tmp > total_sum.tmp
awk '{FS="\t"}{print $5+$6+$7+$8}' mod_icv.tmp > diss_total.tmp

assemble diss_total.tmp total_sum.tmp | awk '{if ($1 == 0) {print "0"} else print $1/$2}'
