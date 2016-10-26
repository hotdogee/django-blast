#!/bin/bash 
#
#  Copy dot files to a dir. 
#
#  Run in a vagrant VM copies dot files to $HOME
#
#  else copies them to the argument dir 
FILES=""

for f in .profile .bashrc .vimrc .inputrc dotcp.sh 
do
    if [[ -f $f ]] ; then 
        FILES="$FILES $f"
    fi
done

if [[ -n $FILES ]] ; then
    if who | grep vagrant > /dev/null ; then 
        cp $FILES ~
    else
        cd ~
        if [[ -d $1 ]] ; then  
            cp $FILES $1
        fi
    fi
fi
