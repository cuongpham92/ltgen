#!/bin/bash

for (( c=1; c<=200; c++ ))
do
	echo "user${c} user${c}" >> imap_users.txt
done
