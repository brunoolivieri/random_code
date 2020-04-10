#!/bin/bash

#=================================================================================
# Automatically add last modified date to .RST files according to last commit date
#=================================================================================

# Parallel runs in N-process batches. Default = 4 
PARALLEL=${1:-4}


# Insert last updated date from last commit date of each file
update_file(){

	echo "Inserting last updated tag on $f"

    commit_date=`git log -n 1 --date=short --pretty=format:%cd -- $1`

	echo "" >> $1
    echo "" >> $1
    echo '*Page last edited on ' "$commit_date"'*' >> $1
	
}

# Runs for each file at PARALLEL at time (thanks to https://unix.stackexchange.com/questions/103920/parallelize-a-bash-for-loop)
for f in `find . -iname "*.rst"`; do

   ((i=i%PARALLEL)); ((i++==0)) && wait
   update_file $f & 
		
done

echo 'Finished to insert last edited date.'

exit 0

