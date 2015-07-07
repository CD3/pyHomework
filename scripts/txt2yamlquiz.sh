#! /bin/bash

TMPFILE="$(mktemp -t txt_yamlquiz_shXXXX)"
trap "rm -f '$TMPFILE'" 0               # EXIT
trap "rm -f '$TMPFILE'; exit 1" 2       # INT
trap "rm -f '$TMPFILE'; exit 1" 1 15    # HUP TERM

for file in $*
do
  cat $file | tr -c "[:print:][:cntrl:]" "X" > $TMPFILE
  outfile=${file%.*}.yaml
  sed "
       s/^.*\(Phys 212.*\)/title : '\1'\nquestions :/;
       /^$/ d
       s/^[0-9]\+\.\s\(.\+\)/  - text : '\1'\n    answer:\n      choices:/;
       s/^[a-e]\+\.\s\(.\+\)/        - '\1'/;
       s/XXX/<FIXME>/g
      " $TMPFILE > $outfile
done
