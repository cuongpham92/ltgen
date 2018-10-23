#!/bin/bash

for (( c=1; c <=100; c++ ))
do
	#echo "user${c} user${c} group$((${c}/10))" >> users.txt
	if (( ${c} % 10 == 0 ))
	then
		echo "smbuser${c} smbuser${c} group$((${c}/10-1))" >> smb_users.txt
	else
		echo "smbuser${c} smbuser${c} group$((${c}/10))" >> smb_users.txt
	fi
done
